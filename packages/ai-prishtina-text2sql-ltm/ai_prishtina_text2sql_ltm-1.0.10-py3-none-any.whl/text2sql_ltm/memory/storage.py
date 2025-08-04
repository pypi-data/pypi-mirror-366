"""
Memory storage backends for Text2SQL-LTM library.

This module provides various storage backends for persistent memory management
including Redis, PostgreSQL, MongoDB, and in-memory storage.
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import uuid

from ..types import MemoryEntry, MemoryQuery, MemoryMetadata
from ..exceptions import MemoryError

logger = logging.getLogger(__name__)


class MemoryStorage(ABC):
    """Abstract base class for memory storage backends."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize storage backend with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up storage resources."""
        pass
    
    @abstractmethod
    async def store_memory(self, memory: MemoryEntry) -> str:
        """
        Store a memory entry.
        
        Args:
            memory: Memory entry to store
            
        Returns:
            str: Memory ID
        """
        pass
    
    @abstractmethod
    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            MemoryEntry: Memory entry if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def search_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """
        Search for memories matching the query.
        
        Args:
            query: Memory search query
            
        Returns:
            List[MemoryEntry]: Matching memory entries
        """
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a memory entry.
        
        Args:
            memory_id: Memory identifier
            updates: Fields to update
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    async def get_user_memories(self, user_id: str, limit: int = 100) -> List[MemoryEntry]:
        """
        Get all memories for a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of memories to return
            
        Returns:
            List[MemoryEntry]: User's memory entries
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dict[str, Any]: Storage statistics
        """
        pass


class InMemoryStorage(MemoryStorage):
    """In-memory storage backend for development and testing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize in-memory storage."""
        super().__init__(config)
        self.memories: Dict[str, MemoryEntry] = {}
        self.user_index: Dict[str, List[str]] = {}  # user_id -> memory_ids
    
    async def initialize(self) -> None:
        """Initialize in-memory storage."""
        self.logger.info("In-memory storage initialized")
    
    async def cleanup(self) -> None:
        """Clean up in-memory storage."""
        self.memories.clear()
        self.user_index.clear()
        self.logger.info("In-memory storage cleaned up")
    
    async def store_memory(self, memory: MemoryEntry) -> str:
        """Store memory in memory dictionary."""
        memory_id = memory.id or str(uuid.uuid4())
        memory.id = memory_id
        memory.created_at = memory.created_at or datetime.now(timezone.utc)
        
        self.memories[memory_id] = memory
        
        # Update user index
        if memory.user_id:
            if memory.user_id not in self.user_index:
                self.user_index[memory.user_id] = []
            self.user_index[memory.user_id].append(memory_id)
        
        self.logger.debug(f"Stored memory {memory_id}")
        return memory_id
    
    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory from dictionary."""
        return self.memories.get(memory_id)
    
    async def search_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memories using simple text matching."""
        results = []
        
        for memory in self.memories.values():
            # Filter by user if specified
            if query.user_id and memory.user_id != query.user_id:
                continue
            
            # Filter by session if specified
            if query.session_id and memory.session_id != query.session_id:
                continue
            
            # Text search in content
            if query.text:
                content_text = memory.content.lower()
                if query.text.lower() not in content_text:
                    continue
            
            # Filter by metadata
            if query.metadata_filters:
                match = True
                for key, value in query.metadata_filters.items():
                    if memory.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            results.append(memory)
        
        # Sort by relevance (creation time for now)
        results.sort(key=lambda m: m.created_at, reverse=True)
        
        # Apply limit
        if query.limit:
            results = results[:query.limit]
        
        return results
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory in dictionary."""
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        memory.updated_at = datetime.now(timezone.utc)
        return True
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory from dictionary."""
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        
        # Remove from user index
        if memory.user_id and memory.user_id in self.user_index:
            if memory_id in self.user_index[memory.user_id]:
                self.user_index[memory.user_id].remove(memory_id)
        
        # Remove memory
        del self.memories[memory_id]
        return True
    
    async def get_user_memories(self, user_id: str, limit: int = 100) -> List[MemoryEntry]:
        """Get all memories for a user."""
        memory_ids = self.user_index.get(user_id, [])
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        
        # Sort by creation time
        memories.sort(key=lambda m: m.created_at, reverse=True)
        
        return memories[:limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            "total_memories": len(self.memories),
            "total_users": len(self.user_index),
            "storage_type": "in_memory"
        }


