"""
Memory management system for TEXT2SQL-LTM using mem0.ai.

This module provides comprehensive memory management capabilities including:
- User memory isolation and management
- Long-term memory storage and retrieval
- Memory lifecycle management
- Context-aware memory operations
- Performance optimization and caching
"""

from .manager import MemoryManager
from .config import MemoryConfig
from .storage import MemoryStorage, RedisStorage, PostgreSQLStorage, MongoDBStorage
from .lifecycle import MemoryLifecycleManager
from .isolation import UserMemoryIsolation
from .context import MemoryContext, ContextualMemory
from .optimization import MemoryOptimizer
from .analytics import MemoryAnalytics

__all__ = [
    # Core classes
    "MemoryManager",
    "MemoryConfig",
    
    # Storage backends
    "MemoryStorage",
    "RedisStorage", 
    "PostgreSQLStorage",
    "MongoDBStorage",
    
    # Memory management
    "MemoryLifecycleManager",
    "UserMemoryIsolation",
    
    # Context and retrieval
    "MemoryContext",
    "ContextualMemory",
    
    # Optimization and analytics
    "MemoryOptimizer",
    "MemoryAnalytics",
]
