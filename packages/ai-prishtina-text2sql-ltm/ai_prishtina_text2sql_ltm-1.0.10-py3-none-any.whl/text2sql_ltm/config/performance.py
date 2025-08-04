"""
Performance configuration for the Text2SQL-LTM library.

This module provides comprehensive performance optimization settings
including connection pooling, caching, concurrency, and resource limits.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import Field, validator, root_validator

from .base import BaseConfig
from ..types import CacheStrategy
from ..exceptions import InvalidConfigurationError


class ConnectionPooling(str, Enum):
    """Connection pooling strategies."""
    DISABLED = "disabled"
    BASIC = "basic"
    ADVANCED = "advanced"
    ADAPTIVE = "adaptive"


class LoadBalancing(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    RANDOM = "random"


class CompressionLevel(int, Enum):
    """Compression levels."""
    NONE = 0
    LOW = 1
    MEDIUM = 3
    HIGH = 6
    MAXIMUM = 9


class PerformanceConfig(BaseConfig):
    """
    Performance optimization configuration for the Text2SQL-LTM library.
    
    This configuration controls all performance-related settings including
    connection pooling, caching, concurrency, resource limits, and optimization.
    """
    
    # Database Connection Pooling
    db_pool_size: int = Field(
        20, 
        ge=1,
        le=1000,
        description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        30, 
        ge=0,
        le=1000,
        description="Database connection pool overflow limit"
    )
    db_pool_timeout: int = Field(
        30,
        ge=1,
        le=300,
        description="Database connection pool timeout in seconds"
    )
    db_pool_recycle: int = Field(
        3600,
        ge=300,
        le=86400,
        description="Database connection recycle time in seconds"
    )
    db_pool_pre_ping: bool = Field(
        True,
        description="Enable connection pre-ping for health checks"
    )
    connection_pooling_strategy: ConnectionPooling = Field(
        ConnectionPooling.ADVANCED,
        description="Connection pooling strategy"
    )
    
    # Redis Connection Pooling
    redis_pool_size: int = Field(
        50, 
        ge=1,
        le=1000,
        description="Redis connection pool size"
    )
    redis_max_connections: int = Field(
        100,
        ge=1,
        le=10000,
        description="Maximum Redis connections"
    )
    redis_connection_timeout: int = Field(
        5,
        ge=1,
        le=60,
        description="Redis connection timeout in seconds"
    )
    redis_socket_keepalive: bool = Field(
        True,
        description="Enable Redis socket keepalive"
    )
    
    # Caching Configuration
    enable_query_cache: bool = Field(
        True, 
        description="Enable query result caching"
    )
    enable_schema_cache: bool = Field(
        True, 
        description="Enable database schema caching"
    )
    enable_memory_cache: bool = Field(
        True, 
        description="Enable memory context caching"
    )
    cache_strategy: CacheStrategy = Field(
        CacheStrategy.LRU,
        description="Cache eviction strategy"
    )
    cache_size_mb: int = Field(
        256, 
        ge=1,
        le=8192,
        description="Total cache size in MB"
    )
    query_cache_size: int = Field(
        1000,
        ge=10,
        le=100000,
        description="Maximum number of cached queries"
    )
    schema_cache_ttl: int = Field(
        3600,
        ge=60,
        le=86400,
        description="Schema cache TTL in seconds"
    )
    memory_cache_ttl: int = Field(
        1800,
        ge=60,
        le=86400,
        description="Memory cache TTL in seconds"
    )
    
    # Async and Concurrency Settings
    max_workers: int = Field(
        10, 
        ge=1,
        le=1000,
        description="Maximum worker threads for async operations"
    )
    max_concurrent_requests: int = Field(
        100,
        ge=1,
        le=10000,
        description="Maximum concurrent requests"
    )
    async_batch_size: int = Field(
        100, 
        ge=1,
        le=10000,
        description="Batch size for async operations"
    )
    connection_timeout: int = Field(
        30, 
        ge=1,
        le=300,
        description="General connection timeout in seconds"
    )
    read_timeout: int = Field(
        60,
        ge=1,
        le=600,
        description="Read timeout in seconds"
    )
    write_timeout: int = Field(
        60,  # Must be greater than connection_timeout (30)
        ge=1,
        le=300,
        description="Write timeout in seconds"
    )
    
    # Memory Management
    memory_limit_mb: int = Field(
        1024, 
        ge=64,
        le=32768,
        description="Memory limit in MB"
    )
    gc_threshold: int = Field(
        1000, 
        ge=100,
        le=100000,
        description="Garbage collection threshold"
    )
    enable_memory_profiling: bool = Field(
        False, 
        description="Enable memory profiling (impacts performance)"
    )
    memory_warning_threshold: float = Field(
        0.8,
        ge=0.1,
        le=0.95,
        description="Memory usage warning threshold (as fraction)"
    )
    
    # Query Optimization
    enable_query_optimization: bool = Field(
        True,
        description="Enable automatic query optimization"
    )
    query_complexity_limit: int = Field(
        100,
        ge=1,
        le=1000,
        description="Maximum query complexity score"
    )
    max_query_execution_time: int = Field(
        300,
        ge=1,
        le=3600,
        description="Maximum query execution time in seconds"
    )
    enable_query_parallelization: bool = Field(
        True,
        description="Enable query parallelization where possible"
    )
    
    # Compression and Serialization
    enable_compression: bool = Field(
        True,
        description="Enable data compression"
    )
    compression_level: CompressionLevel = Field(
        CompressionLevel.MEDIUM,
        description="Compression level (0=none, 9=maximum)"
    )
    compression_threshold: int = Field(
        1024,
        ge=100,
        le=1048576,
        description="Minimum size in bytes before compression is applied"
    )
    enable_binary_serialization: bool = Field(
        True,
        description="Use binary serialization for better performance"
    )
    
    # Load Balancing and Scaling
    enable_load_balancing: bool = Field(
        False,
        description="Enable load balancing across multiple instances"
    )
    load_balancing_strategy: LoadBalancing = Field(
        LoadBalancing.ROUND_ROBIN,
        description="Load balancing strategy"
    )
    health_check_interval: int = Field(
        30, 
        ge=5,
        le=300,
        description="Health check interval in seconds"
    )
    circuit_breaker_enabled: bool = Field(
        True,
        description="Enable circuit breaker pattern for fault tolerance"
    )
    circuit_breaker_threshold: int = Field(
        5,
        ge=1,
        le=100,
        description="Circuit breaker failure threshold"
    )
    
    # Monitoring and Metrics
    enable_metrics: bool = Field(
        True,
        description="Enable performance metrics collection"
    )
    metrics_collection_interval: int = Field(
        60,
        ge=1,
        le=3600,
        description="Metrics collection interval in seconds"
    )
    enable_detailed_metrics: bool = Field(
        False,
        description="Enable detailed performance metrics (impacts performance)"
    )
    metrics_retention_hours: int = Field(
        168,  # 1 week
        ge=1,
        le=8760,  # 1 year
        description="Metrics retention period in hours"
    )
    
    # Resource Limits
    max_memory_per_request: int = Field(
        100,
        ge=1,
        le=1024,
        description="Maximum memory per request in MB"
    )
    max_cpu_time_per_request: int = Field(
        30,
        ge=1,
        le=300,
        description="Maximum CPU time per request in seconds"
    )
    max_file_descriptors: int = Field(
        1024,
        ge=64,
        le=65536,
        description="Maximum number of file descriptors"
    )
    
    # Optimization Flags
    enable_jit_compilation: bool = Field(
        True,
        description="Enable JIT compilation where available"
    )
    enable_vectorization: bool = Field(
        True,
        description="Enable vectorized operations"
    )
    enable_lazy_loading: bool = Field(
        True,
        description="Enable lazy loading of resources"
    )
    enable_prefetching: bool = Field(
        True,
        description="Enable data prefetching"
    )
    prefetch_size: int = Field(
        10,
        ge=1,
        le=1000,
        description="Number of items to prefetch"
    )
    
    @classmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        return "performance"
    
    @validator('db_max_overflow')
    def validate_db_overflow(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate database overflow settings."""
        pool_size = values.get('db_pool_size', 0)
        if v > pool_size * 2:
            raise ValueError("Database overflow should not exceed 2x pool size")
        return v
    
    @validator('redis_max_connections')
    def validate_redis_connections(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate Redis connection settings."""
        pool_size = values.get('redis_pool_size', 0)
        if v < pool_size:
            raise ValueError("Redis max connections must be >= pool size")
        return v
    
    @validator('memory_limit_mb')
    def validate_memory_limit(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate memory limit settings."""
        cache_size = values.get('cache_size_mb', 0)
        if cache_size >= v * 0.8:
            raise ValueError("Cache size should not exceed 80% of memory limit")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_timeout_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate timeout settings consistency."""
        connection_timeout = values.get('connection_timeout', 0)
        read_timeout = values.get('read_timeout', 0)
        write_timeout = values.get('write_timeout', 0)
        
        if read_timeout <= connection_timeout:
            raise ValueError("Read timeout should be greater than connection timeout")
        
        if write_timeout <= connection_timeout:
            raise ValueError("Write timeout should be greater than connection timeout")
        
        return values
    
    @root_validator(skip_on_failure=True)
    def validate_worker_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate worker and concurrency settings."""
        max_workers = values.get('max_workers', 0)
        max_concurrent = values.get('max_concurrent_requests', 0)
        
        if max_concurrent < max_workers:
            raise ValueError("Max concurrent requests should be >= max workers")
        
        return values
    
    def validate_config(self) -> None:
        """Perform additional validation after initialization."""
        # Validate cache settings
        total_cache_items = self.query_cache_size
        estimated_cache_mb = total_cache_items * 0.001  # Rough estimate
        
        if estimated_cache_mb > self.cache_size_mb:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="query_cache_size",
                reason="Estimated cache size exceeds configured cache size limit"
            )
        
        # Validate resource limits
        if self.max_memory_per_request > self.memory_limit_mb:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="max_memory_per_request",
                reason="Per-request memory limit cannot exceed total memory limit"
            )
    
    def validate_production_ready(self) -> None:
        """Validate that configuration is production-ready."""
        if self.enable_memory_profiling:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="enable_memory_profiling",
                reason="Memory profiling should be disabled in production for performance"
            )
        
        if self.enable_detailed_metrics:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="enable_detailed_metrics",
                reason="Detailed metrics should be disabled in production for performance"
            )
        
        if self.db_pool_size < 10:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="db_pool_size",
                reason="Database pool size should be at least 10 in production"
            )
        
        if not self.circuit_breaker_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="circuit_breaker_enabled",
                reason="Circuit breaker should be enabled in production"
            )
    
    def get_memory_usage_mb(self) -> float:
        """Get estimated memory usage in MB."""
        import psutil
        import os
        
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def is_memory_warning_threshold_exceeded(self) -> bool:
        """Check if memory usage exceeds warning threshold."""
        current_usage = self.get_memory_usage_mb()
        threshold = self.memory_limit_mb * self.memory_warning_threshold
        return current_usage > threshold
    
    def get_optimal_batch_size(self, total_items: int) -> int:
        """Calculate optimal batch size based on configuration."""
        if total_items <= self.async_batch_size:
            return total_items
        
        # Calculate based on available workers and memory
        optimal_size = min(
            self.async_batch_size,
            total_items // self.max_workers,
            self.max_memory_per_request * 10  # Rough estimate
        )
        
        return max(1, optimal_size)
