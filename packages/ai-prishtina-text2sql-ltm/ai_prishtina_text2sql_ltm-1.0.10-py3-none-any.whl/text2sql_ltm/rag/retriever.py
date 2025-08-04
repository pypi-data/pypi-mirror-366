"""
RAG Retriever - Advanced retrieval strategies for context augmentation.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

import numpy as np

from .vector_store import BaseVectorStore, SearchResult
from .embeddings import BaseEmbeddingProvider
from ..types import UserID, EmbeddingVector, Score
from ..exceptions import RAGError

logger = logging.getLogger(__name__)


class RetrievalStrategy(str, Enum):
    """Retrieval strategies for RAG."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"
    CONTEXTUAL = "contextual"
    ADAPTIVE = "adaptive"


@dataclass
class RetrievalConfig:
    """Configuration for retrieval."""
    strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC
    max_results: int = 10
    similarity_threshold: float = 0.7
    enable_reranking: bool = True
    diversity_threshold: float = 0.8
    keyword_weight: float = 0.3
    semantic_weight: float = 0.7


class BaseRetriever(ABC):
    """Abstract base class for retrievers."""
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Retrieve relevant documents."""
        pass


class SemanticRetriever(BaseRetriever):
    """Semantic retrieval using vector similarity."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        similarity_threshold: float = 0.7
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.similarity_threshold = similarity_threshold
    
    async def retrieve(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Retrieve documents using semantic similarity."""
        # Generate query embedding
        query_embedding = await self.embedding_provider.embed_text(query)
        
        # Search vector store
        results = await self.vector_store.search(
            query_vector=query_embedding,
            limit=limit,
            filters=filters,
            user_id=user_id
        )
        
        # Filter by similarity threshold
        filtered_results = [
            result for result in results
            if result.score >= self.similarity_threshold
        ]
        
        return filtered_results


class HybridRetriever(BaseRetriever):
    """Hybrid retrieval combining semantic and keyword search."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.semantic_retriever = SemanticRetriever(vector_store, embedding_provider)
    
    async def retrieve(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Retrieve using hybrid semantic + keyword approach."""
        # Get semantic results
        semantic_results = await self.semantic_retriever.retrieve(
            query, user_id, filters, limit * 2  # Get more for reranking
        )
        
        # Get keyword scores
        keyword_scores = await self._get_keyword_scores(query, semantic_results)
        
        # Combine scores
        combined_results = []
        for result in semantic_results:
            doc_id = result.document.id
            semantic_score = float(result.score)
            keyword_score = keyword_scores.get(doc_id, 0.0)
            
            combined_score = (
                self.semantic_weight * semantic_score +
                self.keyword_weight * keyword_score
            )
            
            # Create new result with combined score
            combined_result = SearchResult(
                document=result.document,
                score=Score(combined_score),
                rank=result.rank
            )
            combined_results.append(combined_result)
        
        # Sort by combined score and return top results
        combined_results.sort(key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(combined_results[:limit]):
            result.rank = i + 1
        
        return combined_results[:limit]
    
    async def _get_keyword_scores(
        self,
        query: str,
        results: List[SearchResult]
    ) -> Dict[str, float]:
        """Calculate keyword-based scores for documents."""
        query_terms = set(query.lower().split())
        scores = {}
        
        for result in results:
            doc_terms = set(result.document.content.lower().split())
            
            # Calculate term overlap
            overlap = len(query_terms.intersection(doc_terms))
            total_terms = len(query_terms)
            
            if total_terms > 0:
                scores[result.document.id] = overlap / total_terms
            else:
                scores[result.document.id] = 0.0
        
        return scores


class ContextualRetriever(BaseRetriever):
    """Contextual retrieval that considers conversation history."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        context_window: int = 5
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.context_window = context_window
        self.semantic_retriever = SemanticRetriever(vector_store, embedding_provider)
    
    async def retrieve(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        conversation_history: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Retrieve with conversation context."""
        # Build contextual query
        contextual_query = self._build_contextual_query(query, conversation_history)
        
        # Retrieve using contextual query
        return await self.semantic_retriever.retrieve(
            contextual_query, user_id, filters, limit
        )
    
    def _build_contextual_query(
        self,
        query: str,
        conversation_history: Optional[List[str]] = None
    ) -> str:
        """Build query with conversation context."""
        if not conversation_history:
            return query
        
        # Take recent context
        recent_context = conversation_history[-self.context_window:]
        
        # Combine with current query
        contextual_query = " ".join(recent_context + [query])
        
        return contextual_query


class RAGRetriever:
    """Main RAG retriever that orchestrates different retrieval strategies."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC,
        max_results: int = 10,
        similarity_threshold: float = 0.7,
        enable_reranking: bool = True,
        diversity_threshold: float = 0.8
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.strategy = strategy
        self.max_results = max_results
        self.similarity_threshold = similarity_threshold
        self.enable_reranking = enable_reranking
        self.diversity_threshold = diversity_threshold
        
        # Initialize retrievers
        self.retrievers = {
            RetrievalStrategy.SEMANTIC: SemanticRetriever(
                vector_store, embedding_provider, similarity_threshold
            ),
            RetrievalStrategy.HYBRID: HybridRetriever(
                vector_store, embedding_provider
            ),
            RetrievalStrategy.CONTEXTUAL: ContextualRetriever(
                vector_store, embedding_provider
            )
        }
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def retrieve(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Retrieve relevant documents using the configured strategy."""
        try:
            retriever = self.retrievers.get(self.strategy)
            if not retriever:
                raise RAGError(f"Unsupported retrieval strategy: {self.strategy}")
            
            # Retrieve documents
            if self.strategy == RetrievalStrategy.CONTEXTUAL:
                results = await retriever.retrieve(
                    query=query,
                    user_id=user_id,
                    filters=filters,
                    limit=self.max_results,
                    conversation_history=conversation_history
                )
            else:
                results = await retriever.retrieve(
                    query=query,
                    user_id=user_id,
                    filters=filters,
                    limit=self.max_results
                )
            
            # Apply post-processing
            if self.enable_reranking:
                results = await self._rerank_results(query, results)
            
            results = self._ensure_diversity(results)
            
            return results[:self.max_results]
            
        except Exception as e:
            self.logger.error(f"Retrieval failed: {str(e)}")
            raise RAGError(f"Retrieval failed: {str(e)}") from e
    
    async def _rerank_results(
        self,
        query: str,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """Rerank results using advanced scoring."""
        if len(results) <= 1:
            return results
        
        # Simple reranking based on content length and metadata
        reranked = []
        
        for result in results:
            # Base score
            score = float(result.score)
            
            # Boost based on content quality indicators
            content = result.document.content
            metadata = result.document.metadata
            
            # Prefer longer, more detailed content
            if len(content) > 100:
                score *= 1.1
            
            # Boost recent documents
            if "created_at" in metadata:
                # Simple recency boost (would be more sophisticated in practice)
                score *= 1.05
            
            # Boost documents with specific types
            doc_type = metadata.get("document_type", "")
            if doc_type in ["schema", "query_pattern"]:
                score *= 1.2
            
            reranked.append(SearchResult(
                document=result.document,
                score=Score(score),
                rank=result.rank
            ))
        
        # Sort by new scores
        reranked.sort(key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(reranked):
            result.rank = i + 1
        
        return reranked
    
    def _ensure_diversity(self, results: List[SearchResult]) -> List[SearchResult]:
        """Ensure diversity in results to avoid redundancy."""
        if len(results) <= 1:
            return results
        
        diverse_results = [results[0]]  # Always include top result
        
        for result in results[1:]:
            # Check if this result is too similar to existing ones
            is_diverse = True
            
            for existing in diverse_results:
                similarity = self._calculate_content_similarity(
                    result.document.content,
                    existing.document.content
                )
                
                if similarity > self.diversity_threshold:
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_results.append(result)
        
        return diverse_results
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate simple content similarity."""
        # Simple Jaccard similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
