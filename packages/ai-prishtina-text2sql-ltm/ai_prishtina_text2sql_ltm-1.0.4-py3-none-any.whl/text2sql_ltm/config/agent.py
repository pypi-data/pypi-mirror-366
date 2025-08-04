"""
Agent configuration for the Text2SQL-LTM library.

This module provides comprehensive configuration for the Text2SQL agent,
including LLM settings, query generation, and optimization parameters.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List, Set
from enum import Enum

from pydantic import Field, validator, root_validator

from .base import BaseConfig
from ..types import LLMProvider, SQLDialect, QueryComplexity
from ..exceptions import InvalidConfigurationError


class QueryOptimization(str, Enum):
    """Query optimization strategies."""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"


class ResponseFormat(str, Enum):
    """Response format options."""
    SQL_ONLY = "sql_only"
    SQL_WITH_EXPLANATION = "sql_with_explanation"
    DETAILED = "detailed"
    INTERACTIVE = "interactive"


class AgentConfig(BaseConfig):
    """
    Configuration for the Text2SQL agent behavior and capabilities.
    
    This configuration controls all aspects of the agent including
    LLM integration, query generation, optimization, and response formatting.
    """
    
    # LLM Provider Settings
    llm_provider: LLMProvider = Field(
        LLMProvider.OPENAI, 
        description="LLM provider for query generation"
    )
    llm_model: str = Field(
        "gpt-4", 
        description="Specific LLM model to use"
    )
    llm_api_key: Optional[str] = Field(
        None, 
        description="API key for LLM provider",
        env="LLM_API_KEY"
    )
    llm_base_url: Optional[str] = Field(
        None, 
        description="Custom base URL for LLM API",
        env="LLM_BASE_URL"
    )
    llm_organization_id: Optional[str] = Field(
        None,
        description="Organization ID for LLM provider",
        env="LLM_ORGANIZATION_ID"
    )
    
    # Generation Parameters
    temperature: float = Field(
        0.1, 
        ge=0.0, 
        le=2.0, 
        description="LLM temperature for creativity vs consistency"
    )
    max_tokens: int = Field(
        2048, 
        ge=1, 
        le=32768, 
        description="Maximum tokens per LLM response"
    )
    top_p: float = Field(
        0.95,
        ge=0.0,
        le=1.0,
        description="Top-p sampling parameter"
    )
    frequency_penalty: float = Field(
        0.0,
        ge=-2.0,
        le=2.0,
        description="Frequency penalty for token repetition"
    )
    presence_penalty: float = Field(
        0.0,
        ge=-2.0,
        le=2.0,
        description="Presence penalty for topic repetition"
    )
    
    # SQL Generation Settings
    default_sql_dialect: SQLDialect = Field(
        SQLDialect.POSTGRESQL,
        description="Default SQL dialect for query generation"
    )
    supported_dialects: Set[SQLDialect] = Field(
        default_factory=lambda: {SQLDialect.POSTGRESQL, SQLDialect.MYSQL, SQLDialect.SQLITE},
        description="Set of supported SQL dialects"
    )
    max_query_complexity: QueryComplexity = Field(
        QueryComplexity.COMPLEX,
        description="Maximum allowed query complexity"
    )
    enable_query_optimization: bool = Field(
        True, 
        description="Enable automatic query optimization"
    )
    optimization_strategy: QueryOptimization = Field(
        QueryOptimization.ADVANCED,
        description="Query optimization strategy"
    )
    enable_query_validation: bool = Field(
        True, 
        description="Enable SQL query validation before execution"
    )
    enable_query_explanation: bool = Field(
        True, 
        description="Generate explanations for SQL queries"
    )
    
    # Memory Integration Settings
    memory_influence_weight: float = Field(
        0.3, 
        ge=0.0, 
        le=1.0, 
        description="Weight of memory influence on query generation"
    )
    context_window_size: int = Field(
        10, 
        ge=1,
        le=100,
        description="Number of previous queries to consider for context"
    )
    memory_relevance_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for memory inclusion"
    )
    max_memory_contexts: int = Field(
        5,
        ge=1,
        le=20,
        description="Maximum number of memory contexts to include"
    )
    learning_rate: float = Field(
        0.01, 
        ge=0.0, 
        le=1.0, 
        description="Learning rate for agent adaptation"
    )
    
    # Response and Formatting Settings
    response_format: ResponseFormat = Field(
        ResponseFormat.SQL_WITH_EXPLANATION,
        description="Default response format"
    )
    include_confidence_score: bool = Field(
        True,
        description="Include confidence scores in responses"
    )
    include_execution_plan: bool = Field(
        False,
        description="Include query execution plan in responses"
    )
    include_performance_hints: bool = Field(
        True,
        description="Include performance optimization hints"
    )
    max_explanation_length: int = Field(
        500,
        ge=50,
        le=2000,
        description="Maximum length of query explanations in characters"
    )
    
    # Performance and Timeout Settings
    query_timeout: int = Field(
        30, 
        ge=1,
        le=300,
        description="Query generation timeout in seconds"
    )
    max_concurrent_requests: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum concurrent query generation requests"
    )
    request_rate_limit: int = Field(
        100,
        ge=1,
        le=10000,
        description="Maximum requests per minute per user"
    )
    
    # Caching Settings
    cache_enabled: bool = Field(
        True, 
        description="Enable query result caching"
    )
    cache_ttl: int = Field(
        3600, 
        ge=60,
        le=86400,
        description="Cache TTL in seconds"
    )
    cache_size: int = Field(
        1000,
        ge=10,
        le=100000,
        description="Maximum number of cached queries"
    )
    
    # Error Handling and Retry Settings
    max_retries: int = Field(
        3, 
        ge=0,
        le=10,
        description="Maximum retry attempts for failed requests"
    )
    retry_delay: float = Field(
        1.0, 
        ge=0.1,
        le=60.0,
        description="Base delay between retries in seconds"
    )
    exponential_backoff: bool = Field(
        True,
        description="Use exponential backoff for retries"
    )
    fallback_enabled: bool = Field(
        True, 
        description="Enable fallback to simpler models on failure"
    )
    fallback_model: Optional[str] = Field(
        None,
        description="Fallback model to use when primary model fails"
    )
    
    # Security and Safety Settings
    enable_sql_injection_protection: bool = Field(
        True,
        description="Enable SQL injection protection"
    )
    allowed_sql_operations: Set[str] = Field(
        default_factory=lambda: {"SELECT", "WITH"},
        description="Set of allowed SQL operations"
    )
    blocked_keywords: Set[str] = Field(
        default_factory=lambda: {"DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"},
        description="Set of blocked SQL keywords"
    )
    enable_query_sanitization: bool = Field(
        True,
        description="Enable automatic query sanitization"
    )
    
    # Monitoring and Logging
    enable_metrics: bool = Field(
        True,
        description="Enable performance metrics collection"
    )
    enable_detailed_logging: bool = Field(
        False,
        description="Enable detailed request/response logging"
    )
    log_sensitive_data: bool = Field(
        False,
        description="Include sensitive data in logs (not recommended for production)"
    )
    
    @classmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        return "agent"
    
    def get_sensitive_fields(self) -> List[str]:
        """Get list of field names that contain sensitive data."""
        return [
            "llm_api_key",
            "llm_organization_id"
        ]
    
    @validator('llm_model')
    def validate_llm_model(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate LLM model based on provider."""
        provider = values.get('llm_provider')
        
        # Define valid models for each provider
        valid_models = {
            LLMProvider.OPENAI: {
                "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", 
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
            },
            LLMProvider.ANTHROPIC: {
                "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307", "claude-2.1", "claude-2.0"
            },
            LLMProvider.AZURE_OPENAI: {
                "gpt-4", "gpt-4-32k", "gpt-35-turbo", "gpt-35-turbo-16k"
            }
        }
        
        if provider in valid_models and v not in valid_models[provider]:
            raise ValueError(f"Invalid model '{v}' for provider '{provider}'. "
                           f"Valid models: {', '.join(valid_models[provider])}")
        
        return v
    
    @validator('llm_base_url')
    def validate_llm_base_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate LLM base URL format."""
        if v is None:
            return v
        
        if not v.startswith(('http://', 'https://')):
            raise ValueError("LLM base URL must start with http:// or https://")
        
        return v.rstrip('/')
    
    @validator('supported_dialects')
    def validate_supported_dialects(cls, v: Set[SQLDialect], values: Dict[str, Any]) -> Set[SQLDialect]:
        """Validate that default dialect is in supported dialects."""
        default_dialect = values.get('default_sql_dialect')
        if default_dialect and default_dialect not in v:
            raise ValueError(f"Default SQL dialect '{default_dialect}' must be in supported dialects")
        
        return v
    
    @validator('allowed_sql_operations')
    def validate_allowed_operations(cls, v: Set[str]) -> Set[str]:
        """Validate and normalize allowed SQL operations."""
        # Convert to uppercase for consistency
        normalized = {op.upper() for op in v}
        
        # Ensure SELECT is always allowed for a query system
        normalized.add("SELECT")
        
        return normalized
    
    @validator('blocked_keywords')
    def validate_blocked_keywords(cls, v: Set[str]) -> Set[str]:
        """Validate and normalize blocked keywords."""
        # Convert to uppercase for consistency
        return {keyword.upper() for keyword in v}
    
    @root_validator(skip_on_failure=True)
    def validate_security_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security settings consistency."""
        allowed_ops = values.get('allowed_sql_operations', set())
        blocked_keywords = values.get('blocked_keywords', set())
        
        # Check for conflicts between allowed operations and blocked keywords
        conflicts = allowed_ops.intersection(blocked_keywords)
        if conflicts:
            raise ValueError(f"Conflicting settings: operations {conflicts} are both allowed and blocked")
        
        return values
    
    @root_validator(skip_on_failure=True)
    def validate_llm_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LLM configuration consistency."""
        provider = values.get('llm_provider')
        api_key = values.get('llm_api_key')
        
        # API key is required for cloud providers (but allow test/demo keys)
        cloud_providers = {LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.AZURE_OPENAI}
        test_keys = {"test_key", "demo_key", "your_api_key", "your_openai_key", "", None}

        if provider in cloud_providers and api_key not in test_keys and not api_key:
            raise ValueError(f"API key is required for {provider} provider")
        
        return values
    
    def validate_config(self) -> None:
        """Perform additional validation after initialization."""
        # Validate memory settings
        if self.memory_influence_weight > 0 and self.max_memory_contexts == 0:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="max_memory_contexts",
                reason="max_memory_contexts must be > 0 when memory_influence_weight > 0"
            )
        
        # Validate timeout settings
        if self.retry_delay * self.max_retries > self.query_timeout:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="retry_delay",
                reason="Total retry time cannot exceed query timeout"
            )
    
    def validate_production_ready(self) -> None:
        """Validate that configuration is production-ready."""
        if not self.enable_sql_injection_protection:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="enable_sql_injection_protection",
                reason="SQL injection protection must be enabled in production"
            )
        
        if not self.enable_query_sanitization:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="enable_query_sanitization",
                reason="Query sanitization must be enabled in production"
            )
        
        if self.log_sensitive_data:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="log_sensitive_data",
                reason="Sensitive data logging should be disabled in production"
            )
        
        if self.temperature > 0.3:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="temperature",
                reason="Temperature should be low (≤ 0.3) for consistent production results"
            )
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration for LLM calls."""
        return {
            "model": self.llm_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }
    
    def is_operation_allowed(self, operation: str) -> bool:
        """Check if a SQL operation is allowed."""
        return operation.upper() in self.allowed_sql_operations
    
    def is_keyword_blocked(self, keyword: str) -> bool:
        """Check if a SQL keyword is blocked."""
        return keyword.upper() in self.blocked_keywords
