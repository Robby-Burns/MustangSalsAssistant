import logging
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.models.core import CommDraft
from datetime import datetime

logger = logging.getLogger(__name__)

# Identify template directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "emails")

class CommFactory:
    """Uses Jinja2 to automatically draft reliable templated outputs for the Liaison agent."""
    
    @classmethod
    def process_comm_intent(cls, lead_id: str, intent_type: str, context: dict) -> CommDraft:
        """Renders a Jinja2 template perfectly mapped to the CommDraft schema."""
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR) if os.path.exists(TEMPLATE_DIR) else None,
            autoescape=select_autoescape()
        )
        
        draft_id = f"DRF-{int(datetime.now().timestamp())}"
        
        if intent_type == "design_brief":
            if os.path.exists(os.path.join(TEMPLATE_DIR, "design_brief.j2")):
                template = env.get_template("design_brief.j2")
                body = template.render(**context)
            else:
                body = f"Mocked Design Brief for Lead {lead_id}\nContext: {context}"
                
            return CommDraft(
                Draft_ID=draft_id,
                Draft_Type="design_brief",
                Grounded_To=lead_id,
                Subject=f"Design Brief [{lead_id}]",
                Body=body,
                Review_Required=True,
                Status="draft"
            )
            
        elif intent_type == "follow_up":
            if os.path.exists(os.path.join(TEMPLATE_DIR, "follow_up.j2")):
                template = env.get_template("follow_up.j2")
                body = template.render(**context)
            else:
                body = f"Mocked Follow-Up for Lead {lead_id}\nContext: {context}"
                
            return CommDraft(
                Draft_ID=draft_id,
                Draft_Type="follow_up_email",
                Grounded_To=lead_id,
                Subject=f"Following Up on Your Quote [{lead_id}]",
                Body=body,
                Review_Required=True,
                Status="draft"
            )
        
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
