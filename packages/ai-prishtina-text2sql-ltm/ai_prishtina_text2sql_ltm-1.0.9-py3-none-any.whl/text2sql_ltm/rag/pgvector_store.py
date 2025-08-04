"""
PgVector store implementation for Text2SQL-LTM library.

This module provides integration with PostgreSQL + pgvector extension
for vector similarity search with full SQL capabilities.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import uuid

try:
    import asyncpg
    import numpy as np
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None
    np = None

from .vector_store import BaseVectorStore, VectorDocument, SearchResult, VectorStoreConfig
from ..types import DocumentID, EmbeddingVector, Score
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class PgVectorStore(BaseVectorStore):
    """
    PostgreSQL + pgvector store implementation.
    
    Provides vector similarity search using PostgreSQL with pgvector extension,
    combining the power of SQL with vector operations.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize PgVector store."""
        super().__init__(config)
        
        if not ASYNCPG_AVAILABLE:
            raise VectorStoreError("asyncpg library not installed. Install with: pip install asyncpg numpy")
        
        self.pool: Optional[asyncpg.Pool] = None
        self.table_name = config.collection_name or "text2sql_documents"
        self.dimension = config.dimension or 1536  # Default for OpenAI embeddings
        
        # PostgreSQL connection settings
        self.host = getattr(config, 'pg_host', 'localhost')
        self.port = getattr(config, 'pg_port', 5432)
        self.database = getattr(config, 'pg_database', 'postgres')
        self.user = getattr(config, 'pg_user', 'postgres')
        self.password = getattr(config, 'pg_password', None)
        self.ssl = getattr(config, 'pg_ssl', False)
        
        # Distance operator mapping for pgvector
        distance_map = {
            "cosine": "<=>",  # Cosine distance
            "euclidean": "<->",  # L2 distance
            "dot_product": "<#>",  # Negative inner product
            "manhattan": "<+>"  # L1 distance (if available)
        }
        self.distance_op = distance_map.get(
            config.distance_metric.value if config.distance_metric else "cosine",
            "<=>"
        )
        
    async def _initialize_client(self) -> None:
        """Initialize PostgreSQL connection pool."""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                ssl=self.ssl,
                min_size=1,
                max_size=10
            )
            
            # Ensure pgvector extension and table exist
            await self._ensure_setup()
            
            logger.info(f"PgVector store initialized: {self.table_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize PgVector: {str(e)}")
            raise VectorStoreError(f"PgVector initialization failed: {str(e)}") from e
    
    async def _ensure_setup(self) -> None:
        """Ensure pgvector extension and table exist."""
        try:
            async with self.pool.acquire() as conn:
                # Enable pgvector extension
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                
                # Create table if it doesn't exist
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector({self.dimension}),
                    metadata JSONB DEFAULT '{{}}',
                    source TEXT DEFAULT '',
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
                """
                await conn.execute(create_table_sql)
                
                # Create vector index for similarity search
                index_name = f"{self.table_name}_embedding_idx"
                try:
                    # Try to create HNSW index (more efficient for large datasets)
                    create_index_sql = f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON {self.table_name} 
                    USING hnsw (embedding vector_cosine_ops)
                    """
                    await conn.execute(create_index_sql)
                except:
                    # Fallback to IVFFlat index
                    try:
                        create_index_sql = f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON {self.table_name} 
                        USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100)
                        """
                        await conn.execute(create_index_sql)
                    except:
                        logger.warning("Could not create vector index, searches may be slower")
                
                logger.info(f"PgVector setup complete for table: {self.table_name}")
                
        except Exception as e:
            raise VectorStoreError(f"Failed to setup PgVector: {str(e)}") from e
    
    async def _cleanup_client(self) -> None:
        """Clean up PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("PgVector client cleaned up")
    
    async def add_documents(
        self,
        documents: List[VectorDocument],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to PostgreSQL.
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.pool:
                raise VectorStoreError("PgVector pool not initialized")
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                async with self.pool.acquire() as conn:
                    # Prepare batch insert
                    insert_sql = f"""
                    INSERT INTO {self.table_name} (id, content, embedding, metadata, source, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        source = EXCLUDED.source,
                        timestamp = EXCLUDED.timestamp
                    """
                    
                    # Prepare batch data
                    batch_data = []
                    for doc in batch:
                        batch_data.append((
                            str(doc.id),
                            doc.content,
                            doc.embedding,  # asyncpg handles vector conversion
                            json.dumps(doc.metadata),
                            doc.metadata.get("source", ""),
                            doc.metadata.get("timestamp", datetime.now(timezone.utc).isoformat())
                        ))
                    
                    # Execute batch insert
                    await conn.executemany(insert_sql, batch_data)
                    
                logger.debug(f"Added batch of {len(batch)} documents to PgVector")
            
            logger.info(f"Successfully added {len(documents)} documents to PgVector")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to PgVector: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    async def search_similar(
        self,
        query_vector: EmbeddingVector,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[Score] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in PostgreSQL.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filter_metadata: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            List[SearchResult]: Search results
        """
        try:
            if not self.pool:
                raise VectorStoreError("PgVector pool not initialized")
            
            async with self.pool.acquire() as conn:
                # Build base query
                base_query = f"""
                SELECT id, content, metadata, source, timestamp,
                       embedding {self.distance_op} $1 AS distance
                FROM {self.table_name}
                """
                
                params = [query_vector]
                where_conditions = []
                
                # Add metadata filters
                if filter_metadata:
                    for key, value in filter_metadata.items():
                        if key == "source":
                            where_conditions.append(f"source = ${len(params) + 1}")
                            params.append(value)
                        else:
                            # Search in JSONB metadata
                            where_conditions.append(f"metadata ->> '{key}' = ${len(params) + 1}")
                            params.append(str(value))
                
                # Add WHERE clause if needed
                if where_conditions:
                    base_query += " WHERE " + " AND ".join(where_conditions)
                
                # Add ordering and limit
                base_query += f" ORDER BY distance LIMIT {limit}"
                
                # Execute query
                rows = await conn.fetch(base_query, *params)
                
                # Process results
                results = []
                for i, row in enumerate(rows):
                    # Convert distance to similarity score
                    distance = float(row['distance'])
                    
                    if self.distance_op == "<=>":  # Cosine distance
                        score = 1.0 - distance
                    elif self.distance_op == "<->":  # L2 distance
                        score = 1.0 / (1.0 + distance)
                    elif self.distance_op == "<#>":  # Negative inner product
                        score = -distance
                    else:
                        score = 1.0 - distance  # Default
                    
                    # Skip results below minimum score
                    if min_score and score < min_score:
                        continue
                    
                    # Parse metadata
                    try:
                        metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    except:
                        metadata = {}
                    
                    metadata.update({
                        "source": row['source'] or "",
                        "timestamp": row['timestamp'].isoformat() if row['timestamp'] else ""
                    })
                    
                    # Create VectorDocument
                    document = VectorDocument(
                        id=row['id'],
                        content=row['content'],
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
                
                logger.debug(f"PgVector search returned {len(results)} results")
                return results
            
        except Exception as e:
            logger.error(f"PgVector search failed: {str(e)}")
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
            if not self.pool:
                raise VectorStoreError("PgVector pool not initialized")
            
            async with self.pool.acquire() as conn:
                query = f"""
                SELECT id, content, embedding, metadata, source, timestamp
                FROM {self.table_name}
                WHERE id = $1
                """
                
                row = await conn.fetchrow(query, str(document_id))
                
                if not row:
                    return None
                
                # Parse metadata
                try:
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                except:
                    metadata = {}
                
                return VectorDocument(
                    id=document_id,
                    content=row['content'],
                    embedding=list(row['embedding']) if row['embedding'] else [],
                    metadata=metadata
                )
            
        except Exception as e:
            logger.error(f"Failed to get document from PgVector: {str(e)}")
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
            if not self.pool:
                raise VectorStoreError("PgVector pool not initialized")

            async with self.pool.acquire() as conn:
                query = f"DELETE FROM {self.table_name} WHERE id = $1"
                result = await conn.execute(query, str(document_id))

                # Check if any rows were affected
                rows_affected = int(result.split()[-1]) if result else 0

                if rows_affected == 0:
                    logger.warning(f"Document {document_id} not found for deletion")
                    return False

                logger.debug(f"Deleted document {document_id} from PgVector")
                return True

        except Exception as e:
            logger.error(f"Failed to delete document from PgVector: {str(e)}")
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
            if not self.pool:
                raise VectorStoreError("PgVector pool not initialized")

            async with self.pool.acquire() as conn:
                # Get existing document
                existing_row = await conn.fetchrow(
                    f"SELECT metadata FROM {self.table_name} WHERE id = $1",
                    str(document_id)
                )

                if not existing_row:
                    raise VectorStoreError(f"Document {document_id} not found")

                # Prepare update fields
                update_fields = []
                params = []
                param_count = 1

                if content is not None:
                    update_fields.append(f"content = ${param_count}")
                    params.append(content)
                    param_count += 1

                if embedding is not None:
                    update_fields.append(f"embedding = ${param_count}")
                    params.append(embedding)
                    param_count += 1

                if metadata is not None:
                    # Merge with existing metadata
                    try:
                        existing_metadata = json.loads(existing_row['metadata']) if existing_row['metadata'] else {}
                    except:
                        existing_metadata = {}

                    existing_metadata.update(metadata)
                    update_fields.append(f"metadata = ${param_count}")
                    params.append(json.dumps(existing_metadata))
                    param_count += 1

                # Always update timestamp
                update_fields.append(f"timestamp = ${param_count}")
                params.append(datetime.now(timezone.utc))
                param_count += 1

                # Add document ID as last parameter
                params.append(str(document_id))

                # Build and execute update query
                if update_fields:
                    query = f"""
                    UPDATE {self.table_name}
                    SET {', '.join(update_fields)}
                    WHERE id = ${param_count}
                    """

                    await conn.execute(query, *params)
                    logger.debug(f"Updated document {document_id} in PgVector")

                return True

        except Exception as e:
            logger.error(f"Failed to update document in PgVector: {str(e)}")
            raise VectorStoreError(f"Failed to update document: {str(e)}") from e

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            if not self.pool:
                raise VectorStoreError("PgVector pool not initialized")

            async with self.pool.acquire() as conn:
                # Get document count
                count_result = await conn.fetchval(f"SELECT COUNT(*) FROM {self.table_name}")

                # Get table size
                size_result = await conn.fetchval(
                    "SELECT pg_size_pretty(pg_total_relation_size($1))",
                    self.table_name
                )

                # Check if pgvector extension is available
                extension_result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )

                # Get index information
                index_result = await conn.fetch(
                    """
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = $1 AND indexdef LIKE '%vector%'
                    """,
                    self.table_name
                )

                return {
                    "total_vectors": count_result or 0,
                    "table_name": self.table_name,
                    "dimension": self.dimension,
                    "distance_operator": self.distance_op,
                    "table_size": size_result or "unknown",
                    "pgvector_enabled": bool(extension_result),
                    "vector_indexes": [dict(row) for row in index_result],
                    "store_type": "pgvector",
                    "host": self.host,
                    "port": self.port,
                    "database": self.database
                }

        except Exception as e:
            logger.error(f"Failed to get PgVector stats: {str(e)}")
            return {"error": str(e), "store_type": "pgvector"}
