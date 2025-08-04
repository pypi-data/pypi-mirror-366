"""
Embedding providers for RAG system.

This module provides various embedding providers with support for different
models and optimization strategies.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field

from ..types import EmbeddingVector
from ..exceptions import EmbeddingError, Text2SQLLTMError

logger = logging.getLogger(__name__)


class EmbeddingModel(str, Enum):
    """Supported embedding models."""
    # OpenAI models
    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    
    # HuggingFace models
    SENTENCE_TRANSFORMERS_ALL_MPNET = "sentence-transformers/all-mpnet-base-v2"
    SENTENCE_TRANSFORMERS_ALL_MINILM = "sentence-transformers/all-MiniLM-L6-v2"
    INSTRUCTOR_XL = "hkunlp/instructor-xl"
    
    # Cohere models
    COHERE_EMBED_ENGLISH = "embed-english-v3.0"
    COHERE_EMBED_MULTILINGUAL = "embed-multilingual-v3.0"


@dataclass
class EmbeddingConfig:
    """Configuration for embedding providers."""
    model: EmbeddingModel
    api_key: Optional[str] = None
    batch_size: int = 100
    max_retries: int = 3
    timeout: int = 30
    
    # Model-specific settings
    dimensions: Optional[int] = None
    instruction: Optional[str] = None  # For instructor models
    
    # Caching
    enable_cache: bool = True
    cache_ttl: int = 3600
    
    # Performance
    max_concurrent_requests: int = 10


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        self._client = None
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)
    
    async def initialize(self) -> None:
        """Initialize the embedding provider."""
        if self._initialized:
            return
        
        try:
            await self._initialize_client()
            self._initialized = True
            self.logger.info(f"Embedding provider {self.config.model} initialized")
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize embedding provider: {str(e)}") from e
    
    async def close(self) -> None:
        """Close the embedding provider."""
        if self._client:
            await self._cleanup_client()
            self._client = None
            self._initialized = False
    
    @abstractmethod
    async def _initialize_client(self) -> None:
        """Initialize the embedding client."""
        pass
    
    @abstractmethod
    async def _cleanup_client(self) -> None:
        """Clean up the embedding client."""
        pass
    
    @abstractmethod
    async def embed_text(self, text: str) -> EmbeddingVector:
        """Embed a single text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """Embed a batch of texts."""
        pass
    
    async def embed_documents(
        self, 
        documents: List[str],
        batch_size: Optional[int] = None
    ) -> List[EmbeddingVector]:
        """Embed multiple documents with batching."""
        batch_size = batch_size or self.config.batch_size
        all_embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            embeddings = await self.embed_batch(batch)
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        if self.config.dimensions:
            return self.config.dimensions
        
        # Default dimensions for known models
        dimension_map = {
            EmbeddingModel.OPENAI_ADA_002: 1536,
            EmbeddingModel.OPENAI_3_SMALL: 1536,
            EmbeddingModel.OPENAI_3_LARGE: 3072,
            EmbeddingModel.SENTENCE_TRANSFORMERS_ALL_MPNET: 768,
            EmbeddingModel.SENTENCE_TRANSFORMERS_ALL_MINILM: 384,
            EmbeddingModel.INSTRUCTOR_XL: 768,
            EmbeddingModel.COHERE_EMBED_ENGLISH: 1024,
            EmbeddingModel.COHERE_EMBED_MULTILINGUAL: 1024,
        }
        
        return dimension_map.get(self.config.model, 768)


class OpenAIEmbeddings(BaseEmbeddingProvider):
    """OpenAI embedding provider."""
    
    async def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai
            
            if not self.config.api_key:
                raise EmbeddingError("OpenAI API key is required")
            
            self._client = openai.AsyncOpenAI(api_key=self.config.api_key)
            
        except ImportError:
            raise EmbeddingError("OpenAI library not installed. Install with: pip install openai")
    
    async def _cleanup_client(self) -> None:
        """Clean up OpenAI client."""
        if self._client:
            await self._client.close()
    
    async def embed_text(self, text: str) -> EmbeddingVector:
        """Embed a single text using OpenAI."""
        async with self._semaphore:
            try:
                response = await self._client.embeddings.create(
                    model=self.config.model.value,
                    input=text,
                    dimensions=self.config.dimensions
                )
                
                return np.array(response.data[0].embedding, dtype=np.float32)
                
            except Exception as e:
                raise EmbeddingError(f"OpenAI embedding failed: {str(e)}") from e
    
    async def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """Embed a batch of texts using OpenAI."""
        async with self._semaphore:
            try:
                response = await self._client.embeddings.create(
                    model=self.config.model.value,
                    input=texts,
                    dimensions=self.config.dimensions
                )
                
                return [np.array(item.embedding, dtype=np.float32) for item in response.data]
                
            except Exception as e:
                raise EmbeddingError(f"OpenAI batch embedding failed: {str(e)}") from e


