"""
Logging utilities for the RTF editor.

This module provides a consistent logging setup for all RTF editor components.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def get_logger(name):
    """
    Get a configured logger for the specified module.

    Args:
        name (str): The name of the module (typically __name__)

    Returns:
        logging.Logger: A configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Set level
        logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Add formatter to console handler
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)

        # Optionally add file handler for persistent logs
        try:
            # Create logs directory if it doesn't exist
            log_dir = Path.home() / ".isopgem" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            # Create log file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = log_dir / f"rtf_editor_{timestamp}.log"

            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # More detailed in file
            file_handler.setFormatter(formatter)

            # Add file handler to logger
            logger.addHandler(file_handler)
        except Exception as e:
            # Don't fail if file logging can't be set up
            logger.warning(f"Could not set up file logging: {e}")

    return logger
