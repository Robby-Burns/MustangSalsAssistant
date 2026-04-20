import os
import psycopg2
from pgvector.psycopg2 import register_vector
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("NEON_DATABASE_URL", "postgresql://user:password@localhost/mustangsage")

def get_connection():
    """Establish a connection to Neon Postgres with exponential backoff.
    """
    @retry(
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(psycopg2.OperationalError),
    )
    def _connect():
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        register_vector(conn)
        return conn

    try:
        return _connect()
    except Exception as e:
        logger.error(f"Failed to connect to Neon DB after retries: {e}")
        return None

def init_db():
    """Initializes the database schema for the Archivist's vectorized sandbox."""
    conn = get_connection()
    if not conn:
        logger.warning("Skipping DB initialization (No connection).")
        return
        
    try:
        with conn.cursor() as cur:
            # Enable pgvector if it doesn't exist
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create our recipe table mimicking the S3VectorFactory sandbox requirements
            cur.execute("""
                CREATE TABLE IF NOT EXISTS project_recipes (
                    id bigserial PRIMARY KEY,
                    project_type text,
                    zoning_tags text[],
                    content text,
                    embedding vector(1536)
                );
            """)
        conn.commit()
        logger.info("Neon Vector database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
