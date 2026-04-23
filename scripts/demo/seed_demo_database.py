import logging
import os
import shutil
from app.config import config
from app.factories.embedder_factory import get_embedder_provider
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.models.core import ProjectRecipe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_chroma_db_with_demo_data():
    """
    Seeds the ChromaDB with a set of demo ProjectRecipe documents.
    This script is idempotent: it deletes the old collection before seeding.
    """
    if config.database.vector_store.provider.lower() != "chroma":
        logger.warning("Vector store provider is not ChromaDB. Skipping demo data seeding.")
        return

    persist_directory = config.database.vector_store.get_chroma_path()
    collection_name = config.database.vector_store.collection_name
    embedder = get_embedder_provider()

    # --- Idempotency Step: Delete existing collection ---
    if os.path.exists(persist_directory):
        logger.warning(f"Existing ChromaDB collection found at '{persist_directory}'. Deleting it to ensure a clean seed.")
        try:
            shutil.rmtree(persist_directory)
            logger.info("Successfully deleted old collection.")
        except Exception as e:
            logger.error(f"Failed to delete existing ChromaDB directory: {e}")
            return
    
    os.makedirs(persist_directory, exist_ok=True)

    # --- Define Demo Data ---
    demo_recipes = [
        ProjectRecipe(Recipe_ID="REC-MONUMENT-001", Project_Type="Monument Sign", Part_List=[{"SKU": "MONUMENT-8FT", "Qty": 1}], Labor_Hours=24, Zoning_Tags=["KMC"], Source_Bucket="Demo"),
        ProjectRecipe(Recipe_ID="REC-PYLON-002", Project_Type="Pylon Sign", Part_List=[{"SKU": "PYLON-20FT", "Qty": 1}], Labor_Hours=40, Zoning_Tags=["RMC"], Source_Bucket="Demo"),
        ProjectRecipe(Recipe_ID="REC-CHANNEL-003", Project_Type="Channel Letters", Part_List=[{"SKU": "CHANNEL-LED", "Qty": 10}], Labor_Hours=16, Zoning_Tags=["PMC"], Source_Bucket="Demo"),
    ]

    documents = [Document(page_content=f"Project Type: {r.Project_Type}", metadata=r.model_dump()) for r in demo_recipes]

    try:
        logger.info(f"Seeding ChromaDB collection '{collection_name}' with demo data...")
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embedder,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        vectorstore.persist()
        logger.info("ChromaDB demo data seeding complete and persisted.")
    except Exception as e:
        logger.error(f"Failed to seed ChromaDB with demo data: {e}")

if __name__ == "__main__":
    seed_chroma_db_with_demo_data()
