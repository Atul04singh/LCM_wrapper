import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LCMConfig(BaseModel):
    model: str = "qwen2.5:7b"
    provider: str = "ollama"
    runtime: str = "local"
    base_url: Optional[str] = None
    hf_model: Optional[str] = None
    hf_token: Optional[str] = None
    device: str = "auto"
    timeout: int = 120
    stream: bool = True

class ConfigResolver:
    @staticmethod
    def resolve(overrides: Dict[str, Any]) -> LCMConfig:
        config_dict = {}

        # 1. Load from .model files
        # Order: User home ~/.model, then Project ./.model (Project overrides User home)
        paths = [
            Path.home() / ".model",
            Path(".model")
        ]

        for path in paths:
            if path.exists():
                config_dict.update(ConfigResolver._parse_file(path))

        # 2. Environment Variables override files
        env_map = {
            "LCM_MODEL": "model",
            "LCM_PROVIDER": "provider",
            "LCM_RUNTIME": "runtime",
            "LCM_BASE_URL": "base_url",
            "LCM_HF_MODEL": "hf_model",
            "LCM_HF_TOKEN": "hf_token",
            "HF_TOKEN": "hf_token", # Direct support for official key
            "LCM_DEVICE": "device",
        }
        for env_var, key in env_map.items():
            if val := os.getenv(env_var):
                config_dict[key] = val

        # 3. Explicit overrides (constructor)
        config_dict.update({k: v for k, v in overrides.items() if v is not None})

        return LCMConfig(**config_dict)

    @staticmethod
    def _parse_file(path: Path) -> Dict[str, Any]:
        data = {}
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    # Interpolate environment variables
                    val = re.sub(r"\${(\w+)}", lambda m: os.getenv(m.group(1), ""), val)
                    data[key] = val
        return data
