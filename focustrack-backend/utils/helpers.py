"""
Shared helper functions -- mainly safe JSON persistence.

Since the whole backend uses flat JSON files instead of a database, every
write goes through `atomic_write_json` (write to a temp file, then os.replace)
so a crash or concurrent read mid-write can never observe a half-written,
corrupted file.
"""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def read_json(path: Path, default: Any) -> Any:
    """Read JSON from disk, returning `default` if the file is missing or empty/corrupt."""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return default


def atomic_write_json(path: Path, data: Any) -> None:
    """Write JSON atomically: write to a sibling temp file, then rename over the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
