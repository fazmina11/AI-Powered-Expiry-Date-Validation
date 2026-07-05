"""
utils/logger.py — Structured Rotating File Logger configuration.
Defines logs/application.log and logs/error.log handlers.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure log directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Format specifications
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

# 1. Main Application Handler (Info, Warn, etc.)
app_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "application.log"),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8"
)
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(formatter)

# 2. Dedicated Error Handler (Error, Critical)
error_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "error.log"),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# 3. Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Root Logger Setup
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Avoid duplicate handlers if setup runs multiple times
if not root_logger.handlers:
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance for a given module name."""
    return logging.getLogger(name)
