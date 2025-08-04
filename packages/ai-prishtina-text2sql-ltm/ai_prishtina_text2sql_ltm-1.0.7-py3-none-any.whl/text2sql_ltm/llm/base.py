"""
Base LLM provider interface for Text2SQL-LTM library.

This module defines the abstract base class for all LLM providers with
comprehensive type safety and error handling.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncContextManager
from contextlib import asynccontextmanager

from ..config import AgentConfig
from ..types import (
    QueryResult, MemoryContext, SchemaInfo, SQLDialect, QueryComplexity,
    NaturalLanguageQuery, SQLQuery, Score, Timestamp
)
from ..exceptions import QueryGenerationError, Text2SQLLTMError

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    This class defines the interface that all LLM providers must implement
    to ensure consistent behavior and type safety across different providers.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the LLM provider.
        
        Args:
            config: Agent configuration with LLM settings
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # State tracking
        self._initialized = False
        self._closed = False
        
        # Metrics and monitoring
        self._metrics: Dict[str, Any] = {
            "requests_made": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "total_tokens_used": 0,
            "average_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
    
    async def initialize(self) -> None:
        """
        Initialize the LLM provider.
        
        This method must be called before using the provider.
        """
        if self._initialized:
            return
        
        try:
            self.logger.info(f"Initializing {self.__class__.__name__}...")
            await self._initialize_client()
            self._initialized = True
            self.logger.info(f"{self.__class__.__name__} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {str(e)}")
            raise QueryGenerationError(
                natural_language="",
                reason=f"LLM provider initialization failed: {str(e)}",
                cause=e
            ) from e
    
    async def close(self) -> None:
        """
        Close the LLM provider and clean up resources.
        """
        if self._closed:
            return
        
        try:
            self.logger.info(f"Closing {self.__class__.__name__}...")
            await self._cleanup_client()
            self._closed = True
            self.logger.info(f"{self.__class__.__name__} closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing {self.__class__.__name__}: {str(e)}")
            raise Text2SQLLTMError(
                f"LLM provider cleanup failed: {str(e)}",
                cause=e
            ) from e
    
    @asynccontextmanager
    async def session_context(self) -> AsyncContextManager[BaseLLMProvider]:
        """Async context manager for LLM provider lifecycle."""
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()
    
    def _ensure_initialized(self) -> None:
        """Ensure the provider is initialized."""
        if not self._initialized:
            raise QueryGenerationError(
                natural_language="",
                reason="LLM provider not initialized. Call initialize() first."
            )
        
        if self._closed:
            raise QueryGenerationError(
                natural_language="",
                reason="LLM provider is closed. Create a new instance."
            )
    
    @abstractmethod
    async def _initialize_client(self) -> None:
        """Initialize the LLM client. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def _cleanup_client(self) -> None:
        """Clean up the LLM client. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def generate_sql(
        self,
        natural_query: NaturalLanguageQuery,
        context: Dict[str, Any],
        schema: Optional[SchemaInfo] = None,
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
        max_complexity: QueryComplexity = QueryComplexity.COMPLEX,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> QueryResult:
        """
        Generate SQL query from natural language with context.
        
        Args:
            natural_query: Natural language query to convert
            context: Enhanced context with memory and session information
            schema: Database schema information
            dialect: Target SQL dialect
            max_complexity: Maximum allowed query complexity
            temperature: LLM temperature for creativity vs consistency
            max_tokens: Maximum tokens in response
            
        Returns:
            QueryResult: Generated SQL with metadata
            
        Raises:
            QueryGenerationError: When SQL generation fails
        """
        pass
    
    @abstractmethod
    async def explain_query(self, sql_query: SQLQuery) -> str:
        """
        Generate explanation for a SQL query.
        
        Args:
            sql_query: SQL query to explain
            
        Returns:
            str: Human-readable explanation of the query
            
        Raises:
            QueryGenerationError: When explanation generation fails
        """
        pass
    
    @abstractmethod
    async def optimize_query(
        self,
        sql_query: SQLQuery,
        schema: Optional[SchemaInfo] = None
    ) -> SQLQuery:
        """
        Optimize a SQL query for better performance.
        
        Args:
            sql_query: SQL query to optimize
            schema: Database schema for optimization context
            
        Returns:
            SQLQuery: Optimized SQL query
            
        Raises:
            QueryGenerationError: When optimization fails
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get provider metrics."""
        return self._metrics.copy()
    
    def _update_metrics(
        self,
        success: bool,
        response_time: float,
        tokens_used: int = 0,
        cache_hit: bool = False
    ) -> None:
        """Update provider metrics."""
        self._metrics["requests_made"] += 1
        
        if success:
            self._metrics["requests_successful"] += 1
        else:
            self._metrics["requests_failed"] += 1
        
        self._metrics["total_tokens_used"] += tokens_used
        
        if cache_hit:
            self._metrics["cache_hits"] += 1
        else:
            self._metrics["cache_misses"] += 1
        
        # Update average response time
        current_avg = self._metrics["average_response_time"]
        total_requests = self._metrics["requests_made"]
        self._metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def _build_system_prompt(self, schema: Optional[SchemaInfo], dialect: SQLDialect) -> str:
        """Build system prompt for SQL generation."""
        base_prompt = f"""You are an expert SQL query generator. Your task is to convert natural language queries into accurate {dialect.value.upper()} SQL queries.

