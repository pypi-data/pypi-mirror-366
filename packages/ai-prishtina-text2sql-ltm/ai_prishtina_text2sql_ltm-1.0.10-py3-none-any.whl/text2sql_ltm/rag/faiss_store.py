"""
FAISS vector store implementation for Text2SQL-LTM library.

This module provides integration with Facebook AI Similarity Search (FAISS)
for high-performance local vector similarity search and retrieval.
"""

from __future__ import annotations

import asyncio
import json
import logging
import pickle
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None
    np = None

from .vector_store import BaseVectorStore, VectorDocument, SearchResult, VectorStoreConfig
from ..types import DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class FAISSVectorStore(BaseVectorStore):
    """
    FAISS vector store implementation.
    
    Provides high-performance local vector similarity search using Facebook's
    FAISS library with support for various index types and optimization.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize FAISS vector store."""
        super().__init__(config)
        
        if not FAISS_AVAILABLE:
            raise VectorStoreError("FAISS library not installed. Install with: pip install faiss-cpu or faiss-gpu")
        
        self.dimension = config.dimension or 1536  # Default for OpenAI embeddings
        self.index_type = getattr(config, 'faiss_index_type', 'IndexFlatIP')  # Inner Product (cosine for normalized vectors)
        self.nlist = getattr(config, 'faiss_nlist', 100)  # Number of clusters for IVF indexes
        self.nprobe = getattr(config, 'faiss_nprobe', 10)  # Number of clusters to search
        
        # Storage paths
        self.storage_path = Path(getattr(config, 'storage_path', './faiss_storage'))
        self.index_file = self.storage_path / f"{config.collection_name}.index"
        self.metadata_file = self.storage_path / f"{config.collection_name}.metadata"
        
        # In-memory storage
        self.index: Optional[faiss.Index] = None
        self.id_to_index: Dict[str, int] = {}  # Map document IDs to FAISS index positions
        self.index_to_id: Dict[int, str] = {}  # Map FAISS index positions to document IDs
        self.metadata_store: Dict[str, Dict[str, Any]] = {}  # Store document metadata
        self.next_index = 0
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    async def _initialize_client(self) -> None:
        """Initialize FAISS index."""
        try:
            # Load existing index if available
            if self.index_file.exists() and self.metadata_file.exists():
                await self._load_index()
            else:
                await self._create_new_index()
            
            logger.info(f"FAISS vector store initialized: {self.index_type}, dimension={self.dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {str(e)}")
            raise VectorStoreError(f"FAISS initialization failed: {str(e)}") from e
    
    async def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        try:
            if self.index_type == "IndexFlatIP":
                # Flat index with inner product (good for cosine similarity with normalized vectors)
                self.index = faiss.IndexFlatIP(self.dimension)
            elif self.index_type == "IndexFlatL2":
                # Flat index with L2 distance
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "IndexIVFFlat":
                # IVF (Inverted File) index for faster search on large datasets
                quantizer = faiss.IndexFlatIP(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, self.nlist)
                self.index.nprobe = self.nprobe
            elif self.index_type == "IndexIVFPQ":
                # IVF with Product Quantization for memory efficiency
                quantizer = faiss.IndexFlatIP(self.dimension)
                m = 8  # Number of subquantizers
                bits = 8  # Number of bits per subquantizer
                self.index = faiss.IndexIVFPQ(quantizer, self.dimension, self.nlist, m, bits)
                self.index.nprobe = self.nprobe
            elif self.index_type == "IndexHNSW":
                # Hierarchical Navigable Small World for fast approximate search
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 is M parameter
                self.index.hnsw.efConstruction = 200
                self.index.hnsw.efSearch = 100
            else:
                raise VectorStoreError(f"Unsupported FAISS index type: {self.index_type}")
            
            logger.info(f"Created new FAISS index: {self.index_type}")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to create FAISS index: {str(e)}") from e
    
    async def _load_index(self) -> None:
        """Load existing FAISS index from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load metadata
            with open(self.metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.id_to_index = data['id_to_index']
                self.index_to_id = data['index_to_id']
                self.metadata_store = data['metadata_store']
                self.next_index = data['next_index']
            
            # Set nprobe for IVF indexes
            if hasattr(self.index, 'nprobe'):
                self.index.nprobe = self.nprobe
            
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to load FAISS index: {str(e)}") from e
    
    async def _save_index(self) -> None:
        """Save FAISS index to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            data = {
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id,
                'metadata_store': self.metadata_store,
                'next_index': self.next_index
            }
            
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug("FAISS index saved to disk")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
    
    async def _cleanup_client(self) -> None:
        """Clean up FAISS index."""
        if self.index:
            await self._save_index()
        self.index = None
        logger.info("FAISS client cleaned up")
    
    async def add_documents(
        self,
        documents: List[VectorDocument],
        batch_size: int = 1000
    ) -> bool:
        """
        Add documents to FAISS index.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.index:
                raise VectorStoreError("FAISS index not initialized")
            
            # Prepare vectors and metadata
            vectors = []
            doc_ids = []
            
            for doc in documents:
                # Skip if document already exists
                if str(doc.id) in self.id_to_index:
                    logger.warning(f"Document {doc.id} already exists, skipping")
                    continue
                
                vectors.append(doc.embedding)
                doc_ids.append(str(doc.id))
                
                # Store metadata
                self.metadata_store[str(doc.id)] = {
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if not vectors:
                logger.info("No new documents to add")
                return True
            
            # Convert to numpy array
            vectors_array = np.array(vectors, dtype=np.float32)
            
            # Normalize vectors for cosine similarity (if using IP index)
            if "IP" in self.index_type:
                faiss.normalize_L2(vectors_array)
            
            # Train index if needed (for IVF indexes)
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                if vectors_array.shape[0] >= self.nlist:
                    logger.info("Training FAISS index...")
                    self.index.train(vectors_array)
                else:
                    logger.warning(f"Not enough vectors to train index (need {self.nlist}, have {vectors_array.shape[0]})")
            
            # Add vectors to index
            start_idx = self.index.ntotal
            self.index.add(vectors_array)
            
            # Update ID mappings
            for i, doc_id in enumerate(doc_ids):
                faiss_idx = start_idx + i
                self.id_to_index[doc_id] = faiss_idx
                self.index_to_id[faiss_idx] = doc_id
            
            self.next_index = self.index.ntotal
            
            # Save index periodically
            if len(documents) > 100:
                await self._save_index()
            
            logger.info(f"Successfully added {len(doc_ids)} documents to FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to FAISS: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    async def search_similar(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[Score] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in FAISS.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filter_metadata: Metadata filters (applied post-search)
            min_score: Minimum similarity score
            
        Returns:
            List[SearchResult]: Search results
        """
        try:
            if not self.index:
                raise VectorStoreError("FAISS index not initialized")
            
            if self.index.ntotal == 0:
                logger.warning("FAISS index is empty")
                return []
            
            # Prepare query vector
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Normalize for cosine similarity (if using IP index)
            if "IP" in self.index_type:
                faiss.normalize_L2(query_array)
            
            # Search with extra results for filtering
            search_limit = min(limit * 3, self.index.ntotal)  # Get more results for filtering
            scores, indices = self.index.search(query_array, search_limit)
            
            # Process results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for invalid results
                    continue
                
                # Skip results below minimum score
                if min_score and score < min_score:
                    continue
                
                # Get document ID
                doc_id = self.index_to_id.get(idx)
                if not doc_id:
                    continue
                
                # Get metadata
                doc_data = self.metadata_store.get(doc_id, {})
                content = doc_data.get("content", "")
                metadata = doc_data.get("metadata", {})
                
                # Apply metadata filter
                if filter_metadata:
                    if not self._matches_filter(metadata, filter_metadata):
                        continue
                
                # Create VectorDocument
                document = VectorDocument(
                    id=doc_id,
                    content=content,
                    embedding=[],  # Don't include embedding in results
                    metadata=metadata
                )
                
                # Create SearchResult
                result = SearchResult(
                    document=document,
                    score=float(score),
                    rank=len(results) + 1
                )
                results.append(result)
                
                # Stop when we have enough results
                if len(results) >= limit:
                    break
            
            logger.debug(f"FAISS search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"FAISS search failed: {str(e)}")
            raise VectorStoreError(f"Search failed: {str(e)}") from e
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_metadata.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True

    async def get_document(self, document_id: DocumentID) -> Optional[VectorDocument]:
        """
        Get a specific document by ID.

        Args:
            document_id: Document identifier

        Returns:
            VectorDocument: Document if found, None otherwise
        """
        try:
            doc_id = str(document_id)

            if doc_id not in self.metadata_store:
                return None

            doc_data = self.metadata_store[doc_id]
            faiss_idx = self.id_to_index.get(doc_id)

            # Get embedding from FAISS index
            embedding = []
            if faiss_idx is not None and self.index:
                try:
                    # Reconstruct vector from index (if supported)
                    if hasattr(self.index, 'reconstruct'):
                        embedding = self.index.reconstruct(faiss_idx).tolist()
                except:
                    # Some index types don't support reconstruction
                    pass

            return VectorDocument(
                id=document_id,
                content=doc_data.get("content", ""),
                embedding=embedding,
                metadata=doc_data.get("metadata", {})
            )

        except Exception as e:
            logger.error(f"Failed to get document from FAISS: {str(e)}")
            raise VectorStoreError(f"Failed to get document: {str(e)}") from e

    async def delete_document(self, document_id: DocumentID) -> bool:
        """
        Delete a document by ID.

        Note: FAISS doesn't support efficient deletion. This marks the document
        as deleted in metadata but doesn't remove it from the index.

        Args:
            document_id: Document identifier

        Returns:
            bool: True if successful
        """
        try:
            doc_id = str(document_id)

            if doc_id not in self.metadata_store:
                logger.warning(f"Document {document_id} not found")
                return False

            # Remove from metadata store
            del self.metadata_store[doc_id]

            # Remove from ID mappings
            if doc_id in self.id_to_index:
                faiss_idx = self.id_to_index[doc_id]
                del self.id_to_index[doc_id]
                del self.index_to_id[faiss_idx]

            # Save changes
            await self._save_index()

            logger.debug(f"Deleted document {document_id} from FAISS metadata")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document from FAISS: {str(e)}")
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

        Note: FAISS doesn't support efficient updates. This updates metadata
        but requires re-adding the document for embedding changes.

        Args:
            document_id: Document identifier
            content: New content
            embedding: New embedding
            metadata: New metadata

        Returns:
            bool: True if successful
        """
        try:
            doc_id = str(document_id)

            if doc_id not in self.metadata_store:
                raise VectorStoreError(f"Document {document_id} not found")

            # Update metadata
            doc_data = self.metadata_store[doc_id]

            if content is not None:
                doc_data["content"] = content

            if metadata is not None:
                doc_data["metadata"].update(metadata)

            # If embedding is updated, we need to re-add the document
            if embedding is not None:
                # Create new document
                new_doc = VectorDocument(
                    id=document_id,
                    content=doc_data["content"],
                    embedding=embedding,
                    metadata=doc_data["metadata"]
                )

                # Delete old document
                await self.delete_document(document_id)

                # Add new document
                await self.add_documents([new_doc])
            else:
                # Just update metadata
                doc_data["timestamp"] = datetime.utcnow().isoformat()
                await self._save_index()

            logger.debug(f"Updated document {document_id} in FAISS")
            return True

        except Exception as e:
            logger.error(f"Failed to update document in FAISS: {str(e)}")
            raise VectorStoreError(f"Failed to update document: {str(e)}") from e

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            if not self.index:
                return {"error": "Index not initialized", "store_type": "faiss"}

            return {
                "total_vectors": self.index.ntotal,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "is_trained": getattr(self.index, 'is_trained', True),
                "metadata_count": len(self.metadata_store),
                "storage_path": str(self.storage_path),
                "store_type": "faiss"
            }

        except Exception as e:
            logger.error(f"Failed to get FAISS stats: {str(e)}")
            return {"error": str(e), "store_type": "faiss"}
