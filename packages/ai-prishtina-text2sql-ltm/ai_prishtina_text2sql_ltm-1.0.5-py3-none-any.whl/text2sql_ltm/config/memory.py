"""
Memory configuration for the Text2SQL-LTM library.

This module provides comprehensive configuration for memory management,
including mem0.ai integration, storage backends, and privacy settings.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from pathlib import Path
import re

from pydantic import Field, validator, root_validator

from .base import BaseConfig
from ..types import MemoryBackend, PrivacyMode, CacheStrategy
from ..exceptions import InvalidConfigurationError


class MemoryConfig(BaseConfig):
    """
    Configuration for the memory system using mem0.ai and other backends.
    
    This configuration handles all aspects of memory management including
    storage, privacy, lifecycle, and performance settings.
    """
    
    # mem0.ai configuration
    mem0_api_key: Optional[str] = Field(
        None, 
        description="mem0.ai API key for cloud memory service",
        env="MEM0_API_KEY"
    )
    mem0_organization_id: Optional[str] = Field(
        None, 
        description="mem0.ai organization ID",
        env="MEM0_ORGANIZATION_ID"
    )
    mem0_project_id: Optional[str] = Field(
        None, 
        description="mem0.ai project ID",
        env="MEM0_PROJECT_ID"
    )
    mem0_base_url: Optional[str] = Field(
        None,
        description="Custom mem0.ai base URL for self-hosted instances",
        env="MEM0_BASE_URL"
    )
    
    # Storage backend configuration
    storage_backend: MemoryBackend = Field(
        MemoryBackend.MEMORY,
        description="Primary storage backend for memories"
    )
    storage_url: Optional[str] = Field(
        None, 
        description="Storage backend connection URL"
    )
    backup_storage_backend: Optional[MemoryBackend] = Field(
        None, 
        description="Backup storage backend for redundancy"
    )
    backup_storage_url: Optional[str] = Field(
        None,
        description="Backup storage backend connection URL"
    )
    
    # User isolation and security settings
    user_isolation: bool = Field(
        True, 
        description="Enable strict user memory isolation"
    )
    max_memory_per_user: str = Field(
        "100MB", 
        description="Maximum memory storage per user"
    )
    memory_compression: bool = Field(
        True, 
        description="Enable memory content compression"
    )
    encryption_enabled: bool = Field(
        True, 
        description="Enable memory encryption at rest"
    )
    encryption_key: Optional[str] = Field(
        None,
        description="Encryption key for memory data (auto-generated if not provided)"
    )
    
    # Memory lifecycle settings
    memory_ttl_days: int = Field(
        90, 
        ge=1, 
        le=3650,
        description="Default memory TTL in days"
    )
    session_memory_ttl_hours: int = Field(
        24, 
        ge=1, 
        le=8760,
        description="Session memory TTL in hours"
    )
    schema_memory_ttl_days: int = Field(
        180, 
        ge=1, 
        le=3650,
        description="Schema memory TTL in days"
    )
    auto_cleanup: bool = Field(
        True, 
        description="Enable automatic memory cleanup"
    )
    cleanup_interval_hours: int = Field(
        6,
        ge=1,
        le=168,
        description="Interval between cleanup runs in hours"
    )
    
    # Learning and adaptation settings
    learning_enabled: bool = Field(
        True, 
        description="Enable memory learning from interactions"
    )
    feedback_learning: bool = Field(
        True, 
        description="Learn from user feedback"
    )
    pattern_recognition: bool = Field(
        True, 
        description="Enable query pattern recognition"
    )
    adaptive_personalization: bool = Field(
        True, 
        description="Enable adaptive user personalization"
    )
    learning_rate: float = Field(
        0.01,
        ge=0.001,
        le=1.0,
        description="Learning rate for memory adaptation"
    )
    
    # Performance and caching settings
    memory_cache_size: int = Field(
        1000, 
        ge=10,
        le=100000,
        description="In-memory cache size for frequently accessed memories"
    )
    cache_strategy: CacheStrategy = Field(
        CacheStrategy.LRU,
        description="Cache eviction strategy"
    )
    cache_ttl_seconds: int = Field(
        3600,
        ge=60,
        le=86400,
        description="Cache TTL in seconds"
    )
    batch_size: int = Field(
        100, 
        ge=1,
        le=10000,
        description="Batch size for memory operations"
    )
    max_concurrent_operations: int = Field(
        10, 
        ge=1,
        le=100,
        description="Maximum concurrent memory operations"
    )
    connection_pool_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    
    # Privacy and compliance settings
    privacy_mode: PrivacyMode = Field(
        PrivacyMode.BALANCED, 
        description="Privacy protection level"
    )
    data_retention_days: int = Field(
        90, 
        ge=1,
        le=3650,
        description="Data retention period in days"
    )
    anonymization_enabled: bool = Field(
        True, 
        description="Enable data anonymization"
    )
    gdpr_compliance: bool = Field(
        True,
        description="Enable GDPR compliance features"
    )
    audit_logging: bool = Field(
        True,
        description="Enable audit logging for memory operations"
    )
    
    # Monitoring and metrics
    enable_metrics: bool = Field(
        True,
        description="Enable memory performance metrics"
    )
    metrics_retention_days: int = Field(
        30,
        ge=1,
        le=365,
        description="Metrics retention period in days"
    )
    
    @classmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        return "memory"
    
    def get_sensitive_fields(self) -> List[str]:
        """Get list of field names that contain sensitive data."""
        return [
            "mem0_api_key",
            "storage_url",
            "backup_storage_url",
            "encryption_key"
        ]
    
    @validator('storage_url')
    def validate_storage_url(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate storage URL format based on backend."""
        if v is None:
            return v
        
        backend = values.get('storage_backend')
        if backend == MemoryBackend.REDIS and not v.startswith('redis://'):
            raise ValueError("Redis URL must start with 'redis://'")
        elif backend == MemoryBackend.POSTGRESQL and not v.startswith('postgresql://'):
            raise ValueError("PostgreSQL URL must start with 'postgresql://'")
        elif backend == MemoryBackend.MONGODB and not v.startswith('mongodb://'):
            raise ValueError("MongoDB URL must start with 'mongodb://'")
        elif backend == MemoryBackend.SQLITE and not (v.startswith('sqlite://') or v.endswith('.db')):
            raise ValueError("SQLite URL must start with 'sqlite://' or end with '.db'")
        
        return v
    
    @validator('backup_storage_url')
    def validate_backup_storage_url(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate backup storage URL format."""
        if v is None:
            return v
        
        backend = values.get('backup_storage_backend')
        if backend is None:
            raise ValueError("backup_storage_backend must be set when backup_storage_url is provided")
        
        # Apply same validation as primary storage URL
        return cls.validate_storage_url(v, {'storage_backend': backend})
    
    @validator('max_memory_per_user')
    def validate_memory_size(cls, v: str) -> str:
        """Validate memory size format."""
        pattern = r'^(\d+(?:\.\d+)?)(B|KB|MB|GB|TB)$'
        if not re.match(pattern, v.upper()):
            raise ValueError("Memory size must be in format like '100MB', '1.5GB', etc.")
        return v.upper()
    
    @validator('mem0_base_url')
    def validate_mem0_base_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate mem0.ai base URL format."""
        if v is None:
            return v
        
        if not v.startswith(('http://', 'https://')):
            raise ValueError("mem0.ai base URL must start with http:// or https://")
        
        return v.rstrip('/')
    
    @root_validator(skip_on_failure=True)
    def validate_mem0_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mem0.ai configuration consistency."""
        backend = values.get('storage_backend')
        api_key = values.get('mem0_api_key')

        if backend == MemoryBackend.MEM0 and not api_key:
            raise ValueError("mem0_api_key is required when using MEM0 backend")

        return values
    
    @root_validator(skip_on_failure=True)
    def validate_privacy_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate privacy settings consistency."""
        privacy_mode = values.get('privacy_mode')
        encryption = values.get('encryption_enabled')
        anonymization = values.get('anonymization_enabled')
        
        if privacy_mode == PrivacyMode.STRICT:
            if not encryption:
                raise ValueError("Encryption must be enabled in STRICT privacy mode")
            if not anonymization:
                raise ValueError("Anonymization must be enabled in STRICT privacy mode")
        
        return values
    
    def validate_config(self) -> None:
        """Perform additional validation after initialization."""
        # Validate TTL relationships
        if self.session_memory_ttl_hours > self.memory_ttl_days * 24:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="session_memory_ttl_hours",
                reason="Session memory TTL cannot be longer than general memory TTL"
            )
        
        # Validate cache settings
        if self.cache_ttl_seconds > self.memory_ttl_days * 24 * 3600:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="cache_ttl_seconds",
                reason="Cache TTL cannot be longer than memory TTL"
            )
    
    def validate_production_ready(self) -> None:
        """Validate that configuration is production-ready."""
        if self.storage_backend == MemoryBackend.MEMORY:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="storage_backend",
                reason="In-memory backend is not suitable for production"
            )
        
        if not self.encryption_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="encryption_enabled",
                reason="Encryption must be enabled in production"
            )
        
        if not self.user_isolation:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="user_isolation",
                reason="User isolation must be enabled in production"
            )
        
        if self.privacy_mode == PrivacyMode.PERMISSIVE:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="privacy_mode",
                reason="PERMISSIVE privacy mode is not recommended for production"
            )
    
    def get_memory_size_bytes(self) -> int:
        """Convert max_memory_per_user to bytes."""
        size_str = self.max_memory_per_user.upper()
        
        # Extract number and unit
        import re
        match = re.match(r'^(\d+(?:\.\d+)?)(B|KB|MB|GB|TB)$', size_str)
        if not match:
            raise ValueError(f"Invalid memory size format: {size_str}")
        
        number, unit = match.groups()
        number = float(number)
        
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 ** 2,
            'GB': 1024 ** 3,
            'TB': 1024 ** 4,
        }
        
        return int(number * multipliers[unit])
