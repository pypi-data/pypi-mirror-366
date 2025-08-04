"""
Query RAG - Specialized RAG for query pattern learning and retrieval.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .vector_store import BaseVectorStore, VectorDocument
from .embeddings import BaseEmbeddingProvider
from ..types import UserID, DocumentID
from ..exceptions import RAGError

logger = logging.getLogger(__name__)


@dataclass
class QueryPattern:
    """Query pattern with metadata."""
    natural_language: str
    sql_query: str
    success_rate: float
    usage_count: int
    complexity: str
    metadata: Dict[str, Any]


class QueryRAG:
    """
    Specialized RAG for query pattern learning and retrieval.
    
    This component learns from successful query patterns and provides
    intelligent suggestions based on similar past queries.
    """
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        weight: float = 0.2
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.weight = weight
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Pattern cache
        self._pattern_cache: Dict[str, QueryPattern] = {}
        
        # Metrics
        self._metrics = {
            "patterns_indexed": 0,
            "pattern_retrievals": 0,
            "pattern_matches": 0,
            "cache_hits": 0
        }
    
    async def initialize(self) -> None:
        """Initialize query RAG component."""
        self.logger.info("Query RAG initialized")
    
    async def close(self) -> None:
        """Close query RAG component."""
        self.logger.info("Query RAG closed")
    
    async def index_patterns(
        self,
        patterns: List[Dict[str, Any]],
        user_id: Optional[UserID] = None
    ) -> List[DocumentID]:
        """
        Index query patterns for retrieval.
        
        Args:
            patterns: List of query patterns with metadata
            user_id: Optional user ID for isolation
            
        Returns:
            List of document IDs for indexed patterns
        """
        try:
            indexed_docs = []
            
            for pattern in patterns:
                doc_id = await self._index_single_pattern(pattern, user_id)
                indexed_docs.append(doc_id)
            
            self._metrics["patterns_indexed"] += len(patterns)
            self.logger.info(f"Indexed {len(patterns)} query patterns")
            
            return indexed_docs
            
        except Exception as e:
            self.logger.error(f"Failed to index patterns: {str(e)}")
            raise RAGError(f"Pattern indexing failed: {str(e)}") from e
    
    async def _index_single_pattern(
        self,
        pattern: Dict[str, Any],
        user_id: Optional[UserID]
    ) -> DocumentID:
        """Index a single query pattern."""
        # Create pattern description for embedding
        pattern_description = self._create_pattern_description(pattern)
        
        # Generate embedding
        embedding = await self.embedding_provider.embed_text(pattern_description)
        
        # Create document
        pattern_id = pattern.get("id", f"pattern_{datetime.utcnow().timestamp()}")
        document_id = DocumentID(f"query_pattern_{pattern_id}")
        
        document = VectorDocument(
            id=document_id,
            content=pattern_description,
            embedding=embedding,
            metadata={
                "document_type": "query_pattern",
                "natural_language": pattern.get("natural_language", ""),
                "sql_query": pattern.get("sql_query", ""),
                "success_rate": pattern.get("success_rate", 0.0),
                "usage_count": pattern.get("usage_count", 0),
                "complexity": pattern.get("complexity", "unknown"),
                "domain": pattern.get("domain", "general"),
                "database_type": pattern.get("database_type", "unknown"),
                "indexed_at": datetime.utcnow().isoformat(),
                **pattern.get("metadata", {})
            },
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        # Store in vector database
        await self.vector_store.add_documents([document])
        
        # Update cache
        self._pattern_cache[document_id] = QueryPattern(
            natural_language=pattern.get("natural_language", ""),
            sql_query=pattern.get("sql_query", ""),
            success_rate=pattern.get("success_rate", 0.0),
            usage_count=pattern.get("usage_count", 0),
            complexity=pattern.get("complexity", "unknown"),
            metadata=pattern.get("metadata", {})
        )
        
        return document_id
    
    def _create_pattern_description(self, pattern: Dict[str, Any]) -> str:
        """Create comprehensive pattern description for embedding."""
        description = f"Query Pattern:\n"
        
        # Natural language query
        nl_query = pattern.get("natural_language", "")
        if nl_query:
            description += f"Natural Language: {nl_query}\n"
        
        # SQL query (simplified for embedding)
        sql_query = pattern.get("sql_query", "")
        if sql_query:
            # Extract key SQL components for better matching
            sql_components = self._extract_sql_components(sql_query)
            description += f"SQL Pattern: {sql_components}\n"
        
        # Metadata
        complexity = pattern.get("complexity", "unknown")
        description += f"Complexity: {complexity}\n"
        
        domain = pattern.get("domain", "general")
        description += f"Domain: {domain}\n"
        
        success_rate = pattern.get("success_rate", 0.0)
        description += f"Success Rate: {success_rate}\n"
        
        # Additional context
        if pattern.get("description"):
            description += f"Description: {pattern['description']}\n"
        
        return description
    
    def _extract_sql_components(self, sql_query: str) -> str:
        """Extract key SQL components for pattern matching."""
        sql_upper = sql_query.upper()
        components = []
        
        # Extract main operations
        if "SELECT" in sql_upper:
            components.append("SELECT")
        if "INSERT" in sql_upper:
            components.append("INSERT")
        if "UPDATE" in sql_upper:
            components.append("UPDATE")
        if "DELETE" in sql_upper:
            components.append("DELETE")
        
        # Extract clauses
        if "WHERE" in sql_upper:
            components.append("WHERE")
        if "GROUP BY" in sql_upper:
            components.append("GROUP_BY")
        if "ORDER BY" in sql_upper:
            components.append("ORDER_BY")
        if "HAVING" in sql_upper:
            components.append("HAVING")
        if "JOIN" in sql_upper:
            components.append("JOIN")
        
        # Extract functions
        if any(func in sql_upper for func in ["COUNT", "SUM", "AVG", "MAX", "MIN"]):
            components.append("AGGREGATE")
        
        if "DISTINCT" in sql_upper:
            components.append("DISTINCT")
        
        return " ".join(components)
    
    async def retrieve_patterns(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant query patterns for a natural language query.
        
        Args:
            query: Natural language query
            user_id: Optional user ID for filtering
            limit: Maximum number of patterns to retrieve
            
        Returns:
            List of relevant query patterns with metadata
        """
        try:
            self._metrics["pattern_retrievals"] += 1
            
            # Generate query embedding
            query_embedding = await self.embedding_provider.embed_text(query)
            
            # Search for relevant patterns
            filters = {"document_type": "query_pattern"}
            
            search_results = await self.vector_store.search(
                query_vector=query_embedding,
                limit=limit * 2,  # Get more for filtering
                filters=filters,
                user_id=user_id
            )
            
            # Process and rank results
            patterns = []
            for result in search_results:
                metadata = result.document.metadata
                
                pattern_info = {
                    "natural_language": metadata.get("natural_language", ""),
                    "sql_query": metadata.get("sql_query", ""),
                    "success_rate": metadata.get("success_rate", 0.0),
                    "usage_count": metadata.get("usage_count", 0),
                    "complexity": metadata.get("complexity", "unknown"),
                    "domain": metadata.get("domain", "general"),
                    "relevance_score": float(result.score),
                    "rank": result.rank,
                    "content": result.document.content
                }
                
                # Calculate combined score
                combined_score = self._calculate_pattern_score(pattern_info, query)
                pattern_info["combined_score"] = combined_score
                
                patterns.append(pattern_info)
            
            # Sort by combined score and return top patterns
            patterns.sort(key=lambda p: p["combined_score"], reverse=True)
            
            # Update metrics
            if patterns:
                self._metrics["pattern_matches"] += 1
            
            return patterns[:limit]
            
        except Exception as e:
            self.logger.error(f"Pattern retrieval failed: {str(e)}")
            raise RAGError(f"Pattern retrieval failed: {str(e)}") from e
    
    def _calculate_pattern_score(self, pattern: Dict[str, Any], query: str) -> float:
        """Calculate combined score for pattern ranking."""
        # Base relevance score
        relevance_score = pattern.get("relevance_score", 0.0)
        
        # Success rate boost
        success_rate = pattern.get("success_rate", 0.0)
        
        # Usage count boost (normalized)
        usage_count = pattern.get("usage_count", 0)
        usage_boost = min(usage_count / 100.0, 0.2)  # Max 0.2 boost
        
        # Query similarity boost
        nl_query = pattern.get("natural_language", "")
        similarity_boost = self._calculate_query_similarity(query, nl_query)
        
        # Combine scores
        combined_score = (
            relevance_score * 0.4 +
            success_rate * 0.3 +
            usage_boost +
            similarity_boost * 0.3
        )
        
        return combined_score
    
    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries."""
        if not query1 or not query2:
            return 0.0
        
        # Simple word overlap similarity
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def learn_from_query(
        self,
        natural_language: str,
        sql_query: str,
        success: bool,
        user_id: Optional[UserID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentID:
        """
        Learn from a new query execution.
        
        Args:
            natural_language: Natural language query
            sql_query: Generated SQL query
            success: Whether the query was successful
            user_id: Optional user ID
            metadata: Additional metadata
            
        Returns:
            Document ID of the learned pattern
        """
        try:
            # Create pattern from query
            pattern = {
                "natural_language": natural_language,
                "sql_query": sql_query,
                "success_rate": 1.0 if success else 0.0,
                "usage_count": 1,
                "complexity": self._estimate_complexity(sql_query),
                "domain": metadata.get("domain", "general") if metadata else "general",
                "database_type": metadata.get("database_type", "unknown") if metadata else "unknown",
                "metadata": metadata or {}
            }
            
            # Check if similar pattern exists
            existing_pattern = await self._find_similar_pattern(natural_language, user_id)
            
            if existing_pattern:
                # Update existing pattern
                return await self._update_pattern(existing_pattern, success)
            else:
                # Create new pattern
                return await self._index_single_pattern(pattern, user_id)
                
        except Exception as e:
            self.logger.error(f"Failed to learn from query: {str(e)}")
            raise RAGError(f"Query learning failed: {str(e)}") from e
    
    async def _find_similar_pattern(
        self,
        natural_language: str,
        user_id: Optional[UserID]
    ) -> Optional[str]:
        """Find similar existing pattern."""
        # Search for similar patterns
        query_embedding = await self.embedding_provider.embed_text(natural_language)
        
        results = await self.vector_store.search(
            query_vector=query_embedding,
            limit=1,
            filters={"document_type": "query_pattern"},
            user_id=user_id
        )
        
        if results and results[0].score > 0.9:  # High similarity threshold
            return results[0].document.id
        
        return None
    
    async def _update_pattern(self, pattern_id: str, success: bool) -> DocumentID:
        """Update existing pattern with new execution result."""
        # Get existing document
        document = await self.vector_store.get_document(DocumentID(pattern_id))
        
        if document:
            metadata = document.metadata
            
            # Update success rate and usage count
            current_success_rate = metadata.get("success_rate", 0.0)
            current_usage_count = metadata.get("usage_count", 0)
            
            new_usage_count = current_usage_count + 1
            new_success_rate = (
                (current_success_rate * current_usage_count + (1.0 if success else 0.0)) /
                new_usage_count
            )
            
            # Update metadata
            metadata["success_rate"] = new_success_rate
            metadata["usage_count"] = new_usage_count
            metadata["last_used"] = datetime.utcnow().isoformat()
            
            # Update document
            updated_document = VectorDocument(
                id=document.id,
                content=document.content,
                embedding=document.embedding,
                metadata=metadata,
                user_id=document.user_id,
                created_at=document.created_at,
                updated_at=datetime.utcnow()
            )
            
            await self.vector_store.update_document(document.id, updated_document)
        
        return DocumentID(pattern_id)
    
    def _estimate_complexity(self, sql_query: str) -> str:
        """Estimate SQL query complexity."""
        sql_upper = sql_query.upper()
        complexity_score = 0
        
        # Count complexity indicators
        if "JOIN" in sql_upper:
            complexity_score += sql_upper.count("JOIN") * 2
        
        if any(keyword in sql_upper for keyword in ["GROUP BY", "HAVING", "ORDER BY"]):
            complexity_score += 2
        
        if any(keyword in sql_upper for keyword in ["UNION", "INTERSECT", "EXCEPT"]):
            complexity_score += 3
        
        if "(" in sql_query:  # Subqueries
            complexity_score += 3
        
        if any(func in sql_upper for func in ["WINDOW", "OVER", "PARTITION"]):
            complexity_score += 4
        
        # Determine complexity level
        if complexity_score <= 2:
            return "simple"
        elif complexity_score <= 5:
            return "moderate"
        elif complexity_score <= 10:
            return "complex"
        else:
            return "very_complex"
    
    async def index_query_pattern(self, document: VectorDocument) -> None:
        """Index a query pattern document (called by RAG manager)."""
        # Additional processing for query pattern documents
        metadata = document.metadata
        
        if metadata.get("document_type") == "query_pattern":
            nl_query = metadata.get("natural_language", "")
            success_rate = metadata.get("success_rate", 0.0)
            
            self.logger.debug(f"Indexed query pattern with success rate {success_rate}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get query RAG metrics."""
        return self._metrics.copy()
