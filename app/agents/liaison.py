import logging
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.factories.llm_factory import get_llm_provider
from app.factories.geo_logistics_factory import GeoLogisticsFactory
from app.factories.shopvox_factory import ShopvoxFactory
from app.models.core import LeadContext

logger = logging.getLogger(__name__)

def liaison_node(state: Any):
    logger.info(f"LIAISON: Pulling Lead Context for Lead ID: {state.lead_id}")
    
    shopvox_factory = ShopvoxFactory()
    lead_context_data = shopvox_factory.get_lead_context(state.lead_id)
    
    lead_context = None
    is_verified = False
    
    if lead_context_data:
        try:
            lead_context = LeadContext(**lead_context_data)
            logger.info(f"Successfully loaded LeadContext for {state.lead_id}")
            
            # Geo-Locking
            address = lead_context.Address_Input if lead_context.Address_Input else "Unknown"
            geo_lock = GeoLogisticsFactory.geocode_address(address)
            if geo_lock:
                is_verified = True
                lead_context.Address_Geo_Lock = geo_lock
                logger.info(f"Address '{address}' verified and geo-locked.")
            else:
                logger.warning(f"Address '{address}' could not be verified.")
        except Exception as e:
            logger.error(f"Failed to parse LeadContext data for {state.lead_id}. Error: {e}")
            # Halt gracefully if data is malformed
            # In a real scenario, you might return a specific error card to the user
            return {"lead_context": None, "address_verified": False, "current_intent": "error_halt"}
    else:
        logger.error(f"Could not retrieve LeadContext for Lead ID: {state.lead_id}. Halting workflow.")
        # Halt gracefully if no lead data is found
        return {"lead_context": None, "address_verified": False, "current_intent": "error_halt"}

    # Intent Routing
    llm = get_llm_provider()
    system_prompt = "You are the Mustang Sage Liaison. Evaluate the intent based on lead context."
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=f"Lead ID: {state.lead_id}")])
    logger.info(f"Liaison LLM response for intent: {response.content}")
    
    intent = ""
    # Use getattr for safety or direct access if state is guaranteed to be SageState
    feedback = getattr(state, "current_human_feedback", None)
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
        elif any(kw in feed_lower for kw in ["follow", "nudge", "send follow-up"]):
            intent = "follow_up_email"
            
    return {
        "lead_context": lead_context,
        "address_verified": is_verified, 
        "current_intent": intent
    }
