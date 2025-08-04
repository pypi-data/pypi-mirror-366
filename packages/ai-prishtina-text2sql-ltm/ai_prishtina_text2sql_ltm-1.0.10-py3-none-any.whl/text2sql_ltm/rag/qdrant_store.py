"""
Qdrant vector store implementation for Text2SQL-LTM library.

This module provides integration with Qdrant vector database for
high-performance vector similarity search with advanced filtering capabilities.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    models = None

from .vector_store import BaseVectorStore, VectorDocument, SearchResult, VectorStoreConfig
from ..types import DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class QdrantVectorStore(BaseVectorStore):
    """
    Qdrant vector store implementation.
    
    Provides high-performance vector similarity search using Qdrant's
    vector database with advanced filtering and payload capabilities.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize Qdrant vector store."""
        super().__init__(config)
        
        if not QDRANT_AVAILABLE:
            raise VectorStoreError("Qdrant client not installed. Install with: pip install qdrant-client")
        
        self.client: Optional[QdrantClient] = None
        self.collection_name = config.collection_name or "text2sql_vectors"
        self.dimension = config.dimension or 1536  # Default for OpenAI embeddings
        
        # Qdrant-specific settings
        self.host = getattr(config, 'qdrant_host', 'localhost')
        self.port = getattr(config, 'qdrant_port', 6333)
        self.grpc_port = getattr(config, 'qdrant_grpc_port', 6334)
        self.prefer_grpc = getattr(config, 'qdrant_prefer_grpc', False)
        self.api_key = getattr(config, 'api_key', None)
        self.url = getattr(config, 'qdrant_url', None)
        
        # Distance metric mapping
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot_product": Distance.DOT,
            "manhattan": Distance.MANHATTAN
        }
        self.distance = distance_map.get(
            config.distance_metric.value if config.distance_metric else "cosine",
            Distance.COSINE
        )
        
    async def _initialize_client(self) -> None:
        """Initialize Qdrant client and collection."""
        try:
            # Initialize client
            if self.url:
                # Cloud/remote instance
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    prefer_grpc=self.prefer_grpc
                )
            else:
                # Local instance
                self.client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    grpc_port=self.grpc_port,
                    prefer_grpc=self.prefer_grpc
                )
            
            # Check if collection exists, create if not
            collections = await asyncio.to_thread(self.client.get_collections)
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                await asyncio.to_thread(
                    self.client.create_collection,
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=self.distance
                    )
                )
            
            logger.info(f"Qdrant vector store initialized: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {str(e)}")
            raise VectorStoreError(f"Qdrant initialization failed: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up Qdrant client."""
        if self.client:
            # Qdrant client doesn't require explicit cleanup
            self.client = None
            logger.info("Qdrant client cleaned up")
    
    async def add_documents(
        self,
        documents: List[VectorDocument],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to Qdrant collection.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                raise VectorStoreError("Qdrant client not initialized")
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                points = []
                
                for doc in batch:
                    # Prepare point for Qdrant
                    point = PointStruct(
                        id=str(doc.id),
                        vector=doc.embedding,
                        payload={
                            "content": doc.content,
                            "timestamp": doc.metadata.get("timestamp", datetime.utcnow().isoformat()),
                            **doc.metadata
                        }
                    )
                    points.append(point)
                
                # Upsert batch to Qdrant
                await asyncio.to_thread(
                    self.client.upsert,
                    collection_name=self.collection_name,
                    points=points
                )
                logger.debug(f"Added batch of {len(batch)} documents to Qdrant")
            
            logger.info(f"Successfully added {len(documents)} documents to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Qdrant: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    async def search_similar(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[Score] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in Qdrant.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filter_metadata: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            List[SearchResult]: Search results
        """
        try:
            if not self.client:
                raise VectorStoreError("Qdrant client not initialized")
            
            # Prepare search parameters
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_vector,
                "limit": limit,
                "with_payload": True,
                "with_vectors": False
            }
            
            # Add metadata filter if provided
            if filter_metadata:
                conditions = []
                for key, value in filter_metadata.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                search_params["query_filter"] = Filter(must=conditions)
            
            # Add score threshold if provided
            if min_score:
                search_params["score_threshold"] = min_score
            
            # Execute search
            search_results = await asyncio.to_thread(
                self.client.search,
                **search_params
            )
            
            # Process results
            results = []
            for i, result in enumerate(search_results):
                # Extract payload
                payload = result.payload or {}
                content = payload.pop("content", "")
                
                # Create VectorDocument
                document = VectorDocument(
                    id=result.id,
                    content=content,
                    embedding=[],  # Don't include embedding in results
                    metadata=payload
                )
                
                # Create SearchResult
                search_result = SearchResult(
                    document=document,
                    score=result.score,
                    rank=i + 1
                )
                results.append(search_result)
            
            logger.debug(f"Qdrant search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Qdrant search failed: {str(e)}")
            raise VectorStoreError(f"Search failed: {str(e)}") from e
    
    async def get_document(self, document_id: DocumentID) -> Optional[VectorDocument]:
        """
        Get a specific document by ID.
        
        Args:
            document_id: Document identifier
            
        Returns:
            VectorDocument: Document if found, None otherwise
        """
        try:
            if not self.client:
                raise VectorStoreError("Qdrant client not initialized")
            
            # Retrieve document from Qdrant
            points = await asyncio.to_thread(
                self.client.retrieve,
                collection_name=self.collection_name,
                ids=[str(document_id)],
                with_payload=True,
                with_vectors=True
            )
            
            if not points:
                return None
            
            point = points[0]
            payload = point.payload or {}
            content = payload.pop("content", "")
            
            return VectorDocument(
                id=document_id,
                content=content,
                embedding=point.vector,
                metadata=payload
            )
            
        except Exception as e:
            logger.error(f"Failed to get document from Qdrant: {str(e)}")
            raise VectorStoreError(f"Failed to get document: {str(e)}") from e
    
    async def delete_document(self, document_id: DocumentID) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document identifier
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                raise VectorStoreError("Qdrant client not initialized")
            
            # Delete from Qdrant
            await asyncio.to_thread(
                self.client.delete,
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[str(document_id)]
                )
            )
            
            logger.debug(f"Deleted document {document_id} from Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from Qdrant: {str(e)}")
            raise VectorStoreError(f"Failed to delete document: {str(e)}") from e
    
    async def update_document(
        self,
        document_id: DocumentID,
        content: Optional[str] = None,
        embedding: Optional[EmbeddingVector] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a document.
        
        Args:
            document_id: Document identifier
            content: New content
            embedding: New embedding
            metadata: New metadata
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                raise VectorStoreError("Qdrant client not initialized")
            
            # Get existing document
            existing_doc = await self.get_document(document_id)
            if not existing_doc:
                raise VectorStoreError(f"Document {document_id} not found")
            
            # Prepare updated payload
            updated_payload = existing_doc.metadata.copy()
            if metadata:
                updated_payload.update(metadata)
            
            if content is not None:
                updated_payload["content"] = content
            else:
                updated_payload["content"] = existing_doc.content
            
            updated_payload["timestamp"] = datetime.utcnow().isoformat()
            
            # Prepare updated point
            point = PointStruct(
                id=str(document_id),
                vector=embedding or existing_doc.embedding,
                payload=updated_payload
            )
            
            # Upsert updated document
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"Updated document {document_id} in Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document in Qdrant: {str(e)}")
            raise VectorStoreError(f"Failed to update document: {str(e)}") from e
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            if not self.client:
                raise VectorStoreError("Qdrant client not initialized")
            
            # Get collection info
            collection_info = await asyncio.to_thread(
                self.client.get_collection,
                collection_name=self.collection_name
            )
            
            return {
                "total_vectors": collection_info.points_count,
                "dimension": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "indexed_vectors": collection_info.indexed_vectors_count,
                "collection_status": collection_info.status.value,
                "store_type": "qdrant",
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get Qdrant stats: {str(e)}")
            return {"error": str(e), "store_type": "qdrant"}
