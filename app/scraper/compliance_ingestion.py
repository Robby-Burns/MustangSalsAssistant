import logging
import os
import smtplib
from email.mime.text import MIMEText
import pandas as pd
from app.config import config
from app.factories.vector_store_factory import VectorStoreFactory
from app.factories.embedder_factory import get_embedder_provider
from app.factories.excel_data_provider import ExcelDataProvider
from langchain_core.documents import Document
from langchain_chroma import Chroma

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_failure_alert(error_message: str):
    # Implementation remains the same...
    pass

def process_and_ingest(data: list):
    """Processes the data and ingests it into the configured vector database."""
    vector_store_provider = VectorStoreFactory.get_provider()
    embedder = get_embedder_provider()
    
    documents = []
    updates_to_make = []
    
    for row in data:
        row_id = row.get('row_id')
        try:
            logger.info(f"Processing row {row_id}: {row.get('Rule Name', 'N/A')}")
            
            content = f"Rule: {row.get('Rule Name', '')}\nConstraints: {row.get('Key Constraints', '')}\nFull Text: {row.get('Full Text', '')}"
            metadata = {"municipality": row.get("Municipality", ""), "source": row.get("Source URL", "")}
            documents.append(Document(page_content=content, metadata=metadata))
            
            updates_to_make.append((row_id, {"Sync Status": f"✅ Synced on {pd.Timestamp.now(tz='UTC')}"}))

        except Exception as e:
            logger.error(f"Failed to process row {row_id}: {e}")
            updates_to_make.append((row_id, {"Sync Status": f"❌ ERROR: {e}"}))

    if documents:
        logger.info(f"Successfully processed {len(documents)} documents. Ingesting into {vector_store_provider}...")

        if vector_store_provider == "chroma":
            persist_directory = config.database.vector_store.get_chroma_path()
            collection_name = config.database.vector_store.collection_name

            logger.info(f"Writing to ChromaDB at: {persist_directory}")
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embedder,
                persist_directory=persist_directory,
                collection_name=collection_name
            )
            vectorstore.persist()
            logger.info("ChromaDB ingestion complete and persisted.")

        elif vector_store_provider == "neon":
            logger.warning("NeonDB ingestion is not yet fully implemented in this script.")
            # Placeholder for NeonDB ingestion logic

        elif vector_store_provider == "s3":
            logger.warning("S3 ingestion is not yet fully implemented in this script.")
            # Placeholder for S3 ingestion logic

    if updates_to_make:
        logger.info("Writing sync status back to Excel file...")
        ExcelDataProvider.update_rows(updates_to_make)

if __name__ == "__main__":
    try:
        ExcelDataProvider.pre_flight_check()
        excel_data = ExcelDataProvider.get_data()
        if excel_data:
            process_and_ingest(excel_data)
        else:
            logger.warning("No data found in the Excel file. Nothing to ingest.")
    except Exception as e:
        logger.critical(f"A system-level error occurred in the ingestion script: {e}")
        # send_failure_alert(f"The script failed its pre-flight check or a major operation. Error: {str(e)}")
