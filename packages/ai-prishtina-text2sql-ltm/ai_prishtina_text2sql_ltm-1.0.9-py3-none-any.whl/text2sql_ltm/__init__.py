# -*- coding: utf-8 -*-
"""ai-prishtina-TEXT2SQL-LTM: Production-Grade Text2SQL Agent with Long-Term Memory

A comprehensive, type-safe Text2SQL library with advanced long-term memory capabilities.
Designed for production use with enterprise-grade security, monitoring, and performance.

Key Features:
- Production-ready Text2SQL agent with comprehensive memory integration
- Type-safe interfaces with full async/await support
- Enterprise security with authentication, authorization, and encryption
- Comprehensive monitoring, metrics, and observability
- Flexible configuration management with validation
- Memory isolation and privacy protection
- Multi-dialect SQL support with query optimization
- Extensible architecture with dependency injection support

Core Components:
- Text2SQLAgent: Main agent class with memory integration
- ConfigurationManager: Comprehensive configuration management
- Type system: Complete type definitions for type safety
- Exception hierarchy: Detailed error handling and reporting
"""

from .agent import Text2SQLAgent
from .config import (
    ConfigurationManager,
    MemoryConfig,
    AgentConfig,
    SecurityConfig,
    PerformanceConfig,
    MonitoringConfig,
    create_default_config_manager,
    create_production_config,
    load_config_from_file,
    load_config_from_env
)
from .types import (
    # Core type aliases
    UserID, SessionID, QueryID, MemoryID, SchemaID,
    DatabaseName, TableName, ColumnName,
    SQLQuery, NaturalLanguageQuery,
    Score, Percentage, Timestamp, Duration,

    # Data structures
    QueryResult, MemoryContext, UserSession, SchemaInfo,
    MemoryStats, QueryMetrics,

    # Enums
    QueryStatus, MemoryType, QueryComplexity, SQLDialect,
    LLMProvider, MemoryBackend, PrivacyMode, CacheStrategy,
    LogLevel,

    # Validation functions
    validate_user_id, validate_session_id, validate_score, validate_percentage,

    # Serialization helpers
    serialize_datetime, deserialize_datetime, to_json_serializable
)
from .exceptions import (
    # Base exceptions
    Text2SQLLTMError,

    # Specific exceptions
    MemoryError, MemoryConnectionError, MemoryStorageError, MemoryQuotaExceededError,
    SessionError, SessionNotFoundError, SessionExpiredError, SessionLimitExceededError,
    ContextError, ContextResolutionError, AmbiguousContextError,
    SchemaError, SchemaNotFoundError, SchemaValidationError, TableNotFoundError,
    SecurityError, AuthenticationError, AuthorizationError, RateLimitExceededError,
    QueryError, QueryGenerationError, QueryValidationError, QueryExecutionError,
    ConfigurationError, InvalidConfigurationError, MissingConfigurationError,

    # Exception utilities
    create_exception
)

# Factory functions (imported conditionally)
try:
    from .factory import (
        create_simple_agent,
        create_integrated_agent,
        create_production_agent,
        Text2SQLSession,
        create_session
    )
    # Create alias for backward compatibility
    create_advanced_agent = create_integrated_agent
    _FACTORY_AVAILABLE = True
except ImportError as e:
    _FACTORY_AVAILABLE = False
    print(f"Factory functions not available: {e}")

# Version information
__title__ = "text2sql-ltm"
__version__ = "1.0.9"
__author__ = "Alban Maxhuni, PhD"
__email__ = "info@albanmaxhuni.com"
__license__ = "Commercial"
__copyright__ = "Copyright (c) 2024 Dr. Alban Maxhuni. All rights reserved."
__description__ = "Advanced Text-to-SQL library with AI features"
__url__ = "https://github.com/albanmaxhuni/text2sql-ltm"

# Public API
__all__ = [
    # Core classes
    "Text2SQLAgent",

    # Configuration management
    "ConfigurationManager",
    "MemoryConfig",
    "AgentConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "MonitoringConfig",
    "create_default_config_manager",
    "create_production_config",
    "load_config_from_file",
    "load_config_from_env",

    # Factory functions (if available)
    "create_simple_agent",
    "create_advanced_agent",  # Alias for create_integrated_agent
    "create_integrated_agent",
    "create_production_agent",
    "Text2SQLSession",
    "create_session",

    # Type system
    "UserID", "SessionID", "QueryID", "MemoryID", "SchemaID",
    "DatabaseName", "TableName", "ColumnName",
    "SQLQuery", "NaturalLanguageQuery",
    "Score", "Percentage", "Timestamp", "Duration",
    "QueryResult", "MemoryContext", "UserSession", "SchemaInfo",
    "MemoryStats", "QueryMetrics",
    "QueryStatus", "MemoryType", "QueryComplexity", "SQLDialect",
    "LLMProvider", "MemoryBackend", "PrivacyMode", "CacheStrategy", "LogLevel",
    "validate_user_id", "validate_session_id", "validate_score", "validate_percentage",
    "serialize_datetime", "deserialize_datetime", "to_json_serializable",

    # Exception hierarchy
    "Text2SQLLTMError",
    "MemoryError", "MemoryConnectionError", "MemoryStorageError", "MemoryQuotaExceededError",
    "SessionError", "SessionNotFoundError", "SessionExpiredError", "SessionLimitExceededError",
    "ContextError", "ContextResolutionError", "AmbiguousContextError",
    "SchemaError", "SchemaNotFoundError", "SchemaValidationError", "TableNotFoundError",
    "SecurityError", "AuthenticationError", "AuthorizationError", "RateLimitExceededError",
    "QueryError", "QueryGenerationError", "QueryValidationError", "QueryExecutionError",
    "ConfigurationError", "InvalidConfigurationError", "MissingConfigurationError",
    "create_exception",

    # Metadata
    "__version__", "__author__", "__email__", "__license__", "__description__", "__url__",
]


