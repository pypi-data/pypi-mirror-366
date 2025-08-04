"""
Base configuration classes for the Text2SQL-LTM library.

This module provides the foundation for all configuration management
with proper validation, type safety, and environment variable support.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Type, TypeVar, Generic, ClassVar, Union, List
from abc import ABC, abstractmethod
from pathlib import Path
import os
import json
import yaml
from datetime import datetime
import logging

from pydantic import BaseModel, Field, validator, root_validator
from pydantic_settings import BaseSettings

from ..exceptions import ConfigurationError, InvalidConfigurationError, MissingConfigurationError

logger = logging.getLogger(__name__)

ConfigType = TypeVar('ConfigType', bound='BaseConfig')


class BaseConfig(BaseModel, ABC):
    """
    Abstract base class for all configuration objects.

    Provides common functionality for validation, serialization,
    and environment variable loading with comprehensive type safety.
    """

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        use_enum_values = True
        populate_by_name = True  # Pydantic v2 equivalent of allow_population_by_field_name
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: lambda v: str(v),
        }

    @classmethod
    @abstractmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        ...

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for this configuration."""
        return cls.schema()

    @classmethod
    def from_dict(cls: Type[ConfigType], data: Dict[str, Any]) -> ConfigType:
        """Create configuration from dictionary with proper error handling."""
        try:
            return cls(**data)
        except Exception as e:
            raise InvalidConfigurationError(
                config_section=cls.get_config_section(),
                config_key="*",
                reason=f"Invalid configuration data: {str(e)}"
            ) from e

    @classmethod
    def from_env(cls: Type[ConfigType], prefix: str = "") -> ConfigType:
        """Create configuration from environment variables."""
        env_prefix = f"{prefix}_{cls.get_config_section().upper()}_" if prefix else f"{cls.get_config_section().upper()}_"

        env_data = {}
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                # Convert string values to appropriate types
                env_data[config_key] = cls._convert_env_value(config_key, value)

        return cls.from_dict(env_data)

    @classmethod
    def _convert_env_value(cls, key: str, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Get field info from schema
        schema = cls.schema()
        properties = schema.get('properties', {})
        field_info = properties.get(key, {})
        field_type = field_info.get('type')

        if field_type == 'boolean':
            return value.lower() in ('true', '1', 'yes', 'on')
        elif field_type == 'integer':
            try:
                return int(value)
            except ValueError:
                return value  # Let Pydantic handle the error
        elif field_type == 'number':
            try:
                return float(value)
            except ValueError:
                return value  # Let Pydantic handle the error
        elif field_type == 'array':
            # Simple comma-separated list
            return [item.strip() for item in value.split(',') if item.strip()]
        else:
            return value

    @classmethod
    def from_file(cls: Type[ConfigType], file_path: Path) -> ConfigType:
        """Load configuration from file with comprehensive error handling."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")

            section_data = data.get(cls.get_config_section(), {})
            return cls.from_dict(section_data)

        except Exception as e:
            raise InvalidConfigurationError(
                config_section=cls.get_config_section(),
                config_key="file",
                reason=f"Failed to load from {file_path}: {str(e)}"
            ) from e

    def to_dict(self, exclude_none: bool = False, exclude_defaults: bool = False) -> Dict[str, Any]:
        """Convert configuration to dictionary with options."""
        return self.dict(exclude_none=exclude_none, exclude_defaults=exclude_defaults)

    def to_json(self, indent: int = 2, exclude_none: bool = False) -> str:
        """Convert configuration to JSON string."""
        return self.json(indent=indent, exclude_none=exclude_none)

    def merge(self: ConfigType, other: ConfigType) -> ConfigType:
        """Merge with another configuration object."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Cannot merge {self.__class__} with {other.__class__}")

        # Deep merge dictionaries
        merged_data = self._deep_merge(self.dict(), other.dict())
        return self.__class__(**merged_data)

    @staticmethod
    def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = BaseConfig._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def validate_config(self) -> None:
        """Perform additional validation after initialization."""
        # Override in subclasses for custom validation
        pass

    def get_sensitive_fields(self) -> List[str]:
        """Get list of field names that contain sensitive data."""
        # Override in subclasses to specify sensitive fields
        return []

    def to_safe_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with sensitive fields masked."""
        data = self.to_dict()
        sensitive_fields = self.get_sensitive_fields()

        for field in sensitive_fields:
            if field in data and data[field] is not None:
                data[field] = "***MASKED***"

        return data

    @abstractmethod
    def validate_production_ready(self) -> None:
        """
        Validate that configuration is production-ready.

        This method should be implemented by subclasses to perform
        production-specific validation checks.

        Raises:
            ConfigurationError: When configuration is not production-ready
        """
        pass

    def __post_init_post_parse__(self) -> None:
        """Called after Pydantic validation."""
        self.validate_config()

class ConfigurationManager:
    """
    Manages loading and merging of configuration from multiple sources.

    Supports loading from:
    - Environment variables
    - Configuration files (YAML/JSON)
    - Direct dictionary input
    - Default values

    Provides comprehensive error handling and validation.
    """

    def __init__(self, app_name: str = "text2sql_ltm"):
        self.app_name = app_name
        self._configs: Dict[str, BaseConfig] = {}
        self._config_classes: Dict[str, Type[BaseConfig]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def register_config(self, config_class: Type[BaseConfig]) -> None:
        """Register a configuration class."""
        section = config_class.get_config_section()
        if section in self._configs:
            raise ValueError(f"Configuration section '{section}' already registered")

        self._config_classes[section] = config_class

        # Create default instance
        try:
            self._configs[section] = config_class()
            self.logger.debug(f"Registered configuration section: {section}")
        except Exception as e:
            raise ConfigurationError(f"Failed to create default config for {section}: {str(e)}") from e

    def load_from_env(self, prefix: Optional[str] = None) -> None:
        """Load all configurations from environment variables."""
        env_prefix = prefix or self.app_name.upper()

        for section, config in self._configs.items():
            try:
                env_config = config.__class__.from_env(env_prefix)
                self._configs[section] = config.merge(env_config)
                self.logger.debug(f"Loaded environment configuration for section: {section}")
            except Exception as e:
                # Log warning but don't fail - env vars are optional
                self.logger.warning(f"Failed to load environment config for {section}: {str(e)}")

    def load_from_file(self, file_path: Path) -> None:
        """Load all configurations from file (supports YAML, JSON, and INI formats)."""
        if not file_path.exists():
            self.logger.debug(f"Configuration file not found: {file_path}")
            return  # File is optional

        try:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif file_path.suffix.lower() in ['.ini', '.cfg']:
                data = self._load_ini_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

            for section, config in self._configs.items():
                if section in data:
                    file_config = config.__class__.from_dict(data[section])
                    self._configs[section] = config.merge(file_config)
                    self.logger.debug(f"Loaded file configuration for section: {section}")

            self.logger.info(f"Successfully loaded configuration from: {file_path}")

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {file_path}: {str(e)}") from e

    def _load_ini_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """Load configuration from INI file with environment variable substitution."""
        import configparser
        import os
        import re

        # Create parser with interpolation support
        parser = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation()
        )

        # Read the file with environment variable substitution
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substitute environment variables
        content = self._substitute_env_vars(content)

        # Parse the content
        parser.read_string(content)

        # Convert to nested dictionary
        data = {}
        for section_name in parser.sections():
            section = parser[section_name]
            data[section_name] = {}

            for key, value in section.items():
                # Convert string values to appropriate types
                data[section_name][key] = self._convert_ini_value(value)

        return data

    def _substitute_env_vars(self, content: str) -> str:
        """Substitute environment variables in configuration content."""
        import os
        import re

        # Pattern to match ${VAR_NAME} or ${VAR_NAME:default_value}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)

        return re.sub(pattern, replace_var, content)

    def _convert_ini_value(self, value: str) -> Any:
        """Convert INI string value to appropriate Python type."""
        # Handle boolean values
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        elif value.lower() in ('false', 'no', 'off', '0'):
            return False

        # Handle numeric values
        try:
            # Try integer first
            if '.' not in value and 'e' not in value.lower():
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass

        # Handle lists (comma-separated values)
        if ',' in value:
            return [item.strip() for item in value.split(',') if item.strip()]

        # Return as string
        return value

    def load_from_dict(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Load configurations from dictionary."""
        for section, config in self._configs.items():
            if section in data:
                dict_config = config.__class__.from_dict(data[section])
                self._configs[section] = config.merge(dict_config)
                self.logger.debug(f"Loaded dictionary configuration for section: {section}")

    def get_config(self, section: str) -> BaseConfig:
        """Get configuration for a specific section."""
        if section not in self._configs:
            raise MissingConfigurationError(section)
        return self._configs[section]

    def get_all_configs(self) -> Dict[str, BaseConfig]:
        """Get all configurations."""
        return self._configs.copy()

    def validate_all(self) -> None:
        """Validate all configurations."""
        errors = []
        for section, config in self._configs.items():
            try:
                config.validate_config()
                self.logger.debug(f"Validation passed for section: {section}")
            except Exception as e:
                error_msg = f"Validation failed for {section}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")

    def to_dict(self, safe: bool = False) -> Dict[str, Dict[str, Any]]:
        """Convert all configurations to dictionary."""
        if safe:
            return {section: config.to_safe_dict() for section, config in self._configs.items()}
        else:
            return {section: config.to_dict() for section, config in self._configs.items()}

    def to_json(self, safe: bool = False, indent: int = 2) -> str:
        """Convert all configurations to JSON string."""
        return json.dumps(self.to_dict(safe=safe), indent=indent, default=str)

    def get_schema(self) -> Dict[str, Dict[str, Any]]:
        """Get JSON schema for all registered configurations."""
        return {section: cls.get_config_schema()
                for section, cls in self._config_classes.items()}

    def reload(self, file_path: Optional[Path] = None, env_prefix: Optional[str] = None) -> None:
        """Reload all configurations from sources."""
        # Reset to defaults
        for section, config_class in self._config_classes.items():
            self._configs[section] = config_class()

        # Reload from sources
        if file_path:
            self.load_from_file(file_path)

        self.load_from_env(env_prefix)
        self.validate_all()

        self.logger.info("Configuration reloaded successfully")


class EnvironmentConfig(BaseSettings):
    """
    Environment-based configuration loader.

    This class loads configuration from environment variables
    with proper type conversion and validation.
    """

    # Application settings
    app_name: str = Field("text2sql-ltm", env="TEXT2SQL_APP_NAME")
    app_version: str = Field("1.0.0", env="TEXT2SQL_APP_VERSION")
    environment: str = Field("development", env="TEXT2SQL_ENVIRONMENT")
    debug: bool = Field(False, env="TEXT2SQL_DEBUG")

    # Logging settings
    log_level: str = Field("INFO", env="TEXT2SQL_LOG_LEVEL")
    log_format: str = Field("json", env="TEXT2SQL_LOG_FORMAT")

    # Configuration file paths
    config_file: Optional[Path] = Field(None, env="TEXT2SQL_CONFIG_FILE")
    secrets_file: Optional[Path] = Field(None, env="TEXT2SQL_SECRETS_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator('environment')
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ['development', 'staging', 'production', 'testing']
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()

    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"