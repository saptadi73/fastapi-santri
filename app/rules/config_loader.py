"""Load scoring configuration from JSON file with simple caching."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_scoring_config() -> Dict[str, Any]:
    """Load scoring config fresh on every call to avoid stale thresholds."""
    config_path = Path(__file__).parent / "scoring.json"
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)
