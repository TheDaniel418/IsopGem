#!/usr/bin/env python3
"""IsopGem application entry point.

This is the main entry point for starting the IsopGem application.
"""

import os
import sys

# Initialize GLUT early, before QApplication if possible
from OpenGL.GLUT import glutInit
try:
    # If sys.argv is not appropriate here (e.g. in some frozen app contexts),
    # an empty list might also work: glutInit([])
    glutInit(sys.argv)
    print("INFO: GLUT initialized successfully.") # For confirmation
except Exception as e:
    # Use a simple print here if logger is not yet configured
    print(f"WARNING: Could not initialize GLUT: {e}. Bitmap text may not work.")

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

# Set Qt attributes before creating QApplication
# This is required for PyQt6.QtWebEngineWidgets to work properly
try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication

    # Set the attribute before creating QApplication
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    # Try to import WebEngine to ensure it's loaded before QApplication
    try:
        import PyQt6.QtWebEngineWidgets

        logger.info("Successfully pre-loaded PyQt6.QtWebEngineWidgets")
    except ImportError as e:
        logger.warning(f"Could not pre-load PyQt6.QtWebEngineWidgets: {e}")
except ImportError as e:
    logger.warning(f"Could not set Qt attributes: {e}")

from shared.utils.app import start_application

if __name__ == "__main__":
    sys.exit(start_application())
