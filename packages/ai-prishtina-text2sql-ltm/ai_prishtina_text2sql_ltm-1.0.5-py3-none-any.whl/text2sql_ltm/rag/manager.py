"""
RAG Manager - Central orchestrator for Retrieval-Augmented Generation.

This module provides the main RAG manager that coordinates all RAG components
for enhanced Text2SQL generation with semantic search and context augmentation.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from .vector_store import BaseVectorStore, VectorStoreConfig, VectorDocument, SearchResult, create_vector_store
from .embeddings import BaseEmbeddingProvider, EmbeddingConfig, create_embedding_provider
from .retriever import RAGRetriever, RetrievalStrategy
from .augmentor import ContextAugmentor, AugmentationStrategy
from .schema_rag import SchemaRAG
from .query_rag import QueryRAG
from .adaptive_rag import AdaptiveRAG

from ..types import UserID, DocumentID, EmbeddingVector, Score
from ..exceptions import RAGError, Text2SQLLTMError

logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """Configuration for RAG system."""
    
    # Vector store configuration
    vector_store: VectorStoreConfig
    
    # Embedding configuration
    embedding: EmbeddingConfig
    
    # Retrieval settings
    max_retrieved_docs: int = 10
    similarity_threshold: float = 0.7
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC
    
    # Augmentation settings
    augmentation_strategy: AugmentationStrategy = AugmentationStrategy.CONTEXTUAL
    max_context_length: int = 4000
    
    # Schema RAG settings
    enable_schema_rag: bool = True
    schema_weight: float = 0.3
    
    # Query RAG settings
    enable_query_rag: bool = True
    query_pattern_weight: float = 0.2
    
    # Adaptive RAG settings
    enable_adaptive_rag: bool = True
    learning_rate: float = 0.01
    
    # Performance settings
    enable_parallel_retrieval: bool = True
    cache_embeddings: bool = True
    
    # Quality settings
    enable_reranking: bool = True
    diversity_threshold: float = 0.8


class RAGManager:
    """
    Central RAG manager that orchestrates all RAG components.
    
    This class provides a unified interface for:
    - Document indexing and retrieval
    - Context augmentation for SQL generation
    - Schema-aware and query-pattern-aware retrieval
    - Adaptive learning and optimization
    """
    
    def __init__(self, config: RAGConfig):
        """Initialize RAG manager with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core components
        self.vector_store: Optional[BaseVectorStore] = None
        self.embedding_provider: Optional[BaseEmbeddingProvider] = None
        self.retriever: Optional[RAGRetriever] = None
        self.augmentor: Optional[ContextAugmentor] = None
        
        # Specialized RAG components
        self.schema_rag: Optional[SchemaRAG] = None
        self.query_rag: Optional[QueryRAG] = None
        self.adaptive_rag: Optional[AdaptiveRAG] = None
        
        # State
        self._initialized = False
        self._metrics = {
            "documents_indexed": 0,
            "queries_processed": 0,
            "retrievals_performed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_retrieval_time": 0.0,
            "average_augmentation_time": 0.0,
        }
    
    async def initialize(self) -> None:
        """Initialize all RAG components."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing RAG manager...")
            
            # Initialize vector store
            self.vector_store = create_vector_store(self.config.vector_store)
            await self.vector_store.initialize()
            
            # Initialize embedding provider
            self.embedding_provider = create_embedding_provider(self.config.embedding)
            await self.embedding_provider.initialize()
            
            # Initialize retriever
            self.retriever = RAGRetriever(
                vector_store=self.vector_store,
                embedding_provider=self.embedding_provider,
                strategy=self.config.retrieval_strategy,
                max_results=self.config.max_retrieved_docs,
                similarity_threshold=self.config.similarity_threshold
            )
            
            # Initialize augmentor
            self.augmentor = ContextAugmentor(
                strategy=self.config.augmentation_strategy,
                max_context_length=self.config.max_context_length
            )
            
            # Initialize specialized RAG components
            if self.config.enable_schema_rag:
                self.schema_rag = SchemaRAG(
                    vector_store=self.vector_store,
                    embedding_provider=self.embedding_provider,
                    weight=self.config.schema_weight
                )
                await self.schema_rag.initialize()
            
            if self.config.enable_query_rag:
                self.query_rag = QueryRAG(
                    vector_store=self.vector_store,
                    embedding_provider=self.embedding_provider,
                    weight=self.config.query_pattern_weight
                )
                await self.query_rag.initialize()
            
            if self.config.enable_adaptive_rag:
                self.adaptive_rag = AdaptiveRAG(
                    retriever=self.retriever,
                    learning_rate=self.config.learning_rate
                )
                await self.adaptive_rag.initialize()
            
            self._initialized = True
            self.logger.info("RAG manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG manager: {str(e)}")
            raise RAGError(f"RAG initialization failed: {str(e)}") from e
    
    async def close(self) -> None:
        """Close all RAG components."""
        if not self._initialized:
            return
        
        try:
            # Close components in reverse order
            if self.adaptive_rag:
                await self.adaptive_rag.close()
            
            if self.query_rag:
                await self.query_rag.close()
            
            if self.schema_rag:
                await self.schema_rag.close()
            
            if self.embedding_provider:
                await self.embedding_provider.close()
            
            if self.vector_store:
                await self.vector_store.close()
            
            self._initialized = False
            self.logger.info("RAG manager closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing RAG manager: {str(e)}")
    
    async def index_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        user_id: Optional[UserID] = None,
        document_type: str = "general"
    ) -> DocumentID:
        """Index a document for retrieval."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embedding
            embedding = await self.embedding_provider.embed_text(content)
            
            # Create document
            document_id = DocumentID(f"{document_type}_{datetime.utcnow().timestamp()}")
            document = VectorDocument(
                id=document_id,
                content=content,
                embedding=embedding,
                metadata={
                    **metadata,
                    "document_type": document_type,
                    "indexed_at": datetime.utcnow().isoformat()
                },
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            
            # Store in vector database
            await self.vector_store.add_documents([document])
            
            # Update specialized RAG components
            if self.schema_rag and document_type == "schema":
                await self.schema_rag.index_schema_document(document)
            
            if self.query_rag and document_type == "query_pattern":
                await self.query_rag.index_query_pattern(document)
            
            self._metrics["documents_indexed"] += 1
            self.logger.debug(f"Indexed document {document_id}")
            
            return document_id
            
        except Exception as e:
            self.logger.error(f"Failed to index document: {str(e)}")
            raise RAGError(f"Document indexing failed: {str(e)}") from e
    
    async def index_schema(
        self,
        schema_info: Dict[str, Any],
        database_name: str,
        user_id: Optional[UserID] = None
    ) -> List[DocumentID]:
        """Index database schema information."""
        if not self.schema_rag:
            raise RAGError("Schema RAG not enabled")
        
        return await self.schema_rag.index_schema(schema_info, database_name, user_id)
    
    async def index_query_patterns(
        self,
        patterns: List[Dict[str, Any]],
        user_id: Optional[UserID] = None
    ) -> List[DocumentID]:
        """Index query patterns for pattern-based retrieval."""
        if not self.query_rag:
            raise RAGError("Query RAG not enabled")
        
        return await self.query_rag.index_patterns(patterns, user_id)
    
    async def retrieve_context(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_schema: bool = True,
        include_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query.
        
        Returns comprehensive context including:
        - General documents
        - Schema information
        - Query patterns
        - Adaptive recommendations
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = datetime.utcnow()
        
        try:
            context = {
                "query": query,
                "user_id": user_id,
                "retrieved_at": start_time.isoformat(),
                "documents": [],
                "schema_context": {},
                "query_patterns": [],
                "adaptive_suggestions": {},
                "metadata": {}
            }
            
            # Parallel retrieval for performance
            tasks = []
            
            # General document retrieval
            tasks.append(self._retrieve_general_documents(query, user_id, filters))
            
            # Schema-specific retrieval
            if include_schema and self.schema_rag:
                tasks.append(self.schema_rag.retrieve_schema_context(query, user_id))
            
            # Query pattern retrieval
            if include_patterns and self.query_rag:
                tasks.append(self.query_rag.retrieve_patterns(query, user_id))
            
            # Adaptive retrieval
            if self.adaptive_rag:
                tasks.append(self.adaptive_rag.get_adaptive_suggestions(query, user_id))
            
            # Execute retrievals
            if self.config.enable_parallel_retrieval:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                results = []
                for task in tasks:
                    try:
                        result = await task
                        results.append(result)
                    except Exception as e:
                        results.append(e)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(f"Retrieval task {i} failed: {str(result)}")
                    continue
                
                if i == 0:  # General documents
                    context["documents"] = result
                elif i == 1 and include_schema:  # Schema context
                    context["schema_context"] = result
                elif i == 2 and include_patterns:  # Query patterns
                    context["query_patterns"] = result
                elif i == 3:  # Adaptive suggestions
                    context["adaptive_suggestions"] = result
            
            # Augment context
            augmented_context = await self.augmentor.augment_context(context)
            
            # Update metrics
            retrieval_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_retrieval_metrics(retrieval_time)
            
            self.logger.debug(f"Retrieved context for query in {retrieval_time:.3f}s")
            
            return augmented_context
            
        except Exception as e:
            self.logger.error(f"Context retrieval failed: {str(e)}")
            raise RAGError(f"Context retrieval failed: {str(e)}") from e
    
    async def _retrieve_general_documents(
        self,
        query: str,
        user_id: Optional[UserID],
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Retrieve general documents using the retriever."""
        search_results = await self.retriever.retrieve(
            query=query,
            user_id=user_id,
            filters=filters
        )
        
        return [
            {
                "content": result.document.content,
                "metadata": result.document.metadata,
                "score": float(result.score),
                "rank": result.rank
            }
            for result in search_results
        ]
    
    def _update_retrieval_metrics(self, retrieval_time: float) -> None:
        """Update retrieval metrics."""
        self._metrics["retrievals_performed"] += 1
        
        # Update average retrieval time
        current_avg = self._metrics["average_retrieval_time"]
        total_retrievals = self._metrics["retrievals_performed"]
        self._metrics["average_retrieval_time"] = (
            (current_avg * (total_retrievals - 1) + retrieval_time) / total_retrievals
        )
    
    async def get_similar_documents(
        self,
        document_id: DocumentID,
        limit: int = 5,
        user_id: Optional[UserID] = None
    ) -> List[SearchResult]:
        """Get documents similar to a given document."""
        if not self._initialized:
            await self.initialize()
        
        # Get the document
        document = await self.vector_store.get_document(document_id)
        if not document:
            raise RAGError(f"Document {document_id} not found")
        
        # Search for similar documents
        return await self.vector_store.search(
            query_vector=document.embedding,
            limit=limit + 1,  # +1 to exclude the original document
            user_id=user_id
        )[1:]  # Exclude the first result (original document)
    
    async def delete_documents(
        self,
        document_ids: List[DocumentID],
        user_id: Optional[UserID] = None
    ) -> int:
        """Delete documents from the vector store."""
        if not self._initialized:
            await self.initialize()
        
        return await self.vector_store.delete_documents(document_ids, user_id)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get RAG system metrics."""
        metrics = self._metrics.copy()
        
        # Add component metrics
        if self.vector_store:
            metrics["vector_store"] = "initialized"
        
        if self.embedding_provider:
            metrics["embedding_provider"] = self.config.embedding.model.value
        
        if self.schema_rag:
            schema_metrics = await self.schema_rag.get_metrics()
            metrics["schema_rag"] = schema_metrics
        
        if self.query_rag:
            query_metrics = await self.query_rag.get_metrics()
            metrics["query_rag"] = query_metrics
        
        if self.adaptive_rag:
            adaptive_metrics = await self.adaptive_rag.get_metrics()
            metrics["adaptive_rag"] = adaptive_metrics
        
        return metrics
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize RAG system performance."""
        optimization_results = {}
        
        # Optimize adaptive RAG
        if self.adaptive_rag:
            adaptive_results = await self.adaptive_rag.optimize()
            optimization_results["adaptive_rag"] = adaptive_results
        
        # Optimize vector store (if supported)
        # This could include index optimization, cleanup, etc.
        
        return optimization_results
