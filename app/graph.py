import logging
from typing import Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.config import config
from app.skills.geo_lock_guard import GeoLockGuard
from app.skills.margin_validator import MarginValidator
from app.factories.llm_factory import get_llm_provider
from langchain_core.messages import SystemMessage, HumanMessage
from app.factories.geo_logistics_factory import GeoLogisticsFactory
from app.skills.distance_calculator import DistanceCalculator
from app.factories.comm_template_engine import CommTemplateEngine

logger = logging.getLogger(__name__)

from typing import Optional, List
from app.models.core import LeadContext, ProjectRecipe, ComplianceRule, QuoteDraft, CommDraft

class SageState(BaseModel):
    lead_id: str = Field(default="UNKNOWN")
    lead_context: Optional[LeadContext] = None
    address_verified: bool = Field(default=False)
    recipe_found: bool = Field(default=False)
    project_recipe: Optional[ProjectRecipe] = None
    compliance_passed: bool = Field(default=False)
    compliance_rules: List[ComplianceRule] = Field(default_factory=list)
    travel_sku: str = Field(default="")
    quote_draft: Optional[QuoteDraft] = None
    draft_margin: float = Field(default=0.0)
    comm_draft: Optional[CommDraft] = None
    current_human_feedback: Optional[str] = None
    current_intent: str = Field(default="")

# Conditionally import real or mock agents based on config
if config.orchestration.agent_workflow_enabled:
    from app.agents.liaison import liaison_node
    from app.agents.archivist import archivist_node
    from app.agents.auditor import auditor_node
    from app.agents.merchant import merchant_node
else:
    logger.warning("Feature flag 'agent_workflow_enabled' is False. Using hollow backup routers.")
    def liaison_node(state): return {"address_verified": True}
    def archivist_node(state): return {"recipe_found": True}
    def auditor_node(state): return {"compliance_passed": True, "travel_sku": "TRV-MOCK"}
    def merchant_node(state): return {"draft_margin": 0.40}
    
def comm_node(state: SageState):
    logger.info(f"COMM MODE: Generating Draft outputs for intent: {state.current_intent}")
    intent_type = state.current_intent or "follow_up_email"
    cmp_dict = state.compliance_rules[0].model_dump() if state.compliance_rules else {"Max_Sq_Ft": 150, "Height_Limit_Ft": 30, "Illumination_Notes": "Mocked rules"}

    draft = CommTemplateEngine.process_comm_intent(
        state.lead_id, 
        intent_type, 
        {"contact_name": "Client", "project_type": "Signage", "lead_id": state.lead_id, "compliance": cmp_dict}
    )
    logger.info(f"Generated {draft.Draft_Type} with subject: {draft.Subject}")
    return {"comm_draft": draft}

def human_bridge_node(state: SageState):
    logger.info("HUMAN BRIDGE: Presentation ready. Halting for approval.")
    return {}

def check_human_approval(state: SageState):
    return "approved" if state.current_human_feedback == "approve" else "reviewing"

builder = StateGraph(SageState)
builder.add_node("liaison", liaison_node)
builder.add_node("archivist", archivist_node)
builder.add_node("auditor", auditor_node)
builder.add_node("merchant", merchant_node)
builder.add_node("comm", comm_node)
builder.add_node("human_bridge", human_bridge_node)

def route_liaison_intent(state: SageState):
    feedback = state.current_human_feedback.lower() if state.current_human_feedback else ""
    if any(kw in feedback for kw in ["email", "follow-up", "nudge", "send follow-up"]):
        return "comm"
    return "archivist"

builder.add_edge(START, "liaison")
builder.add_conditional_edges("liaison", route_liaison_intent, {"comm": "comm", "archivist": "archivist"})
builder.add_edge("archivist", "auditor")
builder.add_edge("auditor", "merchant")
builder.add_edge("merchant", "human_bridge")
builder.add_edge("comm", "human_bridge")
builder.add_conditional_edges("human_bridge", check_human_approval, {"approved": END, "reviewing": END})

memory = MemorySaver()
sage_graph = builder.compile(checkpointer=memory, interrupt_before=["human_bridge"])
