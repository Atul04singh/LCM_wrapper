from typing import List, Union, AsyncGenerator, Optional, Any, Dict, Callable
import asyncio
import json
from .config import ConfigResolver, LCMConfig
from .base import Message, ProviderRuntime
from .registry import ProviderRegistry

class AI:
    def __init__(self, model_name: Optional[str] = None, **options):
        # Resolve config
        overrides = options.copy()
        if model_name:
            overrides["model"] = model_name
        self.config: LCMConfig = ConfigResolver.resolve(overrides)
        
        # Internal state
        self._provider: Optional[ProviderRuntime] = None
        self.history: List[Message] = []
        self.middlewares: List[Callable] = []

    async def _get_provider(self) -> ProviderRuntime:
        if self._provider is None:
            provider_name = self.config.provider.lower()
            
            # Ensure built-in providers are loaded if requested
            if provider_name == "ollama":
                from .providers.ollama import OllamaProvider
            elif provider_name == "huggingface":
                from .providers.huggingface import HuggingFaceProvider
                
            provider_cls = ProviderRegistry.get(provider_name)
            if not provider_cls:
                raise ValueError(f"Unknown provider: {self.config.provider}. Loaded providers: {ProviderRegistry.list_providers()}")
            self._provider = provider_cls(self.config)
        return self._provider

    # --- Catchy API (Async) ---

    async def ask(self, input: Union[str, List[Message]], **params) -> str:
        """Catchy version of chat."""
        messages = self._normalize_input(input)
        
        # 1. Middleware (Pre-processing)
        for mw in self.middlewares:
            messages = await mw(messages) if asyncio.iscoroutinefunction(mw) else mw(messages)

        # 2. Cache check
        if self.config.cache:
            from .cache import cache
            cache_key = [self.config.model, self.config.provider, messages, params]
            if cached := cache.get(cache_key):
                if self.config.verbose:
                    print(f"✨ Cache hit for {self.config.model}")
                return cached

        # 3. Management of internal history (remember)
        if hasattr(self, '_use_history') and self._use_history:
            self.history.extend(messages)
            current_messages = self.history
        else:
            current_messages = messages

        provider = await self._get_provider()
        
        if self.config.verbose:
            print(f"🤖 AI is thinking with {self.config.model}...")

        response = await provider.chat(current_messages, **params)
        
        # 4. Cache save
        if self.config.cache:
            cache.set(cache_key, response)

        if hasattr(self, '_use_history') and self._use_history:
            self.history.append({"role": "assistant", "content": response})
            
        return response

    async def flow(self, input: Union[str, List[Message]], **params) -> AsyncGenerator[str, None]:
        """Catchy version of stream."""
        messages = self._normalize_input(input)
        provider = await self._get_provider()
        
        if self.config.verbose:
            print(f"🌊 AI is flowing tokens...")

        async for token in provider.stream(messages, **params):
            yield token

    async def extract(self, input: str, schema: Optional[Dict] = None, **params) -> Dict:
        """Extract structured data (JSON)."""
        prompt = f"{input}\n\nRespond ONLY with valid JSON."
        if schema:
            prompt += f" Follow this schema: {json.dumps(schema)}"
        
        response = await self.ask(prompt, **params)
        try:
            # Basic JSON extraction from markdown or raw text
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            return json.loads(response)
        except Exception as e:
            if self.config.verbose:
                print(f"❌ Failed to extract JSON: {e}")
            return {"error": "Failed to parse JSON", "raw": response}

    async def point(self, text: str) -> List[float]:
        """Catchy version of embed."""
        provider = await self._get_provider()
        return await provider.embed(text)

    def remember(self):
        """Enable context memory."""
        self._use_history = True
        return self

    def forget(self):
        """Clear context memory."""
        self.history = []
        self._use_history = False
        return self

    async def peek(self):
        """Friendly health check."""
        is_healthy = await self.health()
        status = "Ready 🚀" if is_healthy else "Unavailable 🔴"
        print(f"--- AI Status ---")
        print(f"Model:  {self.config.model}")
        print(f"Provider: {self.config.provider}")
        print(f"Status:  {status}")
        print(f"Device:  {self.config.device}")

    # --- Sync Wrappers ---

    def ask_sync(self, input: Union[str, List[Message]], **params) -> str:
        return asyncio.run(self.ask(input, **params))

    def flow_sync(self, input: Union[str, List[Message]], **params):
        import queue
        import threading

        q = queue.Queue()
        done = object()

        async def _run():
            try:
                async for token in self.flow(input, **params):
                    q.put(token)
            except Exception as e:
                q.put(e)
            finally:
                q.put(done)

        t = threading.Thread(target=lambda: asyncio.run(_run()))
        t.start()

        try:
            while True:
                item = q.get()
                if item is done:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            t.join()

    # --- Fluent API (Chaining) ---

    def pipe(self, input: str):
        """Start a chainable task flow."""
        return Chain(self, input)

    # --- Middleware ---

    def use(self, middleware: Callable):
        """Register middleware."""
        self.middlewares.append(middleware)
        return self

    # --- Helpers ---

    async def health(self) -> bool:
        try:
            provider = await self._get_provider()
            return await provider.health()
        except Exception:
            return False

    def _normalize_input(self, input: Union[str, List[Message]]) -> List[Message]:
        if isinstance(input, str):
            return [{"role": "user", "content": input}]
        return input

class Chain:
    """Helper class for fluent API chaining."""
    def __init__(self, ai: AI, initial_input: str):
        self.ai = ai
        self.tasks = []
        self.initial_input = initial_input

    def ask(self, prompt_template: Optional[str] = None):
        self.tasks.append(("ask", prompt_template))
        return self

    def then(self, prompt_template: Optional[str] = None):
        return self.ask(prompt_template)

    def extract(self, schema: Optional[Dict] = None):
        self.tasks.append(("extract", schema))
        return self

    @property
    def jsononly(self):
        return self.extract()

    async def run(self):
        result = self.initial_input
        for task_type, payload in self.tasks:
            if task_type == "ask":
                prompt = payload.replace("${prev}", result) if payload and "${prev}" in payload else f"{result}\n{payload or ''}"
                result = await self.ai.ask(prompt)
            elif task_type == "extract":
                result = await self.ai.extract(result, payload)
        return result

    def __await__(self):
        return self.run().__await__()

    def run_sync(self):
        return asyncio.run(self.run())
