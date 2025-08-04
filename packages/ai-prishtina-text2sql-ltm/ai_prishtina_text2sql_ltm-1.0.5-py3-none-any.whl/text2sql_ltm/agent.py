"""
Main Text2SQL Agent with Long-Term Memory capabilities.

This module provides the core Text2SQLAgent class that integrates natural language
to SQL conversion with advanced long-term memory capabilities.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncContextManager
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uuid

from .config import ConfigurationManager, MemoryConfig, AgentConfig, SecurityConfig, PerformanceConfig, get_config
from .types import (
    UserID, SessionID, QueryID, MemoryID, SchemaID, DatabaseName, TableName,
    QueryResult, MemoryContext, UserSession, SchemaInfo, QueryStatus,
    QueryComplexity, SQLDialect, NaturalLanguageQuery, SQLQuery, QueryContext,
    validate_user_id, validate_session_id, Score, Timestamp
)
from .exceptions import (
    Text2SQLLTMError, QueryGenerationError, SessionError, MemoryError,
    AuthenticationError, AuthorizationError, RateLimitExceededError,
    SchemaError, ContextError
)

# Import components with fallbacks for missing modules
try:
    from .memory import MemoryManager
except ImportError:
    class MemoryManager:
        def __init__(self, *args, **kwargs):
            pass

try:
    from .session import SessionManager
except ImportError:
    class SessionManager:
        def __init__(self, *args, **kwargs):
            pass

try:
    from .context import ContextEngine
except ImportError:
    class ContextEngine:
        def __init__(self, *args, **kwargs):
            pass

try:
    from .schema import SchemaManager
except ImportError:
    class SchemaManager:
        def __init__(self, *args, **kwargs):
            pass

try:
    from .llm import create_llm_provider
except ImportError:
    def create_llm_provider(*args, **kwargs):
        return None

try:
    from .sql_generator import SQLGenerator
except ImportError:
    class SQLGenerator:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)


class Text2SQLAgent:
    """
    Production-grade Text2SQL Agent with Long-Term Memory capabilities.

    This agent provides a comprehensive solution for converting natural language
    queries to SQL with intelligent memory management, featuring:

    - Context-aware SQL generation using historical queries and patterns
    - User-specific memory isolation and personalization
    - Adaptive learning from user feedback and query patterns
    - Multi-turn conversation support with persistent context
    - Comprehensive security, monitoring, and error handling
    - Type-safe interfaces and comprehensive validation

    The agent is designed as a library component and can be easily integrated
    into larger applications or used as a standalone service.
    """

    def __init__(
        self,
        config_manager: ConfigurationManager,
        *,
        memory_manager: Optional[Any] = None,
        session_manager: Optional[Any] = None,
        schema_manager: Optional[Any] = None,
        llm_provider: Optional[Any] = None
    ):
        """
        Initialize the Text2SQL Agent.

        Args:
            config_manager: Configuration manager with all settings
            memory_manager: Optional custom memory manager
            session_manager: Optional custom session manager
            schema_manager: Optional custom schema manager
            llm_provider: Optional custom LLM provider
        """
        self.config_manager = config_manager
        self.memory_config = config_manager.get_config("memory")
        self.agent_config = config_manager.get_config("agent")
        self.security_config = config_manager.get_config("security")
        self.performance_config = config_manager.get_config("performance")

        # Initialize components (will be set during initialization)
        self._memory_manager = memory_manager
        self._session_manager = session_manager
        self._schema_manager = schema_manager
        self._llm_provider = llm_provider

        # State tracking
        self._initialized = False
        self._closed = False
        self._active_sessions: Dict[SessionID, UserSession] = {}
        self._query_cache: Dict[str, QueryResult] = {}
        self._rate_limiters: Dict[UserID, Any] = {}

        # Metrics and monitoring
        self._metrics = {
            "queries_processed": 0,
            "queries_successful": 0,
            "queries_failed": 0,
            "memory_contexts_used": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
        }

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def initialize(self) -> None:
        """
        Initialize the agent and all its components.

        This method must be called before using the agent.
        It sets up all necessary connections and validates the configuration.
        """
        if self._initialized:
            return

        try:
            self.logger.info("Initializing Text2SQL Agent...")

            # Validate configuration
            self.config_manager.validate_all()

            # Initialize memory manager
            if self._memory_manager is None:
                from .memory import MemoryManager
                self._memory_manager = MemoryManager(self.memory_config)
            await self._memory_manager.initialize()

            # Initialize session manager
            if self._session_manager is None:
                from .session import SessionManager
                self._session_manager = SessionManager(
                    self.security_config,
                    self.performance_config
                )
            await self._session_manager.initialize()

            # Initialize schema manager
            if self._schema_manager is None:
                from .schema import SchemaManager
                self._schema_manager = SchemaManager(self.performance_config)
            await self._schema_manager.initialize()

            # Initialize LLM provider
            if self._llm_provider is None:
                from .llm import create_llm_provider
                self._llm_provider = create_llm_provider(self.agent_config)
            await self._llm_provider.initialize()

            self._initialized = True
            self.logger.info("Text2SQL Agent initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Text2SQL Agent: {str(e)}")
            raise Text2SQLLTMError(
                "Agent initialization failed",
                details={"error": str(e)},
                cause=e
            ) from e

    async def close(self) -> None:
        """
        Close the agent and clean up all resources.

        This method should be called when the agent is no longer needed
        to ensure proper cleanup of connections and resources.
        """
        if self._closed:
            return

        try:
            self.logger.info("Closing Text2SQL Agent...")

            # Close all components
            if self._memory_manager:
                await self._memory_manager.close()

            if self._session_manager:
                await self._session_manager.close()

            if self._schema_manager:
                await self._schema_manager.close()

            if self._llm_provider:
                await self._llm_provider.close()

            # Clear caches and state
            self._active_sessions.clear()
            self._query_cache.clear()
            self._rate_limiters.clear()

            self._closed = True
            self.logger.info("Text2SQL Agent closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing Text2SQL Agent: {str(e)}")
            raise Text2SQLLTMError(
                "Agent cleanup failed",
                details={"error": str(e)},
                cause=e
            ) from e

    @asynccontextmanager
    async def session_context(self) -> AsyncContextManager[Text2SQLAgent]:
        """
        Async context manager for the agent lifecycle.

        Usage:
            async with agent.session_context():
                result = await agent.query(...)
        """
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()

    def _ensure_initialized(self) -> None:
        """Ensure the agent is initialized."""
        if not self._initialized:
            raise Text2SQLLTMError("Agent not initialized. Call initialize() first.")

        if self._closed:
            raise Text2SQLLTMError("Agent is closed. Create a new instance.")

    async def _check_rate_limit(self, user_id: UserID) -> None:
        """Check rate limiting for a user."""
        if not self.security_config.rate_limiting_enabled:
            return

        # Implementation would depend on chosen rate limiting library
        # For now, we'll implement a simple in-memory rate limiter
        current_time = datetime.utcnow()

        if user_id not in self._rate_limiters:
            self._rate_limiters[user_id] = {
                "requests": [],
                "last_reset": current_time
            }

        rate_limiter = self._rate_limiters[user_id]

        # Clean old requests (older than 1 minute)
        minute_ago = current_time - timedelta(minutes=1)
        rate_limiter["requests"] = [
            req_time for req_time in rate_limiter["requests"]
            if req_time > minute_ago
        ]

        # Check if limit exceeded
        if len(rate_limiter["requests"]) >= self.security_config.max_requests_per_minute:
            raise RateLimitExceededError(
                user_id=str(user_id),
                limit=self.security_config.max_requests_per_minute,
                window="minute"
            )

        # Add current request
        rate_limiter["requests"].append(current_time)

    async def _authenticate_user(self, user_id: str, auth_token: Optional[str] = None) -> UserID:
        """Authenticate a user and return validated user ID."""
        if not self.security_config.require_authentication:
            return validate_user_id(user_id)

        if not auth_token:
            raise AuthenticationError(user_id=user_id, reason="No authentication token provided")

        # Implementation would depend on chosen authentication method
        # For now, we'll do basic validation
        validated_user_id = validate_user_id(user_id)

        # Check rate limiting
        await self._check_rate_limit(validated_user_id)

        return validated_user_id

    async def query(
        self,
        natural_language: NaturalLanguageQuery,
        user_id: str,
        *,
        session_id: Optional[str] = None,
        database_schema: Optional[SchemaInfo] = None,
        database_name: Optional[str] = None,
        sql_dialect: SQLDialect = SQLDialect.POSTGRESQL,
        context: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
        remember_query: bool = True,
        learn_from_feedback: bool = True,
        include_explanation: bool = True,
        max_complexity: Optional[QueryComplexity] = None
    ) -> QueryResult:
        """
        Process a natural language query and convert it to SQL with memory enhancement.

        This is the main entry point for the Text2SQL agent. It handles the complete
        pipeline from natural language input to SQL output, including memory retrieval,
        context enhancement, query generation, and result caching.

        Args:
            natural_language: The natural language query to convert
            user_id: User identifier for memory isolation and personalization
            session_id: Optional session identifier for conversation context
            database_schema: Database schema information (auto-retrieved if not provided)
            database_name: Database name for schema retrieval
            sql_dialect: Target SQL dialect for the generated query
            context: Additional context information for query generation
            auth_token: Authentication token (required if authentication is enabled)
            remember_query: Whether to store this query in long-term memory
            learn_from_feedback: Whether to enable learning from user feedback
            include_explanation: Whether to include query explanation in response
            max_complexity: Maximum allowed query complexity (uses config default if None)

        Returns:
            QueryResult: Complete query result with SQL, explanation, and metadata

        Raises:
            Text2SQLLTMError: Base exception for all agent errors
            AuthenticationError: When authentication fails
            RateLimitExceededError: When rate limit is exceeded
            QueryGenerationError: When SQL generation fails
            SchemaError: When schema operations fail
            MemoryError: When memory operations fail
        """
        self._ensure_initialized()

        start_time = datetime.utcnow()
        query_id = QueryID(str(uuid.uuid4()))

        try:
            # Authenticate user
            validated_user_id = await self._authenticate_user(user_id, auth_token)

            # Validate input
            if not natural_language or not natural_language.strip():
                raise QueryGenerationError(
                    natural_language="",
                    reason="Natural language query cannot be empty"
                )

            if len(natural_language) > self.agent_config.max_tokens * 4:  # Rough estimate
                raise QueryGenerationError(
                    natural_language=natural_language[:100] + "...",
                    reason="Query too long"
                )

            # Set complexity limit
            complexity_limit = max_complexity or self.agent_config.max_query_complexity

            # Check cache first
            cache_key = self._generate_cache_key(
                natural_language, validated_user_id, sql_dialect, database_name
            )

            if self.agent_config.cache_enabled and cache_key in self._query_cache:
                cached_result = self._query_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self._metrics["cache_hits"] += 1
                    self.logger.debug(f"Cache hit for query: {query_id}")
                    return cached_result

            self._metrics["cache_misses"] += 1

            # Get or create session
            session = await self._get_or_create_session(validated_user_id, session_id)

            # Retrieve database schema if not provided
            if database_schema is None and database_name:
                database_schema = await self._schema_manager.get_schema(
                    DatabaseName(database_name)
                )

            # Retrieve relevant memories
            memory_contexts = await self._retrieve_relevant_memories(
                validated_user_id, natural_language, session
            )

            # Enhance context with memory and session information
            enhanced_context = await self._enhance_query_context(
                natural_language=natural_language,
                user_session=session,
                memory_contexts=memory_contexts,
                additional_context=context or {},
                database_schema=database_schema
            )

            # Generate SQL query
            sql_result = await self._generate_sql_query(
                natural_language=natural_language,
                enhanced_context=enhanced_context,
                schema=database_schema,
                dialect=sql_dialect,
                complexity_limit=complexity_limit
            )

            # Validate generated SQL
            if self.agent_config.enable_query_validation and database_schema:
                await self._validate_sql_query(sql_result.sql, database_schema)

            # Create comprehensive query result
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = QueryResult(
                sql=sql_result.sql,
                explanation=sql_result.explanation if include_explanation else "",
                confidence=sql_result.confidence,
                query_type=sql_result.query_type,
                tables_used=sql_result.tables_used,
                columns_used=sql_result.columns_used,
                complexity=sql_result.complexity,
                dialect=sql_dialect,
                execution_time_ms=int(processing_time * 1000),
                memory_context_used=[ctx.memory_id for ctx in memory_contexts],
                metadata={
                    "query_id": query_id,
                    "user_id": validated_user_id,
                    "session_id": session.session_id,
                    "memory_enhanced": len(memory_contexts) > 0,
                    "context_score": enhanced_context.get("relevance_score", 0.0),
                    "processing_time_ms": int(processing_time * 1000),
                    "cache_used": False,
                    "schema_used": database_schema is not None,
                    "dialect": sql_dialect.value,
                },
                created_at=start_time
            )

            # Store in memory if requested
            if remember_query and self.memory_config.learning_enabled:
                await self._store_query_memory(
                    validated_user_id, natural_language, result, session
                )

            # Update session context
            await self._update_session_context(session, natural_language, result)

            # Cache result
            if self.agent_config.cache_enabled:
                self._query_cache[cache_key] = result
                self._cleanup_cache()

            # Update metrics
            self._update_metrics(result, processing_time)

            self.logger.info(
                f"Query processed successfully",
                extra={
                    "query_id": query_id,
                    "user_id": validated_user_id,
                    "processing_time_ms": int(processing_time * 1000),
                    "confidence": result.confidence,
                    "complexity": result.complexity.name,
                    "memory_contexts": len(memory_contexts)
                }
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._metrics["queries_failed"] += 1

            self.logger.error(
                f"Query processing failed",
                extra={
                    "query_id": query_id,
                    "user_id": user_id,
                    "error": str(e),
                    "processing_time_ms": int(processing_time * 1000)
                }
            )

            if isinstance(e, Text2SQLLTMError):
                raise
            else:
                raise QueryGenerationError(
                    natural_language=natural_language[:100] + "..." if len(natural_language) > 100 else natural_language,
                    reason=f"Unexpected error: {str(e)}",
                    cause=e
                ) from e

    def _generate_cache_key(
        self,
        natural_language: str,
        user_id: UserID,
        dialect: SQLDialect,
        database_name: Optional[str]
    ) -> str:
        """Generate a cache key for the query."""
        import hashlib

        key_components = [
            natural_language.lower().strip(),
            str(user_id),
            dialect.value,
            database_name or "default"
        ]

        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _is_cache_valid(self, cached_result: QueryResult) -> bool:
        """Check if a cached result is still valid."""
        if not self.agent_config.cache_enabled:
            return False

        cache_age = datetime.utcnow() - cached_result.created_at
        return cache_age.total_seconds() < self.agent_config.cache_ttl

    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        if len(self._query_cache) <= self.agent_config.cache_size:
            return

        # Remove expired entries first
        current_time = datetime.utcnow()
        expired_keys = []

        for key, result in self._query_cache.items():
            if not self._is_cache_valid(result):
                expired_keys.append(key)

        for key in expired_keys:
            del self._query_cache[key]

        # If still over limit, remove oldest entries
        if len(self._query_cache) > self.agent_config.cache_size:
            sorted_items = sorted(
                self._query_cache.items(),
                key=lambda x: x[1].created_at
            )

            items_to_remove = len(self._query_cache) - self.agent_config.cache_size
            for key, _ in sorted_items[:items_to_remove]:
                del self._query_cache[key]

    async def _get_or_create_session(
        self,
        user_id: UserID,
        session_id: Optional[str]
    ) -> UserSession:
        """Get existing session or create a new one."""
        if session_id:
            validated_session_id = validate_session_id(session_id)
            session = await self._session_manager.get_session(validated_session_id)
            if session and session.user_id == user_id:
                return session

        # Create new session
        return await self._session_manager.create_session(user_id)

    async def _retrieve_relevant_memories(
        self,
        user_id: UserID,
        natural_language: str,
        session: UserSession
    ) -> List[MemoryContext]:
        """Retrieve relevant memories for query enhancement."""
        if not self.memory_config.learning_enabled:
            return []

        try:
            # Get memories based on query content
            content_memories = await self._memory_manager.search_memories(
                user_id=user_id,
                query=natural_language,
                limit=self.agent_config.max_memory_contexts,
                relevance_threshold=self.agent_config.memory_relevance_threshold
            )

            # Get session-specific memories
            session_memories = await self._memory_manager.get_session_memories(
                user_id=user_id,
                session_id=session.session_id,
                limit=5
            )

            # Combine and deduplicate
            all_memories = content_memories + session_memories
            seen_ids = set()
            unique_memories = []

            for memory in all_memories:
                if memory.memory_id not in seen_ids:
                    seen_ids.add(memory.memory_id)
                    unique_memories.append(memory)

            # Sort by relevance and limit
            unique_memories.sort(key=lambda m: m.relevance_score, reverse=True)
            return unique_memories[:self.agent_config.max_memory_contexts]

        except Exception as e:
            self.logger.warning(f"Failed to retrieve memories: {str(e)}")
            return []

    async def _enhance_query_context(
        self,
        natural_language: str,
        user_session: UserSession,
        memory_contexts: List[MemoryContext],
        additional_context: Dict[str, Any],
        database_schema: Optional[SchemaInfo]
    ) -> Dict[str, Any]:
        """Enhance query context with memory and session information."""
        enhanced_context = {
            "natural_language": natural_language,
            "user_preferences": user_session.preferences,
            "session_context": user_session.context,
            "query_history": user_session.query_history[-self.agent_config.context_window_size:],
            "memory_contexts": [ctx.to_dict() for ctx in memory_contexts],
            "relevance_score": sum(ctx.relevance_score for ctx in memory_contexts) / len(memory_contexts) if memory_contexts else 0.0,
            "schema_available": database_schema is not None,
            **additional_context
        }

        # Add schema information if available
        if database_schema:
            enhanced_context["database_schema"] = database_schema.to_dict()
            enhanced_context["available_tables"] = list(database_schema.get_table_names())

        return enhanced_context

    async def _generate_sql_query(
        self,
        natural_language: str,
        enhanced_context: Dict[str, Any],
        schema: Optional[SchemaInfo],
        dialect: SQLDialect,
        complexity_limit: QueryComplexity
    ) -> QueryResult:
        """Generate SQL query using the LLM provider."""
        try:
            return await self._llm_provider.generate_sql(
                natural_query=natural_language,
                context=enhanced_context,
                schema=schema,
                dialect=dialect,
                max_complexity=complexity_limit,
                temperature=self.agent_config.temperature,
                max_tokens=self.agent_config.max_tokens
            )
        except Exception as e:
            raise QueryGenerationError(
                natural_language=natural_language,
                reason=f"LLM generation failed: {str(e)}",
                cause=e
            ) from e

    async def _validate_sql_query(self, sql: SQLQuery, schema: SchemaInfo) -> None:
        """Validate the generated SQL query."""
        try:
            # Basic SQL syntax validation
            if not sql or not sql.strip():
                raise ValueError("Generated SQL is empty")

            # Check for blocked keywords
            sql_upper = sql.upper()
            for keyword in self.agent_config.blocked_keywords:
                if keyword in sql_upper:
                    raise ValueError(f"Blocked keyword '{keyword}' found in query")

            # Validate against schema if available
            if schema:
                await self._schema_manager.validate_query(sql, schema)

        except Exception as e:
            raise QueryGenerationError(
                natural_language="",
                reason=f"SQL validation failed: {str(e)}",
                cause=e
            ) from e

    async def _store_query_memory(
        self,
        user_id: UserID,
        natural_language: str,
        result: QueryResult,
        session: UserSession
    ) -> None:
        """Store query and result in long-term memory."""
        try:
            memory_content = {
                "natural_language": natural_language,
                "sql_query": result.sql,
                "query_type": result.query_type,
                "tables_used": result.tables_used,
                "confidence": result.confidence,
                "complexity": result.complexity.name,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self._memory_manager.store_memory(
                user_id=user_id,
                content=memory_content,
                memory_type="query_pattern",
                metadata={
                    "session_id": session.session_id,
                    "query_id": result.metadata.get("query_id"),
                    "processing_time_ms": result.execution_time_ms
                }
            )

        except Exception as e:
            self.logger.warning(f"Failed to store query memory: {str(e)}")

    async def _update_session_context(
        self,
        session: UserSession,
        natural_language: str,
        result: QueryResult
    ) -> None:
        """Update session context with query information."""
        try:
            # Add to query history
            query_id = result.metadata.get("query_id")
            if query_id:
                session.query_history.append(QueryID(query_id))

                # Keep only recent queries
                max_history = self.agent_config.context_window_size
                if len(session.query_history) > max_history:
                    session.query_history = session.query_history[-max_history:]

            # Update session context
            session.context["last_query"] = natural_language
            session.context["last_tables"] = result.tables_used
            session.context["last_query_type"] = result.query_type
            session.update_activity()

            # Save session
            await self._session_manager.update_session(session)

        except Exception as e:
            self.logger.warning(f"Failed to update session context: {str(e)}")

    def _update_metrics(self, result: QueryResult, processing_time: float) -> None:
        """Update internal metrics."""
        self._metrics["queries_processed"] += 1
        self._metrics["queries_successful"] += 1

        if result.memory_context_used:
            self._metrics["memory_contexts_used"] += len(result.memory_context_used)

        # Update average response time
        current_avg = self._metrics["average_response_time"]
        total_queries = self._metrics["queries_processed"]
        self._metrics["average_response_time"] = (
            (current_avg * (total_queries - 1) + processing_time) / total_queries
        )

    # Public API methods for additional functionality

    async def get_user_session(self, user_id: str, session_id: str) -> Optional[UserSession]:
        """Get a user session by ID."""
        self._ensure_initialized()

        validated_user_id = validate_user_id(user_id)
        validated_session_id = validate_session_id(session_id)

        session = await self._session_manager.get_session(validated_session_id)
        if session and session.user_id == validated_user_id:
            return session

        return None

    async def create_user_session(self, user_id: str) -> UserSession:
        """Create a new user session."""
        self._ensure_initialized()

        validated_user_id = validate_user_id(user_id)
        return await self._session_manager.create_session(validated_user_id)

    async def delete_user_session(self, user_id: str, session_id: str) -> bool:
        """Delete a user session."""
        self._ensure_initialized()

        validated_user_id = validate_user_id(user_id)
        validated_session_id = validate_session_id(session_id)

        # Verify ownership
        session = await self._session_manager.get_session(validated_session_id)
        if not session or session.user_id != validated_user_id:
            return False

        return await self._session_manager.delete_session(validated_session_id)

    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 10,
        memory_types: Optional[List[str]] = None
    ) -> List[MemoryContext]:
        """Get user memories."""
        self._ensure_initialized()

        validated_user_id = validate_user_id(user_id)
        return await self._memory_manager.get_user_memories(
            user_id=validated_user_id,
            limit=limit,
            memory_types=memory_types
        )

    async def delete_user_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific user memory."""
        self._ensure_initialized()

        validated_user_id = validate_user_id(user_id)
        memory_id_typed = MemoryID(memory_id)

        return await self._memory_manager.delete_memory(
            user_id=validated_user_id,
            memory_id=memory_id_typed
        )

    async def get_database_schema(self, database_name: str) -> Optional[SchemaInfo]:
        """Get database schema information."""
        self._ensure_initialized()

        try:
            return await self._schema_manager.get_schema(DatabaseName(database_name))
        except SchemaError:
            return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics."""
        return self._metrics.copy()

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "memory_backend": self.memory_config.storage_backend.value,
            "llm_provider": self.agent_config.llm_provider.value,
            "llm_model": self.agent_config.llm_model,
            "default_dialect": self.agent_config.default_sql_dialect.value,
            "memory_enabled": self.memory_config.learning_enabled,
            "cache_enabled": self.agent_config.cache_enabled,
            "authentication_required": self.security_config.require_authentication,
            "rate_limiting_enabled": self.security_config.rate_limiting_enabled,
        }

    @property
    def is_initialized(self) -> bool:
        """Check if the agent is initialized."""
        return self._initialized

    @property
    def is_closed(self) -> bool:
        """Check if the agent is closed."""
        return self._closed
    
    def __init__(
        self,
        memory_config: Optional[MemoryConfig] = None,
        agent_config: Optional[AgentConfig] = None,
        **kwargs
    ):
        """
        Initialize the Text2SQL agent with memory capabilities.
        
        Args:
            memory_config: Memory system configuration
            agent_config: Agent behavior configuration
            **kwargs: Additional configuration overrides
        """
        # Load configuration
        config = get_config()
        self.memory_config = memory_config or config.get("memory", MemoryConfig())
        self.agent_config = agent_config or config.get("agent", AgentConfig())
        
        # Apply any overrides
        for key, value in kwargs.items():
            if hasattr(self.memory_config, key):
                setattr(self.memory_config, key, value)
            elif hasattr(self.agent_config, key):
                setattr(self.agent_config, key, value)
        
        # Use standard logger (bind method not available in standard logging)
        self.logger = logger
        
        # Initialize core components
        self._init_components()
        
        # Agent state
        self._initialized = False
        self._stats = {
            "queries_processed": 0,
            "successful_queries": 0,
            "memory_enhanced_queries": 0,
            "learning_events": 0,
        }
        
        self.logger.info("Text2SQLAgent initialized",
                        memory_backend=self.memory_config.storage_backend,
                        llm_provider=self.agent_config.llm_provider)
    
    def _init_components(self) -> None:
        """Initialize all agent components."""
        try:
            # Memory management
            self.memory_manager = MemoryManager(self.memory_config)
            
            # Session management
            self.session_manager = SessionManager(
                memory_manager=self.memory_manager,
                config=self.agent_config
            )
            
            # Context processing
            self.context_engine = ContextEngine(
                memory_manager=self.memory_manager,
                config=self.agent_config
            )
            
            # Schema management
            self.schema_manager = SchemaManager(
                memory_manager=self.memory_manager
            )
            
            # LLM provider
            self.llm_provider = create_llm_provider(self.agent_config)
            
            # SQL generation
            self.sql_generator = SQLGenerator(
                llm_provider=self.llm_provider,
                schema_manager=self.schema_manager,
                config=self.agent_config
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise Text2SQLLTMError(f"Component initialization failed: {str(e)}", cause=e)
    
    async def initialize(self) -> None:
        """Initialize the agent and all components."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing Text2SQL Agent")
            
            # Initialize components that need async setup
            await self.memory_manager.storage.initialize()
            await self.schema_manager.initialize()
            
            self._initialized = True
            self.logger.info("Text2SQL Agent initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {str(e)}")
            raise Text2SQLLTMError(f"Agent initialization failed: {str(e)}", cause=e)
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        try:
            self.logger.info("Cleaning up Text2SQL Agent")
            
            # Cleanup components
            if hasattr(self.memory_manager, 'storage'):
                await self.memory_manager.storage.cleanup()
            
            await self.session_manager.cleanup_expired_sessions()
            
            self._initialized = False
            self.logger.info("Text2SQL Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        context_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserSession:
        """
        Create a new user session with memory context.
        
        Args:
            user_id: User identifier
            session_id: Optional session identifier
            context_type: Type of session context
            metadata: Additional session metadata
            
        Returns:
            UserSession instance
        """
        try:
            session = self.session_manager.create_session(
                user_id=user_id,
                session_id=session_id,
                context_type=context_type,
                metadata=metadata
            )
            
            self.logger.info("Session created",
                           user_id=user_id,
                           session_id=session.session_id,
                           context_type=context_type)
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session for user {user_id}: {str(e)}")
            raise SessionError(f"Failed to create session: {str(e)}", cause=e)
    
    async def query(
        self,
        natural_language: str,
        user_id: str,
        session_id: Optional[str] = None,
        database_schema: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        remember_query: bool = True,
        learn_from_feedback: bool = True
    ) -> QueryResult:
        """
        Process a natural language query with memory enhancement.
        
        Args:
            natural_language: Natural language query
            user_id: User identifier
            session_id: Optional session identifier
            database_schema: Database schema information
            context: Additional query context
            remember_query: Whether to store this query in memory
            learn_from_feedback: Whether to learn from user feedback
            
        Returns:
            QueryResult with SQL and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Processing query",
                           user_id=user_id,
                           query=natural_language[:100])
            
            # Get or create session
            session = self.session_manager.get_session(user_id, session_id)
            if not session:
                session = self.create_session(user_id, session_id)
            
            # Build query context
            query_context = await self._build_query_context(
                natural_language=natural_language,
                user_id=user_id,
                session=session,
                database_schema=database_schema,
                additional_context=context
            )
            
            # Enhance query with memory context
            enhanced_context = await self.context_engine.enhance_query_context(
                query_context=query_context,
                user_id=user_id,
                session_history=session.get_history()
            )
            
            # Generate SQL using enhanced context
            sql_result = await self.sql_generator.generate_sql(
                natural_language=natural_language,
                context=enhanced_context,
                schema=database_schema
            )
            
            # Create query result
            result = QueryResult(
                sql=sql_result.sql,
                explanation=sql_result.explanation,
                confidence=sql_result.confidence,
                query_type=sql_result.query_type,
                tables_used=sql_result.tables_used,
                memory_context_used=enhanced_context.memory_influences,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                metadata={
                    "user_id": user_id,
                    "session_id": session.session_id,
                    "memory_enhanced": len(enhanced_context.memory_influences) > 0,
                    "context_score": enhanced_context.relevance_score,
                }
            )
            
            # Store query in memory if requested
            if remember_query:
                await self._store_query_memory(
                    user_id=user_id,
                    natural_language=natural_language,
                    sql_result=sql_result,
                    context=enhanced_context
                )
            
            # Update session history
            session.add_query(natural_language, result)
            
            # Update statistics
            self._stats["queries_processed"] += 1
            self._stats["successful_queries"] += 1
            if len(enhanced_context.memory_influences) > 0:
                self._stats["memory_enhanced_queries"] += 1
            
            self.logger.info("Query processed successfully",
                           user_id=user_id,
                           sql_length=len(result.sql),
                           confidence=result.confidence,
                           memory_enhanced=result.metadata["memory_enhanced"])
            
            return result
            
        except Exception as e:
            self._stats["queries_processed"] += 1
            self.logger.error(f"Failed to process query for user {user_id}: {str(e)}")
            raise QueryGenerationError(natural_language, str(e), e)
    
    async def learn_from_feedback(
        self,
        user_id: str,
        query_id: str,
        feedback: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> bool:
        """
        Learn from user feedback on query results.
        
        Args:
            user_id: User identifier
            query_id: Query identifier
            feedback: User feedback data
            session_id: Optional session identifier
            
        Returns:
            True if learning was successful
        """
        try:
            self.logger.info("Processing user feedback",
                           user_id=user_id,
                           query_id=query_id,
                           feedback_type=feedback.get("type"))
            
            # Store feedback as memory
            feedback_memory = {
                "query_id": query_id,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            await self.memory_manager.store_memory(
                user_id=user_id,
                content=feedback_memory,
                memory_type="feedback",
                metadata={
                    "query_id": query_id,
                    "feedback_type": feedback.get("type", "general"),
                    "rating": feedback.get("rating"),
                }
            )
            
            # Update learning statistics
            self._stats["learning_events"] += 1
            
            self.logger.info("Feedback processed successfully",
                           user_id=user_id,
                           query_id=query_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process feedback for user {user_id}, query {query_id}: {str(e)}")
            return False
    
    async def learn_database_schema(
        self,
        database_name: str,
        schema: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """
        Learn and remember database schema information.
        
        Args:
            database_name: Database name
            schema: Schema information
            user_id: Optional user context
            
        Returns:
            True if successful
        """
        try:
            await self.schema_manager.learn_schema(
                database_name=database_name,
                schema=schema,
                user_id=user_id
            )
            
            self.logger.info("Database schema learned",
                           database_name=database_name,
                           tables=len(schema.get("tables", {})))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to learn schema for database {database_name}: {str(e)}")
            return False
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get insights about user query patterns and preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            User insights and analytics
        """
        try:
            # Get memory statistics
            memory_stats = await self.memory_manager.get_user_memory_stats(user_id)
            
            # Get session statistics
            session_stats = await self.session_manager.get_user_session_stats(user_id)
            
            # Get recent memories for pattern analysis
            recent_memories = await self.memory_manager.retrieve_memories(
                user_id=user_id,
                memory_type="query",
                limit=50
            )
            
            # Analyze query patterns
            query_patterns = self._analyze_query_patterns(recent_memories)
            
            insights = {
                "memory_stats": memory_stats,
                "session_stats": session_stats,
                "query_patterns": query_patterns,
                "preferences": await self._extract_user_preferences(user_id),
                "learning_progress": {
                    "total_queries": len(recent_memories),
                    "accuracy_trend": self._calculate_accuracy_trend(recent_memories),
                    "complexity_trend": self._calculate_complexity_trend(recent_memories),
                }
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get user insights for user {user_id}: {str(e)}")
            return {}
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            **self._stats,
            "success_rate": (
                self._stats["successful_queries"] / 
                max(self._stats["queries_processed"], 1)
            ),
            "memory_enhancement_rate": (
                self._stats["memory_enhanced_queries"] / 
                max(self._stats["successful_queries"], 1)
            ),
            "components": {
                "memory_manager": self.memory_manager.get_manager_stats(),
                "session_manager": self.session_manager.get_stats(),
            }
        }
    
    async def _build_query_context(
        self,
        natural_language: str,
        user_id: str,
        session: UserSession,
        database_schema: Optional[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]]
    ) -> QueryContext:
        """Build comprehensive query context."""
        return QueryContext(
            user_id=user_id,
            session_id=session.session_id,
            current_query=natural_language,
            conversation_history=session.get_history(),
            database_schema=database_schema,
            additional_context=additional_context or {},
            timestamp=datetime.utcnow()
        )
    
    async def _store_query_memory(
        self,
        user_id: str,
        natural_language: str,
        sql_result: Any,
        context: Any
    ) -> None:
        """Store query and result in memory."""
        try:
            query_memory = {
                "natural_language": natural_language,
                "sql": sql_result.sql,
                "confidence": sql_result.confidence,
                "query_type": sql_result.query_type,
                "tables_used": sql_result.tables_used,
                "context_influences": context.memory_influences,
            }
            
            await self.memory_manager.store_memory(
                user_id=user_id,
                content=query_memory,
                memory_type="query",
                metadata={
                    "query_type": sql_result.query_type,
                    "confidence": sql_result.confidence,
                    "tables": sql_result.tables_used,
                }
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to store query memory for user {user_id}: {str(e)}")
    
    def _analyze_query_patterns(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user query patterns from memories."""
        patterns = {
            "common_query_types": {},
            "frequent_tables": {},
            "query_complexity_distribution": {},
            "time_patterns": {},
        }
        
        for memory in memories:
            content = memory.get("content", {})
            if isinstance(content, dict):
                # Query type analysis
                query_type = content.get("query_type", "unknown")
                patterns["common_query_types"][query_type] = (
                    patterns["common_query_types"].get(query_type, 0) + 1
                )
                
                # Table usage analysis
                tables = content.get("tables_used", [])
                for table in tables:
                    patterns["frequent_tables"][table] = (
                        patterns["frequent_tables"].get(table, 0) + 1
                    )
        
        return patterns
    
    async def _extract_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Extract user preferences from memory and feedback."""
        try:
            # Get feedback memories
            feedback_memories = await self.memory_manager.retrieve_memories(
                user_id=user_id,
                memory_type="feedback",
                limit=20
            )
            
            preferences = {
                "preferred_query_style": "standard",
                "complexity_preference": "medium",
                "explanation_detail": "medium",
            }
            
            # Analyze feedback to extract preferences
            for memory in feedback_memories:
                content = memory.get("content", {})
                feedback = content.get("feedback", {})
                
                # Extract preferences from feedback patterns
                if feedback.get("rating", 0) >= 4:
                    # High-rated queries indicate preferences
                    pass
            
            return preferences
            
        except Exception as e:
            self.logger.warning(f"Failed to extract user preferences for user {user_id}: {str(e)}")
            return {}
    
    def _calculate_accuracy_trend(self, memories: List[Dict[str, Any]]) -> List[float]:
        """Calculate accuracy trend from recent memories."""
        # Simplified implementation - in production, you'd use actual accuracy metrics
        return [0.8, 0.82, 0.85, 0.87, 0.9]  # Mock trend
    
    def _calculate_complexity_trend(self, memories: List[Dict[str, Any]]) -> List[float]:
        """Calculate query complexity trend."""
        # Simplified implementation
        return [2.1, 2.3, 2.5, 2.7, 2.9]  # Mock trend
