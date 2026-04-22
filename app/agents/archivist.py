import logging
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.factories.llm_factory import get_llm_provider
from app.models.core import ProjectRecipe
from app.factories.vector_store_factory import VectorStoreFactory

logger = logging.getLogger(__name__)

def archivist_node(state: Any):
    logger.info("ARCHIVIST: Searching for project recipes.")
    llm = get_llm_provider()
    
    project_type_query = f"Search for similar {state.lead_context.Project_Type}" if state.lead_context else "Search for similar monument signs."
    response = llm.invoke([SystemMessage(content="You are the Archivist. Formulate a search query for recipes based on project type."), HumanMessage(content=project_type_query)])
    logger.info(f"Archivist LLM query: {response.content}")

    query_string = response.content if len(response.content) < 50 else "monument sign"
    
    # Use the main VectorStoreFactory for all searches
    search_results = VectorStoreFactory.semantic_search(query_string, k=1)
    
    project_recipe = None
    recipe_found = False

    if search_results and 'id' in search_results[0]:
        recipe_id = search_results[0]['id']
        logger.info(f"ARCHIVIST: Semantic search found recipe ID: {recipe_id}. Fetching full recipe.")
        # In a real S3 implementation, this would fetch the full object. Here we mock it.
        recipe_data = {"Recipe_ID": recipe_id, "Project_Type": search_results[0].get('project_type'), "Part_List": [], "Labor_Hours": 0, "Zoning_Tags": [], "Source_Bucket": "s3"}
        if recipe_data:
            project_recipe = ProjectRecipe(**recipe_data)
            recipe_found = True
            logger.info(f"ARCHIVIST: Successfully retrieved recipe {recipe_id}.")
    else:
        logger.warning("ARCHIVIST: No recipe found in vector store.")
            
    return {"recipe_found": recipe_found, "project_recipe": project_recipe}
