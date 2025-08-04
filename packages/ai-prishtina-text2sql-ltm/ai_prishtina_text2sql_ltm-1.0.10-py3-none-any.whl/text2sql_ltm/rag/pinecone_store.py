"""
Pinecone vector store implementation for Text2SQL-LTM library.

This module provides integration with Pinecone vector database for
high-performance vector similarity search and retrieval.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

try:
    # Try new pinecone package first
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except (ImportError, Exception) as e:
    # Handle both import errors and the package rename error
    if "pinecone-client" in str(e) and "renamed" in str(e):
        # The old pinecone-client package is installed but deprecated
        PINECONE_AVAILABLE = False
        pinecone = None
        Pinecone = None
        ServerlessSpec = None
    else:
        # Regular import error - package not installed
        PINECONE_AVAILABLE = False
        pinecone = None
        Pinecone = None
        ServerlessSpec = None

from .vector_store import BaseVectorStore, VectorDocument, SearchResult, VectorStoreConfig
from ..types import DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class PineconeVectorStore(BaseVectorStore):
    """
    Pinecone vector store implementation.
    
    Provides high-performance vector similarity search using Pinecone's
    managed vector database service with automatic scaling and optimization.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize Pinecone vector store."""
        super().__init__(config)
        
        if not PINECONE_AVAILABLE:
            raise VectorStoreError(
                "Pinecone library not available. Install with: pip install pinecone\n"
                "Note: If you have 'pinecone-client' installed, please uninstall it first: "
                "pip uninstall pinecone-client && pip install pinecone"
            )
        
        self.client: Optional[Pinecone] = None
        self.index = None
        self.index_name = config.collection_name or "text2sql-vectors"
        self.dimension = config.dimension or 1536  # Default for OpenAI embeddings
        self.metric = config.distance_metric.value if config.distance_metric else "cosine"
        
        # Pinecone-specific settings
        self.environment = getattr(config, 'pinecone_environment', 'us-east-1-aws')
        self.cloud = getattr(config, 'pinecone_cloud', 'aws')
        self.region = getattr(config, 'pinecone_region', 'us-east-1')
        
    async def _initialize_client(self) -> None:
        """Initialize Pinecone client and index."""
        try:
            # Get API key from config
            api_key = getattr(self.config, 'api_key', None)
            if not api_key:
                raise VectorStoreError("Pinecone API key not provided in config")
            
            # Initialize Pinecone client
            self.client = Pinecone(api_key=api_key)
            
            # Check if index exists, create if not
            existing_indexes = self.client.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.region
                    )
                )
                
                # Wait for index to be ready
                await self._wait_for_index_ready()
            
            # Connect to index
            self.index = self.client.Index(self.index_name)
            
            logger.info(f"Pinecone vector store initialized: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise VectorStoreError(f"Pinecone initialization failed: {str(e)}") from e
    
    async def _wait_for_index_ready(self, timeout: int = 300) -> None:
        """Wait for Pinecone index to be ready."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                index_description = self.client.describe_index(self.index_name)
                if index_description.status.ready:
                    logger.info(f"Pinecone index {self.index_name} is ready")
                    return
                
                logger.info(f"Waiting for Pinecone index {self.index_name} to be ready...")
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.warning(f"Error checking index status: {str(e)}")
                await asyncio.sleep(5)
        
        raise VectorStoreError(f"Pinecone index {self.index_name} not ready after {timeout} seconds")
    
    async def _cleanup_client(self) -> None:
        """Clean up Pinecone client."""
        self.index = None
        self.client = None
        logger.info("Pinecone client cleaned up")
    
    async def add_documents(
        self,
        documents: List[VectorDocument],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to Pinecone index.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.index:
                raise VectorStoreError("Pinecone index not initialized")
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vectors = []
                
                for doc in batch:
                    # Prepare vector for Pinecone
                    vector_data = {
                        "id": str(doc.id),
                        "values": doc.embedding,
                        "metadata": {
                            "content": doc.content,
                            "source": doc.metadata.get("source", ""),
                            "timestamp": doc.metadata.get("timestamp", datetime.utcnow().isoformat()),
                            **doc.metadata
                        }
                    }
                    vectors.append(vector_data)
                
                # Upsert batch to Pinecone
                await asyncio.to_thread(self.index.upsert, vectors=vectors)
                logger.debug(f"Added batch of {len(batch)} documents to Pinecone")
            
            logger.info(f"Successfully added {len(documents)} documents to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Pinecone: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    async def search_similar(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[Score] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in Pinecone.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filter_metadata: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            List[SearchResult]: Search results
        """
        try:
            if not self.index:
                raise VectorStoreError("Pinecone index not initialized")
            
            # Prepare query parameters
            query_params = {
                "vector": query_vector,
                "top_k": limit,
                "include_metadata": True,
                "include_values": False
            }
            
            # Add metadata filter if provided
            if filter_metadata:
                query_params["filter"] = filter_metadata
            
            # Execute search
            response = await asyncio.to_thread(self.index.query, **query_params)
            
            # Process results
            results = []
            for i, match in enumerate(response.matches):
                # Skip results below minimum score
                if min_score and match.score < min_score:
                    continue
                
                # Extract metadata
                metadata = match.metadata or {}
                content = metadata.pop("content", "")
                
                # Create VectorDocument
                document = VectorDocument(
                    id=match.id,
                    content=content,
                    embedding=[],  # Don't include embedding in results
                    metadata=metadata
                )
                
                # Create SearchResult
                result = SearchResult(
                    document=document,
                    score=match.score,
                    rank=i + 1
                )
                results.append(result)
            
            logger.debug(f"Pinecone search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {str(e)}")
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
            if not self.index:
                raise VectorStoreError("Pinecone index not initialized")
            
            # Fetch document from Pinecone
            response = await asyncio.to_thread(
                self.index.fetch,
                ids=[str(document_id)]
            )
            
            if str(document_id) not in response.vectors:
                return None
            
            vector_data = response.vectors[str(document_id)]
            metadata = vector_data.metadata or {}
            content = metadata.pop("content", "")
            
            return VectorDocument(
                id=document_id,
                content=content,
                embedding=vector_data.values,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to get document from Pinecone: {str(e)}")
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
            if not self.index:
                raise VectorStoreError("Pinecone index not initialized")
            
            # Delete from Pinecone
            await asyncio.to_thread(
                self.index.delete,
                ids=[str(document_id)]
            )
            
            logger.debug(f"Deleted document {document_id} from Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from Pinecone: {str(e)}")
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
            if not self.index:
                raise VectorStoreError("Pinecone index not initialized")
            
            # Get existing document
            existing_doc = await self.get_document(document_id)
            if not existing_doc:
                raise VectorStoreError(f"Document {document_id} not found")
            
            # Prepare updated vector
            updated_metadata = existing_doc.metadata.copy()
            if metadata:
                updated_metadata.update(metadata)
            
            if content is not None:
                updated_metadata["content"] = content
            
            vector_data = {
                "id": str(document_id),
                "values": embedding or existing_doc.embedding,
                "metadata": updated_metadata
            }
            
            # Upsert updated document
            await asyncio.to_thread(self.index.upsert, vectors=[vector_data])
            
            logger.debug(f"Updated document {document_id} in Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document in Pinecone: {str(e)}")
            raise VectorStoreError(f"Failed to update document: {str(e)}") from e
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            if not self.index:
                raise VectorStoreError("Pinecone index not initialized")
            
            # Get index stats
            stats = await asyncio.to_thread(self.index.describe_index_stats)
            
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {},
                "store_type": "pinecone",
                "index_name": self.index_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {str(e)}")
            return {"error": str(e), "store_type": "pinecone"}
