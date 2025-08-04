"""
Configuration classes for the TEXT2SQL-LTM system.

This module provides comprehensive configuration management for all aspects
of the Text2SQL agent with long-term memory capabilities.
"""

from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pathlib import Path
import os

from pydantic import BaseModel, Field, validator, root_validator
from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class MemoryBackend(str, Enum):
    """Supported memory storage backends."""
    MEM0 = "mem0"
    REDIS = "redis"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    MEMORY = "memory"  # In-memory for testing


class PrivacyMode(str, Enum):
    """Privacy protection levels."""
    STRICT = "strict"      # Maximum privacy, minimal data retention
    BALANCED = "balanced"  # Balance between privacy and functionality
    PERMISSIVE = "permissive"  # Maximum functionality, longer retention


class MemoryConfig(BaseModel):
    """Configuration for the memory system using mem0.ai."""
    
    # mem0.ai configuration
    mem0_api_key: Optional[str] = Field(None, description="mem0.ai API key")
    mem0_organization_id: Optional[str] = Field(None, description="mem0.ai organization ID")
    mem0_project_id: Optional[str] = Field(None, description="mem0.ai project ID")
    
    # Storage backend configuration
    storage_backend: MemoryBackend = Field(
        MemoryBackend.MEM0, 
        description="Primary storage backend for memories"
    )
    storage_url: Optional[str] = Field(None, description="Storage backend connection URL")
    backup_storage_backend: Optional[MemoryBackend] = Field(
        None, 
        description="Backup storage backend"
    )
    
    # User isolation settings
    user_isolation: bool = Field(True, description="Enable user memory isolation")
    max_memory_per_user: str = Field("100MB", description="Maximum memory per user")
    memory_compression: bool = Field(True, description="Enable memory compression")
    
    # Memory lifecycle settings
    memory_ttl_days: int = Field(90, description="Default memory TTL in days")
    session_memory_ttl_hours: int = Field(24, description="Session memory TTL in hours")
    schema_memory_ttl_days: int = Field(180, description="Schema memory TTL in days")
    auto_cleanup: bool = Field(True, description="Enable automatic memory cleanup")
    
    # Learning settings
    learning_enabled: bool = Field(True, description="Enable memory learning")
    feedback_learning: bool = Field(True, description="Learn from user feedback")
    pattern_recognition: bool = Field(True, description="Enable query pattern recognition")
    adaptive_personalization: bool = Field(True, description="Enable adaptive personalization")
    
    # Performance settings
    memory_cache_size: int = Field(1000, description="Memory cache size")
    batch_size: int = Field(100, description="Batch size for memory operations")
    max_concurrent_operations: int = Field(10, description="Max concurrent memory operations")
    
    # Security and privacy
    encryption_enabled: bool = Field(True, description="Enable memory encryption")
    privacy_mode: PrivacyMode = Field(PrivacyMode.BALANCED, description="Privacy protection level")
    data_retention_days: int = Field(90, description="Data retention period in days")
    anonymization_enabled: bool = Field(True, description="Enable data anonymization")
    
    @validator('storage_url')
    def validate_storage_url(cls, v, values):
        """Validate storage URL format."""
        if v is None:
            return v
        
        backend = values.get('storage_backend')
        if backend == MemoryBackend.REDIS and not v.startswith('redis://'):
            raise ValueError("Redis URL must start with 'redis://'")
        elif backend == MemoryBackend.POSTGRESQL and not v.startswith('postgresql://'):
            raise ValueError("PostgreSQL URL must start with 'postgresql://'")
        elif backend == MemoryBackend.MONGODB and not v.startswith('mongodb://'):
            raise ValueError("MongoDB URL must start with 'mongodb://'")
        
        return v
    
    @validator('max_memory_per_user')
    def validate_memory_size(cls, v):
        """Validate memory size format."""
        if not v.endswith(('B', 'KB', 'MB', 'GB')):
            raise ValueError("Memory size must end with B, KB, MB, or GB")
        return v


