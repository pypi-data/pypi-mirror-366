"""
HuggingFace provider for Text2SQL-LTM library.

This module provides integration with HuggingFace models for SQL generation,
supporting both API and local inference with production-grade error handling.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None
    torch = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

from .base import BaseLLMProvider
from ..config import AgentConfig
from ..types import (
    NaturalLanguageQuery, SQLQuery, QueryExplanation, 
    OptimizationSuggestion, DatabaseSchema, SQLDialect
)
from ..exceptions import QueryGenerationError, ConfigurationError

logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseLLMProvider):
    """
    HuggingFace provider for SQL generation and analysis.
    
    Supports both HuggingFace Inference API and local model inference
    with popular SQL-focused models like CodeT5, CodeLlama, etc.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize HuggingFace provider with configuration."""
        super().__init__(config)
        
        if not TRANSFORMERS_AVAILABLE:
            raise ConfigurationError(
                "Transformers library not installed. Install with: pip install transformers torch"
            )
        
        self.model_name = config.llm_model or "microsoft/DialoGPT-medium"
        self.max_tokens = config.llm_max_tokens or 2048
        self.temperature = config.llm_temperature or 0.1
        self.use_api = getattr(config, 'hf_use_api', True)  # Default to API
        
        # Model and tokenizer for local inference
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        # API settings
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.headers = {}
        
    async def _initialize_client(self) -> None:
        """Initialize the HuggingFace client."""
        try:
            if self.use_api:
                await self._initialize_api_client()
            else:
                await self._initialize_local_model()
                
            logger.info("HuggingFace client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace client: {str(e)}")
            raise ConfigurationError(f"HuggingFace initialization failed: {str(e)}") from e
    
    async def _initialize_api_client(self) -> None:
        """Initialize HuggingFace API client."""
        if not REQUESTS_AVAILABLE:
            raise ConfigurationError("Requests library required for HuggingFace API")
        
        api_key = self.config.llm_api_key
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        # Test API connection
        await self._test_api_connection()
    
    async def _initialize_local_model(self) -> None:
        """Initialize local HuggingFace model."""
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load local model: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up the HuggingFace client."""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        # Clear CUDA cache if available
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("HuggingFace client cleaned up")
    
    async def _test_api_connection(self) -> None:
        """Test the HuggingFace API connection."""
        try:
            payload = {
                "inputs": "Test connection",
                "parameters": {"max_new_tokens": 10}
            }
            
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.debug("HuggingFace API connection test successful")
            else:
                raise ConfigurationError(f"API test failed with status {response.status_code}")
                
        except Exception as e:
            raise ConfigurationError(f"HuggingFace API connection test failed: {str(e)}") from e
    
    async def generate_sql(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
        context: Optional[Dict[str, Any]] = None
    ) -> SQLQuery:
        """
        Generate SQL query from natural language using HuggingFace models.
        
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
            
            if self.use_api:
                response_text = await self._generate_with_api(prompt)
            else:
                response_text = await self._generate_with_local_model(prompt)
            
            return self._parse_sql_response(response_text, natural_query)
            
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language=natural_query,
                reason=f"HuggingFace SQL generation failed: {str(e)}",
                cause=e
            ) from e
    
    async def explain_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryExplanation:
        """
        Explain SQL query using HuggingFace models.
        
        Args:
            sql_query: SQL query to explain
            schema: Database schema information
            context: Additional context
            
        Returns:
            QueryExplanation: Detailed query explanation
        """
        try:
            prompt = self._build_explanation_prompt(sql_query, schema, context)
            
            if self.use_api:
                response_text = await self._generate_with_api(prompt)
            else:
                response_text = await self._generate_with_local_model(prompt)
            
            return self._parse_explanation_response(response_text, sql_query)
            
        except Exception as e:
            logger.error(f"Query explanation failed: {str(e)}")
            raise QueryGenerationError(
                natural_language="",
                reason=f"HuggingFace explanation failed: {str(e)}",
                cause=e
            ) from e
    
    async def optimize_query(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationSuggestion]:
        """
        Generate optimization suggestions using HuggingFace models.
        
        Args:
            sql_query: SQL query to optimize
            schema: Database schema information
            context: Additional context
            
        Returns:
            List[OptimizationSuggestion]: Optimization suggestions
        """
        try:
            prompt = self._build_optimization_prompt(sql_query, schema, context)
            
            if self.use_api:
                response_text = await self._generate_with_api(prompt)
            else:
                response_text = await self._generate_with_local_model(prompt)
            
            return self._parse_optimization_response(response_text, sql_query)
            
        except Exception as e:
            logger.error(f"Query optimization failed: {str(e)}")
            return []  # Return empty list on failure
    
    async def _generate_with_api(self, prompt: str) -> str:
        """Generate text using HuggingFace API."""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise QueryGenerationError(
                    natural_language="",
                    reason=f"HuggingFace API error: {response.status_code}",
                    cause=None
                )
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            elif isinstance(result, dict):
                return result.get("generated_text", "")
            else:
                raise QueryGenerationError(
                    natural_language="",
                    reason="Unexpected API response format",
                    cause=None
                )
                
        except Exception as e:
            raise QueryGenerationError(
                natural_language="",
                reason=f"HuggingFace API generation failed: {str(e)}",
                cause=e
            ) from e
    
    async def _generate_with_local_model(self, prompt: str) -> str:
        """Generate text using local HuggingFace model."""
        try:
            if not self.pipeline:
                raise QueryGenerationError(
                    natural_language="",
                    reason="Local model not initialized",
                    cause=None
                )
            
            # Generate response
            result = await asyncio.to_thread(
                self.pipeline,
                prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Remove the original prompt from the response
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                return generated_text
            else:
                raise QueryGenerationError(
                    natural_language="",
                    reason="No text generated by local model",
                    cause=None
                )
                
        except Exception as e:
            raise QueryGenerationError(
                natural_language="",
                reason=f"Local model generation failed: {str(e)}",
                cause=e
            ) from e

    def _build_sql_generation_prompt(
        self,
        natural_query: NaturalLanguageQuery,
        schema: DatabaseSchema,
        dialect: SQLDialect,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for SQL generation optimized for HuggingFace models."""
        schema_info = self._format_schema_info(schema)
        context_info = self._format_context_info(context) if context else ""

        # Use a more direct prompt format for HuggingFace models
        return f"""### Task: Generate SQL Query

Natural Language: {natural_query}
Database Schema: {schema_info}
SQL Dialect: {dialect.value}
{context_info}

### SQL Query:
"""

    def _build_explanation_prompt(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for query explanation."""
        schema_info = self._format_schema_info(schema)

        return f"""### Task: Explain SQL Query

SQL Query: {sql_query}
Database Schema: {schema_info}

### Explanation:
This SQL query """

    def _build_optimization_prompt(
        self,
        sql_query: SQLQuery,
        schema: DatabaseSchema,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for query optimization."""
        schema_info = self._format_schema_info(schema)

        return f"""### Task: Optimize SQL Query

SQL Query: {sql_query}
Database Schema: {schema_info}

### Optimization Suggestions:
1. """

    def _format_schema_info(self, schema: DatabaseSchema) -> str:
        """Format schema information for prompts."""
        if not schema:
            return "No schema provided"

        # Simplified format for HuggingFace models
        schema_parts = []
        for table_name, table_info in schema.items():
            if isinstance(table_info, dict) and 'columns' in table_info:
                columns = table_info['columns']
                column_list = ", ".join(columns.keys())
                schema_parts.append(f"{table_name}({column_list})")
            else:
                schema_parts.append(f"{table_name}")

        return ", ".join(schema_parts)

    def _format_context_info(self, context: Dict[str, Any]) -> str:
        """Format context information for prompts."""
        if not context:
            return ""

        context_parts = []
        for key, value in context.items():
            context_parts.append(f"{key}: {value}")

        return f"\nContext: " + ", ".join(context_parts)

    def _parse_sql_response(self, response_text: str, natural_query: str) -> SQLQuery:
        """Parse HuggingFace SQL generation response."""
        try:
            # Clean the response
            response_text = response_text.strip()

            # Extract SQL from response (look for common SQL keywords)
            sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH", "CREATE"]
            sql_lines = []

            for line in response_text.split('\n'):
                line = line.strip()
                if any(keyword in line.upper() for keyword in sql_keywords):
                    sql_lines.append(line)
                elif sql_lines and line and not line.startswith('#'):
                    sql_lines.append(line)
                elif sql_lines:
                    break  # Stop at first empty line after SQL

            sql = '\n'.join(sql_lines).strip()

            if not sql:
                # Fallback: use entire response
                sql = response_text

            return SQLQuery(
                sql=sql,
                natural_language=natural_query,
                confidence=0.8,  # Lower confidence for HuggingFace models
                metadata={
                    "provider": "huggingface",
                    "model": self.model_name,
                    "use_api": self.use_api,
                    "raw_response": response_text
                }
            )

        except Exception as e:
            logger.warning(f"Failed to parse HuggingFace response: {str(e)}")
            return SQLQuery(
                sql=response_text.strip(),
                natural_language=natural_query,
                confidence=0.6,
                metadata={
                    "provider": "huggingface",
                    "model": self.model_name,
                    "parse_error": str(e)
                }
            )

    def _parse_explanation_response(self, response_text: str, sql_query: str) -> QueryExplanation:
        """Parse HuggingFace explanation response."""
        try:
            # Clean the response
            response_text = response_text.strip()

            # Split into sentences for step-by-step
            sentences = [s.strip() for s in response_text.split('.') if s.strip()]

            # Extract summary (first sentence or paragraph)
            summary = sentences[0] if sentences else response_text

            return QueryExplanation(
                sql_query=sql_query,
                summary=summary,
                step_by_step=sentences[:5],  # Limit to first 5 steps
                complexity="medium",  # Default complexity
                metadata={
                    "provider": "huggingface",
                    "model": self.model_name,
                    "use_api": self.use_api,
                    "raw_response": response_text
                }
            )

        except Exception as e:
            logger.warning(f"Failed to parse HuggingFace explanation: {str(e)}")
            return QueryExplanation(
                sql_query=sql_query,
                summary=response_text.strip(),
                step_by_step=[response_text.strip()],
                complexity="medium",
                metadata={
                    "provider": "huggingface",
                    "model": self.model_name,
                    "parse_error": str(e)
                }
            )

    def _parse_optimization_response(self, response_text: str, sql_query: str) -> List[OptimizationSuggestion]:
        """Parse HuggingFace optimization response."""
        try:
            # Clean the response
            response_text = response_text.strip()

            # Split into suggestions (look for numbered lists or bullet points)
            suggestions = []
            lines = response_text.split('\n')

            current_suggestion = ""
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
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
                        "provider": "huggingface",
                        "model": self.model_name,
                        "sql_query": sql_query
                    }
                ))

            return optimization_suggestions

        except Exception as e:
            logger.warning(f"Failed to parse HuggingFace optimization response: {str(e)}")
            return [OptimizationSuggestion(
                type="general",
                description="Optimization analysis",
                suggestion=response_text.strip(),
                impact="medium",
                effort="moderate",
                metadata={
                    "provider": "huggingface",
                    "model": self.model_name,
                    "parse_error": str(e)
                }
            )]
