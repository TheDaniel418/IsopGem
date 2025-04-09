"""Unit tests for the config module.

This module contains tests for the configuration loading and validation.
"""

import os
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from shared.utils.config import Config, ConfigLoader, Environment, get_config


def test_environment_enum() -> None:
    """Test that Environment enum has expected values."""
    assert Environment.DEVELOPMENT.value == "development"
    assert Environment.PRODUCTION.value == "production"
    assert Environment.TEST.value == "test"


def test_config_model_validation() -> None:
    """Test that Config model validates correctly."""
    # Valid minimal config
    valid_config = {
        "application": {
            "name": "Test App",
            "version": "0.1.0",
        }
    }

    config = Config.model_validate(valid_config)
    assert config.application.name == "Test App"
    assert config.application.version == "0.1.0"

    # Config with invalid type should raise ValidationError
    invalid_config = {
        "application": {
            "name": "Test App",
            "version": "0.1.0",
            "debug": "not_a_boolean",  # should be a boolean
        }
    }

    with pytest.raises(ValidationError):
        Config.model_validate(invalid_config)


def test_config_default_values() -> None:
    """Test that Config model has expected default values."""
    # Empty config should use all defaults
    config = Config.model_validate({})

    assert config.application.name == "IsopGem"
    assert config.application.debug is False
    assert config.ui.window.width == 1280
    assert config.ui.window.height == 800
    assert config.pillars.gematria.enabled is True


def test_config_loader_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ConfigLoader detects the environment correctly."""
    # Test default environment
    monkeypatch.delenv("ISOPGEM_ENV", raising=False)
    loader = ConfigLoader()
    assert loader.environment == Environment.DEVELOPMENT

    # Test setting environment through env var
    monkeypatch.setenv("ISOPGEM_ENV", "production")
    loader = ConfigLoader()
    assert loader.environment == Environment.PRODUCTION

    # Test invalid environment falls back to default
    monkeypatch.setenv("ISOPGEM_ENV", "invalid")
    loader = ConfigLoader()
    assert loader.environment == Environment.DEVELOPMENT


def test_config_loader_load_yaml(temp_config_dir: Path) -> None:
    """Test that ConfigLoader loads YAML files correctly."""
    # Create test YAML file
    test_config = {"application": {"name": "Test App", "version": "1.0.0"}}

    config_file = temp_config_dir / "default.yaml"
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)

    # Test loading the file
    loader = ConfigLoader()
    loaded_config = loader._load_yaml_config(config_file)

    assert loaded_config == test_config

    # Test loading non-existent file returns empty dict
    non_existent = temp_config_dir / "non_existent.yaml"
    loaded_config = loader._load_yaml_config(non_existent)

    assert loaded_config == {}


def test_config_loader_merge_configs() -> None:
    """Test that ConfigLoader merges configs correctly."""
    loader = ConfigLoader()

    base_config = {
        "application": {"name": "Base App", "version": "1.0.0", "debug": False},
        "ui": {"theme": "light"},
    }

    override_config = {"application": {"debug": True}, "ui": {"theme": "dark"}}

    merged = loader._merge_configs(base_config, override_config)

    # Check that values are correctly merged
    assert merged["application"]["name"] == "Base App"  # unchanged
    assert merged["application"]["version"] == "1.0.0"  # unchanged
    assert merged["application"]["debug"] is True  # overridden
    assert merged["ui"]["theme"] == "dark"  # overridden


def test_get_config_singleton() -> None:
    """Test that get_config returns a singleton instance."""
    # Mock the load method to verify it's only called once
    original_load = ConfigLoader.load
    call_count = 0

    def mock_load(self: Any) -> Config:
        nonlocal call_count
        call_count += 1
        return original_load(self)

    ConfigLoader.load = mock_load  # type: ignore

    try:
        # Reset the singleton
        from shared.utils.config import _config_loader

        _config_loader.config = None

        # First call should load
        config1 = get_config()
        assert call_count == 1

        # Second call should use cached instance
        config2 = get_config()
        assert call_count == 1

        # Both should be the same instance
        assert config1 is config2
    finally:
        # Restore original method
        ConfigLoader.load = original_load
