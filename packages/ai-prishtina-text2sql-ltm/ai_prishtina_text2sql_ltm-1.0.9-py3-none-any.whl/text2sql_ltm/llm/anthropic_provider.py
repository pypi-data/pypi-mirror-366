"""
Anthropic Claude provider for Text2SQL-LTM library.

This module provides integration with Anthropic's Claude models for SQL generation,
query explanation, and optimization with production-grade error handling.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

try:
    import anthropic
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None

from .base import BaseLLMProvider
from ..config import AgentConfig
from ..types import (
    NaturalLanguageQuery, SQLQuery, QueryExplanation, 
    OptimizationSuggestion, DatabaseSchema, SQLDialect
)
from ..exceptions import QueryGenerationError, ConfigurationError

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider for SQL generation and analysis.
    
    Supports Claude-3 models with advanced reasoning capabilities for
    complex SQL generation and optimization tasks.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize Anthropic provider with configuration."""
        super().__init__(config)
        
        if not ANTHROPIC_AVAILABLE:
            raise ConfigurationError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )
        
        self.client: Optional[AsyncAnthropic] = None
        self.model = config.llm_model or "claude-3-sonnet-20240229"
        self.max_tokens = config.llm_max_tokens or 4096
        self.temperature = config.llm_temperature or 0.1
        
        # Anthropic-specific settings
        self.system_prompt = self._build_system_prompt()
        
    async def _initialize_client(self) -> None:
        """Initialize the Anthropic client."""
        try:
            api_key = self.config.llm_api_key
            if not api_key:
                raise ConfigurationError("Anthropic API key not provided")
            
            self.client = AsyncAnthropic(api_key=api_key)
            
            # Test connection
            await self._test_connection()
            logger.info("Anthropic client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            raise ConfigurationError(f"Anthropic initialization failed: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up the Anthropic client."""
        if self.client:
            # Anthropic client doesn't require explicit cleanup
            self.client = None
            logger.info("Anthropic client cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the Anthropic API connection."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            logger.debug("Anthropic connection test successful")
        except Exception as e:
            raise ConfigurationError(f"Anthropic connection test failed: {str(e)}") from e
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude."""
        return """You are an expert SQL developer and database architect. Your task is to:

1. Generate accurate, efficient SQL queries from natural language
2. Provide clear explanations of SQL logic
3. Suggest optimizations for better performance
4. Ensure security best practices (prevent SQL injection)
5. Support multiple SQL dialects (PostgreSQL, MySQL, SQLite, SQL Server)

Guidelines:
- Always use parameterized queries when possible
- Prefer explicit JOINs over implicit ones
- Use appropriate indexes and query hints
- Follow SQL best practices and conventions
- Provide clear, educational explanations
- Consider performance implications

Respond with valid JSON when requested, and always prioritize accuracy and security."""
    
    async def generate_sql(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
        context: Optional[Dict[str, Any]] = None
    ) -> SQLQuery:
        """
        Generate SQL query from natural language using Claude.
        
        Args:
            natural_query: Natural language query
            schema: Database schema information
            dialect: Target SQL dialect
            context: Additional context for generation
            
        Returns:
            SQLQuery: Generated SQL query with metadata
            
        Raises:
            QueryGenerationError: When SQL generation fails
        """
        try:
            prompt = self._build_sql_generation_prompt(
                natural_query, schema, dialect, context
            )
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_sql_response(response.content[0].text, natural_query)
            
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language=natural_query,
                reason=f"Claude SQL generation failed: {str(e)}",
                cause=e
            ) from e
    
    async def explain_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryExplanation:
        """
        Explain SQL query using Claude's reasoning capabilities.
        
        Args:
            sql_query: SQL query to explain
            schema: Database schema information
            context: Additional context
            
        Returns:
            QueryExplanation: Detailed query explanation
        """
        try:
            prompt = self._build_explanation_prompt(sql_query, schema, context)
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,  # Slightly higher for more detailed explanations
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_explanation_response(response.content[0].text, sql_query)
            
        except Exception as e:
            logger.error(f"Query explanation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language="",
                reason=f"Claude explanation failed: {str(e)}",
                cause=e
            ) from e
    
    async def optimize_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationSuggestion]:
        """
        Generate optimization suggestions using Claude.
        
        Args:
            sql_query: SQL query to optimize
            schema: Database schema information
            context: Additional context
            
        Returns:
            List[OptimizationSuggestion]: Optimization suggestions
        """
        try:
            prompt = self._build_optimization_prompt(sql_query, schema, context)
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.2,  # Lower temperature for consistent optimization advice
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_optimization_response(response.content[0].text, sql_query)
            
        except Exception as e:
            logger.error(f"Query optimization failed: {str(e)}")
            return []  # Return empty list on failure
    
    def _build_sql_generation_prompt(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for SQL generation."""
        schema_info = self._format_schema_info(schema)
        context_info = self._format_context_info(context) if context else ""
        
        return f"""Generate a SQL query for the following request:

Natural Language Query: {natural_query}
Target SQL Dialect: {dialect.value}

Database Schema:
{schema_info}

{context_info}

Requirements:
1. Generate syntactically correct SQL for {dialect.value}
2. Use appropriate table and column names from the schema
3. Include proper JOINs when needed
4. Use parameterized queries for security
5. Optimize for performance

Respond with a JSON object containing:
{{
    "sql": "the generated SQL query",
    "explanation": "brief explanation of the query logic",
    "parameters": ["list of parameter names if any"],
    "confidence": 0.95
}}"""
    
    def _build_explanation_prompt(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for query explanation."""
        schema_info = self._format_schema_info(schema)
        
        return f"""Explain the following SQL query in detail:

SQL Query:
{sql_query}

Database Schema:
{schema_info}

Provide a comprehensive explanation including:
1. What the query does (high-level purpose)
2. Step-by-step breakdown of each clause
3. How JOINs work (if any)
4. Performance considerations
5. Potential improvements

Respond with a JSON object containing:
{{
    "summary": "high-level explanation",
    "step_by_step": ["detailed breakdown of each part"],
    "performance_notes": "performance analysis",
    "complexity": "simple|medium|complex"
}}"""
    
    def _build_optimization_prompt(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for query optimization."""
        schema_info = self._format_schema_info(schema)
        
        return f"""Analyze and suggest optimizations for this SQL query:

SQL Query:
{sql_query}

Database Schema:
{schema_info}

Provide optimization suggestions including:
1. Index recommendations
2. Query rewriting opportunities
3. Performance improvements
4. Best practice violations

Respond with a JSON array of optimization suggestions:
[
    {{
        "type": "index|rewrite|performance|best_practice",
        "description": "what to optimize",
        "suggestion": "specific recommendation",
        "impact": "high|medium|low",
        "effort": "easy|moderate|complex"
    }}
]"""
