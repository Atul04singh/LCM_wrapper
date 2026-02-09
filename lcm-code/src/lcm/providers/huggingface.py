import os
import httpx
import json
from typing import List, AsyncGenerator, Optional, Any
from ..base import ProviderRuntime, Message
from ..config import LCMConfig
from ..errors import AuthError, RuntimeUnavailableError

class HuggingFaceProvider(ProviderRuntime):
    def __init__(self, config: LCMConfig):
        self.config = config
        self._runtime: Optional[ProviderRuntime] = None

    async def _get_runtime(self) -> ProviderRuntime:
        if self._runtime is None:
            if self.config.runtime == "local":
                self._runtime = HFLocalRuntime(self.config)
            else:
                self._runtime = HFCloudRuntime(self.config)
        return self._runtime

    async def chat(self, messages: List[Message], **params) -> str:
        runtime = await self._get_runtime()
        return await runtime.chat(messages, **params)

    async def stream(self, messages: List[Message], **params) -> AsyncGenerator[str, None]:
        runtime = await self._get_runtime()
        async for token in runtime.stream(messages, **params):
            yield token

    async def embed(self, text: str) -> List[float]:
        runtime = await self._get_runtime()
        return await runtime.embed(text)

    async def health(self) -> bool:
        try:
            runtime = await self._get_runtime()
            return await runtime.health()
        except Exception:
            return False

class HFCloudRuntime(ProviderRuntime):
    def __init__(self, config: LCMConfig):
        self.config = config
        self.token = config.hf_token
        self.model = config.hf_model or config.model
        self.base_url = f"https://api-inference.huggingface.co/models/{self.model}"

    async def chat(self, messages: List[Message], **params) -> str:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                # Note: The Inference API format varies, but usually follows this for conversational models
                payload = {
                    "inputs": messages[-1]["content"], # Simplified for now, real implementation needs template
                    "parameters": params,
                    "options": {"wait_for_model": True}
                }
                resp = await client.post(self.base_url, json=payload, headers=headers)
                if resp.status_code in [401, 403]:
                    raise AuthError(f"Hugging Face auth failed for model {self.model}", "Provide a valid HF_TOKEN in your .model file or environment.")
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    return data[0].get("generated_text", "")
                return str(data)
            except (httpx.ConnectError, httpx.TimeoutException):
                raise RuntimeUnavailableError(f"Hugging Face Inference API is unreachable for {self.model}", "Check your internet connection or model ID.")

    async def stream(self, messages: List[Message], **params) -> AsyncGenerator[str, None]:
        # Inference API supports streaming via different parameters
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            payload = {
                "inputs": messages[-1]["content"],
                "parameters": {**params, "stream": True},
                "options": {"wait_for_model": True}
            }
            async with client.stream("POST", self.base_url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        data = json.loads(line[5:])
                        if "token" in data:
                            yield data["token"].get("text", "")

    async def embed(self, text: str) -> List[float]:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        # Using a dedicated embedding model or the default one
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                self.base_url,
                json={"inputs": text},
                headers=headers
            )
            resp.raise_for_status()
            return resp.json()

    async def health(self) -> bool:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(self.base_url)
            return resp.status_code != 404

class HFLocalRuntime(ProviderRuntime):
    def __init__(self, config: LCMConfig):
        self.config = config
        self.pipeline = None
        self.model_id = config.hf_model or config.model

    def _ensure_pipeline(self):
        if self.pipeline is None:
            from transformers import pipeline
            import torch
            
            device = self.config.device
            if device == "auto":
                device = 0 if torch.cuda.is_available() else -1
            elif device == "cpu":
                device = -1
            elif device == "cuda":
                device = 0
                
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_id,
                device=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True
            )

    async def chat(self, messages: List[Message], **params) -> str:
        self._ensure_pipeline()
        # transformers pipeline handles chat templates in newer versions
        prompt = self.pipeline.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        outputs = self.pipeline(
            prompt,
            max_new_tokens=params.get("max_tokens", 512),
            do_sample=True,
            temperature=params.get("temperature", 0.7),
            **{k: v for k, v in params.items() if k not in ["max_tokens", "temperature"]}
        )
        generated_text = outputs[0]["generated_text"]
        # Remove the prompt from the output
        return generated_text[len(prompt):].strip()

    async def stream(self, messages: List[Message], **params) -> AsyncGenerator[str, None]:
        self._ensure_pipeline()
        from transformers import TextIteratorStreamer
        from threading import Thread
        
        prompt = self.pipeline.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.pipeline.tokenizer(prompt, return_tensors="pt").to(self.pipeline.device)
        
        streamer = TextIteratorStreamer(self.pipeline.tokenizer, skip_prompt=True)
        generation_kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=params.get("max_tokens", 512),
            do_sample=True,
            temperature=params.get("temperature", 0.7),
        )
        
        thread = Thread(target=self.pipeline.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        for new_text in streamer:
            yield new_text

    async def embed(self, text: str) -> List[float]:
        # For embeddings, we'd typically use a SentenceTransformer or specific model
        # Simplified: Use the pooler output of the model if it supports it, 
        # but better to let user specify a dedicated embedding model.
        raise NotImplementedError("Local embeddings require a dedicated embedding model/pipeline.")

    async def health(self) -> bool:
        # If we can import transformers and find the model files, we are healthy
        try:
            from huggingface_hub import model_info
            model_info(self.model_id)
            return True
        except Exception:
            return False
