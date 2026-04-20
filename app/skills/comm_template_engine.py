import logging

logger = logging.getLogger(__name__)

class CommTemplateEngine:
    """Safely constructs standardized outbound communications enforcing compliance headers."""
    
    @classmethod
    def draft_email(cls, lead_id: str, prompt: str) -> dict:
        """Constructs an email template with mandatory headers."""
        header = "[DRAFT FOR REVIEW]\n\n"
        body = f"Generated email for {lead_id} based on intent: {prompt}\n\nPlease review and send."
        return {
            "Draft_Type": "Email",
            "Subject": f"[DRAFT FOR REVIEW] Project Update - {lead_id}",
            "Body": header + body,
            "Grounded_To": lead_id,
            "Review_Required": True
        }
        
    @classmethod
    def draft_design_brief(cls, lead_id: str, prompt: str) -> dict:
        """Constructs a design brief template with mandatory headers."""
        header = "[DRAFT FOR REVIEW]\n\n"
        body = f"Design brief notes for {lead_id}: {prompt}\n\nPlease review before passing to art dept."
        return {
            "Draft_Type": "Design Brief",
            "Subject": f"[DRAFT FOR REVIEW] Design Brief - {lead_id}",
            "Body": header + body,
            "Grounded_To": lead_id,
            "Review_Required": True
        }
