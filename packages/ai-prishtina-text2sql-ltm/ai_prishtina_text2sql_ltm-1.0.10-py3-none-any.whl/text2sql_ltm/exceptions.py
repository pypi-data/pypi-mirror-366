"""
Exception classes for the TEXT2SQL-LTM system.

This module defines all custom exceptions used throughout the Text2SQL
agent with long-term memory capabilities.
"""

from typing import Optional, Dict, Any, List
import traceback


class Text2SQLLTMError(Exception):
    """Base exception for all TEXT2SQL-LTM errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause
        self.traceback = traceback.format_exc() if cause else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "traceback": self.traceback,
        }
    
    def __str__(self) -> str:
        """String representation of the exception."""
        base = f"{self.error_code}: {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            base += f" ({details_str})"
        return base


class MemoryError(Text2SQLLTMError):
    """Errors related to memory operations."""
    pass


class MemoryConnectionError(MemoryError):
    """Error connecting to memory backend."""
    
    def __init__(self, backend: str, connection_url: Optional[str] = None, cause: Optional[Exception] = None):
        message = f"Failed to connect to memory backend: {backend}"
        details = {"backend": backend}
        if connection_url:
            details["connection_url"] = connection_url
        super().__init__(message, details=details, cause=cause)


class MemoryStorageError(MemoryError):
    """Error storing or retrieving memories."""
    
    def __init__(self, operation: str, user_id: Optional[str] = None, cause: Optional[Exception] = None):
        message = f"Memory storage operation failed: {operation}"
        details = {"operation": operation}
        if user_id:
            details["user_id"] = user_id
        super().__init__(message, details=details, cause=cause)


class MemoryQuotaExceededError(MemoryError):
    """User memory quota exceeded."""
    
    def __init__(self, user_id: str, current_usage: str, quota: str):
        message = f"Memory quota exceeded for user {user_id}: {current_usage}/{quota}"
        details = {
            "user_id": user_id,
            "current_usage": current_usage,
            "quota": quota
        }
        super().__init__(message, details=details)


class SessionError(Text2SQLLTMError):
    """Errors related to user sessions."""
    pass


class SessionNotFoundError(SessionError):
    """Session not found."""
    
    def __init__(self, session_id: str):
        message = f"Session not found: {session_id}"
        details = {"session_id": session_id}
        super().__init__(message, details=details)


class SessionExpiredError(SessionError):
    """Session has expired."""
    
    def __init__(self, session_id: str, expired_at: Optional[str] = None):
        message = f"Session expired: {session_id}"
        details = {"session_id": session_id}
        if expired_at:
            details["expired_at"] = expired_at
        super().__init__(message, details=details)


class SessionLimitExceededError(SessionError):
    """Maximum number of sessions exceeded."""
    
    def __init__(self, user_id: str, current_sessions: int, max_sessions: int):
        message = f"Session limit exceeded for user {user_id}: {current_sessions}/{max_sessions}"
        details = {
            "user_id": user_id,
            "current_sessions": current_sessions,
            "max_sessions": max_sessions
        }
        super().__init__(message, details=details)


class ContextError(Text2SQLLTMError):
    """Errors related to context processing."""
    pass


class ContextResolutionError(ContextError):
    """Error resolving query context."""
    
    def __init__(self, query: str, context_type: str, cause: Optional[Exception] = None):
        message = f"Failed to resolve context for query: {query}"
        details = {
            "query": query,
            "context_type": context_type
        }
        super().__init__(message, details=details, cause=cause)


class AmbiguousContextError(ContextError):
    """Query context is ambiguous."""
    
    def __init__(self, query: str, possible_contexts: List[str]):
        message = f"Ambiguous context for query: {query}"
        details = {
            "query": query,
            "possible_contexts": possible_contexts
        }
        super().__init__(message, details=details)


class SchemaError(Text2SQLLTMError):
    """Errors related to database schema operations."""
    pass


class SchemaNotFoundError(SchemaError):
    """Database schema not found."""
    
    def __init__(self, database_name: str, schema_name: Optional[str] = None):
        message = f"Schema not found: {database_name}"
        if schema_name:
            message += f".{schema_name}"
        details = {"database_name": database_name}
        if schema_name:
            details["schema_name"] = schema_name
        super().__init__(message, details=details)


class SchemaValidationError(SchemaError):
    """Schema validation failed."""
    
    def __init__(self, schema_name: str, validation_errors: List[str]):
        message = f"Schema validation failed for {schema_name}"
        details = {
            "schema_name": schema_name,
            "validation_errors": validation_errors
        }
        super().__init__(message, details=details)


class SchemaDiscoveryError(SchemaError):
    """Schema discovery operation failed."""

    def __init__(self, operation: str, database_name: Optional[str] = None, cause: Optional[Exception] = None):
        message = f"Schema discovery failed: {operation}"
        details = {"operation": operation}
        if database_name:
            details["database_name"] = database_name
        super().__init__(message, details=details, cause=cause)


class TableNotFoundError(SchemaError):
    """Database table not found."""

    def __init__(self, table_name: str, database_name: Optional[str] = None):
        message = f"Table not found: {table_name}"
        if database_name:
            message += f" in database {database_name}"
        details = {"table_name": table_name}
        if database_name:
            details["database_name"] = database_name
        super().__init__(message, details=details)


class SecurityError(Text2SQLLTMError):
    """Security-related errors."""
    pass


class AuthenticationError(SecurityError):
    """Authentication failed."""
    
    def __init__(self, user_id: Optional[str] = None, reason: Optional[str] = None):
        message = "Authentication failed"
        if reason:
            message += f": {reason}"
        details = {}
        if user_id:
            details["user_id"] = user_id
        if reason:
            details["reason"] = reason
        super().__init__(message, details=details)


class AuthorizationError(SecurityError):
    """Authorization failed."""
    
    def __init__(self, user_id: str, resource: str, action: str):
        message = f"User {user_id} not authorized to {action} {resource}"
        details = {
            "user_id": user_id,
            "resource": resource,
            "action": action
        }
        super().__init__(message, details=details)


class RateLimitExceededError(SecurityError):
    """Rate limit exceeded."""
    
    def __init__(self, user_id: str, limit: int, window: str):
        message = f"Rate limit exceeded for user {user_id}: {limit} requests per {window}"
        details = {
            "user_id": user_id,
            "limit": limit,
            "window": window
        }
        super().__init__(message, details=details)


class DataPrivacyError(SecurityError):
    """Data privacy violation."""
    
    def __init__(self, violation_type: str, details: Optional[Dict[str, Any]] = None):
        message = f"Data privacy violation: {violation_type}"
        super().__init__(message, details=details or {})


class QueryError(Text2SQLLTMError):
    """Errors related to SQL query generation and execution."""
    pass


class QueryGenerationError(QueryError):
    """Error generating SQL query."""
    
    def __init__(self, natural_language: str, reason: str, cause: Optional[Exception] = None):
        message = f"Failed to generate SQL for: {natural_language}"
        details = {
            "natural_language": natural_language,
            "reason": reason
        }
        super().__init__(message, details=details, cause=cause)


# General validation error
class ValidationError(Text2SQLLTMError):
    """General validation error."""

    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        details = {}
        if validation_errors:
            details["validation_errors"] = validation_errors
        super().__init__(message, details=details)


class QueryValidationError(QueryError):
    """SQL query validation failed."""

    def __init__(self, sql: str, validation_errors: List[str]):
        message = f"Query validation failed: {sql}"
        details = {
            "sql": sql,
            "validation_errors": validation_errors
        }
        super().__init__(message, details=details)


class QueryExecutionError(QueryError):
    """SQL query execution failed."""
    
    def __init__(self, sql: str, database: str, cause: Optional[Exception] = None):
        message = f"Query execution failed on {database}: {sql}"
        details = {
            "sql": sql,
            "database": database
        }
        super().__init__(message, details=details, cause=cause)


class ConfigurationError(Text2SQLLTMError):
    """Configuration-related errors."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration provided."""
    
    def __init__(self, config_section: str, config_key: str, reason: str):
        message = f"Invalid configuration {config_section}.{config_key}: {reason}"
        details = {
            "config_section": config_section,
            "config_key": config_key,
            "reason": reason
        }
        super().__init__(message, details=details)


