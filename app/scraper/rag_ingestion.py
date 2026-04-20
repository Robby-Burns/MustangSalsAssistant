import logging
from app.scraper.codepublishing_scraper import scrape_all_cities
from app.factories.embedder_factory import get_embedder_provider
from app.db import get_connection

logger = logging.getLogger(__name__)

def run_ingestion_pipeline():
    """Pulls full texts from the local City Code Scraper, splits it, vectorizes, and saves to DB."""
    logger.info("Initializing phase 4 Regulatory Code Ingestion...")
    
    cities_data = scrape_all_cities(return_text=True)
    embedder = get_embedder_provider()
    
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
    except ImportError:
        logger.error("langchain-text-splitters not installed.")
        return

    conn = get_connection()
    if not conn:
        logger.warning("No DB connection to insert RAG chunks. MOCKING output.")
        return
        
    inserted_count = 0
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS compliance_rules (
                    id bigserial PRIMARY KEY,
                    city text,
                    content text,
                    embedding vector(1536)
                );
            """)
            
            for city, content_dict in cities_data.items():
                if "error" in content_dict:
                    logger.warning(f"Skipping {city} due to scrape error.")
                    continue
                    
                raw_text = content_dict.get("raw_text", "")
                chunks = text_splitter.split_text(raw_text)
                
                logger.info(f"Vectorizing {len(chunks)} chunks for {city}...")
                
                # We could batch embed_documents, but doing iter for resilience
                for chunk in chunks:
                    try:
                        embedding = embedder.embed_query(chunk)
                        cur.execute(
                            "INSERT INTO compliance_rules (city, content, embedding) VALUES (%s, %s, %s::vector)",
                            (city, chunk, embedding)
                        )
                        inserted_count += 1
                    except Exception as loop_e:
                        logger.error(f"Failed to vector/insert chunk: {loop_e}")
                        
        conn.commit()
        logger.info(f"Ingestion Complete. Inserted {inserted_count} vectorized chunks.")
    except Exception as e:
        logger.error(f"Failed to complete ingestion to database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_ingestion_pipeline()
