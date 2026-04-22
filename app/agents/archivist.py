import logging
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.factories.llm_factory import get_llm_provider
from app.models.core import ProjectRecipe

logger = logging.getLogger(__name__)

def archivist_node(state: Any):
    logger.info("ARCHIVIST: Searching for project recipes.")
    llm = get_llm_provider()
    
    system_prompt = "You are the Archivist. Formulate a search query for S3/vector recipes based on project type."
    # Use the actual project type from the lead context for a better query
    project_type_query = f"Search for similar {state.lead_context.Project_Type}" if state.lead_context else "Search for similar monument signs."
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=project_type_query)])
    logger.info(f"Archivist LLM query: {response.content}")
    
    from app.factories.s3_vector_factory import S3VectorFactory
    
    query_string = response.content if len(response.content) < 50 else "monument sign"
    
    # Primary semantic search
    search_results = S3VectorFactory.semantic_search(query_string, k=1)
    
    project_recipe = None
    recipe_found = False

    if search_results and 'id' in search_results[0]:
        recipe_id = search_results[0]['id']
        logger.info(f"ARCHIVIST: Semantic search found potential recipe ID: {recipe_id}. Fetching full recipe.")
        # Fetch the full, validated recipe object using the ID
        recipe_data = S3VectorFactory.get_recipe_by_id(recipe_id)
        if recipe_data:
            project_recipe = ProjectRecipe(**recipe_data)
            recipe_found = True
            logger.info(f"ARCHIVIST: Successfully retrieved and validated recipe {recipe_id} from S3.")
    else:
        # Secondary fallback search
        logger.info("ARCHIVIST: No semantic match. Falling back to raw S3 legacy search.")
        legacy_results = S3VectorFactory.raw_s3_legacy(query_string)
        if legacy_results and 'Recipe_ID' in legacy_results[0]:
            recipe_id = legacy_results[0]['Recipe_ID']
            logger.info(f"ARCHIVIST: Legacy search found recipe ID: {recipe_id}. Fetching full recipe.")
            recipe_data = S3VectorFactory.get_recipe_by_id(recipe_id)
            if recipe_data:
                project_recipe = ProjectRecipe(**recipe_data)
                recipe_found = True
                logger.info(f"ARCHIVIST: Successfully retrieved and validated legacy recipe {recipe_id}.")
        else:
            logger.warning("ARCHIVIST: No recipe found in either semantic or legacy search.")
            
    return {"recipe_found": recipe_found, "project_recipe": project_recipe}
