import logging
import os
from typing import Any

import boto3
from app.config import config
from app.factories.embedder_factory import get_embedder_provider

logger = logging.getLogger(__name__)

class VectorStoreFactory:
    """
    Master Factory for determining which Vector Database connection to use.
    Controlled securely via `config/scale.yaml`.
    Supports: 'neon' (pgvector), 'chroma' (ChromaDB), and 's3'.
    """

    @classmethod
    def get_provider(cls) -> str:
        return config.database.vector_store.provider.lower()

    @classmethod
    def semantic_search(cls, query_text: str, k: int = 3):
        provider = cls.get_provider()
        if provider == "chroma":
            return cls._chroma_search(query_text, k)
        elif provider == "s3":
            return cls._s3_search(query_text, k)
        elif provider == "neon":
            return cls._neon_search(query_text, k)
        else:
            raise ValueError(f"Unsupported vector provider: {provider}")

    @classmethod
    def _s3_search(cls, query_text: str, k: int):
        """
        Mocks a semantic search against an S3 bucket.
        A real implementation would use a service like OpenSearch or a custom index.
        """
        logger.info(f"Executing mock semantic search against S3 for query: '{query_text}'")
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION_NAME")
        )
        # This is a placeholder. A real implementation would query an index.
        # For now, we return a sample structure.
        return [{"id": "s3-recipe-001", "project_type": "Pylon Sign", "zoning_tags": ["S3_MOCK"], "content": "Mock S3 data for a pylon sign."}]

    @classmethod
    def _neon_search(cls, query_text: str, k: int):
        logger.warning("Neon vector search is not configured in this environment. Falling back to mock results.")
        return cls._fallback_demo_results(query_text, k)

    @classmethod
    def _chroma_search(cls, query_text: str, k: int):
        try:
            from langchain_chroma import Chroma

            vectorstore = Chroma(
                persist_directory=config.database.vector_store.get_chroma_path(),
                embedding_function=get_embedder_provider(),
                collection_name=config.database.vector_store.collection_name,
            )
            results = vectorstore.similarity_search(query_text, k=k)
            if results:
                normalized = []
                for index, doc in enumerate(results):
                    metadata = dict(doc.metadata or {})
                    recipe_id = metadata.get("Recipe_ID", f"doc-{index}")
                    normalized.append(
                        {
                            "id": recipe_id,
                            "project_type": metadata.get("Project_Type"),
                            "part_list": metadata.get("Part_List", []),
                            "labor_hours": metadata.get("Labor_Hours", 0),
                            "zoning_tags": metadata.get("Zoning_Tags", []),
                            "source_bucket": metadata.get("Source_Bucket", "Sandbox"),
                            "content": doc.page_content,
                        }
                    )
                return normalized
        except Exception as exc:
            logger.warning(f"Chroma search unavailable, falling back to demo recipe lookup: {exc}")

        return cls._fallback_demo_results(query_text, k)

    @staticmethod
    def _fallback_demo_results(query_text: str, k: int):
        query = query_text.lower()
        demo_catalog = [
            {
                "id": "REC-MONUMENT-001",
                "project_type": "Monument Sign",
                "part_list": [{"SKU": "MONUMENT-8FT", "Qty": 1, "Description": "8ft monument sign"}],
                "labor_hours": 24,
                "zoning_tags": ["KMC"],
                "source_bucket": "Sandbox",
                "content": "Mock Chroma data for a monument sign.",
            },
            {
                "id": "REC-PYLON-002",
                "project_type": "Pylon Sign",
                "part_list": [{"SKU": "PYLON-20FT", "Qty": 1, "Description": "20ft pylon sign"}],
                "labor_hours": 40,
                "zoning_tags": ["RMC"],
                "source_bucket": "Sandbox",
                "content": "Mock Chroma data for a pylon sign.",
            },
            {
                "id": "REC-CHANNEL-003",
                "project_type": "Channel Letters",
                "part_list": [{"SKU": "CHANNEL-LED", "Qty": 10, "Description": "LED channel letters"}],
                "labor_hours": 16,
                "zoning_tags": ["PMC"],
                "source_bucket": "Sandbox",
                "content": "Mock Chroma data for channel letters.",
            },
        ]

        ranked = [item for item in demo_catalog if any(word in item["project_type"].lower() for word in query.split())]
        if not ranked:
            ranked = demo_catalog
        return ranked[:k]