class MissingConfigurationError(ConfigurationError):
    """Required configuration missing."""

    def __init__(self, config_key: str, config_section: Optional[str] = None):
        message = f"Missing required configuration: {config_key}"
        if config_section:
            message = f"Missing required configuration {config_section}.{config_key}"
        details = {"config_key": config_key}
        if config_section:
            details["config_section"] = config_section
        super().__init__(message, details=details)


class MultiModalError(Text2SQLLTMError):
    """Errors related to multi-modal processing."""
    pass


class TranslationError(Text2SQLLTMError):
    """Errors related to query translation."""
    pass


class LLMError(Text2SQLLTMError):
    """Errors related to LLM operations."""
    pass


class RAGError(Text2SQLLTMError):
    """Errors related to RAG operations."""
    pass


# Exception mapping for common error scenarios
EXCEPTION_MAPPING = {
    "memory_connection": MemoryConnectionError,
    "memory_storage": MemoryStorageError,
    "memory_quota": MemoryQuotaExceededError,
    "session_not_found": SessionNotFoundError,
    "session_expired": SessionExpiredError,
    "session_limit": SessionLimitExceededError,
    "context_resolution": ContextResolutionError,
    "ambiguous_context": AmbiguousContextError,
    "schema_not_found": SchemaNotFoundError,
    "table_not_found": TableNotFoundError,
    "authentication": AuthenticationError,
    "authorization": AuthorizationError,
    "rate_limit": RateLimitExceededError,
    "query_generation": QueryGenerationError,
    "query_validation": QueryValidationError,
    "query_execution": QueryExecutionError,
    "invalid_config": InvalidConfigurationError,
    "missing_config": MissingConfigurationError,
}


def create_exception(error_type: str, *args, **kwargs) -> Text2SQLLTMError:
    """
    Create an exception instance based on error type.
    
    Args:
        error_type: Type of error to create
        *args: Positional arguments for exception
        **kwargs: Keyword arguments for exception
        
    Returns:
        Exception instance
    """
    exception_class = EXCEPTION_MAPPING.get(error_type, Text2SQLLTMError)
    return exception_class(*args, **kwargs)


class VectorStoreError(Text2SQLLTMError):
    """Errors related to vector store operations."""
    pass


class EmbeddingError(Text2SQLLTMError):
    """Errors related to embedding operations."""
    pass
