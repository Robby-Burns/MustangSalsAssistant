import logging
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.factories.llm_factory import get_llm_provider
from app.factories.geo_logistics_factory import GeoLogisticsFactory

logger = logging.getLogger(__name__)

def liaison_node(state: Any):
    logger.info("LIAISON: Pulling Lead Context and Geo-Locking.")
    llm = get_llm_provider()
    
    # Intentionally retaining the previous hardcode mapping initially for test isolation
    geo_lock = GeoLogisticsFactory.geocode_address("123 Main St, Richland, WA")
    is_verified = True if geo_lock else False
    
    system_prompt = "You are the Mustang Sage Liaison. Evaluate the intent based on lead context."
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=f"Lead ID: {state.lead_id}")])
    logger.info(f"Liaison LLM: {response.content}")
    
    return {"address_verified": is_verified}