# Convenience functions for common use cases

def create_agent(
    config_file: str = None,
    env_prefix: str = "TEXT2SQL_LTM",
    **config_overrides
) -> Text2SQLAgent:
    """
    Create a Text2SQL agent with default configuration.

    Args:
        config_file: Optional path to configuration file
        env_prefix: Environment variable prefix
        **config_overrides: Configuration overrides

    Returns:
        Text2SQLAgent: Configured agent instance

    Example:
        >>> agent = create_agent(
        ...     config_file="config.yaml",
        ...     memory__storage_backend="redis",
        ...     agent__llm_provider="openai"
        ... )
        >>> async with agent.session_context():
        ...     result = await agent.query("Show me all users", user_id="user123")
    """
    if config_file:
        config_manager = load_config_from_file(config_file)
    else:
        config_manager = load_config_from_env(env_prefix)

    # Apply overrides
    if config_overrides:
        override_dict = {}
        for key, value in config_overrides.items():
            if "__" in key:
                section, field = key.split("__", 1)
                if section not in override_dict:
                    override_dict[section] = {}
                override_dict[section][field] = value

        config_manager.load_from_dict(override_dict)

    return Text2SQLAgent(config_manager)


def create_production_agent(
    config_file: str = None,
    env_prefix: str = "TEXT2SQL_LTM"
) -> Text2SQLAgent:
    """
    Create a production-ready Text2SQL agent with security validation.

    Args:
        config_file: Optional path to configuration file
        env_prefix: Environment variable prefix

    Returns:
        Text2SQLAgent: Production-ready agent instance

    Raises:
        ConfigurationError: If configuration is not production-ready

    Example:
        >>> agent = create_production_agent("production.yaml")
        >>> async with agent.session_context():
        ...     result = await agent.query(
        ...         "SELECT * FROM users WHERE active = true",
        ...         user_id="user123",
        ...         auth_token="secure_token"
        ...     )
    """
    if config_file:
        config_manager = load_config_from_file(config_file)
    else:
        config_manager = create_production_config()

    return Text2SQLAgent(config_manager)


# Add convenience imports for core modules
try:
    from .memory import MemoryManager
    from .session import SessionManager
    from .schema import SchemaManager
    from .llm import BaseLLMProvider, create_llm_provider

    __all__.extend([
        "MemoryManager",
        "SessionManager",
        "SchemaManager",
        "BaseLLMProvider",
        "create_llm_provider"
    ])
except ImportError as e:
    # Log import errors but don't fail - allows partial functionality
    import logging
    logging.getLogger(__name__).warning(f"Some modules not available: {e}")

# Module-level configuration
import logging
from typing import Dict

# Configure default logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Feature availability checking
def get_available_features() -> Dict[str, bool]:
    """
    Get available features based on installed dependencies.

    Returns:
        Dict[str, bool]: Feature availability mapping
    """
    features = {}

    # Check for mem0 availability
    try:
        import mem0
        features["memory_mem0"] = True
    except ImportError:
        features["memory_mem0"] = False

    # Check for OpenAI availability
    try:
        import openai
        features["llm_openai"] = True
    except ImportError:
        features["llm_openai"] = False

    # Check for Anthropic availability
    try:
        import anthropic
        features["llm_anthropic"] = True
    except ImportError:
        features["llm_anthropic"] = False

    return features

def get_version() -> str:
    """Get the current version of the library."""
    return __version__

def get_features() -> dict:
    """Get available features based on installed dependencies."""
    return FEATURES.copy()

def check_dependencies() -> dict:
    """Check which optional dependencies are available."""
    return {
        "mem0ai": HAS_MEM0,
        "redis": HAS_REDIS,
        "asyncpg": HAS_POSTGRESQL,
        "pymongo": HAS_MONGODB,
    }

# Quick start helper function
def create_agent(
    memory_config: MemoryConfig = None,
    agent_config: AgentConfig = None,
    **kwargs
) -> Text2SQLAgent:
    """
    Quick start helper to create a Text2SQL agent with memory.
    
    Args:
        memory_config: Memory system configuration
        agent_config: Agent behavior configuration
        **kwargs: Additional configuration options
        
    Returns:
        Configured Text2SQLAgent instance
        
    Example:
        >>> agent = create_agent(
        ...     memory_config=MemoryConfig(user_isolation=True),
        ...     agent_config=AgentConfig(llm_provider="openai")
        ... )
        >>> session = agent.create_session(user_id="user123")
        >>> result = await session.query("Show me all customers")
    """
    if memory_config is None:
        memory_config = MemoryConfig()
    
    if agent_config is None:
        agent_config = AgentConfig()
    
    # Apply any additional kwargs to configs
    for key, value in kwargs.items():
        if hasattr(memory_config, key):
            setattr(memory_config, key, value)
        elif hasattr(agent_config, key):
            setattr(agent_config, key, value)
    
    return Text2SQLAgent(
        memory_config=memory_config,
        agent_config=agent_config
    )


# Conditionally remove factory functions from __all__ if not available
if not _FACTORY_AVAILABLE:
    factory_functions = [
        "create_simple_agent",
        "create_advanced_agent",
        "create_integrated_agent",
        "create_production_agent",
        "Text2SQLSession",
        "create_session",
    ]
    __all__ = [item for item in __all__ if item not in factory_functions]
