"""
OpenAI LLM provider for Text2SQL-LTM library.

This module provides OpenAI GPT integration with comprehensive error handling,
rate limiting, and production-grade features.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import openai
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    # Mock classes for development
    class AsyncOpenAI:
        def __init__(self, *args, **kwargs):
            pass
        
        class chat:
            class completions:
                @staticmethod
                async def create(*args, **kwargs):
                    return type('MockResponse', (), {
                        'choices': [type('Choice', (), {
                            'message': type('Message', (), {
                                'content': 'SELECT * FROM users WHERE id = 1;'
                            })()
                        })()],
                        'usage': type('Usage', (), {
                            'total_tokens': 50
                        })()
                    })()

from .base import BaseLLMProvider
from ..config import AgentConfig
from ..types import (
    QueryResult, MemoryContext, SchemaInfo, SQLDialect, QueryComplexity,
    NaturalLanguageQuery, SQLQuery, Score, Timestamp, TableName, ColumnName
)
from ..exceptions import QueryGenerationError, Text2SQLLTMError


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI GPT provider for SQL generation with production-grade features.
    
    This provider supports:
    - GPT-4 and GPT-3.5-turbo models
    - Async operations with proper error handling
    - Rate limiting and retry logic
    - Token usage tracking and optimization
    - Context-aware SQL generation with memory integration
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize OpenAI provider."""
        super().__init__(config)
        
        if not HAS_OPENAI:
            self.logger.warning("OpenAI library not available, using mock implementation")
        
        self._client: Optional[AsyncOpenAI] = None
        self._rate_limiter: Dict[str, float] = {}
    
    async def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            if not self.config.llm_api_key:
                raise ValueError("OpenAI API key is required")
            
            client_kwargs = {
                "api_key": self.config.llm_api_key,
            }
            
            if self.config.llm_base_url:
                client_kwargs["base_url"] = self.config.llm_base_url
            
            if self.config.llm_organization_id:
                client_kwargs["organization"] = self.config.llm_organization_id
            
            self._client = AsyncOpenAI(**client_kwargs)
            
            # Test the connection
            await self._test_connection()
            
        except Exception as e:
            raise QueryGenerationError(
                natural_language="",
                reason=f"Failed to initialize OpenAI client: {str(e)}",
                cause=e
            ) from e
    
    async def _cleanup_client(self) -> None:
        """Clean up OpenAI client."""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def _test_connection(self) -> None:
        """Test OpenAI API connection."""
        try:
            # Make a minimal test request
            response = await self._client.chat.completions.create(
                model=self.config.llm_model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                temperature=0
            )
            
            if not response.choices:
                raise ValueError("Invalid response from OpenAI API")
                
        except Exception as e:
            raise QueryGenerationError(
                natural_language="",
                reason=f"OpenAI API connection test failed: {str(e)}",
                cause=e
            ) from e
    
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
        """Generate SQL query using OpenAI GPT."""
        self._ensure_initialized()
        
        start_time = time.time()
        
        try:
            # Check rate limits
            await self._check_rate_limits()
            
            # Build messages for chat completion
            messages = self._build_messages(
                natural_query, context, schema, dialect, max_complexity
            )
            
            # Make API request
            response = await self._client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
            )
            
            # Extract SQL from response
            sql_content = response.choices[0].message.content
            sql_query = self._extract_sql_from_response(sql_content)
            
            if not sql_query:
                raise QueryGenerationError(
                    natural_language=natural_query,
                    reason="No valid SQL found in OpenAI response"
                )
            
            # Validate SQL syntax
            if not self._is_valid_sql(sql_query):
                raise QueryGenerationError(
                    natural_language=natural_query,
                    reason="Generated SQL has invalid syntax"
                )
            
            # Extract metadata
            tables_used = self._extract_tables_from_sql(sql_query)
            columns_used = self._extract_columns_from_sql(sql_query)
            complexity = self._estimate_query_complexity(sql_query)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                natural_query, sql_query, context, schema
            )
            
            # Generate explanation if requested
            explanation = ""
            if context.get("include_explanation", True):
                explanation = await self._generate_explanation(sql_query)
            
            # Create result
            result = QueryResult(
                sql=sql_query,
                explanation=explanation,
                confidence=confidence,
                query_type=self._determine_query_type(sql_query),
                tables_used=tables_used,
                columns_used=columns_used,
                complexity=complexity,
                dialect=dialect,
                execution_time_ms=int((time.time() - start_time) * 1000),
                memory_context_used=[],  # Will be populated by agent
                metadata={
                    "provider": "openai",
                    "model": self.config.llm_model,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                created_at=datetime.utcnow()
            )
            
            # Update metrics
            self._update_metrics(
                success=True,
                response_time=time.time() - start_time,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return result
            
        except Exception as e:
            # Update metrics
            self._update_metrics(
                success=False,
                response_time=time.time() - start_time
            )
            
            if isinstance(e, QueryGenerationError):
                raise
            
            self.logger.error(f"OpenAI SQL generation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language=natural_query,
                reason=f"OpenAI API error: {str(e)}",
                cause=e
            ) from e
    
    async def explain_query(self, sql_query: SQLQuery) -> str:
        """Generate explanation for SQL query."""
        self._ensure_initialized()
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert SQL analyst. Explain SQL queries in clear, simple language that non-technical users can understand."
                },
                {
                    "role": "user",
                    "content": f"Please explain what this SQL query does:\n\n{sql_query}"
                }
            ]
            
            response = await self._client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate explanation: {str(e)}")
            return f"Unable to generate explanation: {str(e)}"
    
    async def optimize_query(
        self,
        sql_query: SQLQuery,
        schema: Optional[SchemaInfo] = None
    ) -> SQLQuery:
        """Optimize SQL query for better performance."""
        self._ensure_initialized()
        
        try:
            system_prompt = "You are an expert SQL optimizer. Optimize the given SQL query for better performance while maintaining the same results."
            
            if schema:
                schema_info = self._format_schema_for_prompt(schema)
                system_prompt += f"\n\nDatabase Schema:\n{schema_info}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": f"Optimize this SQL query:\n\n{sql_query}\n\nReturn only the optimized SQL query."
                }
            ]
            
            response = await self._client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            optimized_sql = self._extract_sql_from_response(response.choices[0].message.content)
            return optimized_sql if optimized_sql else sql_query
            
        except Exception as e:
            self.logger.error(f"Failed to optimize query: {str(e)}")
            return sql_query  # Return original query if optimization fails
    
    # Helper methods
    
    async def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        current_time = time.time()
        
        # Simple rate limiting - in production, use more sophisticated approach
        last_request = self._rate_limiter.get("last_request", 0)
        min_interval = 60.0 / self.config.request_rate_limit  # Convert to seconds
        
        if current_time - last_request < min_interval:
            sleep_time = min_interval - (current_time - last_request)
            await asyncio.sleep(sleep_time)
        
        self._rate_limiter["last_request"] = time.time()
    
    def _build_messages(
        self,
        natural_query: str,
        context: Dict[str, Any],
        schema: Optional[SchemaInfo],
        dialect: SQLDialect,
        max_complexity: QueryComplexity
    ) -> List[Dict[str, str]]:
        """Build messages for OpenAI chat completion."""
        system_prompt = self._build_system_prompt(schema, dialect)
        
        # Add complexity constraint
        system_prompt += f"\nMaximum query complexity allowed: {max_complexity.name}\n"
        
        # Add context information
        if context.get("memory_contexts"):
            system_prompt += "\nRelevant context from previous queries:\n"
            for memory_ctx in context["memory_contexts"][:3]:  # Limit context
                if isinstance(memory_ctx, dict):
                    content = memory_ctx.get("content", "")
                    if isinstance(content, str) and content:
                        system_prompt += f"- {content}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Convert this natural language query to SQL: {natural_query}"}
        ]
        
        return messages
    
    async def _generate_explanation(self, sql_query: str) -> str:
        """Generate explanation for the SQL query."""
        try:
            return await self.explain_query(sql_query)
        except Exception as e:
            self.logger.warning(f"Failed to generate explanation: {str(e)}")
            return "Explanation not available"
    
    def _is_valid_sql(self, sql_query: str) -> bool:
        """Basic SQL syntax validation."""
        if not sql_query or not sql_query.strip():
            return False
        
        # Basic checks
        sql_upper = sql_query.upper().strip()
        
        # Must start with a valid SQL keyword
        valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE', 'DROP', 'ALTER']
        if not any(sql_upper.startswith(keyword) for keyword in valid_starts):
            return False
        
        # Check for balanced parentheses
        open_count = sql_query.count('(')
        close_count = sql_query.count(')')
        if open_count != close_count:
            return False
        
        return True
    
    def _extract_tables_from_sql(self, sql_query: str) -> List[TableName]:
        """Extract table names from SQL query."""
        import re
        
        # Simple regex to find table references
        table_pattern = r'(?:FROM|JOIN|UPDATE|INTO)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(table_pattern, sql_query, re.IGNORECASE)
        
        return [TableName(match.lower()) for match in matches]
    
    def _extract_columns_from_sql(self, sql_query: str) -> List[ColumnName]:
        """Extract column names from SQL query."""
        # This is a simplified implementation
        # In production, you'd want a proper SQL parser
        columns = []
        
        # Extract from SELECT clause
        import re
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        match = re.search(select_pattern, sql_query, re.IGNORECASE | re.DOTALL)
        
        if match:
            select_clause = match.group(1)
            # Simple column extraction (doesn't handle all cases)
            if '*' not in select_clause:
                column_parts = select_clause.split(',')
                for part in column_parts:
                    part = part.strip()
                    # Extract column name (handle aliases)
                    if ' AS ' in part.upper():
                        column_name = part.split(' AS ')[0].strip()
                    else:
                        column_name = part.strip()
                    
                    # Remove table prefixes
                    if '.' in column_name:
                        column_name = column_name.split('.')[-1]
                    
                    # Clean up
                    column_name = column_name.strip('`"[]')
                    if column_name and column_name.isidentifier():
                        columns.append(ColumnName(column_name.lower()))
        
        return columns
    
    def _determine_query_type(self, sql_query: str) -> str:
        """Determine the type of SQL query."""
        sql_upper = sql_query.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return "SELECT"
        elif sql_upper.startswith('INSERT'):
            return "INSERT"
        elif sql_upper.startswith('UPDATE'):
            return "UPDATE"
        elif sql_upper.startswith('DELETE'):
            return "DELETE"
        elif sql_upper.startswith('WITH'):
            return "CTE"
        else:
            return "OTHER"
    
    def _calculate_confidence_score(
        self,
        natural_query: str,
        sql_query: str,
        context: Dict[str, Any],
        schema: Optional[SchemaInfo]
    ) -> Score:
        """Calculate confidence score for the generated SQL."""
        score = 0.5  # Base score
        
        # Increase confidence if schema is available
        if schema:
            score += 0.2
        
        # Increase confidence if memory context is used
        if context.get("memory_contexts"):
            score += 0.1
        
        # Increase confidence based on query complexity match
        if len(sql_query.split()) > 10:  # More detailed query
            score += 0.1
        
        # Decrease confidence for very short or very long queries
        if len(sql_query) < 20 or len(sql_query) > 1000:
            score -= 0.1
        
        return Score(max(0.0, min(1.0, score)))
