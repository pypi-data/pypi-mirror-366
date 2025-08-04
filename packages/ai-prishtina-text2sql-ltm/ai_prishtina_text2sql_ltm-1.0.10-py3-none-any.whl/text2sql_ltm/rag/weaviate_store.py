"""
Weaviate vector store implementation for Text2SQL-LTM library.

This module provides integration with Weaviate vector database for
semantic search with rich schema and GraphQL query capabilities.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

try:
    import weaviate
    from weaviate.client import Client
    from weaviate.gql import Query
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None
    Client = None
    Query = None

from .vector_store import BaseVectorStore, VectorDocument, SearchResult, VectorStoreConfig
from ..types import DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class WeaviateVectorStore(BaseVectorStore):
    """
    Weaviate vector store implementation.
    
    Provides semantic search using Weaviate's vector database with
    rich schema support, GraphQL queries, and automatic vectorization.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize Weaviate vector store."""
        super().__init__(config)
        
        if not WEAVIATE_AVAILABLE:
            raise VectorStoreError("Weaviate client not installed. Install with: pip install weaviate-client")
        
        self.client: Optional[Client] = None
        self.class_name = (config.collection_name or "Text2SQLDocument").title()
        self.dimension = config.dimension or 1536  # Default for OpenAI embeddings
        
        # Weaviate-specific settings
        self.url = getattr(config, 'weaviate_url', 'http://localhost:8080')
        self.api_key = getattr(config, 'api_key', None)
        self.openai_api_key = getattr(config, 'openai_api_key', None)
        self.use_openai_vectorizer = getattr(config, 'weaviate_use_openai', False)
        
        # Distance metric mapping
        distance_map = {
            "cosine": "cosine",
            "euclidean": "l2-squared", 
            "dot_product": "dot",
            "manhattan": "manhattan"
        }
        self.distance = distance_map.get(
            config.distance_metric.value if config.distance_metric else "cosine",
            "cosine"
        )
        
    async def _initialize_client(self) -> None:
        """Initialize Weaviate client and schema."""
        try:
            # Initialize client
            auth_config = None
            if self.api_key:
                auth_config = weaviate.AuthApiKey(api_key=self.api_key)
            
            additional_headers = {}
            if self.openai_api_key and self.use_openai_vectorizer:
                additional_headers["X-OpenAI-Api-Key"] = self.openai_api_key
            
            self.client = weaviate.Client(
                url=self.url,
                auth_client_secret=auth_config,
                additional_headers=additional_headers
            )
            
            # Check if client is ready
            if not await asyncio.to_thread(self.client.is_ready):
                raise VectorStoreError("Weaviate client is not ready")
            
            # Create schema if it doesn't exist
            await self._ensure_schema_exists()
            
            logger.info(f"Weaviate vector store initialized: {self.class_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {str(e)}")
            raise VectorStoreError(f"Weaviate initialization failed: {str(e)}") from e
    
    async def _ensure_schema_exists(self) -> None:
        """Ensure the schema class exists in Weaviate."""
        try:
            # Check if class exists
            schema = await asyncio.to_thread(self.client.schema.get)
            existing_classes = [cls["class"] for cls in schema.get("classes", [])]
            
            if self.class_name not in existing_classes:
                logger.info(f"Creating Weaviate class: {self.class_name}")
                
                # Define class schema
                class_schema = {
                    "class": self.class_name,
                    "description": "Text2SQL document storage",
                    "vectorizer": "text2vec-openai" if self.use_openai_vectorizer else "none",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "model": "ada",
                            "modelVersion": "002",
                            "type": "text"
                        }
                    } if self.use_openai_vectorizer else {},
                    "vectorIndexConfig": {
                        "distance": self.distance
                    },
                    "properties": [
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "Document content",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": False,
                                    "vectorizePropertyName": False
                                }
                            } if self.use_openai_vectorizer else {}
                        },
                        {
                            "name": "source",
                            "dataType": ["string"],
                            "description": "Document source"
                        },
                        {
                            "name": "timestamp",
                            "dataType": ["date"],
                            "description": "Document timestamp"
                        },
                        {
                            "name": "metadata",
                            "dataType": ["object"],
                            "description": "Additional metadata"
                        }
                    ]
                }
                
                await asyncio.to_thread(self.client.schema.create_class, class_schema)
                logger.info(f"Created Weaviate class: {self.class_name}")
        
        except Exception as e:
            raise VectorStoreError(f"Failed to ensure schema exists: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up Weaviate client."""
        if self.client:
            # Weaviate client doesn't require explicit cleanup
            self.client = None
            logger.info("Weaviate client cleaned up")
    
    async def add_documents(
        self,
        documents: List[VectorDocument],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to Weaviate.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                raise VectorStoreError("Weaviate client not initialized")
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Configure batch
                with self.client.batch as batch_client:
                    batch_client.batch_size = len(batch)
                    
                    for doc in batch:
                        # Prepare properties
                        properties = {
                            "content": doc.content,
                            "source": doc.metadata.get("source", ""),
                            "timestamp": doc.metadata.get("timestamp", datetime.utcnow().isoformat()),
                            "metadata": doc.metadata
                        }
                        
                        # Add object to batch
                        if self.use_openai_vectorizer:
                            # Let Weaviate generate the vector
                            batch_client.add_data_object(
                                data_object=properties,
                                class_name=self.class_name,
                                uuid=str(doc.id)
                            )
                        else:
                            # Provide our own vector
                            batch_client.add_data_object(
                                data_object=properties,
                                class_name=self.class_name,
                                uuid=str(doc.id),
                                vector=doc.embedding
                            )
                
                logger.debug(f"Added batch of {len(batch)} documents to Weaviate")
            
            logger.info(f"Successfully added {len(documents)} documents to Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Weaviate: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    async def search_similar(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[Score] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in Weaviate.
        
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
                raise VectorStoreError("Weaviate client not initialized")
            
            # Build GraphQL query
            query_builder = (
                self.client.query
                .get(self.class_name, ["content", "source", "timestamp", "metadata"])
                .with_near_vector({"vector": query_vector})
                .with_limit(limit)
                .with_additional(["id", "distance"])
            )
            
            # Add where filter if provided
            if filter_metadata:
                where_conditions = []
                for key, value in filter_metadata.items():
                    where_conditions.append({
                        "path": [key],
                        "operator": "Equal",
                        "valueString": str(value)
                    })
                
                if len(where_conditions) == 1:
                    query_builder = query_builder.with_where(where_conditions[0])
                else:
                    query_builder = query_builder.with_where({
                        "operator": "And",
                        "operands": where_conditions
                    })
            
            # Execute query
            result = await asyncio.to_thread(query_builder.do)
            
            if "errors" in result:
                raise VectorStoreError(f"Weaviate query error: {result['errors']}")
            
            # Process results
            results = []
            objects = result.get("data", {}).get("Get", {}).get(self.class_name, [])
            
            for i, obj in enumerate(objects):
                # Calculate score from distance (lower distance = higher score)
                distance = obj.get("_additional", {}).get("distance", 1.0)
                score = 1.0 - distance  # Convert distance to similarity score
                
                # Skip results below minimum score
                if min_score and score < min_score:
                    continue
                
                # Extract properties
                content = obj.get("content", "")
                metadata = obj.get("metadata", {})
                metadata.update({
                    "source": obj.get("source", ""),
                    "timestamp": obj.get("timestamp", "")
                })
                
                # Create VectorDocument
                document = VectorDocument(
                    id=obj.get("_additional", {}).get("id", ""),
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
            
            logger.debug(f"Weaviate search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Weaviate search failed: {str(e)}")
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
                raise VectorStoreError("Weaviate client not initialized")
            
            # Get object by UUID
            result = await asyncio.to_thread(
                self.client.data_object.get_by_id,
                str(document_id),
                class_name=self.class_name,
                with_vector=True
            )
            
            if not result:
                return None
            
            properties = result.get("properties", {})
            vector = result.get("vector", [])
            
            return VectorDocument(
                id=document_id,
                content=properties.get("content", ""),
                embedding=vector,
                metadata=properties.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to get document from Weaviate: {str(e)}")
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
                raise VectorStoreError("Weaviate client not initialized")
            
            # Delete object by UUID
            await asyncio.to_thread(
                self.client.data_object.delete,
                str(document_id),
                class_name=self.class_name
            )
            
            logger.debug(f"Deleted document {document_id} from Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from Weaviate: {str(e)}")
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
                raise VectorStoreError("Weaviate client not initialized")

            # Get existing document
            existing_doc = await self.get_document(document_id)
            if not existing_doc:
                raise VectorStoreError(f"Document {document_id} not found")

            # Prepare updated properties
            updated_properties = {
                "content": content if content is not None else existing_doc.content,
                "source": existing_doc.metadata.get("source", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": existing_doc.metadata.copy()
            }

            if metadata:
                updated_properties["metadata"].update(metadata)

            # Update object
            if embedding is not None and not self.use_openai_vectorizer:
                # Update with new vector
                await asyncio.to_thread(
                    self.client.data_object.replace,
                    data_object=updated_properties,
                    class_name=self.class_name,
                    uuid=str(document_id),
                    vector=embedding
                )
            else:
                # Update without vector (let Weaviate re-vectorize if using OpenAI)
                await asyncio.to_thread(
                    self.client.data_object.replace,
                    data_object=updated_properties,
                    class_name=self.class_name,
                    uuid=str(document_id)
                )

            logger.debug(f"Updated document {document_id} in Weaviate")
            return True

        except Exception as e:
            logger.error(f"Failed to update document in Weaviate: {str(e)}")
            raise VectorStoreError(f"Failed to update document: {str(e)}") from e

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            if not self.client:
                raise VectorStoreError("Weaviate client not initialized")

            # Get object count
            result = await asyncio.to_thread(
                self.client.query.aggregate(self.class_name).with_meta_count().do
            )

            count = 0
            if "data" in result and "Aggregate" in result["data"]:
                aggregate_data = result["data"]["Aggregate"].get(self.class_name, [])
                if aggregate_data:
                    count = aggregate_data[0].get("meta", {}).get("count", 0)

            # Get schema info
            schema = await asyncio.to_thread(self.client.schema.get)
            class_info = None
            for cls in schema.get("classes", []):
                if cls["class"] == self.class_name:
                    class_info = cls
                    break

            return {
                "total_vectors": count,
                "class_name": self.class_name,
                "vectorizer": class_info.get("vectorizer", "none") if class_info else "unknown",
                "distance_metric": self.distance,
                "store_type": "weaviate",
                "url": self.url
            }

        except Exception as e:
            logger.error(f"Failed to get Weaviate stats: {str(e)}")
            return {"error": str(e), "store_type": "weaviate"}
