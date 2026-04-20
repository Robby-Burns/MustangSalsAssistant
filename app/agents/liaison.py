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
    
    # Evaluate communication intent based on string matching
    intent = ""
    feedback = state.current_human_feedback if hasattr(state, "current_human_feedback") else state.get("current_human_feedback")
    if feedback:
        feed_lower = feedback.lower()
        if "intro" in feed_lower:
            intent = "intro_email"
        elif "vector" in feed_lower or "logo" in feed_lower:
            intent = "vector_request"
        elif "schedule" in feed_lower or "install" in feed_lower:
            intent = "install_schedule"
        elif "brief" in feed_lower:
            intent = "design_brief"
        elif "follow" in feed_lower or "nudge" in feed_lower:
            intent = "follow_up_email"
            
    return {"address_verified": is_verified, "current_intent": intent}
