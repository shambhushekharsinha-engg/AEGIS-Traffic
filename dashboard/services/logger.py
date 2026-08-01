"""
AEGIS-Traffic — Structured Logging Service
Configures file and console loggers for frontend and backend components.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logger(name: str = "aegis_frontend", log_file: str = "frontend.log", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a thread-safe logger with console and rotating file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_path = os.path.join(LOGS_DIR, log_file)
    file_handler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger("aegis_frontend", "frontend.log")