class HuggingFaceEmbeddings(BaseEmbeddingProvider):
    """HuggingFace embedding provider."""
    
    async def _initialize_client(self) -> None:
        """Initialize HuggingFace client."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load model
            model_name = self.config.model.value
            if model_name.startswith("sentence-transformers/"):
                model_name = model_name.replace("sentence-transformers/", "")
            
            self._client = SentenceTransformer(model_name)
            
        except ImportError:
            raise EmbeddingError("sentence-transformers not installed. Install with: pip install sentence-transformers")
    
    async def _cleanup_client(self) -> None:
        """Clean up HuggingFace client."""
        # No explicit cleanup needed
        pass
    
    async def embed_text(self, text: str) -> EmbeddingVector:
        """Embed a single text using HuggingFace."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self._client.encode, 
                text
            )
            
            return np.array(embedding, dtype=np.float32)
            
        except Exception as e:
            raise EmbeddingError(f"HuggingFace embedding failed: {str(e)}") from e
    
    async def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """Embed a batch of texts using HuggingFace."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self._client.encode,
                texts
            )
            
            return [np.array(emb, dtype=np.float32) for emb in embeddings]
            
        except Exception as e:
            raise EmbeddingError(f"HuggingFace batch embedding failed: {str(e)}") from e


class CohereEmbeddings(BaseEmbeddingProvider):
    """Cohere embedding provider."""
    
    async def _initialize_client(self) -> None:
        """Initialize Cohere client."""
        try:
            import cohere
            
            if not self.config.api_key:
                raise EmbeddingError("Cohere API key is required")
            
            self._client = cohere.AsyncClient(api_key=self.config.api_key)
            
        except ImportError:
            raise EmbeddingError("Cohere library not installed. Install with: pip install cohere")
    
    async def _cleanup_client(self) -> None:
        """Clean up Cohere client."""
        if self._client:
            await self._client.close()
    
    async def embed_text(self, text: str) -> EmbeddingVector:
        """Embed a single text using Cohere."""
        async with self._semaphore:
            try:
                response = await self._client.embed(
                    texts=[text],
                    model=self.config.model.value,
                    input_type="search_document"
                )
                
                return np.array(response.embeddings[0], dtype=np.float32)
                
            except Exception as e:
                raise EmbeddingError(f"Cohere embedding failed: {str(e)}") from e
    
    async def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """Embed a batch of texts using Cohere."""
        async with self._semaphore:
            try:
                response = await self._client.embed(
                    texts=texts,
                    model=self.config.model.value,
                    input_type="search_document"
                )
                
                return [np.array(emb, dtype=np.float32) for emb in response.embeddings]
                
            except Exception as e:
                raise EmbeddingError(f"Cohere batch embedding failed: {str(e)}") from e


class CachedEmbeddingProvider(BaseEmbeddingProvider):
    """Wrapper that adds caching to any embedding provider."""
    
    def __init__(self, provider: BaseEmbeddingProvider, cache_backend: Optional[Any] = None):
        super().__init__(provider.config)
        self.provider = provider
        self.cache = cache_backend or {}  # Simple dict cache if no backend provided
    
    async def _initialize_client(self) -> None:
        """Initialize the wrapped provider."""
        await self.provider.initialize()
    
    async def _cleanup_client(self) -> None:
        """Clean up the wrapped provider."""
        await self.provider.close()
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        import hashlib
        return f"embed:{self.config.model.value}:{hashlib.md5(text.encode()).hexdigest()}"
    
    async def embed_text(self, text: str) -> EmbeddingVector:
        """Embed text with caching."""
        if not self.config.enable_cache:
            return await self.provider.embed_text(text)
        
        cache_key = self._get_cache_key(text)
        
        # Try to get from cache
        if hasattr(self.cache, 'get'):
            cached = await self.cache.get(cache_key) if asyncio.iscoroutinefunction(self.cache.get) else self.cache.get(cache_key)
            if cached is not None:
                return np.array(cached, dtype=np.float32)
        elif cache_key in self.cache:
            return np.array(self.cache[cache_key], dtype=np.float32)
        
        # Generate embedding
        embedding = await self.provider.embed_text(text)
        
        # Store in cache
        if hasattr(self.cache, 'set'):
            if asyncio.iscoroutinefunction(self.cache.set):
                await self.cache.set(cache_key, embedding.tolist(), ttl=self.config.cache_ttl)
            else:
                self.cache.set(cache_key, embedding.tolist())
        else:
            self.cache[cache_key] = embedding.tolist()
        
        return embedding
    
    async def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """Embed batch with caching."""
        if not self.config.enable_cache:
            return await self.provider.embed_batch(texts)
        
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            
            cached = None
            if hasattr(self.cache, 'get'):
                cached = await self.cache.get(cache_key) if asyncio.iscoroutinefunction(self.cache.get) else self.cache.get(cache_key)
            elif cache_key in self.cache:
                cached = self.cache[cache_key]
            
            if cached is not None:
                embeddings.append(np.array(cached, dtype=np.float32))
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = await self.provider.embed_batch(uncached_texts)
            
            # Store in cache and update results
            for idx, embedding in zip(uncached_indices, new_embeddings):
                embeddings[idx] = embedding
                
                cache_key = self._get_cache_key(texts[idx])
                if hasattr(self.cache, 'set'):
                    if asyncio.iscoroutinefunction(self.cache.set):
                        await self.cache.set(cache_key, embedding.tolist(), ttl=self.config.cache_ttl)
                    else:
                        self.cache.set(cache_key, embedding.tolist())
                else:
                    self.cache[cache_key] = embedding.tolist()
        
        return embeddings


def create_embedding_provider(config: EmbeddingConfig) -> BaseEmbeddingProvider:
    """Create an embedding provider based on configuration."""
    
    if config.model.value.startswith("text-embedding"):
        provider = OpenAIEmbeddings(config)
    elif config.model.value.startswith("sentence-transformers") or config.model.value.startswith("hkunlp"):
        provider = HuggingFaceEmbeddings(config)
    elif config.model.value.startswith("embed-"):
        provider = CohereEmbeddings(config)
    else:
        raise EmbeddingError(f"Unsupported embedding model: {config.model}")
    
    # Wrap with caching if enabled
    if config.enable_cache:
        provider = CachedEmbeddingProvider(provider)
    
    return provider


# Alias for backward compatibility
EmbeddingProvider = BaseEmbeddingProvider
