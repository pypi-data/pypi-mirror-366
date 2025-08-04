"""
Local LLM provider for Text2SQL-LTM library.

This module provides integration with locally hosted LLM models via
various backends like Ollama, LM Studio, or custom API endpoints.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

from .base import BaseLLMProvider
from ..config import AgentConfig
from ..types import (
    NaturalLanguageQuery, SQLQuery, QueryExplanation, 
    OptimizationSuggestion, DatabaseSchema, SQLDialect
)
from ..exceptions import QueryGenerationError, ConfigurationError

logger = logging.getLogger(__name__)


class LocalProvider(BaseLLMProvider):
    """
    Local LLM provider for SQL generation and analysis.
    
    Supports various local LLM backends:
    - Ollama (http://localhost:11434)
    - LM Studio (http://localhost:1234)
    - Custom API endpoints
    - Text Generation WebUI
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize Local provider with configuration."""
        super().__init__(config)
        
        if not AIOHTTP_AVAILABLE:
            raise ConfigurationError(
                "aiohttp library not installed. Install with: pip install aiohttp"
            )
        
        # Local server configuration
        self.base_url = getattr(config, 'local_llm_url', 'http://localhost:11434')
        self.model_name = config.llm_model or "llama2"
        self.max_tokens = config.llm_max_tokens or 2048
        self.temperature = config.llm_temperature or 0.1
        
        # Backend type detection
        self.backend_type = self._detect_backend_type()
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
    def _detect_backend_type(self) -> str:
        """Detect the type of local backend based on URL."""
        if "11434" in self.base_url:
            return "ollama"
        elif "1234" in self.base_url:
            return "lm_studio"
        elif "7860" in self.base_url:
            return "text_generation_webui"
        else:
            return "custom"
    
    async def _initialize_client(self) -> None:
        """Initialize the local LLM client."""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection
            await self._test_connection()
            logger.info(f"Local LLM client initialized successfully ({self.backend_type})")
            
        except Exception as e:
            logger.error(f"Failed to initialize local LLM client: {str(e)}")
            raise ConfigurationError(f"Local LLM initialization failed: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up the local LLM client."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Local LLM client cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the local LLM API connection."""
        try:
            if self.backend_type == "ollama":
                url = f"{self.base_url}/api/tags"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        logger.debug("Ollama connection test successful")
                    else:
                        raise ConfigurationError(f"Ollama test failed with status {response.status}")
            
            elif self.backend_type == "lm_studio":
                url = f"{self.base_url}/v1/models"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        logger.debug("LM Studio connection test successful")
                    else:
                        raise ConfigurationError(f"LM Studio test failed with status {response.status}")
            
            else:
                # Generic test for custom endpoints
                url = f"{self.base_url}/health" if "/health" not in self.base_url else self.base_url
                try:
                    async with self.session.get(url) as response:
                        logger.debug(f"Custom endpoint connection test: {response.status}")
                except:
                    logger.warning("Custom endpoint health check failed, but continuing...")
                    
        except Exception as e:
            raise ConfigurationError(f"Local LLM connection test failed: {str(e)}") from e
    
    async def generate_sql(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
        context: Optional[Dict[str, Any]] = None
    ) -> SQLQuery:
        """
        Generate SQL query from natural language using local LLM.
        
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
            
            response_text = await self._generate_text(prompt)
            return self._parse_sql_response(response_text, natural_query)
            
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language=natural_query,
                reason=f"Local LLM SQL generation failed: {str(e)}",
                cause=e
            ) from e
    
    async def explain_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryExplanation:
        """
        Explain SQL query using local LLM.
        
        Args:
            sql_query: SQL query to explain
            schema: Database schema information
            context: Additional context
            
        Returns:
            QueryExplanation: Detailed query explanation
        """
        try:
            prompt = self._build_explanation_prompt(sql_query, schema, context)
            response_text = await self._generate_text(prompt)
            return self._parse_explanation_response(response_text, sql_query)
            
        except Exception as e:
            logger.error(f"Query explanation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language="",
                reason=f"Local LLM explanation failed: {str(e)}",
                cause=e
            ) from e
    
    async def optimize_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationSuggestion]:
        """
        Generate optimization suggestions using local LLM.
        
        Args:
            sql_query: SQL query to optimize
            schema: Database schema information
            context: Additional context
            
        Returns:
            List[OptimizationSuggestion]: Optimization suggestions
        """
        try:
            prompt = self._build_optimization_prompt(sql_query, schema, context)
            response_text = await self._generate_text(prompt)
            return self._parse_optimization_response(response_text, sql_query)
            
        except Exception as e:
            logger.error(f"Query optimization failed: {str(e)}")
            return []  # Return empty list on failure
    
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using the local LLM backend."""
        try:
            if self.backend_type == "ollama":
                return await self._generate_ollama(prompt)
            elif self.backend_type == "lm_studio":
                return await self._generate_lm_studio(prompt)
            elif self.backend_type == "text_generation_webui":
                return await self._generate_text_generation_webui(prompt)
            else:
                return await self._generate_custom(prompt)
                
        except Exception as e:
            raise QueryGenerationError(
                natural_language="",
                reason=f"Local LLM text generation failed: {str(e)}",
                cause=e
            ) from e
    
    async def _generate_ollama(self, prompt: str) -> str:
        """Generate text using Ollama API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                raise QueryGenerationError(
                    natural_language="",
                    reason=f"Ollama API error: {response.status}",
                    cause=None
                )
            
            result = await response.json()
            return result.get("response", "")
    
    async def _generate_lm_studio(self, prompt: str) -> str:
        """Generate text using LM Studio API."""
        url = f"{self.base_url}/v1/completions"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                raise QueryGenerationError(
                    natural_language="",
                    reason=f"LM Studio API error: {response.status}",
                    cause=None
                )
            
            result = await response.json()
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("text", "")
            return ""
    
    async def _generate_text_generation_webui(self, prompt: str) -> str:
        """Generate text using Text Generation WebUI API."""
        url = f"{self.base_url}/api/v1/generate"
        payload = {
            "prompt": prompt,
            "max_new_tokens": self.max_tokens,
            "temperature": self.temperature,
            "do_sample": True,
            "stopping_strings": ["</s>", "<|endoftext|>"]
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                raise QueryGenerationError(
                    natural_language="",
                    reason=f"Text Generation WebUI API error: {response.status}",
                    cause=None
                )
            
            result = await response.json()
            results = result.get("results", [])
            if results:
                return results[0].get("text", "")
            return ""
    
    async def _generate_custom(self, prompt: str) -> str:
        """Generate text using custom API endpoint."""
        # Generic implementation for custom endpoints
        payload = {
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        async with self.session.post(self.base_url, json=payload) as response:
            if response.status != 200:
                raise QueryGenerationError(
                    natural_language="",
                    reason=f"Custom API error: {response.status}",
                    cause=None
                )
            
            result = await response.json()
            # Try common response formats
            if "response" in result:
                return result["response"]
            elif "text" in result:
                return result["text"]
            elif "generated_text" in result:
                return result["generated_text"]
            else:
                return str(result)

    def _build_sql_generation_prompt(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for SQL generation optimized for local models."""
        schema_info = self._format_schema_info(schema)
        context_info = self._format_context_info(context) if context else ""

        return f"""You are an expert SQL developer. Generate a SQL query for the following request.

Natural Language Query: {natural_query}
Database Schema: {schema_info}
SQL Dialect: {dialect.value}
{context_info}

Requirements:
- Generate syntactically correct SQL for {dialect.value}
- Use appropriate table and column names from the schema
- Include proper JOINs when needed
- Optimize for performance

SQL Query:"""

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

Explanation:"""

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

Optimization Suggestions:"""

    def _format_schema_info(self, schema: DatabaseSchema) -> str:
        """Format schema information for prompts."""
        if not schema:
            return "No schema provided"

        schema_parts = []
        for table_name, table_info in schema.items():
            if isinstance(table_info, dict) and 'columns' in table_info:
                columns = table_info['columns']
                column_list = ", ".join([f"{col} ({info.get('type', 'unknown')})"
                                       for col, info in columns.items()])
                schema_parts.append(f"Table {table_name}: {column_list}")
            else:
                schema_parts.append(f"Table {table_name}: {str(table_info)}")

        return "\n".join(schema_parts)

    def _format_context_info(self, context: Dict[str, Any]) -> str:
        """Format context information for prompts."""
        if not context:
            return ""

        context_parts = []
        for key, value in context.items():
            context_parts.append(f"{key}: {value}")

        return f"\nAdditional Context:\n" + "\n".join(context_parts)

    def _parse_sql_response(self, response_text: str, natural_query: str) -> SQLQuery:
        """Parse local LLM SQL generation response."""
        try:
            # Clean the response
            response_text = response_text.strip()

            # Extract SQL from response
            lines = response_text.split('\n')
            sql_lines = []

            # Look for SQL keywords to identify the query
            sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH", "CREATE"]
            found_sql = False

            for line in lines:
                line = line.strip()
                if any(keyword in line.upper() for keyword in sql_keywords):
                    found_sql = True
                    sql_lines.append(line)
                elif found_sql and line and not line.startswith('#') and not line.startswith('--'):
                    sql_lines.append(line)
                elif found_sql and not line:
                    break  # Stop at first empty line after SQL

            sql = '\n'.join(sql_lines).strip()

            if not sql:
                # Fallback: use entire response
                sql = response_text

            return SQLQuery(
                sql=sql,
                natural_language=natural_query,
                confidence=0.85,  # Good confidence for local models
                metadata={
                    "provider": "local",
                    "backend": self.backend_type,
                    "model": self.model_name,
                    "base_url": self.base_url,
                    "raw_response": response_text
                }
            )

        except Exception as e:
            logger.warning(f"Failed to parse local LLM response: {str(e)}")
            return SQLQuery(
                sql=response_text.strip(),
                natural_language=natural_query,
                confidence=0.7,
                metadata={
                    "provider": "local",
                    "backend": self.backend_type,
                    "model": self.model_name,
                    "parse_error": str(e)
                }
            )

    def _parse_explanation_response(self, response_text: str, sql_query: str) -> QueryExplanation:
        """Parse local LLM explanation response."""
        try:
            # Clean the response
            response_text = response_text.strip()

            # Split into paragraphs for step-by-step
            paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]

            # Extract summary (first paragraph)
            summary = paragraphs[0] if paragraphs else response_text

            # Create step-by-step from sentences
            sentences = []
            for paragraph in paragraphs[:3]:  # Limit to first 3 paragraphs
                sentences.extend([s.strip() for s in paragraph.split('.') if s.strip()])

            return QueryExplanation(
                sql_query=sql_query,
                summary=summary,
                step_by_step=sentences[:5],  # Limit to first 5 steps
                complexity="medium",
                metadata={
                    "provider": "local",
                    "backend": self.backend_type,
                    "model": self.model_name,
                    "raw_response": response_text
                }
            )

        except Exception as e:
            logger.warning(f"Failed to parse local LLM explanation: {str(e)}")
            return QueryExplanation(
                sql_query=sql_query,
                summary=response_text.strip(),
                step_by_step=[response_text.strip()],
                complexity="medium",
                metadata={
                    "provider": "local",
                    "backend": self.backend_type,
                    "model": self.model_name,
                    "parse_error": str(e)
                }
            )

    def _parse_optimization_response(self, response_text: str, sql_query: str) -> List[OptimizationSuggestion]:
        """Parse local LLM optimization response."""
        try:
            # Clean the response
            response_text = response_text.strip()

            # Split into suggestions
            suggestions = []
            lines = response_text.split('\n')

            current_suggestion = ""
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*') or line.startswith('•')):
                    if current_suggestion:
                        suggestions.append(current_suggestion.strip())
                    current_suggestion = line
                elif current_suggestion and line:
                    current_suggestion += " " + line

            if current_suggestion:
                suggestions.append(current_suggestion.strip())

            # Convert to OptimizationSuggestion objects
            optimization_suggestions = []
            for i, suggestion in enumerate(suggestions[:5]):  # Limit to 5 suggestions
                optimization_suggestions.append(OptimizationSuggestion(
                    type="general",
                    description=f"Optimization suggestion {i+1}",
                    suggestion=suggestion,
                    impact="medium",
                    effort="moderate",
                    metadata={
                        "provider": "local",
                        "backend": self.backend_type,
                        "model": self.model_name,
                        "sql_query": sql_query
                    }
                ))

            return optimization_suggestions

        except Exception as e:
            logger.warning(f"Failed to parse local LLM optimization response: {str(e)}")
            return [OptimizationSuggestion(
                type="general",
                description="Optimization analysis",
                suggestion=response_text.strip(),
                impact="medium",
                effort="moderate",
                metadata={
                    "provider": "local",
                    "backend": self.backend_type,
                    "model": self.model_name,
                    "parse_error": str(e)
                }
            )]