Guidelines:
1. Generate syntactically correct {dialect.value.upper()} SQL
2. Use proper table and column names from the provided schema
3. Include appropriate WHERE clauses, JOINs, and aggregations as needed
4. Optimize for readability and performance
5. Return only the SQL query without explanations unless specifically requested
6. Use standard SQL formatting with proper indentation

"""
        
        if schema:
            schema_info = self._format_schema_for_prompt(schema)
            base_prompt += f"\nDatabase Schema:\n{schema_info}\n"
        
        return base_prompt
    
    def _format_schema_for_prompt(self, schema: SchemaInfo) -> str:
        """Format schema information for inclusion in prompts."""
        schema_text = f"Database: {schema.database_name}\n\n"
        
        for table_name, table_info in schema.tables.items():
            schema_text += f"Table: {table_name}\n"
            
            columns = table_info.get("columns", {})
            for col_name, col_info in columns.items():
                col_type = col_info.get("type", "unknown")
                nullable = "" if col_info.get("nullable", True) else " NOT NULL"
                pk = " (PRIMARY KEY)" if col_info.get("primary_key", False) else ""
                fk = f" (FOREIGN KEY -> {col_info['foreign_key']})" if col_info.get("foreign_key") else ""
                
                schema_text += f"  - {col_name}: {col_type}{nullable}{pk}{fk}\n"
            
            schema_text += "\n"
        
        # Add relationships if available
        if schema.relationships:
            schema_text += "Relationships:\n"
            for rel in schema.relationships:
                rel_type = rel.get("relationship_type", "unknown")
                source = f"{rel.get('source_table')}.{rel.get('source_column')}"
                target = f"{rel.get('target_table')}.{rel.get('target_column')}"
                schema_text += f"  - {source} -> {target} ({rel_type})\n"
        
        return schema_text
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from LLM response."""
        # Remove markdown code blocks if present
        import re
        
        # Look for SQL code blocks
        sql_pattern = r'```(?:sql|SQL)?\s*(.*?)\s*```'
        matches = re.findall(sql_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks, try to extract SQL-like content
        lines = response.strip().split('\n')
        sql_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                sql_lines.append(line)
        
        return '\n'.join(sql_lines).strip()
    
    def _estimate_query_complexity(self, sql_query: str) -> QueryComplexity:
        """Estimate query complexity based on SQL content."""
        query_upper = sql_query.upper()
        
        complexity_score = 0
        
        # Count complexity indicators
        if 'JOIN' in query_upper:
            complexity_score += query_upper.count('JOIN') * 2
        
        if 'SUBQUERY' in query_upper or '(' in query_upper:
            complexity_score += 3
        
        if any(keyword in query_upper for keyword in ['GROUP BY', 'HAVING', 'ORDER BY']):
            complexity_score += 2
        
        if any(keyword in query_upper for keyword in ['UNION', 'INTERSECT', 'EXCEPT']):
            complexity_score += 4
        
        if any(keyword in query_upper for keyword in ['WINDOW', 'OVER', 'PARTITION']):
            complexity_score += 5
        
        # Determine complexity level
        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 5:
            return QueryComplexity.MODERATE
        elif complexity_score <= 10:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
