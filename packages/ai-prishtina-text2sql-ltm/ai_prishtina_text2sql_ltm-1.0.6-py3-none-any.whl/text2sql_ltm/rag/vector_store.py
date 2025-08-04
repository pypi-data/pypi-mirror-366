"""
Vector database integration for RAG capabilities.

This module provides comprehensive vector storage solutions with support for
multiple vector databases and advanced search capabilities.
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field

from ..types import UserID, DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError, Text2SQLLTMError

logger = logging.getLogger(__name__)


class VectorStoreType(str, Enum):
    """Supported vector database types."""
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    FAISS = "faiss"
    REDIS = "redis"
    PGVECTOR = "pgvector"


class DistanceMetric(str, Enum):
    """Distance metrics for vector similarity."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


@dataclass
class VectorDocument:
    """Document with vector embedding and metadata."""
    id: DocumentID
    content: str
    embedding: EmbeddingVector
    metadata: Dict[str, Any]
    user_id: Optional[UserID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """Vector search result with similarity score."""
    document: VectorDocument
    score: Score
    rank: int


class VectorStoreConfig(BaseModel):
    """Configuration for vector store."""
    
    store_type: VectorStoreType = VectorStoreType.CHROMA
    connection_string: Optional[str] = None
    collection_name: str = "text2sql_vectors"
    dimension: int = 1536  # OpenAI embedding dimension
    distance_metric: DistanceMetric = DistanceMetric.COSINE
    
    # Performance settings
    max_connections: int = 10
    timeout_seconds: int = 30
    batch_size: int = 100
    
    # Index settings
    index_type: str = "HNSW"
    ef_construction: int = 200
    m: int = 16
    
    # Security
    api_key: Optional[str] = None
    environment: Optional[str] = None
    
    # Caching
    enable_cache: bool = True
    cache_ttl: int = 3600
    
    class Config:
        use_enum_values = True


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""
    
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        self._client = None
    
    async def initialize(self) -> None:
        """Initialize the vector store."""
        if self._initialized:
            return
        
        try:
            await self._initialize_client()
            await self._create_collection_if_not_exists()
            self._initialized = True
            self.logger.info(f"Vector store {self.config.store_type} initialized")
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize vector store: {str(e)}") from e
    
    async def close(self) -> None:
        """Close the vector store connection."""
        if self._client:
            await self._cleanup_client()
            self._client = None
            self._initialized = False
    
    @abstractmethod
    async def _initialize_client(self) -> None:
        """Initialize the vector database client."""
        pass
    
    @abstractmethod
    async def _cleanup_client(self) -> None:
        """Clean up the vector database client."""
        pass
    
    @abstractmethod
    async def _create_collection_if_not_exists(self) -> None:
        """Create collection if it doesn't exist."""
        pass
    
    @abstractmethod
    async def add_documents(
        self, 
        documents: List[VectorDocument],
        batch_size: Optional[int] = None
    ) -> List[DocumentID]:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[UserID] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: DocumentID) -> Optional[VectorDocument]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def delete_documents(
        self, 
        document_ids: List[DocumentID],
        user_id: Optional[UserID] = None
    ) -> int:
        """Delete documents by IDs."""
        pass
    
    @abstractmethod
    async def update_document(
        self, 
        document_id: DocumentID, 
        document: VectorDocument
    ) -> bool:
        """Update a document."""
        pass


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""
    
    async def _initialize_client(self) -> None:
        """Initialize ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            if self.config.connection_string:
                # Remote ChromaDB
                self._client = chromadb.HttpClient(
                    host=self.config.connection_string.split("://")[1].split(":")[0],
                    port=int(self.config.connection_string.split(":")[-1]),
                    settings=Settings(
                        chroma_client_auth_provider="chromadb.auth.basic.BasicAuthClientProvider",
                        chroma_client_auth_credentials=self.config.api_key
                    ) if self.config.api_key else None
                )
            else:
                # Local ChromaDB
                self._client = chromadb.Client()
                
        except ImportError:
            raise VectorStoreError("ChromaDB not installed. Install with: pip install chromadb")
    
    async def _cleanup_client(self) -> None:
        """Clean up ChromaDB client."""
        # ChromaDB doesn't require explicit cleanup
        pass
    
    async def _create_collection_if_not_exists(self) -> None:
        """Create ChromaDB collection."""
        try:
            self._collection = self._client.get_or_create_collection(
                name=self.config.collection_name,
                metadata={
                    "dimension": self.config.dimension,
                    "distance_metric": self.config.distance_metric.value
                }
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to create collection: {str(e)}") from e
    
    async def add_documents(
        self, 
        documents: List[VectorDocument],
        batch_size: Optional[int] = None
    ) -> List[DocumentID]:
        """Add documents to ChromaDB."""
        batch_size = batch_size or self.config.batch_size
        added_ids = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            ids = [doc.id for doc in batch]
            embeddings = [doc.embedding.tolist() if isinstance(doc.embedding, np.ndarray) 
                         else doc.embedding for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            documents_text = [doc.content for doc in batch]
            
            try:
                self._collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents_text
                )
                added_ids.extend(ids)
            except Exception as e:
                self.logger.error(f"Failed to add batch: {str(e)}")
                raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
        
        return added_ids
    
    async def search(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[UserID] = None
    ) -> List[SearchResult]:
        """Search ChromaDB for similar vectors."""
        try:
            # Add user filter if specified
            where_clause = filters or {}
            if user_id:
                where_clause["user_id"] = user_id
            
            query_embedding = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
            
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            search_results = []
            for i, (doc_id, distance, metadata, document) in enumerate(zip(
                results["ids"][0],
                results["distances"][0], 
                results["metadatas"][0],
                results["documents"][0]
            )):
                # Convert distance to similarity score
                score = 1.0 - distance if self.config.distance_metric == DistanceMetric.COSINE else distance
                
                vector_doc = VectorDocument(
                    id=DocumentID(doc_id),
                    content=document,
                    embedding=np.array([]),  # Not returned by ChromaDB query
                    metadata=metadata,
                    user_id=UserID(metadata.get("user_id")) if metadata.get("user_id") else None
                )
                
                search_results.append(SearchResult(
                    document=vector_doc,
                    score=Score(score),
                    rank=i + 1
                ))
            
            return search_results
            
        except Exception as e:
            raise VectorStoreError(f"Search failed: {str(e)}") from e
    
    async def get_document(self, document_id: DocumentID) -> Optional[VectorDocument]:
        """Get document from ChromaDB."""
        try:
            results = self._collection.get(ids=[document_id])
            
            if not results["ids"]:
                return None
            
            return VectorDocument(
                id=DocumentID(results["ids"][0]),
                content=results["documents"][0],
                embedding=np.array(results["embeddings"][0]) if results["embeddings"] else np.array([]),
                metadata=results["metadatas"][0],
                user_id=UserID(results["metadatas"][0].get("user_id")) if results["metadatas"][0].get("user_id") else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {str(e)}")
            return None
    
    async def delete_documents(
        self, 
        document_ids: List[DocumentID],
        user_id: Optional[UserID] = None
    ) -> int:
        """Delete documents from ChromaDB."""
        try:
            where_clause = {"user_id": user_id} if user_id else None
            
            self._collection.delete(
                ids=document_ids,
                where=where_clause
            )
            
            return len(document_ids)
            
        except Exception as e:
            self.logger.error(f"Failed to delete documents: {str(e)}")
            return 0
    
    async def update_document(
        self, 
        document_id: DocumentID, 
        document: VectorDocument
    ) -> bool:
        """Update document in ChromaDB."""
        try:
            embedding = document.embedding.tolist() if isinstance(document.embedding, np.ndarray) else document.embedding
            
            self._collection.update(
                ids=[document_id],
                embeddings=[embedding],
                metadatas=[document.metadata],
                documents=[document.content]
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update document {document_id}: {str(e)}")
            return False


# Factory function for vector stores
def create_vector_store(config: VectorStoreConfig) -> BaseVectorStore:
    """Create a vector store based on configuration."""
    
    store_map = {
        VectorStoreType.CHROMA: ChromaVectorStore,
        # Add other implementations as needed
        # VectorStoreType.PINECONE: PineconeVectorStore,
        # VectorStoreType.WEAVIATE: WeaviateVectorStore,
        # VectorStoreType.QDRANT: QdrantVectorStore,
    }
    
    if config.store_type not in store_map:
        raise VectorStoreError(f"Unsupported vector store type: {config.store_type}")
    
    return store_map[config.store_type](config)


# Alias for backward compatibility
VectorStore = BaseVectorStore
