"""
Schema management for the Text2SQL-LTM library.

This module provides comprehensive database schema management with caching,
validation, and type safety for SQL query generation.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, AsyncContextManager
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from .config import PerformanceConfig
from .types import (
    DatabaseName, TableName, ColumnName, SchemaID, SchemaInfo,
    SQLQuery, SQLDialect, ColumnSchema, IndexSchema, Relationship
)
from .exceptions import (
    SchemaError, SchemaNotFoundError, SchemaValidationError,
    TableNotFoundError, Text2SQLLTMError
)

logger = logging.getLogger(__name__)


class SchemaManager:
    """
    Production-grade schema manager with comprehensive caching and validation.
    
    This class provides:
    - Type-safe schema retrieval and caching
    - SQL query validation against schema
    - Schema relationship analysis
    - Performance optimization with intelligent caching
    - Comprehensive error handling and logging
    """
    
    def __init__(self, performance_config: PerformanceConfig):
        """
        Initialize the schema manager.
        
        Args:
            performance_config: Performance configuration settings
        """
        self.performance_config = performance_config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # State tracking
        self._initialized = False
        self._closed = False
        
        # Schema storage and caching
        self._schemas: Dict[DatabaseName, SchemaInfo] = {}
        self._schema_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Metrics and monitoring
        self._schema_metrics: Dict[str, int] = {
            "schemas_loaded": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "validations_performed": 0,
            "validation_failures": 0,
        }
        
        # Async locks for thread safety
        self._schemas_lock = asyncio.Lock()
        self._cache_lock = asyncio.Lock()
        self._metrics_lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the schema manager."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing SchemaManager...")
            
            # Initialize schema cache if enabled
            if self.performance_config.enable_schema_cache:
                await self._initialize_schema_cache()
            
            self._initialized = True
            self.logger.info("SchemaManager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SchemaManager: {str(e)}")
            raise SchemaError(
                "Schema manager initialization failed",
                details={"error": str(e)},
                cause=e
            ) from e
    
    async def close(self) -> None:
        """Close the schema manager and clean up resources."""
        if self._closed:
            return
        
        try:
            self.logger.info("Closing SchemaManager...")
            
            # Clear caches
            async with self._cache_lock:
                self._schema_cache.clear()
                self._cache_timestamps.clear()
            
            async with self._schemas_lock:
                self._schemas.clear()
            
            self._closed = True
            self.logger.info("SchemaManager closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing SchemaManager: {str(e)}")
            raise SchemaError(
                "Failed to close schema manager",
                details={"error": str(e)},
                cause=e
            ) from e
    
    @asynccontextmanager
    async def session_context(self) -> AsyncContextManager[SchemaManager]:
        """Async context manager for schema manager lifecycle."""
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()
    
    def _ensure_initialized(self) -> None:
        """Ensure the schema manager is initialized."""
        if not self._initialized:
            raise SchemaError("SchemaManager not initialized. Call initialize() first.")
        
        if self._closed:
            raise SchemaError("SchemaManager is closed. Create a new instance.")
    
    async def get_schema(self, database_name: str) -> SchemaInfo:
        """
        Get database schema with caching and validation.
        
        Args:
            database_name: Name of the database
            
        Returns:
            SchemaInfo: Complete schema information
            
        Raises:
            SchemaNotFoundError: When schema is not found
            SchemaError: When schema retrieval fails
        """
        self._ensure_initialized()
        
        try:
            db_name = DatabaseName(database_name)
            
            # Check cache first
            if self.performance_config.enable_schema_cache:
                cached_schema = await self._get_cached_schema(db_name)
                if cached_schema:
                    async with self._metrics_lock:
                        self._schema_metrics["cache_hits"] += 1
                    return cached_schema
            
            async with self._metrics_lock:
                self._schema_metrics["cache_misses"] += 1
            
            # Load schema from storage/database
            schema_info = await self._load_schema_from_source(db_name)
            
            # Cache the schema
            if self.performance_config.enable_schema_cache:
                await self._cache_schema(db_name, schema_info)
            
            # Store in memory
            async with self._schemas_lock:
                self._schemas[db_name] = schema_info
            
            async with self._metrics_lock:
                self._schema_metrics["schemas_loaded"] += 1
            
            self.logger.info(f"Schema loaded successfully: {database_name}")
            return schema_info
            
        except Exception as e:
            if isinstance(e, (SchemaNotFoundError, SchemaError)):
                raise
            
            self.logger.error(f"Failed to get schema: {str(e)}")
            raise SchemaError(
                f"Schema retrieval failed for database: {database_name}",
                details={"database_name": database_name, "error": str(e)},
                cause=e
            ) from e
    
    async def validate_query(self, sql_query: str, schema: SchemaInfo) -> bool:
        """
        Validate SQL query against database schema.
        
        Args:
            sql_query: SQL query to validate
            schema: Database schema to validate against
            
        Returns:
            bool: True if query is valid
            
        Raises:
            SchemaValidationError: When validation fails
        """
        self._ensure_initialized()
        
        try:
            async with self._metrics_lock:
                self._schema_metrics["validations_performed"] += 1
            
            # Basic SQL syntax validation
            if not sql_query or not sql_query.strip():
                raise SchemaValidationError(
                    query=sql_query,
                    reason="Empty or invalid SQL query"
                )
            
            # Parse and validate table references
            referenced_tables = self._extract_table_references(sql_query)
            available_tables = schema.get_table_names()
            
            invalid_tables = referenced_tables - available_tables
            if invalid_tables:
                raise SchemaValidationError(
                    query=sql_query,
                    reason=f"Referenced tables not found in schema: {', '.join(invalid_tables)}"
                )
            
            # Validate column references for each table
            for table_name in referenced_tables:
                await self._validate_table_columns(sql_query, table_name, schema)
            
            self.logger.debug(f"Query validation successful")
            return True
            
        except SchemaValidationError:
            async with self._metrics_lock:
                self._schema_metrics["validation_failures"] += 1
            raise
        except Exception as e:
            async with self._metrics_lock:
                self._schema_metrics["validation_failures"] += 1
            
            self.logger.error(f"Query validation failed: {str(e)}")
            raise SchemaValidationError(
                query=sql_query,
                reason=f"Validation error: {str(e)}",
                cause=e
            ) from e
    
    async def get_table_schema(self, database_name: str, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        self._ensure_initialized()
        
        try:
            schema = await self.get_schema(database_name)
            table_name_typed = TableName(table_name)
            
            if table_name_typed not in schema.tables:
                raise TableNotFoundError(
                    database_name=database_name,
                    table_name=table_name
                )
            
            return schema.tables[table_name_typed]
            
        except Exception as e:
            if isinstance(e, (TableNotFoundError, SchemaError)):
                raise
            
            self.logger.error(f"Failed to get table schema: {str(e)}")
            raise SchemaError(
                f"Table schema retrieval failed",
                details={"database_name": database_name, "table_name": table_name, "error": str(e)},
                cause=e
            ) from e
    
    async def get_table_relationships(self, database_name: str, table_name: str) -> List[Relationship]:
        """Get relationships for a specific table."""
        self._ensure_initialized()
        
        try:
            schema = await self.get_schema(database_name)
            table_name_typed = TableName(table_name)
            
            relationships = []
            for relationship in schema.relationships:
                if (relationship.get("source_table") == table_name or 
                    relationship.get("target_table") == table_name):
                    relationships.append(relationship)
            
            return relationships
            
        except Exception as e:
            self.logger.error(f"Failed to get table relationships: {str(e)}")
            return []
    
    def get_metrics(self) -> Dict[str, int]:
        """Get schema manager metrics."""
        return self._schema_metrics.copy()
    
    # Helper methods
    
    async def _initialize_schema_cache(self) -> None:
        """Initialize schema caching system."""
        self.logger.info("Schema caching initialized")
    
    async def _get_cached_schema(self, database_name: DatabaseName) -> Optional[SchemaInfo]:
        """Get schema from cache if valid."""
        async with self._cache_lock:
            cache_key = str(database_name)
            
            if cache_key not in self._schema_cache:
                return None
            
            timestamp = self._cache_timestamps.get(cache_key)
            if not timestamp:
                return None
            
            # Check if cache is expired
            cache_age = datetime.utcnow() - timestamp
            if cache_age.total_seconds() > self.performance_config.schema_cache_ttl:
                # Remove expired cache
                del self._schema_cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None
            
            return self._schema_cache[cache_key]
    
    async def _cache_schema(self, database_name: DatabaseName, schema: SchemaInfo) -> None:
        """Cache schema information."""
        async with self._cache_lock:
            cache_key = str(database_name)
            self._schema_cache[cache_key] = schema
            self._cache_timestamps[cache_key] = datetime.utcnow()
    
    async def _load_schema_from_source(self, database_name: DatabaseName) -> SchemaInfo:
        """Load schema from the actual database or storage."""
        # This is a mock implementation - in a real system, this would
        # connect to the database and introspect the schema
        
        # For now, return a mock schema
        mock_schema = SchemaInfo(
            schema_id=SchemaID(f"schema_{database_name}"),
            database_name=database_name,
            tables={
                TableName("users"): {
                    "columns": {
                        "id": {"type": "integer", "nullable": False, "primary_key": True},
                        "name": {"type": "varchar", "nullable": False},
                        "email": {"type": "varchar", "nullable": False},
                        "created_at": {"type": "timestamp", "nullable": False}
                    }
                },
                TableName("orders"): {
                    "columns": {
                        "id": {"type": "integer", "nullable": False, "primary_key": True},
                        "user_id": {"type": "integer", "nullable": False, "foreign_key": "users.id"},
                        "total": {"type": "decimal", "nullable": False},
                        "created_at": {"type": "timestamp", "nullable": False}
                    }
                }
            },
            relationships=[
                {
                    "name": "user_orders",
                    "source_table": "orders",
                    "source_column": "user_id",
                    "target_table": "users",
                    "target_column": "id",
                    "relationship_type": "many_to_one"
                }
            ],
            dialect=SQLDialect.POSTGRESQL,
            created_at=datetime.utcnow()
        )
        
        return mock_schema
    
    def _extract_table_references(self, sql_query: str) -> Set[TableName]:
        """Extract table references from SQL query."""
        # This is a simplified implementation - a real parser would be more robust
        import re
        
        # Convert to uppercase for parsing
        query_upper = sql_query.upper()
        
        # Find table references after FROM and JOIN keywords
        table_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(table_pattern, query_upper)
        
        return {TableName(match.lower()) for match in matches}
    
    async def _validate_table_columns(self, sql_query: str, table_name: TableName, schema: SchemaInfo) -> None:
        """Validate column references for a specific table."""
        # This is a simplified implementation
        # In a real system, this would parse the SQL and validate all column references
        
        table_schema = schema.tables.get(table_name)
        if not table_schema:
            raise SchemaValidationError(
                query=sql_query,
                reason=f"Table {table_name} not found in schema"
            )
        
        # For now, just check that the table exists
        # A full implementation would parse SELECT clauses, WHERE conditions, etc.
        pass
