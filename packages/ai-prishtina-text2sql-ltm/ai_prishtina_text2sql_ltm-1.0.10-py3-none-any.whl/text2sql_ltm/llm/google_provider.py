"""
Google Gemini provider for Text2SQL-LTM library.

This module provides integration with Google's Gemini models for SQL generation,
query explanation, and optimization with production-grade error handling.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    genai = None

from .base import BaseLLMProvider
from ..config import AgentConfig
from ..types import (
    NaturalLanguageQuery, SQLQuery, QueryExplanation, 
    OptimizationSuggestion, DatabaseSchema, SQLDialect
)
from ..exceptions import QueryGenerationError, ConfigurationError

logger = logging.getLogger(__name__)


class GoogleProvider(BaseLLMProvider):
    """
    Google Gemini provider for SQL generation and analysis.
    
    Supports Gemini Pro and other Google AI models with advanced
    reasoning capabilities for SQL generation tasks.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize Google provider with configuration."""
        super().__init__(config)
        
        if not GOOGLE_AVAILABLE:
            raise ConfigurationError(
                "Google AI library not installed. Install with: pip install google-generativeai"
            )
        
        self.model_name = config.llm_model or "gemini-pro"
        self.max_tokens = config.llm_max_tokens or 4096
        self.temperature = config.llm_temperature or 0.1
        
        # Google-specific settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            candidate_count=1
        )
        
        self.model = None
        
    async def _initialize_client(self) -> None:
        """Initialize the Google AI client."""
        try:
            api_key = self.config.llm_api_key
            if not api_key:
                raise ConfigurationError("Google AI API key not provided")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Test connection
            await self._test_connection()
            logger.info("Google AI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google AI client: {str(e)}")
            raise ConfigurationError(f"Google AI initialization failed: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up the Google AI client."""
        if self.model:
            self.model = None
            logger.info("Google AI client cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the Google AI API connection."""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                "Test connection",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            logger.debug("Google AI connection test successful")
        except Exception as e:
            raise ConfigurationError(f"Google AI connection test failed: {str(e)}") from e
    
    async def generate_sql(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
        context: Optional[Dict[str, Any]] = None
    ) -> SQLQuery:
        """
        Generate SQL query from natural language using Gemini.
        
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
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if not response.text:
                raise QueryGenerationError(
                    natural_language=natural_query,
                    reason="Gemini returned empty response",
                    cause=None
                )
            
            return self._parse_sql_response(response.text, natural_query)
            
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language=natural_query,
                reason=f"Gemini SQL generation failed: {str(e)}",
                cause=e
            ) from e
    
    async def explain_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryExplanation:
        """
        Explain SQL query using Gemini's reasoning capabilities.
        
        Args:
            sql_query: SQL query to explain
            schema: Database schema information
            context: Additional context
            
        Returns:
            QueryExplanation: Detailed query explanation
        """
        try:
            prompt = self._build_explanation_prompt(sql_query, schema, context)
            
            config = genai.types.GenerationConfig(
                temperature=0.3,  # Slightly higher for more detailed explanations
                max_output_tokens=self.max_tokens,
                candidate_count=1
            )
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            if not response.text:
                raise QueryGenerationError(
                    natural_language="",
                    reason="Gemini returned empty explanation",
                    cause=None
                )
            
            return self._parse_explanation_response(response.text, sql_query)
            
        except Exception as e:
            logger.error(f"Query explanation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language="",
                reason=f"Gemini explanation failed: {str(e)}",
                cause=e
            ) from e
    
    async def optimize_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationSuggestion]:
        """
        Generate optimization suggestions using Gemini.
        
        Args:
            sql_query: SQL query to optimize
            schema: Database schema information
            context: Additional context
            
        Returns:
            List[OptimizationSuggestion]: Optimization suggestions
        """
        try:
            prompt = self._build_optimization_prompt(sql_query, schema, context)
            
            config = genai.types.GenerationConfig(
                temperature=0.2,  # Lower temperature for consistent optimization advice
                max_output_tokens=self.max_tokens,
                candidate_count=1
            )
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            if not response.text:
                logger.warning("Gemini returned empty optimization response")
                return []
            
            return self._parse_optimization_response(response.text, sql_query)
            
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
        
        return f"""You are an expert SQL developer. Generate a SQL query for the following request:

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
}}

Important: Respond ONLY with the JSON object, no additional text."""
    
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
}}

Important: Respond ONLY with the JSON object, no additional text."""
    
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
]