class AgentConfig(BaseModel):
    """Configuration for the Text2SQL agent behavior."""
    
    # LLM settings
    llm_provider: LLMProvider = Field(LLMProvider.OPENAI, description="LLM provider")
    llm_model: str = Field("gpt-4", description="LLM model name")
    llm_api_key: Optional[str] = Field(None, description="LLM API key")
    llm_base_url: Optional[str] = Field(None, description="Custom LLM base URL")
    temperature: float = Field(0.1, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Maximum tokens per response")
    
    # SQL generation settings
    max_query_complexity: int = Field(100, description="Maximum query complexity score")
    enable_query_optimization: bool = Field(True, description="Enable query optimization")
    enable_query_validation: bool = Field(True, description="Enable query validation")
    enable_query_explanation: bool = Field(True, description="Generate query explanations")
    
    # Memory integration settings
    memory_influence_weight: float = Field(
        0.3, ge=0.0, le=1.0, 
        description="Weight of memory influence on query generation"
    )
    context_window_size: int = Field(10, description="Number of previous queries to consider")
    learning_rate: float = Field(0.01, ge=0.0, le=1.0, description="Learning rate for adaptation")
    
    # Performance settings
    query_timeout: int = Field(30, description="Query timeout in seconds")
    max_concurrent_sessions: int = Field(100, description="Maximum concurrent user sessions")
    cache_enabled: bool = Field(True, description="Enable query result caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    
    # Error handling
    max_retries: int = Field(3, description="Maximum retry attempts")
    retry_delay: float = Field(1.0, description="Delay between retries in seconds")
    fallback_enabled: bool = Field(True, description="Enable fallback mechanisms")


class SecurityConfig(BaseModel):
    """Security and privacy configuration."""
    
    # Authentication and authorization
    require_authentication: bool = Field(True, description="Require user authentication")
    session_secret_key: str = Field(..., description="Secret key for session management")
    token_expiry_hours: int = Field(24, description="Token expiry time in hours")
    
    # Data protection
    encrypt_memories: bool = Field(True, description="Encrypt stored memories")
    encryption_key: Optional[str] = Field(None, description="Encryption key for memories")
    hash_user_ids: bool = Field(True, description="Hash user IDs for privacy")
    
    # Access control
    rate_limiting_enabled: bool = Field(True, description="Enable rate limiting")
    max_requests_per_minute: int = Field(60, description="Max requests per minute per user")
    ip_whitelist: List[str] = Field(default_factory=list, description="IP whitelist")
    
    # Audit and compliance
    audit_logging: bool = Field(True, description="Enable audit logging")
    gdpr_compliance: bool = Field(True, description="Enable GDPR compliance features")
    data_export_enabled: bool = Field(True, description="Enable user data export")
    data_deletion_enabled: bool = Field(True, description="Enable user data deletion")
    
    # Security headers and policies
    cors_origins: List[str] = Field(default_factory=list, description="CORS allowed origins")
    content_security_policy: Optional[str] = Field(None, description="Content Security Policy")


class PerformanceConfig(BaseModel):
    """Performance optimization configuration."""
    
    # Connection pooling
    db_pool_size: int = Field(20, description="Database connection pool size")
    db_max_overflow: int = Field(30, description="Database connection pool overflow")
    redis_pool_size: int = Field(50, description="Redis connection pool size")
    
    # Caching
    enable_query_cache: bool = Field(True, description="Enable query result caching")
    enable_schema_cache: bool = Field(True, description="Enable schema caching")
    enable_memory_cache: bool = Field(True, description="Enable memory caching")
    cache_size_mb: int = Field(256, description="Cache size in MB")
    
    # Async and concurrency
    max_workers: int = Field(10, description="Maximum worker threads")
    async_batch_size: int = Field(100, description="Async operation batch size")
    connection_timeout: int = Field(30, description="Connection timeout in seconds")
    
    # Memory optimization
    memory_limit_mb: int = Field(1024, description="Memory limit in MB")
    gc_threshold: int = Field(1000, description="Garbage collection threshold")
    enable_memory_profiling: bool = Field(False, description="Enable memory profiling")
    
    # Monitoring
    enable_metrics: bool = Field(True, description="Enable performance metrics")
    metrics_port: int = Field(9090, description="Metrics server port")
    health_check_interval: int = Field(30, description="Health check interval in seconds")


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field("ai-prishtina-TEXT2SQL-LTM", description="Application name")
    app_version: str = Field("1.0.0", description="Application version")
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")
    
    # Server settings
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    workers: int = Field(1, description="Number of worker processes")
    
    # Configuration file paths
    config_file: Optional[Path] = Field(None, description="Configuration file path")
    secrets_file: Optional[Path] = Field(None, description="Secrets file path")
    
    # Environment-specific settings
    environment: str = Field("development", description="Environment name")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @root_validator
    def validate_environment(cls, values):
        """Validate environment-specific settings."""
        env = values.get('environment', 'development')
        
        if env == 'production':
            # Production-specific validations
            if values.get('debug', False):
                raise ValueError("Debug mode should be disabled in production")
            if values.get('log_level', 'INFO') == 'DEBUG':
                values['log_level'] = 'INFO'
        
        return values


def load_config(
    config_file: Optional[Union[str, Path]] = None,
    **overrides
) -> Dict[str, Any]:
    """
    Load configuration from file and environment variables.
    
    Args:
        config_file: Path to configuration file
        **overrides: Configuration overrides
        
    Returns:
        Complete configuration dictionary
    """
    # Load base settings
    settings = Settings()
    
    config = {
        "memory": MemoryConfig(),
        "agent": AgentConfig(),
        "security": SecurityConfig(session_secret_key=os.urandom(32).hex()),
        "performance": PerformanceConfig(),
        "settings": settings,
    }
    
    # Load from file if provided
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                file_config = yaml.safe_load(f)
            
            # Update config with file values
            for section, values in file_config.items():
                if section in config and isinstance(values, dict):
                    for key, value in values.items():
                        if hasattr(config[section], key):
                            setattr(config[section], key, value)
    
    # Apply overrides
    for key, value in overrides.items():
        if '.' in key:
            section, field = key.split('.', 1)
            if section in config and hasattr(config[section], field):
                setattr(config[section], field, value)
        else:
            if key in config:
                config[key] = value
    
    return config


# Global configuration instance
_config = None

def get_config() -> Dict[str, Any]:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config

def set_config(config: Dict[str, Any]) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
