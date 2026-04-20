import logging
import os
from typing import Any

from app.config import config
from app.factories.embedder_factory import get_embedder_provider
from psycopg2 import sql

logger = logging.getLogger(__name__)

class VectorStoreFactory:
    """
    Master Factory for determining which Vector Database connection to use.
    Controlled securely via `config/scale.yaml`.
    Currently supports: 'neon' (pgvector), 'chroma' (ChromaDB), and 's3'
    """

    @classmethod
    def get_provider(cls) -> str:
        provider = config.database.vector_store.provider.lower()
        if provider not in ["neon", "chroma", "s3"]:
             logger.warning(f"Unknown vector provider: {provider}, falling back to 'neon'")
             return "neon"
        return provider

    @classmethod
    def get_collection_name(cls) -> str:
        return config.database.vector_store.collection_name

    @classmethod
    def semantic_search(cls, query_text: str, k: int = 3):
        provider = cls.get_provider()
        
        if provider == "chroma":
            return cls._chroma_search(query_text, k)
        elif provider == "s3":
            return cls._s3_search(query_text, k)
        else:
            return cls._neon_search(query_text, k)

    @classmethod
    def _neon_search(cls, query_text: str, k: int):
        from app.db import get_connection
        
        try:
            embeddings_model = get_embedder_provider()
            query_vector = embeddings_model.embed_query(query_text)
        except Exception as e:
            logger.error(f"Text vectorization failed: {e}")
            return []

        conn = get_connection()
        if not conn:
            logger.warning("No DB connection; falling back to Mock S3 Recipe.")
            return [{"id": 0, "project_type": "Mock Recipe", "zoning_tags": ["NONE"], "content": "Mock data"}]
            
        try:
            with conn.cursor() as cur:
                collection = cls.get_collection_name()
                
                # We strictly cast the parameterized query array to `::vector` for pgvector L2 operator `<->`
                # Use psycopg2.sql.SQL to safely bind the table name instead of an f-string
                query = sql.SQL(
                    "SELECT id, project_type, zoning_tags, content FROM {table} ORDER BY embedding <-> %s::vector LIMIT %s;"
                ).format(table=sql.Identifier(collection))
                
                cur.execute(query, (query_vector, k))
                rows = cur.fetchall()
                return [{"id": r[0], "project_type": r[1], "zoning_tags": r[2], "content": r[3]} for r in rows]
        except Exception as e:
            logger.error(f"Neon DB Semantic Search Exception: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def _chroma_search(cls, query_text: str, k: int):
        from langchain_chroma import Chroma
        
        try:
            embeddings_model = get_embedder_provider()
        except Exception as e:
            logger.error(f"Failed to load embedder provider for Chroma: {e}")
            return []

        persist_directory = config.database.vector_store.get_chroma_path()
        collection_name = cls.get_collection_name()
        
        if not os.path.exists(persist_directory):
            logger.warning(f"Chroma persist directory {persist_directory} does not exist. Returning empty or mock.")
            return [{"id": 0, "project_type": "Mock Recipe", "zoning_tags": ["NONE"], "content": "Mock data"}]

        try:
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings_model,
                persist_directory=persist_directory
            )
            
            results = vectorstore.similarity_search_with_score(query_text, k=k)
            
            formatted_results = []
            for i, (doc, score) in enumerate(results):
                formatted_results.append({
                    "id": doc.metadata.get("id", i),
                    "project_type": doc.metadata.get("project_type", "Unknown"),
                    "zoning_tags": doc.metadata.get("zoning_tags", []),
                    "content": doc.page_content
                })
            
            # If no results, mock a return per original pipeline
            if not formatted_results:
                return [{"id": 0, "project_type": "Mock Recipe", "zoning_tags": ["NONE"], "content": "Mock data"}]
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Chroma Semantic Search Exception: {e}")
            return []
            
    @classmethod
    def _s3_search(cls, query_text: str, k: int):
        # Placeholder for strict S3 object pulling
        logger.info("Executing S3 vector search (Placeholder)")
        return [{"id": 0, "project_type": "Mock S3 Recipe", "zoning_tags": ["S3_MOCK"], "content": "Mock S3 data"}]
