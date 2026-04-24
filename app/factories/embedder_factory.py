import os
from langchain_core.embeddings import Embeddings
import logging

logger = logging.getLogger(__name__)

class MockEmbeddings(Embeddings):
    """Provides a zero-layer mock when API keys are absent."""
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]
        
    def embed_query(self, text):
        return [0.0] * 1536

from app.config import config

def get_embedder_provider() -> Embeddings:
    """Agnostic factory returning an active LangChain Embedder."""
    provider = config.llm.embedder.provider.lower()
    
    if provider in {"gemini", "google"}:
        if not os.getenv("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY missing. Returning MockEmbeddings.")
            return MockEmbeddings()
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY missing. Returning MockEmbeddings.")
            return MockEmbeddings()
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings()
        
    else:
        raise ValueError(f"Unknown EMBEDDER_PROVIDER: {provider}")
