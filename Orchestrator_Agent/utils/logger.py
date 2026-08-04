"""
==========================================================
Orchestrator Agent Logger

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Provides a centralized logging utility for the
Orchestrator Agent.

Author:
Team Orchestrator
==========================================================
"""

from pathlib import Path
import logging

from config import settings


# ==========================================================
# Create Logs Directory
# ==========================================================

LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIRECTORY / "orchestrator.log"


# ==========================================================
# Logger Factory
# ==========================================================

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Parameters
    ----------
    name : str
        Name of the logger.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ======================================================
    # Console Handler
    # ======================================================

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ======================================================
    # File Handler
    # ======================================================

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # ======================================================
    # Attach Handlers
    # ======================================================

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger