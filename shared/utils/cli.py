"""Command-line interface for IsopGem.

This module provides the command-line entry point for the application.
"""

import argparse
import os
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

from loguru import logger

from shared.utils.config import Environment, get_config


class LogLevel(str, Enum):
    """Log levels for the application."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(log_level: str) -> None:
    """Configure logging for the application.

    Args:
        log_level: The log level to use.
    """
    # Remove default loguru handler
    logger.remove()

    # Add console handler with appropriate format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler for errors
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logger.add(
        logs_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",
    )


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (uses sys.argv if None).

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="isopgem",
        description="IsopGem - Sacred Geometry & Gematria Tool",
    )

    parser.add_argument(
        "--env",
        type=str,
        choices=[e.value for e in Environment],
        help=f"Set application environment (default: {os.getenv('ISOPGEM_ENV', 'development')})",
    )

    parser.add_argument(
        "--log",
        type=str,
        choices=[level.value for level in LogLevel],
        help="Set log level",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no GUI)",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )

    return parser.parse_args(args)


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_args()

    if args.env:
        os.environ["ISOPGEM_ENV"] = args.env

    # Load configuration
    config = get_config()

    # Handle --version flag
    if args.version:
        print(f"IsopGem v{config.application.version}")
        return 0

    # Configure logging
    log_level = args.log or config.application.log_level
    configure_logging(log_level)

    logger.info(f"Starting IsopGem v{config.application.version}")
    logger.info(f"Environment: {os.getenv('ISOPGEM_ENV', 'development')}")
    logger.debug(f"Log level: {log_level}")

    if args.headless:
        # Run in headless mode
        logger.info("Running in headless mode")
        # TODO: Implement headless mode
        return 0
    else:
        # Run GUI application
        try:
            # Importing here to avoid circular imports
            from shared.utils.app import start_application

            return start_application()
        except ImportError:
            logger.error("Failed to import GUI components")
            return 1
        except Exception as e:
            logger.exception(f"Error starting application: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
