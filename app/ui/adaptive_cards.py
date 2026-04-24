import json
from typing import Dict, Any

class AdaptiveCardGenerator:
    """Generates MS Teams Adaptive Cards following strict JSON schema requirements."""
    
    @staticmethod
    def generate_quote_draft_card(quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a Quote Draft Card."""
        project_name = quote_data.get("Project_Name", quote_data.get("project_name", "Unknown"))
        margin_pct = quote_data.get("Gross_Margin_Pct", quote_data.get("gross_margin", quote_data.get("gross_margin_pct", 0.0)))
        travel_sku = quote_data.get("Travel_SKU", quote_data.get("travel_sku", "N/A"))
        quote_id = quote_data.get("Quote_ID", quote_data.get("quote_id"))
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"Quote Draft: {project_name}",
                    "size": "ExtraLarge",
                    "weight": "Bolder"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Gross Margin:", "value": f"{margin_pct * 100:.1f}%"},
                        {"title": "Travel SKU:", "value": travel_sku}
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Approve & Submit",
                    "data": {"action": "approve_quote", "quote_id": quote_id}
                }
            ]
        }
    
    @staticmethod
    def generate_margin_alert_card(margin: float) -> Dict[str, Any]:
        """Creates a Margin Alert Warning."""
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "⚠️ MARGIN FLOOR BREACH",
                    "color": "Attention",
                    "size": "ExtraLarge",
                    "weight": "Bolder"
                },
                {
                    "type": "TextBlock",
                    "text": f"Proposed margin {margin * 100:.1f}% is below 35% minimum.",
                    "wrap": True
                }
            ]
        }