class RedisStorage(MemoryStorage):
    """Redis storage backend for high-performance memory management."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Redis storage."""
        super().__init__(config)
        self.client = None
        self.host = config.get('redis_host', 'localhost')
        self.port = config.get('redis_port', 6379)
        self.password = config.get('redis_password')
        self.db = config.get('redis_db', 0)
        self.key_prefix = config.get('redis_key_prefix', 'text2sql:memory:')

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        try:
            import redis.asyncio as redis

            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True
            )

            # Test connection
            await self.client.ping()
            self.logger.info("Redis storage initialized")

        except ImportError:
            raise MemoryError("Redis library not installed. Install with: pip install redis")
        except Exception as e:
            raise MemoryError(f"Failed to initialize Redis: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None
            self.logger.info("Redis storage cleaned up")

    async def store_memory(self, memory: MemoryEntry) -> str:
        """Store memory in Redis."""
        memory_id = memory.id or str(uuid.uuid4())
        memory.id = memory_id
        memory.created_at = memory.created_at or datetime.now(timezone.utc)

        # Serialize memory
        memory_data = {
            'id': memory.id,
            'content': memory.content,
            'user_id': memory.user_id,
            'session_id': memory.session_id,
            'metadata': json.dumps(memory.metadata),
            'created_at': memory.created_at.isoformat(),
            'updated_at': memory.updated_at.isoformat() if memory.updated_at else None
        }

        # Store in Redis
        key = f"{self.key_prefix}{memory_id}"
        await self.client.hset(key, mapping=memory_data)

        # Add to user index
        if memory.user_id:
            user_key = f"{self.key_prefix}user:{memory.user_id}"
            await self.client.sadd(user_key, memory_id)

        # Add to session index
        if memory.session_id:
            session_key = f"{self.key_prefix}session:{memory.session_id}"
            await self.client.sadd(session_key, memory_id)

        self.logger.debug(f"Stored memory {memory_id} in Redis")
        return memory_id

    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory from Redis."""
        key = f"{self.key_prefix}{memory_id}"
        data = await self.client.hgetall(key)

        if not data:
            return None

        # Deserialize memory
        return MemoryEntry(
            id=data['id'],
            content=data['content'],
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            metadata=json.loads(data.get('metadata', '{}')),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

    async def search_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memories in Redis."""
        memory_ids = set()

        # Get candidate memory IDs based on filters
        if query.user_id:
            user_key = f"{self.key_prefix}user:{query.user_id}"
            user_memory_ids = await self.client.smembers(user_key)
            memory_ids.update(user_memory_ids)
        elif query.session_id:
            session_key = f"{self.key_prefix}session:{query.session_id}"
            session_memory_ids = await self.client.smembers(session_key)
            memory_ids.update(session_memory_ids)
        else:
            # Get all memory keys
            pattern = f"{self.key_prefix}*"
            keys = await self.client.keys(pattern)
            memory_ids = {key.replace(self.key_prefix, '') for key in keys
                         if not key.endswith(':user:') and not key.endswith(':session:')}

        # Retrieve and filter memories
        results = []
        for memory_id in memory_ids:
            memory = await self.retrieve_memory(memory_id)
            if not memory:
                continue

            # Apply text filter
            if query.text and query.text.lower() not in memory.content.lower():
                continue

            # Apply metadata filters
            if query.metadata_filters:
                match = True
                for key, value in query.metadata_filters.items():
                    if memory.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            results.append(memory)

        # Sort by creation time
        results.sort(key=lambda m: m.created_at, reverse=True)

        # Apply limit
        if query.limit:
            results = results[:query.limit]

        return results

    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory in Redis."""
        key = f"{self.key_prefix}{memory_id}"

        # Check if memory exists
        exists = await self.client.exists(key)
        if not exists:
            return False

        # Prepare updates
        redis_updates = {}
        for field, value in updates.items():
            if field == 'metadata':
                redis_updates[field] = json.dumps(value)
            elif isinstance(value, datetime):
                redis_updates[field] = value.isoformat()
            else:
                redis_updates[field] = str(value)

        redis_updates['updated_at'] = datetime.now(timezone.utc).isoformat()

        # Update in Redis
        await self.client.hset(key, mapping=redis_updates)
        return True

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory from Redis."""
        # Get memory first to clean up indexes
        memory = await self.retrieve_memory(memory_id)
        if not memory:
            return False

        # Remove from indexes
        if memory.user_id:
            user_key = f"{self.key_prefix}user:{memory.user_id}"
            await self.client.srem(user_key, memory_id)

        if memory.session_id:
            session_key = f"{self.key_prefix}session:{memory.session_id}"
            await self.client.srem(session_key, memory_id)

        # Delete memory
        key = f"{self.key_prefix}{memory_id}"
        result = await self.client.delete(key)
        return result > 0

    async def get_user_memories(self, user_id: str, limit: int = 100) -> List[MemoryEntry]:
        """Get all memories for a user from Redis."""
        user_key = f"{self.key_prefix}user:{user_id}"
        memory_ids = await self.client.smembers(user_key)

        memories = []
        for memory_id in memory_ids:
            memory = await self.retrieve_memory(memory_id)
            if memory:
                memories.append(memory)

        # Sort by creation time
        memories.sort(key=lambda m: m.created_at, reverse=True)
        return memories[:limit]

    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis storage statistics."""
        # Count memories
        pattern = f"{self.key_prefix}*"
        keys = await self.client.keys(pattern)
        memory_keys = [k for k in keys if not ':user:' in k and not ':session:' in k]

        # Count users
        user_pattern = f"{self.key_prefix}user:*"
        user_keys = await self.client.keys(user_pattern)

        return {
            "total_memories": len(memory_keys),
            "total_users": len(user_keys),
            "storage_type": "redis",
            "host": self.host,
            "port": self.port,
            "db": self.db
        }


class PostgreSQLStorage(MemoryStorage):
    """PostgreSQL storage backend for persistent memory management."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize PostgreSQL storage."""
        super().__init__(config)
        self.pool = None
        self.host = config.get('pg_host', 'localhost')
        self.port = config.get('pg_port', 5432)
        self.database = config.get('pg_database', 'text2sql_ltm')
        self.user = config.get('pg_user', 'postgres')
        self.password = config.get('pg_password')
        self.table_name = config.get('pg_table', 'memories')

    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool."""
        try:
            import asyncpg

            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=1,
                max_size=10
            )

            # Create table if it doesn't exist
            await self._ensure_table_exists()
            self.logger.info("PostgreSQL storage initialized")

        except ImportError:
            raise MemoryError("asyncpg library not installed. Install with: pip install asyncpg")
        except Exception as e:
            raise MemoryError(f"Failed to initialize PostgreSQL: {str(e)}")

    async def _ensure_table_exists(self) -> None:
        """Ensure the memories table exists."""
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    metadata JSONB DEFAULT '{{}}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                )
            """)

            # Create indexes
            await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_user_id ON {self.table_name}(user_id)")
            await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_session_id ON {self.table_name}(session_id)")
            await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created_at ON {self.table_name}(created_at)")

    async def cleanup(self) -> None:
        """Clean up PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.logger.info("PostgreSQL storage cleaned up")

    async def store_memory(self, memory: MemoryEntry) -> str:
        """Store memory in PostgreSQL."""
        memory_id = memory.id or str(uuid.uuid4())
        memory.id = memory_id
        memory.created_at = memory.created_at or datetime.now(timezone.utc)

        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO {self.table_name} (id, content, user_id, session_id, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    user_id = EXCLUDED.user_id,
                    session_id = EXCLUDED.session_id,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """, memory_id, memory.content, memory.user_id, memory.session_id,
                json.dumps(memory.metadata), memory.created_at)

        self.logger.debug(f"Stored memory {memory_id} in PostgreSQL")
        return memory_id

    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory from PostgreSQL."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(f"""
                SELECT id, content, user_id, session_id, metadata, created_at, updated_at
                FROM {self.table_name}
                WHERE id = $1
            """, memory_id)

            if not row:
                return None

            return MemoryEntry(
                id=row['id'],
                content=row['content'],
                user_id=row['user_id'],
                session_id=row['session_id'],
                metadata=row['metadata'] or {},
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )

    async def search_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memories in PostgreSQL."""
        conditions = []
        params = []
        param_count = 1

        # Build WHERE conditions
        if query.user_id:
            conditions.append(f"user_id = ${param_count}")
            params.append(query.user_id)
            param_count += 1

        if query.session_id:
            conditions.append(f"session_id = ${param_count}")
            params.append(query.session_id)
            param_count += 1

        if query.text:
            conditions.append(f"content ILIKE ${param_count}")
            params.append(f"%{query.text}%")
            param_count += 1

        # Build metadata filters
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                conditions.append(f"metadata ->> '{key}' = ${param_count}")
                params.append(str(value))
                param_count += 1

        # Build query
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        limit_clause = f"LIMIT {query.limit}" if query.limit else ""

        sql = f"""
            SELECT id, content, user_id, session_id, metadata, created_at, updated_at
            FROM {self.table_name}
            WHERE {where_clause}
            ORDER BY created_at DESC
            {limit_clause}
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

            return [
                MemoryEntry(
                    id=row['id'],
                    content=row['content'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    metadata=row['metadata'] or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]

    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory in PostgreSQL."""
        if not updates:
            return True

        set_clauses = []
        params = []
        param_count = 1

        for field, value in updates.items():
            if field == 'metadata':
                set_clauses.append(f"metadata = ${param_count}")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{field} = ${param_count}")
                params.append(value)
            param_count += 1

        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.now(timezone.utc))
        param_count += 1

        params.append(memory_id)  # For WHERE clause

        sql = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE id = ${param_count}
        """

        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, *params)
            return result.split()[-1] == '1'  # Check if one row was updated

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory from PostgreSQL."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(f"DELETE FROM {self.table_name} WHERE id = $1", memory_id)
            return result.split()[-1] == '1'  # Check if one row was deleted

    async def get_user_memories(self, user_id: str, limit: int = 100) -> List[MemoryEntry]:
        """Get all memories for a user from PostgreSQL."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT id, content, user_id, session_id, metadata, created_at, updated_at
                FROM {self.table_name}
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, user_id, limit)

            return [
                MemoryEntry(
                    id=row['id'],
                    content=row['content'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    metadata=row['metadata'] or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]

    async def get_stats(self) -> Dict[str, Any]:
        """Get PostgreSQL storage statistics."""
        async with self.pool.acquire() as conn:
            # Get total memories
            total_memories = await conn.fetchval(f"SELECT COUNT(*) FROM {self.table_name}")

            # Get unique users
            total_users = await conn.fetchval(f"SELECT COUNT(DISTINCT user_id) FROM {self.table_name} WHERE user_id IS NOT NULL")

            # Get table size
            table_size = await conn.fetchval("""
                SELECT pg_size_pretty(pg_total_relation_size($1))
            """, self.table_name)

            return {
                "total_memories": total_memories,
                "total_users": total_users,
                "table_size": table_size,
                "storage_type": "postgresql",
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "table_name": self.table_name
            }
