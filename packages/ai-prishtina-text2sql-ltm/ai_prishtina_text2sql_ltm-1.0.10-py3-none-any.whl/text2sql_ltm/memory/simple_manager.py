"""
Simplified memory manager for Text2SQL-LTM library.

This module provides a clean, production-ready memory manager without mocks,
using our storage backends for persistent memory management.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid

from .storage import MemoryStorage, InMemoryStorage, RedisStorage, PostgreSQLStorage
from ..types import MemoryEntry, MemoryQuery, MemoryMetadata
from ..exceptions import MemoryError

logger = logging.getLogger(__name__)


class SimpleMemoryManager:
    """
    Simplified memory manager for the Text2SQL agent.
    
    Provides persistent storage and retrieval of user interactions,
    query patterns, and learning data to improve future responses.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the memory manager."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage backend
        self.storage = self._create_storage_backend()
        self._initialized = False
        
        self.logger.info(f"Memory manager initialized with {self.storage.__class__.__name__}")
    
    def _create_storage_backend(self) -> MemoryStorage:
        """Create the appropriate storage backend based on configuration."""
        storage_type = self.config.get('storage_type', 'in_memory')
        
        if storage_type == 'redis':
            return RedisStorage(self.config)
        elif storage_type == 'postgresql':
            return PostgreSQLStorage(self.config)
        elif storage_type == 'in_memory':
            return InMemoryStorage(self.config)
        else:
            self.logger.warning(f"Unknown storage type: {storage_type}, falling back to in_memory")
            return InMemoryStorage(self.config)
    
    async def initialize(self) -> None:
        """Initialize the memory manager and storage backend."""
        if not self._initialized:
            await self.storage.initialize()
            self._initialized = True
            self.logger.info("Memory manager initialized")
    
    async def store_interaction(
        self,
        user_query: str,
        sql_query: str,
        success: bool,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a user interaction in memory.
        
        Args:
            user_query: The natural language query
            sql_query: The generated SQL query
            success: Whether the query was successful
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional metadata about the interaction
            
        Returns:
            str: Memory ID
        """
        await self.initialize()
        
        # Create memory entry
        memory = MemoryEntry(
            content=f"Query: {user_query}\nSQL: {sql_query}\nSuccess: {success}",
            user_id=user_id,
            session_id=session_id,
            metadata={
                "type": "interaction",
                "user_query": user_query,
                "sql_query": sql_query,
                "success": success,
                "query_length": len(user_query),
                "sql_length": len(sql_query),
                **(metadata or {})
            }
        )
        
        memory_id = await self.storage.store_memory(memory)
        self.logger.debug(f"Stored interaction memory: {memory_id}")
        
        return memory_id
    
    async def store_learning_data(
        self,
        content: str,
        category: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store learning data for future reference.
        
        Args:
            content: The learning content
            category: Category of learning (e.g., 'schema', 'pattern', 'error')
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            str: Memory ID
        """
        await self.initialize()
        
        memory = MemoryEntry(
            content=content,
            user_id=user_id,
            metadata={
                "type": "learning",
                "category": category,
                **(metadata or {})
            }
        )
        
        memory_id = await self.storage.store_memory(memory)
        self.logger.debug(f"Stored learning data: {memory_id}")
        
        return memory_id
    
    async def retrieve_similar_queries(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """
        Retrieve similar queries from memory.
        
        Args:
            query: The query to find similar examples for
            user_id: User identifier to filter by
            limit: Maximum number of results to return
            
        Returns:
            List[MemoryEntry]: Similar query memories
        """
        await self.initialize()
        
        # Search for similar interactions
        search_query = MemoryQuery(
            text=query,
            user_id=user_id,
            metadata_filters={"type": "interaction"},
            limit=limit
        )
        
        memories = await self.storage.search_memories(search_query)
        self.logger.debug(f"Found {len(memories)} similar queries")
        
        return memories
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context about a specific user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict[str, Any]: User context information
        """
        await self.initialize()
        
        # Get user memories
        memories = await self.storage.get_user_memories(user_id, limit=100)
        
        # Analyze user patterns
        total_queries = len([m for m in memories if m.metadata.get("type") == "interaction"])
        successful_queries = len([m for m in memories 
                                if m.metadata.get("type") == "interaction" and m.metadata.get("success")])
        
        success_rate = successful_queries / total_queries if total_queries > 0 else 0
        
        # Extract common patterns
        common_patterns = self._extract_patterns(memories)
        
        return {
            "user_id": user_id,
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": success_rate,
            "common_patterns": common_patterns,
            "recent_activity": len([m for m in memories[:10]]),  # Last 10 memories
            "preferences": self._extract_preferences(memories)
        }
    
    async def search_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[MemoryEntry]:
        """
        Search memories with various filters.
        
        Args:
            query: Text to search for
            user_id: User identifier filter
            session_id: Session identifier filter
            category: Category filter
            limit: Maximum results
            
        Returns:
            List[MemoryEntry]: Matching memories
        """
        await self.initialize()
        
        metadata_filters = {}
        if category:
            metadata_filters["category"] = category
        
        search_query = MemoryQuery(
            text=query,
            user_id=user_id,
            session_id=session_id,
            metadata_filters=metadata_filters if metadata_filters else None,
            limit=limit
        )
        
        return await self.storage.search_memories(search_query)
    
    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing memory.
        
        Args:
            memory_id: The memory identifier
            updates: Fields to update
            
        Returns:
            bool: True if successful
        """
        await self.initialize()
        
        result = await self.storage.update_memory(memory_id, updates)
        if result:
            self.logger.debug(f"Updated memory: {memory_id}")
        
        return result
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            memory_id: The memory identifier
            
        Returns:
            bool: True if successful
        """
        await self.initialize()
        
        result = await self.storage.delete_memory(memory_id)
        if result:
            self.logger.debug(f"Deleted memory: {memory_id}")
        
        return result
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Dict[str, Any]: Memory statistics
        """
        await self.initialize()
        
        storage_stats = await self.storage.get_stats()
        
        return {
            **storage_stats,
            "manager_type": "SimpleMemoryManager",
            "initialized": self._initialized
        }
    
    def _extract_patterns(self, memories: List[MemoryEntry]) -> List[str]:
        """Extract common patterns from user memories."""
        patterns = []
        
        # Analyze query types
        query_types = {}
        for memory in memories:
            if memory.metadata.get("type") == "interaction":
                user_query = memory.metadata.get("user_query", "").lower()
                
                # Simple pattern detection
                if "select" in user_query or "show" in user_query or "get" in user_query:
                    query_types["select"] = query_types.get("select", 0) + 1
                elif "insert" in user_query or "add" in user_query or "create" in user_query:
                    query_types["insert"] = query_types.get("insert", 0) + 1
                elif "update" in user_query or "modify" in user_query or "change" in user_query:
                    query_types["update"] = query_types.get("update", 0) + 1
                elif "delete" in user_query or "remove" in user_query:
                    query_types["delete"] = query_types.get("delete", 0) + 1
        
        # Convert to patterns
        for query_type, count in query_types.items():
            if count > 1:  # Only include patterns that appear multiple times
                patterns.append(f"Frequently uses {query_type} queries ({count} times)")
        
        return patterns
    
    def _extract_preferences(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """Extract user preferences from memories."""
        preferences = {
            "preferred_query_style": "natural",  # Default
            "complexity_level": "medium",
            "common_tables": [],
            "frequent_columns": []
        }
        
        # Analyze SQL patterns
        sql_queries = [m.metadata.get("sql_query", "") for m in memories 
                      if m.metadata.get("type") == "interaction"]
        
        if sql_queries:
            # Simple analysis of SQL complexity
            avg_length = sum(len(q) for q in sql_queries) / len(sql_queries)
            if avg_length > 200:
                preferences["complexity_level"] = "high"
            elif avg_length < 50:
                preferences["complexity_level"] = "low"
        
        return preferences
    
    async def cleanup(self) -> None:
        """Clean up memory resources."""
        if self._initialized:
            await self.storage.cleanup()
            self._initialized = False
            self.logger.info("Memory manager cleaned up")
