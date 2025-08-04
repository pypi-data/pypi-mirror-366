"""
LLM provider factory for Text2SQL-LTM library.

This module provides factory functions to create LLM providers based on
configuration with proper error handling and validation.
"""

from __future__ import annotations

import logging
from typing import Type

from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from ..config import AgentConfig
from ..types import LLMProvider as LLMProviderEnum
from ..exceptions import QueryGenerationError

logger = logging.getLogger(__name__)


def create_llm_provider(config: AgentConfig) -> BaseLLMProvider:
    """
    Create an LLM provider based on configuration.
    
    Args:
        config: Agent configuration with LLM settings
        
    Returns:
        BaseLLMProvider: Configured LLM provider instance
        
    Raises:
        QueryGenerationError: When provider creation fails
    """
    try:
        provider_class = _get_provider_class(config.llm_provider)
        return provider_class(config)
        
    except Exception as e:
        logger.error(f"Failed to create LLM provider: {str(e)}")
        raise QueryGenerationError(
            natural_language="",
            reason=f"LLM provider creation failed: {str(e)}",
            cause=e
        ) from e


def _get_provider_class(provider_type: LLMProviderEnum) -> Type[BaseLLMProvider]:
    """Get the provider class for the specified type."""
    
    provider_map = {
        LLMProviderEnum.OPENAI: OpenAIProvider,
        LLMProviderEnum.AZURE_OPENAI: OpenAIProvider,  # Uses same implementation
        # Add other providers as they are implemented
        # LLMProviderEnum.ANTHROPIC: AnthropicProvider,
        # LLMProviderEnum.GOOGLE: GoogleProvider,
        # LLMProviderEnum.HUGGINGFACE: HuggingFaceProvider,
        # LLMProviderEnum.LOCAL: LocalProvider,
    }
    
    if provider_type not in provider_map:
        raise ValueError(f"Unsupported LLM provider: {provider_type}")
    
    return provider_map[provider_type]


# Placeholder for Anthropic provider
class AnthropicProvider(BaseLLMProvider):
    """Placeholder Anthropic provider - to be implemented."""
    
    async def _initialize_client(self) -> None:
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    async def _cleanup_client(self) -> None:
        pass
    
    async def generate_sql(self, *args, **kwargs):
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    async def explain_query(self, *args, **kwargs):
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    async def optimize_query(self, *args, **kwargs):
        raise NotImplementedError("Anthropic provider not yet implemented")
