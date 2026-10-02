"""Shared logger so every module logs consistently to console (and a rotating file)."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "data"
_LOG_FILE = _LOG_DIR / "focustrack.log"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        # Already configured (avoids duplicate handlers on re-import/reload).
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(_LOG_FILE, maxBytes=2_000_000, backupCount=3)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        # Non-fatal: fall back to console-only logging if the data dir isn't writable yet.
        pass

    return logger
