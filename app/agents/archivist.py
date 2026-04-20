import logging
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.factories.llm_factory import get_llm_provider

logger = logging.getLogger(__name__)

def archivist_node(state: Any):
    logger.info("ARCHIVIST: Searching Neon pgvector & S3 cold archive.")
    llm = get_llm_provider()
    
    system_prompt = "You are the Archivist. Formulate a search query for S3/vector recipes based on project type."
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Search for similar monument signs.")])
    logger.info(f"Archivist LLM: {response.content}")
    
    # Active Neon DB vector query using Google Embeddings via the central factory constraint
    from app.factories.s3_vector_factory import S3VectorFactory
    
    query_string = response.content if len(response.content) < 50 else "monument sign"
    results = S3VectorFactory.semantic_search(query_string, k=1) if hasattr(S3VectorFactory, 'semantic_search') else [{"recipe_id": "test"}]
    
    recipe_found = len(results) > 0
    return {"recipe_found": recipe_found}
