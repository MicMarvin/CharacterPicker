# logging_setup.py
import os
import logging
import sys
from pathlib import Path

def setup_logging():
    log_level = logging.DEBUG  # Most verbose to least: DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Get the root logger
    root_logger = logging.getLogger()
    
    # Check if the logger already has handlers to avoid duplicate logging
    if root_logger.hasHandlers():
        root_logger.handlers.clear()  # Remove existing handlers before re-adding

    # Determine the AppData directory (Windows) or HOME (~) for other OS
    appdata = Path(os.getenv("APPDATA", Path.home()))
    log_dir = appdata / "CharacterPicker" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Define the log file path
    log_file = log_dir / "character_picker.log"

    # Create a file handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="w")  # Overwrite each time
    file_handler.setLevel(log_level)

    # Create a stream handler (for Maya's Script Editor)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)

    # Define a consistent format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers back to the root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    # Debug confirmation message
    root_logger.info(f"Logging initialized. Log file at: {log_file}")

setup_logging()
