"""Load scoring configuration from JSON file with simple caching."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

_CONFIG_CACHE: Dict[str, Any] | None = None


def load_scoring_config() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    config_path = Path(__file__).parent / "scoring.json"
    with config_path.open("r", encoding="utf-8") as f:
        _CONFIG_CACHE = json.load(f)
    return _CONFIG_CACHE  # type: ignore[return-value]
