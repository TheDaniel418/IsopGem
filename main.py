#!/usr/bin/env python3
"""IsopGem application entry point.

This is the main entry point for starting the IsopGem application.
"""

import os
import sys

# Set environment variables for debugging
os.environ["ISOPGEM_ENV"] = "development"
os.environ["ISOPGEM_LOG_LEVEL"] = "DEBUG"

# Configure logging before importing other modules
from loguru import logger

logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

from shared.utils.app import start_application

if __name__ == "__main__":
    sys.exit(start_application())
