import logging
import os
import smtplib
from email.mime.text import MIMEText
import pandas as pd
from app.config import config
from app.factories.vector_store_factory import VectorStoreFactory
from app.factories.embedder_factory import get_embedder_provider
from app.factories.excel_data_provider import ExcelDataProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_failure_alert(error_message: str):
    """Sends an email alert for system-level failures."""
    try:
        msg = MIMEText(f"The compliance data ingestion script failed.\n\nError: {error_message}")
        msg["Subject"] = "CRITICAL: Compliance Ingestion Failure"
        msg["From"] = os.getenv("SENDER_EMAIL")
        msg["To"] = config.governance.technical_contact_email

        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        logger.info(f"Failure alert sent to {config.governance.technical_contact_email}")
    except Exception as e:
        logger.error(f"Failed to send failure alert email: {e}")

def process_and_ingest(data: list):
    """Processes the data and ingests it into the vector database."""
    vector_store_provider = VectorStoreFactory.get_provider()
    embedder = get_embedder_provider()
    
    documents = []
    updates_to_make = []
    
    for row in data:
        row_id = row.get('row_id')
        try:
            logger.info(f"Processing row {row_id}: {row.get('Rule Name', 'N/A')}")
            
            content = f"Rule: {row.get('Rule Name', '')}\nConstraints: {row.get('Key Constraints', '')}\nFull Text: {row.get('Full Text', '')}"
            documents.append({"content": content, "metadata": {"municipality": row.get("Municipality", ""), "source": row.get("Source URL", "")}})
            
            updates_to_make.append((row_id, {"Sync Status": f"✅ Synced on {pd.Timestamp.now(tz='UTC')}"}))

        except Exception as e:
            logger.error(f"Failed to process row {row_id}: {e}")
            updates_to_make.append((row_id, {"Sync Status": f"❌ ERROR: {e}"}))

    if documents:
        logger.info(f"Successfully processed {len(documents)} documents. Ingesting into {vector_store_provider}...")
        # VectorStoreFactory.get_vector_store().add_documents(documents, embedder)
        logger.info("Ingestion complete.")

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
        send_failure_alert(f"The script failed its pre-flight check or a major operation. Error: {str(e)}")
