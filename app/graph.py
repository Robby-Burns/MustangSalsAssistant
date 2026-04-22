import logging
from typing import Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
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

# The global state object that flows between agents
class SageState(BaseModel):
    # See mustang_whisper_system_prompt.md (State Schema)
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
    
import os
import yaml

try:
    with open("config/scale.yaml", "r") as f:
        _cfg = yaml.safe_load(f)
        ENABLE_NEW_AGENTS = _cfg.get("orchestration", {}).get("enable_new_agents", False)
except Exception:
    ENABLE_NEW_AGENTS = False

if ENABLE_NEW_AGENTS:
    from app.agents.liaison import liaison_node
    from app.agents.archivist import archivist_node
    from app.agents.auditor import auditor_node
    from app.agents.merchant import merchant_node
else:
    logger.warning("Feature flag ENABLE_NEW_AGENTS=False. Using hollow backup routers.")
    def liaison_node(state): return {"address_verified": True}
    def archivist_node(state): return {"recipe_found": True}
    def auditor_node(state): return {"compliance_passed": True, "travel_sku": "TRV-MOCK"}
    def merchant_node(state): return {"draft_margin": 0.40}
    
# 5. The Communicator (Comm Mode)
def comm_node(state: SageState):
    logger.info(f"COMM MODE: Generating Draft outputs for intent: {state.current_intent}")
    intent_type = state.current_intent if hasattr(state, "current_intent") and state.current_intent else "follow_up_email"
    # Safely extract compliance dict for Jinja templates
    cmp_dict = {}
    if state.compliance_rules:
        cmp_dict = state.compliance_rules[0].model_dump()
    else:
        cmp_dict = {"Max_Sq_Ft": 150, "Height_Limit_Ft": 30, "Illumination_Notes": "Mocked rules"}

    draft = CommTemplateEngine.process_comm_intent(
        state.lead_id, 
        intent_type, 
        {
            "contact_name": "Client", 
            "project_type": "Signage", 
            "lead_id": state.lead_id, 
            "compliance": cmp_dict
        }
    )
    logger.info(f"Generated {draft.Draft_Type} with subject: {draft.Subject}")
    return {"comm_draft": draft}

# 6. Human-in-the-loop Bridge
def human_bridge_node(state: SageState):
    logger.info("HUMAN BRIDGE: Presentation ready. Halting for approval.")
    return {}

# Gatekeeper router
def check_human_approval(state: SageState):
    """Routes based on whether humanity approved the draft."""
    feedback = state.current_human_feedback
    if feedback == "approve":
        return "approved"
    return "reviewing"

# Initialize graph architecture
builder = StateGraph(SageState)

# Add all agents
builder.add_node("liaison", liaison_node)
builder.add_node("archivist", archivist_node)
builder.add_node("auditor", auditor_node)
builder.add_node("merchant", merchant_node)
builder.add_node("comm", comm_node)
builder.add_node("human_bridge", human_bridge_node)

def route_liaison_intent(state: SageState):
    """Dynamic Edge resolving execution intention."""
    if state.current_human_feedback and "email" in state.current_human_feedback.lower():
        return "comm"
    return "archivist"

# Flow logic mapping directly to AgentSpec
builder.add_edge(START, "liaison")
builder.add_conditional_edges("liaison", route_liaison_intent, {
    "comm": "comm",
    "archivist": "archivist"
})
builder.add_edge("archivist", "auditor")
builder.add_edge("auditor", "merchant")
builder.add_edge("merchant", "human_bridge")
builder.add_edge("comm", "human_bridge")

# The graph stays halted at the bridge or ends if approved
builder.add_conditional_edges(
    "human_bridge",
    check_human_approval,
    {
        "approved": END,
        "reviewing": END # A true implementation would use a Memory checkpoint here to halt.
    }
)

memory = MemorySaver()
# Define the interruption barrier at the human_bridge
# See mustang_whisper_system_prompt.md (Human-In-The-Loop protocol)
sage_graph = builder.compile(checkpointer=memory, interrupt_before=["human_bridge"])
