from typing import List, Union, AsyncGenerator, Optional, Any
from .config import ConfigResolver, LCMConfig
from .base import Message, ProviderRuntime

class Model:
    def __init__(self, model_name: Optional[str] = None, **options):
        # Resolve config
        overrides = options.copy()
        if model_name:
            overrides["model"] = model_name
        self.config: LCMConfig = ConfigResolver.resolve(overrides)
        
        # Lazy provider initialization
        self._provider: Optional[ProviderRuntime] = None

    async def _get_provider(self) -> ProviderRuntime:
        if self._provider is None:
            self._provider = await self._instantiate_provider()
        return self._provider

    async def _instantiate_provider(self) -> ProviderRuntime:
        # Import runtimes lazily to avoid heavy dependencies if not used
        if self.config.provider == "ollama":
            from .providers.ollama import OllamaProvider
            return OllamaProvider(self.config)
        elif self.config.provider == "huggingface":
            from .providers.huggingface import HuggingFaceProvider
            return HuggingFaceProvider(self.config)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")

    async def chat(self, input: Union[str, List[Message]], **params) -> str:
        messages = self._normalize_input(input)
        provider = await self._get_provider()
        return await provider.chat(messages, **params)

    def chat_sync(self, input: Union[str, List[Message]], **params) -> str:
        """Synchronous version of chat."""
        import asyncio
        return asyncio.run(self.chat(input, **params))

    async def stream(self, input: Union[str, List[Message]], **params) -> AsyncGenerator[str, None]:
        messages = self._normalize_input(input)
        provider = await self._get_provider()
        async for token in provider.stream(messages, **params):
            yield token

    def stream_sync(self, input: Union[str, List[Message]], **params):
        """Synchronous version of stream."""
        import asyncio
        import queue
        import threading

        q = queue.Queue()
        done = object()

        async def _run():
            try:
                async for token in self.stream(input, **params):
                    q.put(token)
            except Exception as e:
                q.put(e)
            finally:
                q.put(done)

        # Run the async generator in a dedicated thread with its own loop
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

    async def embed(self, text: str) -> List[float]:
        provider = await self._get_provider()
        return await provider.embed(text)

    def embed_sync(self, text: str) -> List[float]:
        """Synchronous version of embed."""
        import asyncio
        return asyncio.run(self.embed(text))

    async def health(self) -> bool:
        try:
            provider = await self._get_provider()
            return await provider.health()
        except Exception:
            return False

    def health_sync(self) -> bool:
        """Synchronous version of health."""
        import asyncio
        return asyncio.run(self.health())

    def _normalize_input(self, input: Union[str, List[Message]]) -> List[Message]:
        if isinstance(input, str):
            return [{"role": "user", "content": input}]
        return input
