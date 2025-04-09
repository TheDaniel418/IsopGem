"""Global pytest configuration for the IsopGem project.

This module contains shared pytest fixtures and configuration for all tests.
"""

import os
import sys
import pytest
from pathlib import Path
from typing import Any, Generator

# Add the project root to the Python path
# This makes imports work correctly from any test
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import PyQt fixtures
from PyQt6.QtWidgets import QApplication
from _pytest.fixtures import SubRequest


# Set test environment
os.environ["ISOPGEM_ENV"] = "test"


@pytest.fixture(scope="session")
def qapp():
    """Provide a QApplication instance for the test session.

    This fixture ensures that only one QApplication instance is created
    for the entire test session, which is required by PyQt.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary config directory for tests.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Yields:
        Path to the temporary config directory.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Store original environment variable
    original_env = os.environ.get("ISOPGEM_CONFIG_DIR")

    # Set environment variable to point to temp directory
    os.environ["ISOPGEM_CONFIG_DIR"] = str(config_dir)

    yield config_dir

    # Restore original environment variable
    if original_env:
        os.environ["ISOPGEM_CONFIG_DIR"] = original_env
    else:
        del os.environ["ISOPGEM_CONFIG_DIR"]


@pytest.fixture
def mock_config() -> dict[str, Any]:
    """Return a minimal config dict for testing."""
    return {
        "application": {
            "name": "IsopGem-Test",
            "version": "0.1.0",
            "debug": True,
            "log_level": "DEBUG",
        },
        "ui": {
            "window": {
                "width": 800,
                "height": 600,
                "title": "IsopGem Test",
                "maximize_on_start": False,
            }
        },
        "pillars": {
            "gematria": {"enabled": True},
            "geometry": {"enabled": True},
            "document_manager": {"enabled": True},
            "astrology": {"enabled": True},
            "tq": {"enabled": True},
        },
    }


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary data directory for tests.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Yields:
        Path to the temporary data directory.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Store original environment variable
    original_env = os.environ.get("ISOPGEM_DATA_DIR")

    # Set environment variable to point to temp directory
    os.environ["ISOPGEM_DATA_DIR"] = str(data_dir)

    yield data_dir

    # Restore original environment variable
    if original_env:
        os.environ["ISOPGEM_DATA_DIR"] = original_env
    else:
        del os.environ["ISOPGEM_DATA_DIR"]
