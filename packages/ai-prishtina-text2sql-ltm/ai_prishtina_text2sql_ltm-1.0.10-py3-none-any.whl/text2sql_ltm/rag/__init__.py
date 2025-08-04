"""
RAG (Retrieval-Augmented Generation) system for Text2SQL-LTM library.

This module provides advanced RAG capabilities including:
- Vector database integration for semantic search
- Document embedding and retrieval
- Context augmentation for SQL generation
- Multi-modal RAG with schema understanding
- Adaptive retrieval strategies
"""

from .vector_store import VectorStore, VectorStoreConfig
from .embeddings import EmbeddingProvider, OpenAIEmbeddings, HuggingFaceEmbeddings
from .retriever import RAGRetriever, RetrievalStrategy
from .augmentor import ContextAugmentor, AugmentationStrategy
from .manager import RAGManager
from .schema_rag import SchemaRAG, SchemaEmbedding
from .query_rag import QueryRAG, QueryPattern
from .adaptive_rag import AdaptiveRAG, RetrievalOptimizer

__all__ = [
    # Core RAG components
    "RAGManager",
    "RAGRetriever", 
    "ContextAugmentor",
    
    # Vector storage
    "VectorStore",
    "VectorStoreConfig",
    
    # Embeddings
    "EmbeddingProvider",
    "OpenAIEmbeddings",
    "HuggingFaceEmbeddings",
    
    # Specialized RAG
    "SchemaRAG",
    "QueryRAG", 
    "AdaptiveRAG",
    
    # Strategies and optimizers
    "RetrievalStrategy",
    "AugmentationStrategy",
    "RetrievalOptimizer",
    
    # Data structures
    "SchemaEmbedding",
    "QueryPattern",
]
