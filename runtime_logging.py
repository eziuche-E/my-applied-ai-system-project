"""Bounded local telemetry. Never log secrets or raw user questions."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging() -> None:
    logger = logging.getLogger("guesswise.coach")
    if logger.handlers:
        return
    directory = Path(__file__).resolve().parent / "logs"
    try:
        directory.mkdir(exist_ok=True)
        handler = RotatingFileHandler(directory / "coach.log", maxBytes=100_000,
                                      backupCount=2, encoding="utf-8")
    except OSError:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
