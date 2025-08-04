"""
Professional configuration management for Text2SQL-LTM library.

This module provides type-safe, validated configuration classes for all
aspects of the Text2SQL agent with comprehensive validation and defaults.
"""

from .base import BaseConfig, ConfigurationManager, EnvironmentConfig
from .memory import MemoryConfig
from .agent import AgentConfig, QueryOptimization, ResponseFormat
from .security import SecurityConfig, EncryptionMethod, AuthenticationMethod, HashingAlgorithm
from .performance import PerformanceConfig, ConnectionPooling, LoadBalancing, CompressionLevel
from .monitoring import MonitoringConfig, MetricsBackend, TracingBackend, AlertingBackend, LogFormat

# Import types for convenience
from ..types import (
    MemoryBackend, PrivacyMode, CacheStrategy, LLMProvider, SQLDialect,
    LogLevel, QueryComplexity
)
from ..exceptions import ConfigurationError, InvalidConfigurationError, MissingConfigurationError

# Global configuration instance
_global_config = None

def get_config() -> dict:
    """Get global configuration dictionary."""
    global _global_config
    if _global_config is None:
        _global_config = {
            "memory": MemoryConfig(),
            "agent": AgentConfig(),
            "security": SecurityConfig(),
            "performance": PerformanceConfig(),
            "monitoring": MonitoringConfig()
        }
    return _global_config

def set_config(config: dict) -> None:
    """Set global configuration dictionary."""
    global _global_config
    _global_config = config

# Public API
__all__ = [
    # Base classes
    "BaseConfig",
    "ConfigurationManager",
    "EnvironmentConfig",

    # Configuration classes
    "MemoryConfig",
    "AgentConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "MonitoringConfig",

    # Configuration functions
    "get_config",
    "set_config",

    # Enums from config modules
    "QueryOptimization",
    "ResponseFormat",
    "EncryptionMethod",
    "AuthenticationMethod",
    "HashingAlgorithm",
    "ConnectionPooling",
    "LoadBalancing",
    "CompressionLevel",
    "MetricsBackend",
    "TracingBackend",
    "AlertingBackend",
    "LogFormat",

    # Types from types module
    "MemoryBackend",
    "PrivacyMode",
    "CacheStrategy",
    "LLMProvider",
    "SQLDialect",
    "LogLevel",
    "QueryComplexity",

    # Exceptions
    "ConfigurationError",
    "InvalidConfigurationError",
    "MissingConfigurationError",
]


def create_default_config_manager() -> ConfigurationManager:
    """
    Create a configuration manager with all default configurations registered.

    Returns:
        ConfigurationManager: Configured manager with all config classes registered
    """
    manager = ConfigurationManager()

    # Register all configuration classes
    manager.register_config(MemoryConfig)
    manager.register_config(AgentConfig)
    manager.register_config(SecurityConfig)
    manager.register_config(PerformanceConfig)
    manager.register_config(MonitoringConfig)

    return manager


def load_config_from_file(config_file_path: str) -> ConfigurationManager:
    """
    Load configuration from a file.

    Args:
        config_file_path: Path to the configuration file (YAML or JSON)

    Returns:
        ConfigurationManager: Loaded configuration manager
    """
    from pathlib import Path

    manager = create_default_config_manager()
    manager.load_from_file(Path(config_file_path))
    manager.validate_all()

    return manager


def load_config_from_env(env_prefix: str = "TEXT2SQL_LTM") -> ConfigurationManager:
    """
    Load configuration from environment variables.

    Args:
        env_prefix: Prefix for environment variables

    Returns:
        ConfigurationManager: Loaded configuration manager
    """
    manager = create_default_config_manager()
    manager.load_from_env(env_prefix)
    manager.validate_all()

    return manager


def create_production_config() -> ConfigurationManager:
    """
    Create a production-ready configuration with secure defaults.

    Returns:
        ConfigurationManager: Production-ready configuration manager
    """
    manager = create_default_config_manager()

    # Load from environment variables
    manager.load_from_env("TEXT2SQL_LTM")

    # Validate all configurations
    manager.validate_all()

    # Validate production readiness
    for config in manager.get_all_configs().values():
        config.validate_production_ready()

    return manager

__all__ = [
    # Base configuration
    "BaseConfig",
    "ConfigurationError",
    
    # Memory configuration
    "MemoryConfig",
    "MemoryBackend", 
    "PrivacyMode",
    
    # Agent configuration
    "AgentConfig",
    "LLMProvider",
    "QueryOptimization",
    
    # Security configuration
    "SecurityConfig",
    "EncryptionMethod",
    "AuthenticationMethod",
    
    # Performance configuration
    "PerformanceConfig",
    "CacheStrategy",
    "ConnectionPooling",
    
    # Monitoring configuration
    "MonitoringConfig",
    "MetricsBackend",
    "LogLevel",
]