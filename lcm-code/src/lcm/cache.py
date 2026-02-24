import json
import os
import hashlib
from pathlib import Path
from typing import Optional, Any

class LCMCache:
    def __init__(self):
        self.cache_dir = Path.home() / ".lcm"
        self.cache_file = self.cache_dir / "cache.json"
        self.cache_dir.mkdir(exist_ok=True)
        self._data = self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        with open(self.cache_file, "w") as f:
            json.dump(self._data, f)

    def get(self, key_parts: list) -> Optional[Any]:
        key = self._make_key(key_parts)
        return self._data.get(key)

    def set(self, key_parts: list, value: Any):
        key = self._make_key(key_parts)
        self._data[key] = value
        self._save()

    def _make_key(self, parts: list) -> str:
        serialized = json.dumps(parts, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

# Global singleton
cache = LCMCache()
