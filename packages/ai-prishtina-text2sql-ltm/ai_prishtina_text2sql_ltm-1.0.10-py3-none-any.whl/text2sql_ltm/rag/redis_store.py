"""
Redis vector store implementation for Text2SQL-LTM library.

This module provides integration with Redis Stack for vector similarity search
using RediSearch with vector indexing capabilities.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import uuid

try:
    import redis
    from redis.commands.search.field import VectorField, TextField, NumericField
    from redis.commands.search.indexDefinition import IndexDefinition, IndexType
    from redis.commands.search.query import Query
    import numpy as np
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    np = None

from .vector_store import BaseVectorStore, VectorDocument, SearchResult, VectorStoreConfig
from ..types import DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class RedisVectorStore(BaseVectorStore):
    """
    Redis vector store implementation.
    
    Provides high-performance vector similarity search using Redis Stack
    with RediSearch vector indexing and real-time updates.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize Redis vector store."""
        super().__init__(config)
        
        if not REDIS_AVAILABLE:
            raise VectorStoreError("Redis library not installed. Install with: pip install redis numpy")
        
        self.client: Optional[redis.Redis] = None
        self.index_name = config.collection_name or "text2sql_vectors"
        self.dimension = config.dimension or 1536  # Default for OpenAI embeddings
        
        # Redis-specific settings
        self.host = getattr(config, 'redis_host', 'localhost')
        self.port = getattr(config, 'redis_port', 6379)
        self.password = getattr(config, 'redis_password', None)
        self.db = getattr(config, 'redis_db', 0)
        self.key_prefix = getattr(config, 'redis_key_prefix', 'doc:')
        
        # Distance metric mapping
        distance_map = {
            "cosine": "COSINE",
            "euclidean": "L2",
            "dot_product": "IP"  # Inner Product
        }
        self.distance_metric = distance_map.get(
            config.distance_metric.value if config.distance_metric else "cosine",
            "COSINE"
        )
        
    async def _initialize_client(self) -> None:
        """Initialize Redis client and index."""
        try:
            # Initialize Redis client
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True
            )
            
            # Test connection
            await asyncio.to_thread(self.client.ping)
            
            # Create index if it doesn't exist
            await self._ensure_index_exists()
            
            logger.info(f"Redis vector store initialized: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            raise VectorStoreError(f"Redis initialization failed: {str(e)}") from e
    
    async def _ensure_index_exists(self) -> None:
        """Ensure the vector index exists in Redis."""
        try:
            # Check if index exists
            try:
                await asyncio.to_thread(self.client.ft(self.index_name).info)
                logger.debug(f"Redis index {self.index_name} already exists")
                return
            except redis.ResponseError:
                # Index doesn't exist, create it
                pass
            
            logger.info(f"Creating Redis index: {self.index_name}")
            
            # Define index schema
            schema = [
                VectorField(
                    "embedding",
                    "HNSW",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": self.dimension,
                        "DISTANCE_METRIC": self.distance_metric,
                        "INITIAL_CAP": 1000,
                        "M": 16,
                        "EF_CONSTRUCTION": 200
                    }
                ),
                TextField("content"),
                TextField("source"),
                TextField("timestamp"),
                TextField("metadata")
            ]
            
            # Create index
            await asyncio.to_thread(
                self.client.ft(self.index_name).create_index,
                schema,
                definition=IndexDefinition(
                    prefix=[self.key_prefix],
                    index_type=IndexType.HASH
                )
            )
            
            logger.info(f"Created Redis index: {self.index_name}")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to ensure index exists: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up Redis client."""
        if self.client:
            await asyncio.to_thread(self.client.close)
            self.client = None
            logger.info("Redis client cleaned up")
    
    async def add_documents(
        self,
        documents: List[VectorDocument],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to Redis.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                raise VectorStoreError("Redis client not initialized")
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Use pipeline for batch operations
                pipe = self.client.pipeline()
                
                for doc in batch:
                    key = f"{self.key_prefix}{doc.id}"
                    
                    # Convert embedding to bytes
                    embedding_bytes = np.array(doc.embedding, dtype=np.float32).tobytes()
                    
                    # Prepare document data
                    doc_data = {
                        "embedding": embedding_bytes,
                        "content": doc.content,
                        "source": doc.metadata.get("source", ""),
                        "timestamp": doc.metadata.get("timestamp", datetime.now(timezone.utc).isoformat()),
                        "metadata": json.dumps(doc.metadata)
                    }
                    
                    # Add to pipeline
                    pipe.hset(key, mapping=doc_data)
                
                # Execute pipeline
                await asyncio.to_thread(pipe.execute)
                logger.debug(f"Added batch of {len(batch)} documents to Redis")
            
            logger.info(f"Successfully added {len(documents)} documents to Redis")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Redis: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    async def search_similar(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[Score] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in Redis.
        
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
                raise VectorStoreError("Redis client not initialized")
            
            # Convert query vector to bytes
            query_bytes = np.array(query_vector, dtype=np.float32).tobytes()
            
            # Build query
            base_query = f"*=>[KNN {limit} @embedding $query_vector AS score]"
            
            # Add metadata filters
            if filter_metadata:
                filter_parts = []
                for key, value in filter_metadata.items():
                    if key == "source":
                        filter_parts.append(f"@source:{value}")
                    else:
                        # For other metadata, search in the metadata JSON field
                        filter_parts.append(f"@metadata:*{key}*{value}*")
                
                if filter_parts:
                    filter_query = " ".join(filter_parts)
                    base_query = f"({filter_query})=>[KNN {limit} @embedding $query_vector AS score]"
            
            # Create query object
            query = Query(base_query).return_fields("content", "source", "timestamp", "metadata", "score").sort_by("score").paging(0, limit)
            
            # Execute search
            result = await asyncio.to_thread(
                self.client.ft(self.index_name).search,
                query,
                query_params={"query_vector": query_bytes}
            )
            
            # Process results
            results = []
            for i, doc in enumerate(result.docs):
                # Extract score (Redis returns distance, convert to similarity)
                distance = float(doc.score) if hasattr(doc, 'score') else 1.0
                
                # Convert distance to similarity score based on metric
                if self.distance_metric == "COSINE":
                    score = 1.0 - distance
                elif self.distance_metric == "L2":
                    score = 1.0 / (1.0 + distance)
                else:  # IP (Inner Product)
                    score = distance
                
                # Skip results below minimum score
                if min_score and score < min_score:
                    continue
                
                # Extract document data
                content = getattr(doc, 'content', '')
                source = getattr(doc, 'source', '')
                timestamp = getattr(doc, 'timestamp', '')
                metadata_str = getattr(doc, 'metadata', '{}')
                
                try:
                    metadata = json.loads(metadata_str)
                except:
                    metadata = {}
                
                metadata.update({
                    "source": source,
                    "timestamp": timestamp
                })
                
                # Extract document ID from Redis key
                doc_id = doc.id.replace(self.key_prefix, "") if hasattr(doc, 'id') else str(i)
                
                # Create VectorDocument
                document = VectorDocument(
                    id=doc_id,
                    content=content,
                    embedding=[],  # Don't include embedding in results
                    metadata=metadata
                )
                
                # Create SearchResult
                search_result = SearchResult(
                    document=document,
                    score=score,
                    rank=i + 1
                )
                results.append(search_result)
            
            logger.debug(f"Redis search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Redis search failed: {str(e)}")
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
                raise VectorStoreError("Redis client not initialized")
            
            key = f"{self.key_prefix}{document_id}"
            
            # Get document data
            doc_data = await asyncio.to_thread(self.client.hgetall, key)
            
            if not doc_data:
                return None
            
            # Parse metadata
            try:
                metadata = json.loads(doc_data.get('metadata', '{}'))
            except:
                metadata = {}
            
            # Convert embedding bytes back to list
            embedding = []
            if 'embedding' in doc_data:
                try:
                    embedding = np.frombuffer(doc_data['embedding'], dtype=np.float32).tolist()
                except:
                    pass
            
            return VectorDocument(
                id=document_id,
                content=doc_data.get('content', ''),
                embedding=embedding,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to get document from Redis: {str(e)}")
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
                raise VectorStoreError("Redis client not initialized")

            key = f"{self.key_prefix}{document_id}"

            # Delete document
            result = await asyncio.to_thread(self.client.delete, key)

            if result == 0:
                logger.warning(f"Document {document_id} not found for deletion")
                return False

            logger.debug(f"Deleted document {document_id} from Redis")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document from Redis: {str(e)}")
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
                raise VectorStoreError("Redis client not initialized")

            key = f"{self.key_prefix}{document_id}"

            # Get existing document
            existing_data = await asyncio.to_thread(self.client.hgetall, key)
            if not existing_data:
                raise VectorStoreError(f"Document {document_id} not found")

            # Prepare updated data
            updated_data = {}

            if content is not None:
                updated_data["content"] = content

            if embedding is not None:
                updated_data["embedding"] = np.array(embedding, dtype=np.float32).tobytes()

            if metadata is not None:
                # Merge with existing metadata
                try:
                    existing_metadata = json.loads(existing_data.get('metadata', '{}'))
                except:
                    existing_metadata = {}

                existing_metadata.update(metadata)
                updated_data["metadata"] = json.dumps(existing_metadata)

            # Update timestamp
            updated_data["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Update document
            await asyncio.to_thread(self.client.hset, key, mapping=updated_data)

            logger.debug(f"Updated document {document_id} in Redis")
            return True

        except Exception as e:
            logger.error(f"Failed to update document in Redis: {str(e)}")
            raise VectorStoreError(f"Failed to update document: {str(e)}") from e

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            if not self.client:
                raise VectorStoreError("Redis client not initialized")

            # Get index info
            index_info = await asyncio.to_thread(self.client.ft(self.index_name).info)

            # Count documents
            doc_count = 0
            try:
                # Count keys with our prefix
                keys = await asyncio.to_thread(self.client.keys, f"{self.key_prefix}*")
                doc_count = len(keys)
            except:
                pass

            return {
                "total_vectors": doc_count,
                "index_name": self.index_name,
                "dimension": self.dimension,
                "distance_metric": self.distance_metric,
                "key_prefix": self.key_prefix,
                "index_info": dict(index_info) if index_info else {},
                "store_type": "redis",
                "host": self.host,
                "port": self.port,
                "db": self.db
            }

        except Exception as e:
            logger.error(f"Failed to get Redis stats: {str(e)}")
            return {"error": str(e), "store_type": "redis"}