Important: Respond ONLY with the JSON array, no additional text."""

    def _format_schema_info(self, schema: DatabaseSchema) -> str:
        """Format schema information for prompts."""
        if not schema:
            return "No schema information provided"

        # Format tables and columns
        schema_parts = []
        for table_name, table_info in schema.items():
            if isinstance(table_info, dict) and 'columns' in table_info:
                columns = table_info['columns']
                column_list = ", ".join([f"{col}: {info.get('type', 'unknown')}"
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
        """Parse Gemini's SQL generation response."""
        try:
            import json

            # Clean response text
            response_text = response_text.strip()

            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                # Fallback: treat entire response as SQL
                return SQLQuery(
                    sql=response_text.strip(),
                    natural_language=natural_query,
                    confidence=0.8,
                    metadata={"provider": "google", "model": self.model_name}
                )

            parsed = json.loads(json_text)

            return SQLQuery(
                sql=parsed.get("sql", "").strip(),
                natural_language=natural_query,
                confidence=float(parsed.get("confidence", 0.9)),
                explanation=parsed.get("explanation", ""),
                parameters=parsed.get("parameters", []),
                metadata={
                    "provider": "google",
                    "model": self.model_name,
                    "raw_response": response_text
                }
            )

        except Exception as e:
            logger.warning(f"Failed to parse Gemini response as JSON: {str(e)}")
            # Fallback to simple parsing
            return SQLQuery(
                sql=response_text.strip(),
                natural_language=natural_query,
                confidence=0.7,
                metadata={"provider": "google", "model": self.model_name, "parse_error": str(e)}
            )

    def _parse_explanation_response(self, response_text: str, sql_query: str) -> QueryExplanation:
        """Parse Gemini's explanation response."""
        try:
            import json

            # Clean response text
            response_text = response_text.strip()

            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                # Fallback: treat entire response as explanation
                return QueryExplanation(
                    sql_query=sql_query,
                    summary=response_text.strip(),
                    step_by_step=[response_text.strip()],
                    complexity="medium",
                    metadata={"provider": "google", "model": self.model_name}
                )

            parsed = json.loads(json_text)

            return QueryExplanation(
                sql_query=sql_query,
                summary=parsed.get("summary", ""),
                step_by_step=parsed.get("step_by_step", []),
                performance_notes=parsed.get("performance_notes", ""),
                complexity=parsed.get("complexity", "medium"),
                metadata={
                    "provider": "google",
                    "model": self.model_name,
                    "raw_response": response_text
                }
            )

        except Exception as e:
            logger.warning(f"Failed to parse Gemini explanation as JSON: {str(e)}")
            return QueryExplanation(
                sql_query=sql_query,
                summary=response_text.strip(),
                step_by_step=[response_text.strip()],
                complexity="medium",
                metadata={"provider": "google", "model": self.model_name, "parse_error": str(e)}
            )

    def _parse_optimization_response(self, response_text: str, sql_query: str) -> List[OptimizationSuggestion]:
        """Parse Gemini's optimization response."""
        try:
            import json

            # Clean response text
            response_text = response_text.strip()

            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "[" in response_text and "]" in response_text:
                json_start = response_text.find("[")
                json_end = response_text.rfind("]") + 1
                json_text = response_text[json_start:json_end]
            else:
                # Fallback: create basic suggestion
                return [OptimizationSuggestion(
                    type="general",
                    description="General optimization advice",
                    suggestion=response_text.strip(),
                    impact="medium",
                    effort="moderate",
                    metadata={"provider": "google", "model": self.model_name}
                )]

            parsed = json.loads(json_text)
            suggestions = []

            for item in parsed:
                suggestions.append(OptimizationSuggestion(
                    type=item.get("type", "general"),
                    description=item.get("description", ""),
                    suggestion=item.get("suggestion", ""),
                    impact=item.get("impact", "medium"),
                    effort=item.get("effort", "moderate"),
                    metadata={
                        "provider": "google",
                        "model": self.model_name,
                        "sql_query": sql_query
                    }
                ))

            return suggestions

        except Exception as e:
            logger.warning(f"Failed to parse Gemini optimization response: {str(e)}")
            return [OptimizationSuggestion(
                type="general",
                description="Optimization analysis",
                suggestion=response_text.strip(),
                impact="medium",
                effort="moderate",
                metadata={"provider": "google", "model": self.model_name, "parse_error": str(e)}
            )]
