"""Configuration management for IsopGem.

This module provides utilities for loading and validating configuration from
various sources (default config, environment variables, etc).
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import yaml
from loguru import logger
from pydantic import BaseModel, Field

# Environment variable that determines which config to load
ENV_VAR_NAME = "ISOPGEM_ENV"
DEFAULT_ENV = "development"


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class ApplicationConfig(BaseModel):
    """Application configuration settings."""

    name: str = "IsopGem"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    theme: str = "light"
    locale: str = "en_US"


class WindowConfig(BaseModel):
    """Window configuration settings."""

    width: int = 1280
    height: int = 800
    title: str = "IsopGem - Sacred Geometry & Gematria Tool"
    maximize_on_start: bool = False


class FontConfig(BaseModel):
    """Font configuration."""

    main: str = "Roboto"
    size: int = 12


class ThemeColors(BaseModel):
    """Theme color configuration."""

    primary: str = "#4a86e8"
    secondary: str = "#ff9900"
    background: str = "#ffffff"
    text: str = "#333333"


class UIConfig(BaseModel):
    """UI configuration settings."""

    window: WindowConfig = Field(default_factory=WindowConfig)
    fonts: FontConfig = Field(default_factory=FontConfig)
    theme_colors: ThemeColors = Field(default_factory=ThemeColors)


class StorageConfig(BaseModel):
    """Storage configuration settings."""

    data_dir: str = "./data"
    backup_dir: str = "./backups"
    autosave_interval_minutes: int = 10
    max_backups: int = 5


class GematriaConfig(BaseModel):
    """Gematria pillar configuration."""

    enabled: bool = True
    default_methods: List[str] = ["standard", "ordinal", "reduced"]


class GeometryConfig(BaseModel):
    """Geometry pillar configuration."""

    enabled: bool = True
    precision_decimals: int = 4


class DocumentManagerConfig(BaseModel):
    """Document manager pillar configuration."""

    enabled: bool = True
    allowed_extensions: List[str] = [".txt", ".pdf", ".docx"]
    max_file_size_mb: int = 50


class AstrologyConfig(BaseModel):
    """Astrology pillar configuration."""

    enabled: bool = True
    default_system: str = "tropical"


class TQConfig(BaseModel):
    """TQ pillar configuration."""

    enabled: bool = True
    default_view: str = "grid"


class PillarsConfig(BaseModel):
    """Configuration for all pillars."""

    gematria: GematriaConfig = Field(default_factory=GematriaConfig)
    geometry: GeometryConfig = Field(default_factory=GeometryConfig)
    document_manager: DocumentManagerConfig = Field(default_factory=DocumentManagerConfig)
    astrology: AstrologyConfig = Field(default_factory=AstrologyConfig)
    tq: TQConfig = Field(default_factory=TQConfig)


class ServicesConfig(BaseModel):
    """External services configuration."""

    enable_updates: bool = True
    api_timeout_seconds: int = 30


class DevelopmentConfig(BaseModel):
    """Development-specific configuration."""

    enable_hot_reload: bool = True
    profile_performance: bool = True
    show_debug_panel: bool = True
    mock_external_services: bool = True


class ProductionConfig(BaseModel):
    """Production-specific configuration."""

    error_reporting: bool = True
    telemetry_enabled: bool = True
    update_check_interval_hours: int = 24


class Config(BaseModel):
    """Main configuration model for the entire application."""

    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    pillars: PillarsConfig = Field(default_factory=PillarsConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    development: Optional[DevelopmentConfig] = None
    production: Optional[ProductionConfig] = None


class ConfigLoader:
    """Handles loading and merging configuration from multiple sources."""

    def __init__(self) -> None:
        """Initialize the config loader."""
        self.config_dir = Path("config")
        self.environment = self._get_environment()
        self.config: Optional[Config] = None

    def _get_environment(self) -> Environment:
        """Get the current environment from environment variable or default."""
        env = os.environ.get(ENV_VAR_NAME, DEFAULT_ENV).lower()
        try:
            return Environment(env)
        except ValueError:
            logger.warning(
                f"Invalid environment: {env}. Using default: {DEFAULT_ENV}"
            )
            return Environment(DEFAULT_ENV)

    def _load_yaml_config(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as file:
                    return yaml.safe_load(file) or {}
            else:
                logger.warning(f"Config file not found: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading config file {file_path}: {e}")
            return {}

    def load(self) -> Config:
        """Load configuration from all sources and create a Config object."""
        # Load default config first
        default_config = self._load_yaml_config(self.config_dir / "default.yaml")

        # Load environment-specific config
        env_config = self._load_yaml_config(
            self.config_dir / f"{self.environment.value}.yaml"
        )

        # Merge configs
        merged_config = self._merge_configs(default_config, env_config)

        # Create and validate config object
        self.config = Config.model_validate(merged_config)
        return self.config

    def _merge_configs(
        self, base_config: Dict[str, Any], override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge two config dictionaries."""
        result = base_config.copy()

        for key, value in override_config.items():
            if isinstance(value, dict) and key in result and isinstance(
                result[key], dict
            ):
                # Recursively merge nested dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Override or add values
                result[key] = value

        return result


# Singleton instance
_config_loader = ConfigLoader()


def get_config() -> Config:
    """Get the application configuration.

    Returns:
        A validated Config object containing all application settings.
    """
    if _config_loader.config is None:
        _config_loader.config = _config_loader.load()
    return _config_loader.config 