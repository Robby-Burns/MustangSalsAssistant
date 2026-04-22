import logging
from app.factories.vector_store_factory import VectorStoreFactory

logger = logging.getLogger(__name__)

class S3VectorFactory:
    """
    Manages vector semantics and legacy file pulling, wrapping DB and S3 queries.
    As per AgentSpec, this Factory provides the primary sandbox retrievals.
    """
    
    @classmethod
    def semantic_search(cls, query_text: str, k: int = 3):
        """Executes a live vector similarity search against the configured sandbox."""
        return VectorStoreFactory.semantic_search(query_text, k)

    @classmethod
    def get_recipe_by_id(cls, recipe_id: str):
        logger.info(f"Mocking S3 object pull for recipe: {recipe_id}")
        return {
            "Recipe_ID": recipe_id,
            "Project_Type": "Monument Sign",
            "Part_List": [{"SKU": "MONUMENT-8FT", "Qty": 1, "Description": "8ft Monument Base"}],
            "Labor_Hours": 16,
            "Zoning_Tags": ["KMC", "monument"],
            "Source_Bucket": "Sandbox"
        }

    @classmethod
    def list_recent_won(cls):
        logger.info("Mocking S3 list operation for recent won projects.")
        return [
            {"Recipe_ID": "REC-001", "Project_Type": "Pylon Sign"},
            {"Recipe_ID": "REC-002", "Project_Type": "Channel Letters"}
        ]

    @classmethod
    def raw_s3_legacy(cls, query: str):
        logger.info(f"Mocking raw S3 legacy search for: {query}")
        return []
