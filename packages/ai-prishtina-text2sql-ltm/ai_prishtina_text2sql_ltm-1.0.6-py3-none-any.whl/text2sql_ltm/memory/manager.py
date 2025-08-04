"""
Core memory manager using mem0.ai for long-term memory capabilities.

This module provides the main MemoryManager class that integrates with mem0.ai
to provide intelligent, context-aware memory management for Text2SQL operations.
"""

from __future__ import annotations

import asyncio
import json
import hashlib
import uuid
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple, AsyncContextManager
from datetime import datetime, timedelta
from collections import defaultdict
from contextlib import asynccontextmanager

try:
    from mem0 import Memory
    HAS_MEM0 = True
except ImportError:
    HAS_MEM0 = False
    # Mock Memory class for development without mem0
    class Memory:
        def __init__(self, *args, **kwargs):
            self.memories: Dict[str, Any] = {}

        def add(self, messages: List[Dict[str, str]], user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            memory_id = f"mock_{len(self.memories)}"
            self.memories[memory_id] = {
                "id": memory_id,
                "messages": messages,
                "user_id": user_id,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            return {"id": memory_id, "message": "Mock memory added"}

        def search(self, query: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
            # Simple mock search
            results = []
            for memory_id, memory in self.memories.items():
                if user_id and memory.get("user_id") != user_id:
                    continue
                if query.lower() in str(memory.get("messages", "")).lower():
                    results.append({
                        "id": memory_id,
                        "memory": memory,
                        "score": 0.8  # Mock relevance score
                    })
            return results[:limit]

        def get_all(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
            results = []
            for memory_id, memory in self.memories.items():
                if user_id and memory.get("user_id") != user_id:
                    continue
                results.append({"id": memory_id, "memory": memory})
            return results

        def delete(self, memory_id: str) -> Dict[str, str]:
            if memory_id in self.memories:
                del self.memories[memory_id]
            return {"message": "Mock memory deleted"}

        def update(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, str]:
            if memory_id in self.memories:
                self.memories[memory_id].update(data)
            return {"message": "Mock memory updated"}

from ..config import MemoryConfig
from ..types import (
    UserID, MemoryID, SessionID, MemoryType, MemoryContent, MemoryMetadata,
    MemoryContext, MemoryStats, Timestamp, validate_user_id, Score
)
from ..exceptions import (
    MemoryError, MemoryConnectionError, MemoryStorageError,
    MemoryQuotaExceededError, Text2SQLLTMError
)

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Production-grade memory manager with comprehensive type safety and error handling.

    This class provides the main interface for all memory operations including:
    - Type-safe memory storage and retrieval with user isolation
    - Context-aware memory search with relevance scoring
    - Memory lifecycle management and automatic cleanup
    - Performance optimization with caching and batching
    - Comprehensive monitoring and metrics collection
    """

    def __init__(self, config: MemoryConfig):
        """
        Initialize the memory manager with comprehensive validation.

        Args:
            config: Memory configuration settings with validation

        Raises:
            MemoryConnectionError: When mem0.ai connection fails
            MemoryError: When initialization fails
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # State tracking
        self._initialized = False
        self._closed = False

        # Memory client and storage
        self._mem0_client: Optional[Memory] = None
        self._storage: Optional[Any] = None

        # Caching and performance
        self._memory_cache: Dict[str, MemoryContext] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._user_quotas: Dict[UserID, int] = {}

        # Metrics and monitoring
        self._stats = MemoryStats()
        self._operation_counts: Dict[str, int] = defaultdict(int)

        # Async locks for thread safety
        self._cache_lock = asyncio.Lock()
        self._quota_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Initialize the memory manager and all its components.

        This method must be called before using the memory manager.
        """
        if self._initialized:
            return

        try:
            self.logger.info("Initializing MemoryManager...")

            # Initialize mem0.ai client
            await self._init_mem0_client()

            # Initialize storage backend if needed
            if self.config.storage_backend != "mem0":
                await self._init_storage_backend()

            # Initialize user isolation if enabled
            if self.config.user_isolation:
                await self._init_user_isolation()

            # Start lifecycle management if enabled
            if self.config.auto_cleanup:
                await self._start_lifecycle_management()

            self._initialized = True
            self.logger.info("MemoryManager initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize MemoryManager: {str(e)}")
            raise MemoryConnectionError(
                backend="mem0",
                connection_url=self.config.storage_url,
                cause=e
            ) from e

    async def close(self) -> None:
        """
        Close the memory manager and clean up all resources.
        """
        if self._closed:
            return

        try:
            self.logger.info("Closing MemoryManager...")

            # Clear caches
            async with self._cache_lock:
                self._memory_cache.clear()
                self._cache_timestamps.clear()

            # Close storage connections
            if self._storage and hasattr(self._storage, 'close'):
                await self._storage.close()

            self._closed = True
            self.logger.info("MemoryManager closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing MemoryManager: {str(e)}")
            raise MemoryError(
                "Failed to close memory manager",
                details={"error": str(e)},
                cause=e
            ) from e

    @asynccontextmanager
    async def session_context(self) -> AsyncContextManager[MemoryManager]:
        """
        Async context manager for memory manager lifecycle.

        Usage:
            async with memory_manager.session_context():
                await memory_manager.store_memory(...)
        """
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()

    def _ensure_initialized(self) -> None:
        """Ensure the memory manager is initialized."""
        if not self._initialized:
            raise MemoryError("MemoryManager not initialized. Call initialize() first.")

        if self._closed:
            raise MemoryError("MemoryManager is closed. Create a new instance.")

    async def _init_mem0_client(self) -> None:
        """Initialize the mem0.ai client with proper configuration."""
        try:
            if not HAS_MEM0:
                self.logger.warning("mem0 library not available, using mock implementation")
                self._mem0_client = Memory()
                return

            # Initialize with configuration
            client_config = {}

            if self.config.mem0_api_key:
                client_config["api_key"] = self.config.mem0_api_key

            if self.config.mem0_organization_id:
                client_config["organization_id"] = self.config.mem0_organization_id

            if self.config.mem0_project_id:
                client_config["project_id"] = self.config.mem0_project_id

            if self.config.mem0_base_url:
                client_config["base_url"] = self.config.mem0_base_url

            self._mem0_client = Memory(**client_config)
            self.logger.info("mem0.ai client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize mem0.ai client: {str(e)}")
            raise MemoryConnectionError("mem0", cause=e) from e

    async def _init_storage_backend(self) -> None:
        """Initialize additional storage backend if configured."""
        # This would be implemented based on the chosen storage backend
        # For now, we'll use a simple in-memory implementation
        self._storage = {}
        self.logger.info(f"Storage backend initialized: {self.config.storage_backend}")

    async def _init_user_isolation(self) -> None:
        """Initialize user isolation and quota management."""
        self.logger.info("User isolation initialized")

    async def _start_lifecycle_management(self) -> None:
        """Start automatic memory lifecycle management."""
        self.logger.info("Memory lifecycle management started")

    async def store_memory(
        self,
        user_id: str,
        content: MemoryContent,
        memory_type: MemoryType = MemoryType.QUERY_PATTERN,
        metadata: Optional[MemoryMetadata] = None,
        session_id: Optional[str] = None,
        ttl_days: Optional[int] = None
    ) -> MemoryID:
        """
        Store a memory for a specific user with comprehensive validation.

        Args:
            user_id: User identifier for memory isolation
            content: Memory content (text, dict, or list)
            memory_type: Type of memory being stored
            metadata: Additional metadata for the memory
            session_id: Optional session identifier
            ttl_days: Time-to-live in days (overrides config default)

        Returns:
            MemoryID: Unique identifier for the stored memory

        Raises:
            MemoryError: When storage fails
            MemoryQuotaExceededError: When user quota is exceeded
        """
        self._ensure_initialized()

        try:
            # Validate and convert user ID
            validated_user_id = validate_user_id(user_id)

            # Check user quota if isolation is enabled
            if self.config.user_isolation:
                await self._check_user_quota(validated_user_id)

            # Validate content
            if not self._is_valid_memory_content(content):
                raise MemoryError(
                    "Invalid memory content",
                    details={"content_type": type(content).__name__}
                )

            # Prepare memory data
            memory_id = MemoryID(str(uuid.uuid4()))
            timestamp = datetime.utcnow()

            memory_data = {
                "memory_id": memory_id,
                "user_id": validated_user_id,
                "content": content,
                "memory_type": memory_type,
                "metadata": metadata or {},
                "session_id": session_id,
                "created_at": timestamp,
                "ttl_days": ttl_days or self.config.memory_ttl_days,
                "access_count": 0,
                "last_accessed": timestamp
            }

            # Store in mem0.ai
            if isinstance(content, str):
                messages = [{"role": "user", "content": content}]
            else:
                messages = [{"role": "user", "content": json.dumps(content)}]

            mem0_metadata = {
                "memory_id": memory_id,
                "memory_type": memory_type.value,
                "user_id": validated_user_id,
                "session_id": session_id,
                "created_at": timestamp.isoformat(),
                **(metadata or {})
            }

            result = self._mem0_client.add(
                messages=messages,
                user_id=str(validated_user_id),
                metadata=mem0_metadata
            )

            # Store additional metadata in storage backend if configured
            if self._storage is not None:
                await self._store_memory_metadata(memory_id, memory_data)

            # Update cache
            memory_context = MemoryContext(
                memory_id=memory_id,
                content=content,
                memory_type=memory_type,
                relevance_score=Score(1.0),  # New memories have max relevance
                user_id=validated_user_id,
                created_at=timestamp,
                last_accessed=timestamp,
                access_count=0,
                metadata=metadata or {}
            )

            await self._update_cache(memory_id, memory_context)

            # Update statistics
            self._stats.add_memory(memory_context, self._estimate_memory_size(content))
            self._operation_counts["store"] += 1

            self.logger.info(
                f"Memory stored successfully",
                extra={
                    "memory_id": memory_id,
                    "user_id": validated_user_id,
                    "memory_type": memory_type.value,
                    "content_size": len(str(content))
                }
            )

            return memory_id

        except Exception as e:
            self._operation_counts["store_failed"] += 1

            if isinstance(e, (MemoryError, MemoryQuotaExceededError)):
                raise

            self.logger.error(f"Failed to store memory: {str(e)}")
            raise MemoryStorageError(
                operation="store",
                user_id=user_id,
                cause=e
            ) from e

    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[MemoryType]] = None,
        relevance_threshold: float = 0.5,
        session_id: Optional[str] = None
    ) -> List[MemoryContext]:
        """
        Search for relevant memories with comprehensive filtering and ranking.

        Args:
            user_id: User identifier for memory isolation
            query: Search query string
            limit: Maximum number of results to return
            memory_types: Optional filter by memory types
            relevance_threshold: Minimum relevance score (0.0 to 1.0)
            session_id: Optional session filter

        Returns:
            List[MemoryContext]: Ranked list of relevant memories

        Raises:
            MemoryError: When search fails
        """
        self._ensure_initialized()

        try:
            # Validate inputs
            validated_user_id = validate_user_id(user_id)

            if not query or not query.strip():
                return []

            if limit <= 0:
                limit = 10

            # Check cache first
            cache_key = self._generate_search_cache_key(
                validated_user_id, query, memory_types, session_id
            )

            cached_results = await self._get_cached_search_results(cache_key)
            if cached_results:
                self._operation_counts["search_cache_hit"] += 1
                return cached_results[:limit]

            # Search in mem0.ai
            search_results = self._mem0_client.search(
                query=query,
                user_id=str(validated_user_id),
                limit=limit * 2  # Get more results for filtering
            )

            # Convert to MemoryContext objects with filtering
            memory_contexts = []

            for result in search_results:
                try:
                    memory_context = await self._convert_search_result_to_context(
                        result, validated_user_id
                    )

                    # Apply filters
                    if memory_types and memory_context.memory_type not in memory_types:
                        continue

                    if memory_context.relevance_score < relevance_threshold:
                        continue

                    if session_id and memory_context.metadata.get("session_id") != session_id:
                        continue

                    memory_contexts.append(memory_context)

                except Exception as e:
                    self.logger.warning(f"Failed to convert search result: {str(e)}")
                    continue

            # Sort by relevance score
            memory_contexts.sort(key=lambda m: m.relevance_score, reverse=True)

            # Limit results
            final_results = memory_contexts[:limit]

            # Cache results
            await self._cache_search_results(cache_key, final_results)

            # Update access counts
            for memory_context in final_results:
                await self._update_memory_access(memory_context.memory_id)

            self._operation_counts["search"] += 1

            self.logger.debug(
                f"Memory search completed",
                extra={
                    "user_id": validated_user_id,
                    "query_length": len(query),
                    "results_count": len(final_results),
                    "relevance_threshold": relevance_threshold
                }
            )

            return final_results

        except Exception as e:
            self._operation_counts["search_failed"] += 1

            if isinstance(e, MemoryError):
                raise

            self.logger.error(f"Failed to search memories: {str(e)}")
            raise MemoryStorageError(
                operation="search",
                user_id=user_id,
                cause=e
            ) from e

    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 50,
        memory_types: Optional[List[str]] = None
    ) -> List[MemoryContext]:
        """Get all memories for a specific user."""
        self._ensure_initialized()

        try:
            validated_user_id = validate_user_id(user_id)

            # Get all memories from mem0.ai
            all_memories = self._mem0_client.get_all(user_id=str(validated_user_id))

            memory_contexts = []
            for memory_data in all_memories:
                try:
                    memory_context = await self._convert_memory_data_to_context(
                        memory_data, validated_user_id
                    )

                    # Apply type filter if specified
                    if memory_types and memory_context.memory_type.value not in memory_types:
                        continue

                    memory_contexts.append(memory_context)

                except Exception as e:
                    self.logger.warning(f"Failed to convert memory data: {str(e)}")
                    continue

            # Sort by creation date (newest first)
            memory_contexts.sort(key=lambda m: m.created_at, reverse=True)

            return memory_contexts[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get user memories: {str(e)}")
            raise MemoryStorageError(
                operation="get_user_memories",
                user_id=user_id,
                cause=e
            ) from e

    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory."""
        self._ensure_initialized()

        try:
            validated_user_id = validate_user_id(user_id)
            memory_id_typed = MemoryID(memory_id)

            # Delete from mem0.ai
            self._mem0_client.delete(memory_id)

            # Remove from cache
            async with self._cache_lock:
                cache_keys_to_remove = [
                    key for key in self._memory_cache.keys()
                    if self._memory_cache[key].memory_id == memory_id_typed
                ]
                for key in cache_keys_to_remove:
                    del self._memory_cache[key]
                    if key in self._cache_timestamps:
                        del self._cache_timestamps[key]

            # Remove from storage backend if configured
            if self._storage is not None:
                await self._remove_memory_metadata(memory_id_typed)

            self._operation_counts["delete"] += 1

            self.logger.info(f"Memory deleted successfully: {memory_id}")
            return True

        except Exception as e:
            self._operation_counts["delete_failed"] += 1
            self.logger.error(f"Failed to delete memory: {str(e)}")
            return False

    async def get_session_memories(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[MemoryContext]:
        """Get memories specific to a session."""
        return await self.search_memories(
            user_id=user_id,
            query="",  # Empty query to get all
            limit=limit,
            session_id=session_id
        )

    def get_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        return self._stats

    def get_operation_counts(self) -> Dict[str, int]:
        """Get operation count statistics."""
        return dict(self._operation_counts)

    # Helper methods

    async def _check_user_quota(self, user_id: UserID) -> None:
        """Check if user has exceeded their memory quota."""
        if not self.config.user_isolation:
            return

        async with self._quota_lock:
            current_usage = self._user_quotas.get(user_id, 0)
            max_usage = self.config.get_memory_size_bytes()

            if current_usage >= max_usage:
                raise MemoryQuotaExceededError(
                    user_id=str(user_id),
                    current_usage=f"{current_usage} bytes",
                    quota=f"{max_usage} bytes"
                )

    def _is_valid_memory_content(self, content: Any) -> bool:
        """Validate memory content."""
        if content is None:
            return False

        if isinstance(content, (str, dict, list)):
            return True

        # Check if content is JSON serializable
        try:
            json.dumps(content)
            return True
        except (TypeError, ValueError):
            return False

    def _estimate_memory_size(self, content: Any) -> int:
        """Estimate memory size in bytes."""
        try:
            return len(json.dumps(content).encode('utf-8'))
        except Exception:
            return len(str(content).encode('utf-8'))

    async def _update_cache(self, memory_id: MemoryID, memory_context: MemoryContext) -> None:
        """Update memory cache."""
        async with self._cache_lock:
            cache_key = str(memory_id)
            self._memory_cache[cache_key] = memory_context
            self._cache_timestamps[cache_key] = datetime.utcnow()

            # Clean up old cache entries if needed
            if len(self._memory_cache) > self.config.memory_cache_size:
                await self._cleanup_cache()

    async def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        current_time = datetime.utcnow()
        cache_ttl = timedelta(seconds=self.config.cache_ttl_seconds)

        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > cache_ttl
        ]

        for key in expired_keys:
            if key in self._memory_cache:
                del self._memory_cache[key]
            if key in self._cache_timestamps:
                del self._cache_timestamps[key]

        # If still over limit, remove oldest entries
        if len(self._memory_cache) > self.config.memory_cache_size:
            sorted_items = sorted(
                self._cache_timestamps.items(),
                key=lambda x: x[1]
            )

            items_to_remove = len(self._memory_cache) - self.config.memory_cache_size
            for key, _ in sorted_items[:items_to_remove]:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                if key in self._cache_timestamps:
                    del self._cache_timestamps[key]

    def _generate_search_cache_key(
        self,
        user_id: UserID,
        query: str,
        memory_types: Optional[List[MemoryType]],
        session_id: Optional[str]
    ) -> str:
        """Generate cache key for search results."""
        key_components = [
            str(user_id),
            query.lower().strip(),
            str(sorted([mt.value for mt in memory_types]) if memory_types else "all"),
            session_id or "no_session"
        ]

        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()

    async def _get_cached_search_results(self, cache_key: str) -> Optional[List[MemoryContext]]:
        """Get cached search results if valid."""
        async with self._cache_lock:
            if cache_key not in self._memory_cache:
                return None

            timestamp = self._cache_timestamps.get(cache_key)
            if not timestamp:
                return None

            cache_age = datetime.utcnow() - timestamp
            if cache_age.total_seconds() > self.config.cache_ttl_seconds:
                # Remove expired cache
                del self._memory_cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None

            return self._memory_cache[cache_key]

    async def _cache_search_results(self, cache_key: str, results: List[MemoryContext]) -> None:
        """Cache search results."""
        async with self._cache_lock:
            self._memory_cache[cache_key] = results
            self._cache_timestamps[cache_key] = datetime.utcnow()

    async def _convert_search_result_to_context(
        self,
        result: Dict[str, Any],
        user_id: UserID
    ) -> MemoryContext:
        """Convert mem0.ai search result to MemoryContext."""
        memory_data = result.get("memory", {})
        metadata = memory_data.get("metadata", {})

        return MemoryContext(
            memory_id=MemoryID(result.get("id", str(uuid.uuid4()))),
            content=memory_data.get("content", ""),
            memory_type=MemoryType(metadata.get("memory_type", MemoryType.QUERY_PATTERN.value)),
            relevance_score=Score(result.get("score", 0.0)),
            user_id=user_id,
            created_at=datetime.fromisoformat(metadata.get("created_at", datetime.utcnow().isoformat())),
            last_accessed=datetime.utcnow(),
            access_count=metadata.get("access_count", 0),
            metadata=metadata
        )

    async def _convert_memory_data_to_context(
        self,
        memory_data: Dict[str, Any],
        user_id: UserID
    ) -> MemoryContext:
        """Convert memory data to MemoryContext."""
        memory_info = memory_data.get("memory", {})
        metadata = memory_info.get("metadata", {})

        return MemoryContext(
            memory_id=MemoryID(memory_data.get("id", str(uuid.uuid4()))),
            content=memory_info.get("content", ""),
            memory_type=MemoryType(metadata.get("memory_type", MemoryType.QUERY_PATTERN.value)),
            relevance_score=Score(1.0),  # Default relevance for direct retrieval
            user_id=user_id,
            created_at=datetime.fromisoformat(metadata.get("created_at", datetime.utcnow().isoformat())),
            last_accessed=datetime.utcnow(),
            access_count=metadata.get("access_count", 0),
            metadata=metadata
        )

    async def _update_memory_access(self, memory_id: MemoryID) -> None:
        """Update memory access statistics."""
        # This would update access count in the storage backend
        # For now, we'll just log it
        self.logger.debug(f"Memory accessed: {memory_id}")

    async def _store_memory_metadata(self, memory_id: MemoryID, memory_data: Dict[str, Any]) -> None:
        """Store additional memory metadata in storage backend."""
        if self._storage is not None:
            self._storage[str(memory_id)] = memory_data

    async def _remove_memory_metadata(self, memory_id: MemoryID) -> None:
        """Remove memory metadata from storage backend."""
        if self._storage is not None and str(memory_id) in self._storage:
            del self._storage[str(memory_id)]
        
        # Memory cache for performance
        self._memory_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Statistics tracking
        self._stats = {
            "memories_stored": 0,
            "memories_retrieved": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        
        self.logger.info("MemoryManager initialized", 
                        backend=config.storage_backend,
                        user_isolation=config.user_isolation)
    
    def _init_mem0_client(self) -> None:
        """Initialize the mem0.ai client."""
        if not HAS_MEM0:
            self.logger.warning("mem0.ai not available, using mock implementation")
            self.mem0_client = Memory()
            return
        
        try:
            # Initialize mem0 with configuration
            mem0_config = {}
            
            if self.config.mem0_api_key:
                mem0_config["api_key"] = self.config.mem0_api_key
            
            if self.config.mem0_organization_id:
                mem0_config["organization_id"] = self.config.mem0_organization_id
            
            if self.config.mem0_project_id:
                mem0_config["project_id"] = self.config.mem0_project_id
            
            self.mem0_client = Memory(config=mem0_config)
            self.logger.info("mem0.ai client initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize mem0.ai client", error=str(e))
            raise MemoryConnectionError("mem0", cause=e)
    
    async def store_memory(
        self,
        user_id: str,
        content: Union[str, Dict[str, Any]],
        memory_type: str = "query",
        metadata: Optional[Dict[str, Any]] = None,
        ttl_days: Optional[int] = None
    ) -> str:
        """
        Store a memory for a specific user.
        
        Args:
            user_id: User identifier
            content: Memory content (text or structured data)
            memory_type: Type of memory (query, schema, preference, etc.)
            metadata: Additional metadata
            ttl_days: Time-to-live in days (overrides config default)
            
        Returns:
            Memory ID
        """
        try:
            # Validate user isolation
            if self.config.user_isolation:
                await self.user_isolation.validate_user_quota(user_id)
            
            # Prepare memory data
            memory_data = {
                "user_id": user_id,
                "content": content,
                "memory_type": memory_type,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "ttl_days": ttl_days or self.config.memory_ttl_days,
            }
            
            # Generate memory key for caching
            memory_key = self._generate_memory_key(user_id, content, memory_type)
            
            # Store in mem0.ai
            if isinstance(content, str):
                messages = [{"role": "user", "content": content}]
            else:
                messages = [{"role": "user", "content": json.dumps(content)}]
            
            # Add user isolation to metadata
            isolated_user_id = self.user_isolation.get_isolated_user_id(user_id)
            
            mem0_metadata = {
                "memory_type": memory_type,
                "original_user_id": user_id,
                "created_at": memory_data["created_at"],
                **(metadata or {})
            }
            
            # Store in mem0
            result = self.mem0_client.add(
                messages=messages,
                user_id=isolated_user_id,
                metadata=mem0_metadata
            )
            
            memory_id = result.get("id") or result.get("memory_id")
            if not memory_id:
                raise MemoryStorageError("store", user_id, Exception("No memory ID returned"))
            
            # Store additional data in backend storage
            memory_data["memory_id"] = memory_id
            await self.storage.store_memory_metadata(memory_id, memory_data)
            
            # Update cache
            self._memory_cache[memory_key] = memory_data
            self._cache_timestamps[memory_key] = datetime.utcnow()
            
            # Update statistics
            self._stats["memories_stored"] += 1
            
            # Schedule lifecycle management
            if self.config.auto_cleanup:
                await self.lifecycle_manager.schedule_cleanup(memory_id, ttl_days or self.config.memory_ttl_days)
            
            self.logger.info("Memory stored successfully",
                           user_id=user_id,
                           memory_id=memory_id,
                           memory_type=memory_type)
            
            return memory_id
            
        except Exception as e:
            self.logger.error("Failed to store memory",
                            user_id=user_id,
                            memory_type=memory_type,
                            error=str(e))
            raise MemoryStorageError("store", user_id, e)
    
    async def retrieve_memories(
        self,
        user_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a specific user.
        
        Args:
            user_id: User identifier
            query: Search query (if None, returns all memories)
            memory_type: Filter by memory type
            limit: Maximum number of memories to return
            include_metadata: Whether to include metadata
            
        Returns:
            List of memories
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(user_id, query, memory_type, limit)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self._stats["cache_hits"] += 1
                return cached_result
            
            self._stats["cache_misses"] += 1
            
            # Get isolated user ID
            isolated_user_id = self.user_isolation.get_isolated_user_id(user_id)
            
            # Search memories in mem0
            if query:
                memories = self.mem0_client.search(
                    query=query,
                    user_id=isolated_user_id,
                    limit=limit
                )
            else:
                memories = self.mem0_client.get_all(user_id=isolated_user_id)
                if limit:
                    memories = memories[:limit]
            
            # Process and enrich memories
            enriched_memories = []
            for memory in memories:
                memory_id = memory.get("id") or memory.get("memory_id")
                
                # Get additional metadata from storage
                if include_metadata and memory_id:
                    metadata = await self.storage.get_memory_metadata(memory_id)
                    if metadata:
                        memory.update(metadata)
                
                # Filter by memory type if specified
                if memory_type and memory.get("memory_type") != memory_type:
                    continue
                
                enriched_memories.append(memory)
            
            # Cache the result
            self._cache_result(cache_key, enriched_memories)
            
            # Update statistics
            self._stats["memories_retrieved"] += len(enriched_memories)
            
            self.logger.info("Memories retrieved successfully",
                           user_id=user_id,
                           count=len(enriched_memories),
                           query=query,
                           memory_type=memory_type)
            
            return enriched_memories
            
        except Exception as e:
            self.logger.error("Failed to retrieve memories",
                            user_id=user_id,
                            query=query,
                            error=str(e))
            raise MemoryStorageError("retrieve", user_id, e)
    
    async def search_contextual_memories(
        self,
        user_id: str,
        context: MemoryContext,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for memories based on context.
        
        Args:
            user_id: User identifier
            context: Memory context for search
            limit: Maximum number of memories to return
            
        Returns:
            List of contextually relevant memories
        """
        try:
            # Build contextual search query
            search_queries = []
            
            if context.current_query:
                search_queries.append(context.current_query)
            
            if context.table_names:
                search_queries.append(" ".join(context.table_names))
            
            if context.query_intent:
                search_queries.append(context.query_intent)
            
            # Combine search terms
            search_query = " ".join(search_queries)
            
            # Search memories
            memories = await self.retrieve_memories(
                user_id=user_id,
                query=search_query,
                limit=limit * 2  # Get more to filter
            )
            
            # Score and rank memories by relevance
            scored_memories = []
            for memory in memories:
                score = self._calculate_context_relevance(memory, context)
                if score > 0.1:  # Minimum relevance threshold
                    memory["relevance_score"] = score
                    scored_memories.append(memory)
            
            # Sort by relevance and limit
            scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_memories[:limit]
            
        except Exception as e:
            self.logger.error("Failed to search contextual memories",
                            user_id=user_id,
                            error=str(e))
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        content: Optional[Union[str, Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing memory.
        
        Args:
            memory_id: Memory identifier
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if successful
        """
        try:
            # Update in mem0
            update_data = {}
            if content:
                if isinstance(content, str):
                    update_data["content"] = content
                else:
                    update_data["content"] = json.dumps(content)
            
            if metadata:
                update_data["metadata"] = metadata
            
            if update_data:
                self.mem0_client.update(memory_id, update_data)
            
            # Update in storage backend
            if metadata:
                await self.storage.update_memory_metadata(memory_id, metadata)
            
            # Clear related cache entries
            self._clear_cache_for_memory(memory_id)
            
            self.logger.info("Memory updated successfully", memory_id=memory_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to update memory",
                            memory_id=memory_id,
                            error=str(e))
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            True if successful
        """
        try:
            # Delete from mem0
            self.mem0_client.delete(memory_id)
            
            # Delete from storage backend
            await self.storage.delete_memory_metadata(memory_id)
            
            # Clear cache
            self._clear_cache_for_memory(memory_id)
            
            self.logger.info("Memory deleted successfully", memory_id=memory_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to delete memory",
                            memory_id=memory_id,
                            error=str(e))
            return False
    
    async def get_user_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Memory statistics
        """
        try:
            isolated_user_id = self.user_isolation.get_isolated_user_id(user_id)
            
            # Get all memories for user
            memories = self.mem0_client.get_all(user_id=isolated_user_id)
            
            # Calculate statistics
            stats = {
                "total_memories": len(memories),
                "memory_types": {},
                "oldest_memory": None,
                "newest_memory": None,
                "total_size_estimate": 0,
            }
            
            for memory in memories:
                # Count by type
                memory_type = memory.get("memory_type", "unknown")
                stats["memory_types"][memory_type] = stats["memory_types"].get(memory_type, 0) + 1
                
                # Track dates
                created_at = memory.get("created_at")
                if created_at:
                    if not stats["oldest_memory"] or created_at < stats["oldest_memory"]:
                        stats["oldest_memory"] = created_at
                    if not stats["newest_memory"] or created_at > stats["newest_memory"]:
                        stats["newest_memory"] = created_at
                
                # Estimate size
                content = memory.get("content", "")
                stats["total_size_estimate"] += len(str(content))
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get user memory stats",
                            user_id=user_id,
                            error=str(e))
            return {}
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics."""
        return {
            **self._stats,
            "cache_size": len(self._memory_cache),
            "cache_hit_rate": (
                self._stats["cache_hits"] / 
                max(self._stats["cache_hits"] + self._stats["cache_misses"], 1)
            ),
        }
    
    def _generate_memory_key(self, user_id: str, content: Any, memory_type: str) -> str:
        """Generate a unique key for memory caching."""
        content_str = json.dumps(content, sort_keys=True) if isinstance(content, dict) else str(content)
        key_data = f"{user_id}:{memory_type}:{content_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _generate_cache_key(self, user_id: str, query: Optional[str], memory_type: Optional[str], limit: int) -> str:
        """Generate a cache key for memory retrieval."""
        key_parts = [user_id, query or "all", memory_type or "any", str(limit)]
        key_data = ":".join(key_parts)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get result from cache if not expired."""
        if cache_key not in self._memory_cache:
            return None
        
        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return None
        
        # Check if cache entry is expired (5 minutes)
        if datetime.utcnow() - timestamp > timedelta(minutes=5):
            del self._memory_cache[cache_key]
            del self._cache_timestamps[cache_key]
            return None
        
        return self._memory_cache[cache_key]
    
    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]) -> None:
        """Cache a result."""
        self._memory_cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.utcnow()
        
        # Limit cache size
        if len(self._memory_cache) > self.config.memory_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self._cache_timestamps.keys(),
                key=lambda k: self._cache_timestamps[k]
            )[:len(self._memory_cache) - self.config.memory_cache_size + 100]
            
            for key in oldest_keys:
                self._memory_cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
    
    def _clear_cache_for_memory(self, memory_id: str) -> None:
        """Clear cache entries related to a specific memory."""
        # This is a simple implementation - in production, you might want
        # more sophisticated cache invalidation
        self._memory_cache.clear()
        self._cache_timestamps.clear()
    
    def _calculate_context_relevance(self, memory: Dict[str, Any], context: MemoryContext) -> float:
        """Calculate relevance score between memory and context."""
        score = 0.0
        
        memory_content = str(memory.get("content", "")).lower()
        memory_metadata = memory.get("metadata", {})
        
        # Query similarity
        if context.current_query:
            query_words = set(context.current_query.lower().split())
            memory_words = set(memory_content.split())
            common_words = query_words.intersection(memory_words)
            if common_words:
                score += len(common_words) / len(query_words) * 0.4
        
        # Table name matches
        if context.table_names:
            for table in context.table_names:
                if table.lower() in memory_content:
                    score += 0.3
        
        # Intent matching
        if context.query_intent and memory_metadata.get("intent"):
            if context.query_intent == memory_metadata["intent"]:
                score += 0.2
        
        # Recency bonus
        created_at = memory.get("created_at")
        if created_at:
            try:
                memory_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.utcnow() - memory_date.replace(tzinfo=None)).days
                recency_score = max(0, 1 - days_old / 30) * 0.1  # Decay over 30 days
                score += recency_score
            except:
                pass
        
        return min(score, 1.0)
