"""
logger.py — Centralised logging for the project.

Usage:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("Pack opened")
"""

import logging
import sys
from utils.config import LOG_FILE, LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with both file and console handlers."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        # File
        try:
            fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except OSError:
            logger.warning("Cannot open log file %s — file logging disabled.", LOG_FILE)

    return logger
