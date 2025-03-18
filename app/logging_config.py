# app/logging_config.py
import logging
import os
from datetime import datetime


def setup_logging():
    # Ensure logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # File handler for recognition logs
    recognition_log_file = os.path.join(
        log_dir, f"recognition_{datetime.now().strftime('%Y%m%d')}.log"
    )
    recognition_handler = logging.FileHandler(recognition_log_file)
    recognition_handler.setLevel(logging.INFO)
    recognition_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    recognition_handler.setFormatter(recognition_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Root logger
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])

    # Specific logger for recognition
    recognition_logger = logging.getLogger("recognition")
    recognition_logger.handlers = []  # Clear default handlers
    recognition_logger.addHandler(recognition_handler)
    recognition_logger.setLevel(logging.INFO)

    # Ensure other loggers don’t duplicate
    logging.getLogger().propagate = False


setup_logging()

