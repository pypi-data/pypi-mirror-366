"""
Configuration settings for instant-crud library.
Supports environment variables and JSON config files.
"""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from instant_crud.core.strings import Strings


class InstantCRUDSettings(BaseSettings):
    """
    Configuration settings for instant-crud library.

    Environment variables should be prefixed with INSTANT_CRUD_
    Example: INSTANT_CRUD_DEBUG=true
    """

    model_config = SettingsConfigDict(
        env_prefix="INSTANT_CRUD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core settings
    debug: bool = Field(default=False, description="Enable debug mode")
    api_prefix: str = Field(default="/api/v1", description="API prefix for all routes")

    # Pagination settings
    default_page_size: int = Field(
        default=100, ge=1, le=1000, description="Default number of items per page"
    )
    max_page_size: int = Field(
        default=1000, ge=1, description="Maximum allowed page size"
    )
    pagination_format: str = Field(
        default="offset_based", description="Default pagination format"
    )

    # Export settings
    enable_export: bool = Field(default=True, description="Enable export functionality")
    max_export_rows: int = Field(
        default=10000, ge=1, description="Maximum rows for export"
    )
    export_timeout_seconds: int = Field(
        default=300, ge=30, description="Export operation timeout"
    )

    # Auth settings
    enable_auth: bool = Field(default=False, description="Enable authentication")
    jwt_secret_key: str | None = Field(default=None, description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(
        default=30, ge=1, description="JWT token expiration in minutes"
    )

    # Advanced configuration
    config_file: str | None = Field(
        default=None, description="Path to JSON configuration file"
    )

    # Loaded from config file
    auth_config: dict[str, Any] = Field(
        default_factory=dict, description="Authentication configuration"
    )
    export_config: dict[str, Any] = Field(
        default_factory=dict, description="Export configuration"
    )
    pagination_config: dict[str, Any] = Field(
        default_factory=dict, description="Pagination configuration"
    )
    custom_routes: dict[str, Any] = Field(
        default_factory=dict, description="Custom routes configuration"
    )

    @field_validator("pagination_format")
    @classmethod
    def validate_pagination_format(cls, v: str) -> str:
        """Validate pagination format."""
        allowed_formats = ["offset_based", "page_based", "cursor_based", "custom"]
        if v not in allowed_formats:
            raise ValueError(f"pagination_format must be one of {allowed_formats}")
        return v

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, v: str) -> str:
        """Ensure API prefix starts with /"""
        if not v.startswith("/"):
            return f"/{v}"
        return v

    def model_post_init(self, *args: Any, **kwargs: Any) -> None:
        """Load additional configuration from file if specified."""
        if self.config_file:
            self._load_config_file()

    def _load_config_file(self) -> None:
        """Load configuration from JSON file."""
        try:
            config_path = Path(self.config_file) if self.config_file else None
            if not config_path or not config_path.exists():
                logging.warning(
                    Strings.CONFIG_SETTINGS_FILE_NOT_FOUND, self.config_file
                )
                return

            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            # Update configuration sections
            for section in [
                "auth_config",
                "export_config",
                "pagination_config",
                "custom_routes",
            ]:
                if section in config_data:
                    setattr(self, section, config_data[section])

            # Update direct settings from config file
            direct_settings = [
                "debug",
                "api_prefix",
                "default_page_size",
                "max_page_size",
                "pagination_format",
                "enable_export",
                "max_export_rows",
                "enable_auth",
                "jwt_expire_minutes",
            ]

            for setting in direct_settings:
                if setting in config_data:
                    setattr(self, setting, config_data[setting])

            logging.info(Strings.CONFIG_SETTINGS_FILE_LOADED, self.config_file)

        except json.JSONDecodeError as e:
            logging.error(
                Strings.CONFIG_SETTINGS_INVALID_JSON, self.config_file, str(e)
            )
            raise ValueError(
                Strings.CONFIG_SETTINGS_INVALID_JSON_NO_NAME, str(e)
            ) from e
        except Exception as e:
            logging.error(
                Strings.CONFIG_SETTINGS_ERROR_LOADING, self.config_file, str(e)
            )
            raise

    def get_pagination_config(self) -> dict[str, Any]:
        """Get pagination configuration with defaults."""
        if self.pagination_config:
            return self.pagination_config

        # Default configurations for different formats
        default_configs = {
            "offset_based": {
                "items_key": "items",
                "total_key": "total",
                "skip_key": "skip",
                "limit_key": "limit",
            },
            "page_based": {
                "items_key": "data",
                "wrapper_key": "pagination",
                "current_page_key": "current_page",
                "per_page_key": "per_page",
                "total_pages_key": "total_pages",
                "total_count_key": "total_count",
                "has_next_key": "has_next",
                "has_prev_key": "has_prev",
            },
            "cursor_based": {
                "items_key": "results",
                "wrapper_key": "meta",
                "count_key": "count",
                "next_key": "next",
                "previous_key": "previous",
            },
        }

        return {"response_format": self.pagination_format, "formats": default_configs}

    def get_export_config(self) -> dict[str, Any]:
        """Get export configuration with defaults."""
        default_config = {
            "max_rows": self.max_export_rows,
            "timeout_seconds": self.export_timeout_seconds,
            "allowed_formats": ["excel", "csv", "pdf", "json", "parquet"],
            "default_format": "excel",
            "compress_large_files": True,
            "include_metadata": True,
        }

        # Merge with custom export config
        if self.export_config:
            default_config.update(self.export_config)

        return default_config

    def get_auth_config(self) -> dict[str, Any]:
        """Get authentication configuration with defaults."""
        default_config = {
            "enabled": self.enable_auth,
            "jwt_secret_key": self.jwt_secret_key,
            "jwt_algorithm": self.jwt_algorithm,
            "jwt_expire_minutes": self.jwt_expire_minutes,
            "require_roles": False,
            "default_roles": [],
            "protected_endpoints": ["POST", "PUT", "PATCH", "DELETE"],
        }

        # Merge with custom auth config
        if self.auth_config:
            default_config.update(self.auth_config)

        return default_config


class SettingsManager:
    """
    Singleton manager for InstantCRUDSettings.
    """

    _instance: InstantCRUDSettings | None = None

    @classmethod
    def get_settings(cls, config_file: str | None = None) -> InstantCRUDSettings:
        """
        Get or create the settings instance.

        Args:
            config_file: Optional path to configuration file

        Returns:
            InstantCRUDSettings instance
        """
        if cls._instance is None or config_file:
            if config_file:
                cls._instance = InstantCRUDSettings(config_file=config_file)
            else:
                cls._instance = InstantCRUDSettings()

        return cls._instance

    @classmethod
    def reset_settings(cls) -> None:
        """Reset the settings instance. Useful for testing."""
        cls._instance = None
