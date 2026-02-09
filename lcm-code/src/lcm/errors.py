class LCMError(Exception):
    """Base class for all LCM errors."""
    def __init__(self, message: str, fix: str = ""):
        self.fix = fix
        super().__init__(f"{message}\n\nHOW TO FIX: {fix}")

class ConfigError(LCMError):
    """Raised when there is an issue with the .model configuration."""
    pass

class ProviderNotConfiguredError(LCMError):
    """Raised when a requested provider is missing required fields."""
    pass

class RuntimeUnavailableError(LCMError):
    """Raised when the local runtime (Ollama/Transformers) is not reachable or fails to load."""
    pass

class AuthError(LCMError):
    """Raised when there is an authentication failure (e.g., HF_TOKEN)."""
    pass
