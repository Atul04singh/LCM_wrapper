from typing import Dict, Type, Optional
from .base import ProviderRuntime

class ProviderRegistry:
    _providers: Dict[str, Type[ProviderRuntime]] = {}

    @classmethod
    def register(cls, name: str):
        def wrapper(provider_cls: Type[ProviderRuntime]):
            cls._providers[name.lower()] = provider_cls
            return provider_cls
        return wrapper

    @classmethod
    def get(cls, name: str) -> Optional[Type[ProviderRuntime]]:
        return cls._providers.get(name.lower())

    @classmethod
    def list_providers(cls):
        return list(cls._providers.keys())
