"""
Type definitions for the Text2SQL-LTM library.

This module provides comprehensive type definitions for type safety
and better IDE support throughout the library.
"""

from __future__ import annotations

from typing import (
    Dict, List, Optional, Union, Any, TypeVar, Generic, Protocol,
    Literal, NewType, TypedDict, Callable, Awaitable, AsyncIterator,
    AsyncContextManager, Sequence, Mapping, Set, Tuple, ClassVar
)
from typing_extensions import NotRequired, TypeAlias, Self, Final
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from uuid import UUID
from decimal import Decimal
import json
from abc import ABC, abstractmethod

# Type aliases for better readability and type safety
UserID = NewType('UserID', str)
SessionID = NewType('SessionID', str)
QueryID = NewType('QueryID', str)
MemoryID = NewType('MemoryID', str)
SchemaID = NewType('SchemaID', str)
TableName = NewType('TableName', str)
ColumnName = NewType('ColumnName', str)
DatabaseName = NewType('DatabaseName', str)

# Generic type variables with proper bounds
T = TypeVar('T')
UserType = TypeVar('UserType', bound=str)
ResultType = TypeVar('ResultType')
ConfigType = TypeVar('ConfigType', bound='BaseConfig')
MemoryContentType = TypeVar('MemoryContentType', str, Dict[str, Any])

# Protocol definitions for better type safety
class Serializable(Protocol):
    """Protocol for objects that can be serialized to JSON."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Create object from dictionary."""
        ...

class AsyncCloseable(Protocol):
    """Protocol for async resources that need cleanup."""

    async def close(self) -> None:
        """Close the resource."""
        ...

# Enums with proper type safety
class QueryStatus(str, Enum):
    """Status of query processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class MemoryType(str, Enum):
    """Types of memories stored in the system."""
    USER_PREFERENCE = "user_preference"
    QUERY_PATTERN = "query_pattern"
    SCHEMA_KNOWLEDGE = "schema_knowledge"
    CONVERSATION_CONTEXT = "conversation_context"
    FEEDBACK = "feedback"
    SYSTEM_LEARNING = "system_learning"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_PATTERN = "error_pattern"

class QueryComplexity(IntEnum):
    """Query complexity levels with numeric values for comparison."""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    VERY_COMPLEX = 4
    EXTREME = 5

class SQLDialect(str, Enum):
    """Supported SQL dialects."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    REDSHIFT = "redshift"

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
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

