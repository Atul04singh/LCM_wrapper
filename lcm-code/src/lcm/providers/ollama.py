from typing import List, AsyncGenerator
import httpx
from ..base import ProviderRuntime, Message
from ..config import LCMConfig
from ..errors import RuntimeUnavailableError

class OllamaProvider(ProviderRuntime):
    def __init__(self, config: LCMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"

    async def chat(self, messages: List[Message], **params) -> str:
        await self._ensure_model()
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.config.model,
                        "messages": messages,
                        "stream": False,
                        "options": params
                    }
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise RuntimeUnavailableError(f"Could not connect to Ollama at {self.base_url}", "Is Ollama running? Run `ollama serve`.")

    async def stream(self, messages: List[Message], **params) -> AsyncGenerator[str, None]:
        await self._ensure_model()
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "stream": True,
                    "options": params
                }
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                yield data["message"]["content"]
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

    async def embed(self, text: str) -> List[float]:
        await self._ensure_model()
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.config.model, "prompt": text}
            )
            resp.raise_for_status()
            return resp.json()["embedding"]

    async def _ensure_model(self):
        """Checks if model exists, if not pulls it."""
        if not await self._check_model_exists():
            print(f"Model {self.config.model} not found locally. Pulling...")
            await self.pull()

    async def _check_model_exists(self) -> bool:
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                models = resp.json().get("models", [])
                return any(m["name"] == self.config.model or m["name"].split(":")[0] == self.config.model for m in models)
            except Exception:
                return False

    async def pull(self):
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json={"name": self.config.model}
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if data.get("status") == "success":
                            break

    async def health(self) -> bool:
        try:
            return await self._check_model_exists()
        except Exception:
            return False
