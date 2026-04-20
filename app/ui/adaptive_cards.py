import json
from typing import Dict, Any

class AdaptiveCardGenerator:
    """Generates MS Teams Adaptive Cards following strict JSON schema requirements."""
    
    @staticmethod
    def generate_quote_draft_card(quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a Quote Draft Card."""
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"Quote Draft: {quote_data.get('project_name', 'Unknown')}",
                    "size": "ExtraLarge",
                    "weight": "Bolder"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Gross Margin:", "value": f"{quote_data.get('gross_margin', 0.0) * 100:.1f}%"},
                        {"title": "Travel SKU:", "value": quote_data.get('travel_sku', 'N/A')}
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Approve & Submit",
                    "data": {"action": "approve_quote", "quote_id": quote_data.get('quote_id')}
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