class CacheStrategy(str, Enum):
    """Cache strategy options."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    FIFO = "fifo"
    NONE = "none"

class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Type aliases for complex types
JSONValue: TypeAlias = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
SQLQuery: TypeAlias = str
NaturalLanguageQuery: TypeAlias = str
Timestamp: TypeAlias = datetime
Duration: TypeAlias = timedelta
Score: TypeAlias = float  # Confidence/relevance scores between 0.0 and 1.0
Percentage: TypeAlias = float  # Percentage values between 0.0 and 100.0

# Configuration type aliases
ConfigDict: TypeAlias = Dict[str, Any]
EnvironmentVariables: TypeAlias = Dict[str, str]
ConnectionString: TypeAlias = str

# Memory-related type aliases
MemoryContent: TypeAlias = Union[str, Dict[str, Any], List[Any]]
MemoryMetadata: TypeAlias = Dict[str, JSONValue]
MemoryFilter: TypeAlias = Dict[str, Any]

# Query-related type aliases
QueryParameters: TypeAlias = Dict[str, Any]
QueryMetadata: TypeAlias = Dict[str, JSONValue]
QueryContext: TypeAlias = Dict[str, Any]

# Schema-related type aliases
TableSchema: TypeAlias = Dict[str, Any]
ColumnInfo: TypeAlias = Dict[str, Any]
DatabaseSchema: TypeAlias = Dict[TableName, TableSchema]
SchemaMetadata: TypeAlias = Dict[str, JSONValue]

# Dataclass definitions for structured data
@dataclass(frozen=True)
class QueryResult:
    """Result of a Text2SQL query generation."""

    sql: SQLQuery
    explanation: str
    confidence: Score
    query_type: str
    tables_used: List[TableName]
    columns_used: List[ColumnName]
    complexity: QueryComplexity
    dialect: SQLDialect
    execution_time_ms: Optional[int] = None
    memory_context_used: List[MemoryID] = field(default_factory=list)
    metadata: QueryMetadata = field(default_factory=dict)
    created_at: Timestamp = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "sql": self.sql,
            "explanation": self.explanation,
            "confidence": self.confidence,
            "query_type": self.query_type,
            "tables_used": list(self.tables_used),
            "columns_used": list(self.columns_used),
            "complexity": self.complexity.value,
            "dialect": self.dialect.value,
            "execution_time_ms": self.execution_time_ms,
            "memory_context_used": list(self.memory_context_used),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

@dataclass(frozen=True)
class MemoryContext:
    """Context information from memory system."""

    memory_id: MemoryID
    content: MemoryContent
    memory_type: MemoryType
    relevance_score: Score
    user_id: UserID
    created_at: Timestamp
    last_accessed: Optional[Timestamp] = None
    access_count: int = 0
    metadata: MemoryMetadata = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "relevance_score": self.relevance_score,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count,
            "metadata": self.metadata,
        }

@dataclass
class UserSession:
    """User session information."""

    session_id: SessionID
    user_id: UserID
    created_at: Timestamp
    last_activity: Timestamp
    context: QueryContext = field(default_factory=dict)
    query_history: List[QueryID] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    expires_at: Optional[Timestamp] = None
    metadata: Dict[str, JSONValue] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "context": self.context,
            "query_history": list(self.query_history),
            "preferences": self.preferences,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }

@dataclass(frozen=True)
class SchemaInfo:
    """Database schema information."""

    schema_id: SchemaID
    database_name: DatabaseName
    tables: Dict[TableName, TableSchema]
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    dialect: SQLDialect = SQLDialect.POSTGRESQL
    version: str = "1.0"
    created_at: Timestamp = field(default_factory=datetime.utcnow)
    updated_at: Optional[Timestamp] = None
    metadata: SchemaMetadata = field(default_factory=dict)

    def get_table_names(self) -> Set[TableName]:
        """Get all table names in the schema."""
        return set(self.tables.keys())

    def get_column_names(self, table_name: TableName) -> Set[ColumnName]:
        """Get column names for a specific table."""
        table_schema = self.tables.get(table_name, {})
        columns = table_schema.get("columns", {})
        return set(ColumnName(col) for col in columns.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "schema_id": self.schema_id,
            "database_name": self.database_name,
            "tables": self.tables,
            "relationships": self.relationships,
            "indexes": self.indexes,
            "constraints": self.constraints,
            "dialect": self.dialect.value,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }

# TypedDict definitions for configuration
class MemoryConfigDict(TypedDict):
    """Type definition for memory configuration dictionary."""
    backend: MemoryBackend
    connection_url: NotRequired[str]
    user_isolation: NotRequired[bool]
    ttl_days: NotRequired[int]
    cache_size: NotRequired[int]
    encryption_enabled: NotRequired[bool]

class AgentConfigDict(TypedDict):
    """Type definition for agent configuration dictionary."""
    llm_provider: LLMProvider
    llm_model: str
    temperature: float
    max_tokens: int
    enable_caching: NotRequired[bool]
    enable_metrics: NotRequired[bool]
    query_timeout: NotRequired[int]

class SecurityConfigDict(TypedDict):
    """Type definition for security configuration dictionary."""
    require_authentication: NotRequired[bool]
    encrypt_memories: NotRequired[bool]
    rate_limiting_enabled: NotRequired[bool]
    max_requests_per_minute: NotRequired[int]
    audit_logging: NotRequired[bool]

class PerformanceConfigDict(TypedDict):
    """Type definition for performance configuration dictionary."""
    db_pool_size: NotRequired[int]
    cache_strategy: NotRequired[CacheStrategy]
    max_workers: NotRequired[int]
    memory_limit_mb: NotRequired[int]
    enable_metrics: NotRequired[bool]

# Callback type definitions
QueryCallback = Callable[[QueryResult], Awaitable[None]]
MemoryCallback = Callable[[MemoryContext], Awaitable[None]]
ErrorCallback = Callable[[Exception], Awaitable[None]]
SessionCallback = Callable[[UserSession], Awaitable[None]]
SchemaCallback = Callable[[SchemaInfo], Awaitable[None]]

# Async iterator types
MemoryIterator = AsyncIterator[MemoryContext]
QueryIterator = AsyncIterator[QueryResult]
SessionIterator = AsyncIterator[UserSession]

# Context manager types
MemoryManager = AsyncContextManager[Any]
SessionManager = AsyncContextManager[UserSession]
DatabaseConnection = AsyncContextManager[Any]

# Function type definitions
MemoryRetriever = Callable[[UserID, str], Awaitable[List[MemoryContext]]]
QueryGenerator = Callable[[NaturalLanguageQuery, QueryContext], Awaitable[QueryResult]]
SchemaAnalyzer = Callable[[DatabaseSchema], Awaitable[SchemaInfo]]
UserAuthenticator = Callable[[str], Awaitable[Optional[UserID]]]

# Validation functions
def validate_score(score: float) -> Score:
    """Validate and convert a score to the proper range."""
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Score must be between 0.0 and 1.0, got {score}")
    return Score(score)

def validate_percentage(percentage: float) -> Percentage:
    """Validate and convert a percentage to the proper range."""
    if not 0.0 <= percentage <= 100.0:
        raise ValueError(f"Percentage must be between 0.0 and 100.0, got {percentage}")
    return Percentage(percentage)

def validate_user_id(user_id: str) -> UserID:
    """Validate and convert a user ID."""
    if not user_id or not isinstance(user_id, str):
        raise ValueError("User ID must be a non-empty string")
    return UserID(user_id)

def validate_session_id(session_id: str) -> SessionID:
    """Validate and convert a session ID."""
    if not session_id or not isinstance(session_id, str):
        raise ValueError("Session ID must be a non-empty string")
    return SessionID(session_id)

# JSON serialization helpers
def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format."""
    return dt.isoformat()

