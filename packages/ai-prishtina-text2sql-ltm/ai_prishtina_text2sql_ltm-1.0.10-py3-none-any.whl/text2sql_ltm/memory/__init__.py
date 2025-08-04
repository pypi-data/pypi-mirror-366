"""
Memory management system for TEXT2SQL-LTM using mem0.ai.

This module provides comprehensive memory management capabilities including:
- User memory isolation and management
- Long-term memory storage and retrieval
- Memory lifecycle management
- Context-aware memory operations
- Performance optimization and caching
"""

# Use simple manager to avoid complex dependencies and mock implementations
from .simple_manager import SimpleMemoryManager as MemoryManager
from .storage import MemoryStorage, InMemoryStorage, RedisStorage, PostgreSQLStorage

# Import with fallbacks for optional components
try:
    from ..config.memory import MemoryConfig
except ImportError:
    MemoryConfig = None

__all__ = [
    # Core classes
    "MemoryManager",
    "MemoryConfig",

    # Storage backends
    "MemoryStorage",
    "InMemoryStorage",
    "RedisStorage",
    "PostgreSQLStorage",
]
