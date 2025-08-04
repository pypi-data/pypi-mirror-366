"""
Schema RAG - Specialized RAG for database schema understanding.
"""

from __future__ import annotations

import asyncio
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
class SchemaEmbedding:
    """Schema embedding with metadata."""
    table_name: str
    column_info: Dict[str, Any]
    relationships: List[Dict[str, Any]]
    embedding: Any
    metadata: Dict[str, Any]


class SchemaRAG:
    """
    Specialized RAG for database schema understanding and retrieval.
    
    This component provides intelligent schema-aware context retrieval
    for better SQL generation with deep understanding of database structure.
    """
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        weight: float = 0.3
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.weight = weight
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Schema cache
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        self._relationship_graph: Dict[str, List[str]] = {}
        
        # Metrics
        self._metrics = {
            "schemas_indexed": 0,
            "schema_retrievals": 0,
            "relationship_queries": 0,
            "cache_hits": 0
        }
    
    async def initialize(self) -> None:
        """Initialize schema RAG component."""
        self.logger.info("Schema RAG initialized")
    
    async def close(self) -> None:
        """Close schema RAG component."""
        self.logger.info("Schema RAG closed")
    
    async def index_schema(
        self,
        schema_info: Dict[str, Any],
        database_name: str,
        user_id: Optional[UserID] = None
    ) -> List[DocumentID]:
        """
        Index database schema information for retrieval.
        
        Args:
            schema_info: Complete schema information
            database_name: Name of the database
            user_id: Optional user ID for isolation
            
        Returns:
            List of document IDs for indexed schema components
        """
        try:
            indexed_docs = []
            
            # Index each table separately
            for table_name, table_info in schema_info.get("tables", {}).items():
                doc_id = await self._index_table_schema(
                    table_name, table_info, database_name, user_id
                )
                indexed_docs.append(doc_id)
            
            # Index relationships
            relationships = schema_info.get("relationships", [])
            if relationships:
                doc_id = await self._index_relationships(
                    relationships, database_name, user_id
                )
                indexed_docs.append(doc_id)
            
            # Index views
            for view_name, view_info in schema_info.get("views", {}).items():
                doc_id = await self._index_view_schema(
                    view_name, view_info, database_name, user_id
                )
                indexed_docs.append(doc_id)
            
            # Index functions/procedures
            for func_name, func_info in schema_info.get("functions", {}).items():
                doc_id = await self._index_function_schema(
                    func_name, func_info, database_name, user_id
                )
                indexed_docs.append(doc_id)
            
            # Update cache and relationship graph
            self._update_schema_cache(database_name, schema_info)
            self._build_relationship_graph(schema_info)
            
            self._metrics["schemas_indexed"] += 1
            self.logger.info(f"Indexed schema for database {database_name}")
            
            return indexed_docs
            
        except Exception as e:
            self.logger.error(f"Failed to index schema: {str(e)}")
            raise RAGError(f"Schema indexing failed: {str(e)}") from e
    
    async def _index_table_schema(
        self,
        table_name: str,
        table_info: Dict[str, Any],
        database_name: str,
        user_id: Optional[UserID]
    ) -> DocumentID:
        """Index individual table schema."""
        # Create comprehensive table description
        table_description = self._create_table_description(table_name, table_info)
        
        # Generate embedding
        embedding = await self.embedding_provider.embed_text(table_description)
        
        # Create document
        document_id = DocumentID(f"schema_table_{database_name}_{table_name}")
        document = VectorDocument(
            id=document_id,
            content=table_description,
            embedding=embedding,
            metadata={
                "document_type": "schema_table",
                "database_name": database_name,
                "table_name": table_name,
                "column_count": len(table_info.get("columns", {})),
                "has_primary_key": any(
                    col.get("primary_key", False) 
                    for col in table_info.get("columns", {}).values()
                ),
                "has_foreign_keys": any(
                    col.get("foreign_key") 
                    for col in table_info.get("columns", {}).values()
                ),
                "indexed_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        # Store in vector database
        await self.vector_store.add_documents([document])
        
        return document_id
    
    async def _index_relationships(
        self,
        relationships: List[Dict[str, Any]],
        database_name: str,
        user_id: Optional[UserID]
    ) -> DocumentID:
        """Index table relationships."""
        # Create relationships description
        rel_description = self._create_relationships_description(relationships)
        
        # Generate embedding
        embedding = await self.embedding_provider.embed_text(rel_description)
        
        # Create document
        document_id = DocumentID(f"schema_relationships_{database_name}")
        document = VectorDocument(
            id=document_id,
            content=rel_description,
            embedding=embedding,
            metadata={
                "document_type": "schema_relationships",
                "database_name": database_name,
                "relationship_count": len(relationships),
                "indexed_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        await self.vector_store.add_documents([document])
        return document_id
    
    async def _index_view_schema(
        self,
        view_name: str,
        view_info: Dict[str, Any],
        database_name: str,
        user_id: Optional[UserID]
    ) -> DocumentID:
        """Index database view schema."""
        view_description = f"View: {view_name}\n"
        view_description += f"Definition: {view_info.get('definition', 'N/A')}\n"
        
        if view_info.get("columns"):
            view_description += "Columns:\n"
            for col_name, col_info in view_info["columns"].items():
                view_description += f"  - {col_name}: {col_info.get('type', 'unknown')}\n"
        
        embedding = await self.embedding_provider.embed_text(view_description)
        
        document_id = DocumentID(f"schema_view_{database_name}_{view_name}")
        document = VectorDocument(
            id=document_id,
            content=view_description,
            embedding=embedding,
            metadata={
                "document_type": "schema_view",
                "database_name": database_name,
                "view_name": view_name,
                "indexed_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        await self.vector_store.add_documents([document])
        return document_id
    
    async def _index_function_schema(
        self,
        func_name: str,
        func_info: Dict[str, Any],
        database_name: str,
        user_id: Optional[UserID]
    ) -> DocumentID:
        """Index database function/procedure schema."""
        func_description = f"Function: {func_name}\n"
        func_description += f"Return Type: {func_info.get('return_type', 'unknown')}\n"
        
        if func_info.get("parameters"):
            func_description += "Parameters:\n"
            for param in func_info["parameters"]:
                func_description += f"  - {param.get('name', 'unknown')}: {param.get('type', 'unknown')}\n"
        
        if func_info.get("description"):
            func_description += f"Description: {func_info['description']}\n"
        
        embedding = await self.embedding_provider.embed_text(func_description)
        
        document_id = DocumentID(f"schema_function_{database_name}_{func_name}")
        document = VectorDocument(
            id=document_id,
            content=func_description,
            embedding=embedding,
            metadata={
                "document_type": "schema_function",
                "database_name": database_name,
                "function_name": func_name,
                "indexed_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        await self.vector_store.add_documents([document])
        return document_id
    
    def _create_table_description(self, table_name: str, table_info: Dict[str, Any]) -> str:
        """Create comprehensive table description for embedding."""
        description = f"Table: {table_name}\n"
        
        # Add table description if available
        if table_info.get("description"):
            description += f"Description: {table_info['description']}\n"
        
        # Add columns
        columns = table_info.get("columns", {})
        if columns:
            description += "Columns:\n"
            for col_name, col_info in columns.items():
                col_desc = f"  - {col_name}: {col_info.get('type', 'unknown')}"
                
                if col_info.get("nullable", True):
                    col_desc += " (nullable)"
                else:
                    col_desc += " (not null)"
                
                if col_info.get("primary_key"):
                    col_desc += " (primary key)"
                
                if col_info.get("foreign_key"):
                    col_desc += f" (foreign key -> {col_info['foreign_key']})"
                
                if col_info.get("description"):
                    col_desc += f" - {col_info['description']}"
                
                description += col_desc + "\n"
        
        # Add indexes
        indexes = table_info.get("indexes", [])
        if indexes:
            description += "Indexes:\n"
            for index in indexes:
                description += f"  - {index.get('name', 'unknown')}: {index.get('columns', [])}\n"
        
        return description
    
    def _create_relationships_description(self, relationships: List[Dict[str, Any]]) -> str:
        """Create relationships description for embedding."""
        description = "Database Relationships:\n"
        
        for rel in relationships:
            rel_type = rel.get("relationship_type", "unknown")
            source = f"{rel.get('source_table')}.{rel.get('source_column')}"
            target = f"{rel.get('target_table')}.{rel.get('target_column')}"
            
            description += f"  - {source} -> {target} ({rel_type})\n"
            
            if rel.get("description"):
                description += f"    Description: {rel['description']}\n"
        
        return description
    
    def _update_schema_cache(self, database_name: str, schema_info: Dict[str, Any]) -> None:
        """Update schema cache for fast access."""
        self._schema_cache[database_name] = schema_info
    
    def _build_relationship_graph(self, schema_info: Dict[str, Any]) -> None:
        """Build relationship graph for traversal."""
        relationships = schema_info.get("relationships", [])
        
        for rel in relationships:
            source_table = rel.get("source_table")
            target_table = rel.get("target_table")
            
            if source_table and target_table:
                if source_table not in self._relationship_graph:
                    self._relationship_graph[source_table] = []
                
                if target_table not in self._relationship_graph[source_table]:
                    self._relationship_graph[source_table].append(target_table)
    
    async def retrieve_schema_context(
        self,
        query: str,
        user_id: Optional[UserID] = None,
        database_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant schema context for a query.
        
        Args:
            query: Natural language query
            user_id: Optional user ID for filtering
            database_name: Optional database name for filtering
            
        Returns:
            Schema context with relevant tables, relationships, and metadata
        """
        try:
            self._metrics["schema_retrievals"] += 1
            
            # Check cache first
            if database_name and database_name in self._schema_cache:
                self._metrics["cache_hits"] += 1
                cached_schema = self._schema_cache[database_name]
                return self._filter_relevant_schema(query, cached_schema)
            
            # Generate query embedding
            query_embedding = await self.embedding_provider.embed_text(query)
            
            # Search for relevant schema documents
            filters = {"document_type": "schema_table"}
            if database_name:
                filters["database_name"] = database_name
            
            search_results = await self.vector_store.search(
                query_vector=query_embedding,
                limit=10,
                filters=filters,
                user_id=user_id
            )
            
            # Build schema context from results
            schema_context = {
                "relevant_tables": [],
                "relationships": [],
                "suggested_joins": [],
                "column_mappings": {},
                "query_hints": []
            }
            
            for result in search_results:
                metadata = result.document.metadata
                
                if metadata.get("document_type") == "schema_table":
                    table_info = {
                        "table_name": metadata.get("table_name"),
                        "content": result.document.content,
                        "relevance_score": float(result.score),
                        "has_primary_key": metadata.get("has_primary_key", False),
                        "has_foreign_keys": metadata.get("has_foreign_keys", False)
                    }
                    schema_context["relevant_tables"].append(table_info)
            
            # Add relationship information
            if database_name:
                schema_context["suggested_joins"] = self._suggest_joins(
                    [t["table_name"] for t in schema_context["relevant_tables"]],
                    database_name
                )
            
            return schema_context
            
        except Exception as e:
            self.logger.error(f"Schema context retrieval failed: {str(e)}")
            raise RAGError(f"Schema context retrieval failed: {str(e)}") from e
    
    def _filter_relevant_schema(self, query: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Filter schema information based on query relevance."""
        # Simple keyword-based filtering (would be more sophisticated in practice)
        query_lower = query.lower()
        relevant_tables = []
        
        for table_name, table_info in schema_info.get("tables", {}).items():
            # Check if table name or columns are mentioned in query
            if table_name.lower() in query_lower:
                relevant_tables.append({
                    "table_name": table_name,
                    "table_info": table_info,
                    "relevance_score": 1.0
                })
                continue
            
            # Check column names
            columns = table_info.get("columns", {})
            for col_name in columns.keys():
                if col_name.lower() in query_lower:
                    relevant_tables.append({
                        "table_name": table_name,
                        "table_info": table_info,
                        "relevance_score": 0.8
                    })
                    break
        
        return {
            "relevant_tables": relevant_tables,
            "relationships": schema_info.get("relationships", []),
            "suggested_joins": self._suggest_joins(
                [t["table_name"] for t in relevant_tables],
                "cached"
            )
        }
    
    def _suggest_joins(self, table_names: List[str], database_name: str) -> List[Dict[str, Any]]:
        """Suggest possible joins between tables."""
        suggested_joins = []
        
        for i, table1 in enumerate(table_names):
            for table2 in table_names[i+1:]:
                # Check if there's a relationship between these tables
                if table1 in self._relationship_graph:
                    if table2 in self._relationship_graph[table1]:
                        suggested_joins.append({
                            "table1": table1,
                            "table2": table2,
                            "join_type": "inner",
                            "confidence": 0.9
                        })
                
                if table2 in self._relationship_graph:
                    if table1 in self._relationship_graph[table2]:
                        suggested_joins.append({
                            "table1": table2,
                            "table2": table1,
                            "join_type": "inner",
                            "confidence": 0.9
                        })
        
        return suggested_joins
    
    async def index_schema_document(self, document: VectorDocument) -> None:
        """Index a schema document (called by RAG manager)."""
        # Additional processing for schema documents
        metadata = document.metadata
        
        if metadata.get("document_type") == "schema_table":
            table_name = metadata.get("table_name")
            database_name = metadata.get("database_name")
            
            # Update internal tracking
            if database_name and table_name:
                self.logger.debug(f"Indexed schema table {table_name} for database {database_name}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get schema RAG metrics."""
        return self._metrics.copy()