def deserialize_datetime(dt_str: str) -> datetime:
    """Deserialize datetime from ISO format."""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

def serialize_enum(enum_value: Enum) -> str:
    """Serialize enum to string value."""
    return enum_value.value

def serialize_dataclass(obj: Any) -> Dict[str, Any]:
    """Serialize dataclass to dictionary."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj)} is not serializable")

# Constants
DEFAULT_QUERY_TIMEOUT: Final[int] = 30
DEFAULT_SESSION_TIMEOUT: Final[int] = 3600  # 1 hour
DEFAULT_MEMORY_TTL_DAYS: Final[int] = 90
DEFAULT_CACHE_SIZE: Final[int] = 1000
MAX_QUERY_LENGTH: Final[int] = 10000
MAX_MEMORY_SIZE_MB: Final[int] = 100
MIN_CONFIDENCE_THRESHOLD: Final[Score] = Score(0.1)
DEFAULT_TEMPERATURE: Final[float] = 0.1
DEFAULT_MAX_TOKENS: Final[int] = 2048

# Type guards
def is_valid_sql_query(query: str) -> bool:
    """Check if a string is a valid SQL query."""
    if not query or not isinstance(query, str):
        return False
    # Basic SQL validation - starts with common SQL keywords
    query_upper = query.strip().upper()
    sql_keywords = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH'}
    return any(query_upper.startswith(keyword) for keyword in sql_keywords)

def is_valid_memory_content(content: Any) -> bool:
    """Check if content is valid for memory storage."""
    if content is None:
        return False
    if isinstance(content, (str, dict, list)):
        return True
    return False

# Additional dataclass definitions for comprehensive schema support
@dataclass(frozen=True)
class ColumnSchema:
    """Immutable column schema information."""
    name: ColumnName
    data_type: str
    nullable: bool
    default_value: Optional[str] = None
    description: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "nullable": self.nullable,
            "default_value": self.default_value,
            "description": self.description,
            "constraints": self.constraints,
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "foreign_key_reference": self.foreign_key_reference,
        }

@dataclass(frozen=True)
class IndexSchema:
    """Immutable index schema information."""
    name: str
    table_name: TableName
    columns: List[ColumnName]
    unique: bool = False
    index_type: str = "btree"
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "table_name": self.table_name,
            "columns": list(self.columns),
            "unique": self.unique,
            "index_type": self.index_type,
            "description": self.description,
        }

@dataclass(frozen=True)
class Relationship:
    """Immutable relationship between tables."""
    name: str
    source_table: TableName
    source_column: ColumnName
    target_table: TableName
    target_column: ColumnName
    relationship_type: Literal["one_to_one", "one_to_many", "many_to_many"]
    constraint_name: Optional[str] = None
    on_delete: str = "RESTRICT"
    on_update: str = "RESTRICT"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "source_table": self.source_table,
            "source_column": self.source_column,
            "target_table": self.target_table,
            "target_column": self.target_column,
            "relationship_type": self.relationship_type,
            "constraint_name": self.constraint_name,
            "on_delete": self.on_delete,
            "on_update": self.on_update,
        }

@dataclass
class MemoryStats:
    """Memory usage statistics."""
    total_memories: int = 0
    memories_by_type: Dict[MemoryType, int] = field(default_factory=dict)
    total_size_bytes: int = 0
    average_relevance_score: Score = Score(0.0)
    oldest_memory: Optional[Timestamp] = None
    newest_memory: Optional[Timestamp] = None
    user_count: int = 0
    active_sessions: int = 0
    cache_hit_rate: Percentage = Percentage(0.0)

    def add_memory(self, memory: MemoryContext, size_bytes: int) -> None:
        """Add memory to statistics."""
        self.total_memories += 1
        self.total_size_bytes += size_bytes

        if memory.memory_type not in self.memories_by_type:
            self.memories_by_type[memory.memory_type] = 0
        self.memories_by_type[memory.memory_type] += 1

        if self.oldest_memory is None or memory.created_at < self.oldest_memory:
            self.oldest_memory = memory.created_at
        if self.newest_memory is None or memory.created_at > self.newest_memory:
            self.newest_memory = memory.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_memories": self.total_memories,
            "memories_by_type": {k.value: v for k, v in self.memories_by_type.items()},
            "total_size_bytes": self.total_size_bytes,
            "average_relevance_score": self.average_relevance_score,
            "oldest_memory": self.oldest_memory.isoformat() if self.oldest_memory else None,
            "newest_memory": self.newest_memory.isoformat() if self.newest_memory else None,
            "user_count": self.user_count,
            "active_sessions": self.active_sessions,
            "cache_hit_rate": self.cache_hit_rate,
        }

@dataclass(frozen=True)
class QueryMetrics:
    """Query performance metrics."""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time_ms: float = 0.0
    median_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    queries_by_complexity: Dict[QueryComplexity, int] = field(default_factory=dict)
    cache_hit_rate: Percentage = Percentage(0.0)
    memory_usage_mb: float = 0.0

    @property
    def success_rate(self) -> Percentage:
        """Calculate success rate."""
        if self.total_queries == 0:
            return Percentage(0.0)
        return Percentage((self.successful_queries / self.total_queries) * 100.0)

    @property
    def failure_rate(self) -> Percentage:
        """Calculate failure rate."""
        return Percentage(100.0 - self.success_rate)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "average_response_time_ms": self.average_response_time_ms,
            "median_response_time_ms": self.median_response_time_ms,
            "p95_response_time_ms": self.p95_response_time_ms,
            "queries_by_complexity": {k.name: v for k, v in self.queries_by_complexity.items()},
            "cache_hit_rate": self.cache_hit_rate,
            "memory_usage_mb": self.memory_usage_mb,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
        }

# Protocol definitions for better type safety and dependency injection
class MemoryProviderProtocol(Protocol):
    """Protocol for memory providers."""

    async def store_memory(
        self,
        user_id: UserID,
        memory: MemoryContext
    ) -> MemoryID:
        """Store a memory."""
        ...

    async def retrieve_memories(
        self,
        user_id: UserID,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[MemoryType]] = None
    ) -> List[MemoryContext]:
        """Retrieve relevant memories."""
        ...

    async def delete_memory(self, memory_id: MemoryID) -> bool:
        """Delete a memory."""
        ...

    async def get_memory_stats(self, user_id: Optional[UserID] = None) -> MemoryStats:
        """Get memory statistics."""
        ...

class LLMProviderProtocol(Protocol):
    """Protocol for LLM providers."""

    async def generate_sql(
        self,
        natural_query: NaturalLanguageQuery,
        schema: SchemaInfo,
        context: List[MemoryContext],
        dialect: SQLDialect = SQLDialect.POSTGRESQL
    ) -> QueryResult:
        """Generate SQL from natural language."""
        ...

    async def explain_query(self, sql_query: SQLQuery) -> str:
        """Explain what a SQL query does."""
        ...

    async def optimize_query(self, sql_query: SQLQuery, schema: SchemaInfo) -> SQLQuery:
        """Optimize a SQL query."""
        ...

class SchemaProviderProtocol(Protocol):
    """Protocol for schema providers."""

    async def get_schema(self, database_name: DatabaseName) -> SchemaInfo:
        """Get database schema information."""
        ...

    async def get_table_schema(self, database_name: DatabaseName, table_name: TableName) -> TableSchema:
        """Get specific table schema."""
        ...

    async def validate_query(self, sql_query: SQLQuery, schema: SchemaInfo) -> bool:
        """Validate query against schema."""
        ...

class SessionProviderProtocol(Protocol):
    """Protocol for session providers."""

    async def create_session(self, user_id: UserID) -> UserSession:
        """Create a new user session."""
        ...

    async def get_session(self, session_id: SessionID) -> Optional[UserSession]:
        """Get session by ID."""
        ...

    async def update_session(self, session: UserSession) -> None:
        """Update session information."""
        ...

    async def delete_session(self, session_id: SessionID) -> bool:
        """Delete a session."""
        ...

# Enhanced JSON serialization with proper type handling
def to_json_serializable(obj: Any) -> JSONValue:
    """Convert object to JSON serializable format with proper type handling."""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, datetime):
        return serialize_datetime(obj)
    elif isinstance(obj, Enum):
        return serialize_enum(obj)
    elif isinstance(obj, (UserID, SessionID, QueryID, MemoryID, SchemaID, TableName, ColumnName, DatabaseName)):
        return str(obj)
    elif hasattr(obj, 'to_dict'):  # Custom serializable objects
        return obj.to_dict()
    elif hasattr(obj, 'dict'):  # Pydantic models
        return obj.dict()
    elif isinstance(obj, (list, tuple, set)):
        return [to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): to_json_serializable(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):  # Dataclasses and other objects
        return {k: to_json_serializable(v) for k, v in obj.__dict__.items()}
    else:
        # Fallback to string representation
        return str(obj)


# Additional type aliases for vector stores and LLM providers
DocumentID = Union[str, int]
EmbeddingVector = List[float]
Score = float


@dataclass
class QueryExplanation:
    """Explanation of a SQL query."""
    sql_query: str
    summary: str
    step_by_step: List[str]
    performance_notes: Optional[str] = None
    complexity: str = "medium"  # simple, medium, complex
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OptimizationSuggestion:
    """Suggestion for query optimization."""
    type: str  # index, rewrite, performance, best_practice
    description: str
    suggestion: str
    impact: str = "medium"  # high, medium, low
    effort: str = "moderate"  # easy, moderate, complex
    metadata: Optional[Dict[str, Any]] = None