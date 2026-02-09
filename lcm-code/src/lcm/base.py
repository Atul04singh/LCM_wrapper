from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Dict, Any, Union

class Message(Dict[str, str]):
    """Standard message format: {'role': '...', 'content': '...'}"""
    pass

class ProviderRuntime(ABC):
    @abstractmethod
    async def chat(self, messages: List[Message], **params) -> str:
        """Complete a chat inference."""
        pass

    @abstractmethod
    async def stream(self, messages: List[Message], **params) -> AsyncGenerator[str, None]:
        """Stream chat completions."""
        yield ""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check provider health."""
        pass
