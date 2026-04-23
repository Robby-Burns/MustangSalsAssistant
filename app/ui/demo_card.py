from typing import Dict, Any

class DemoCardGenerator:
    """
    Generates a high-quality, detailed Adaptive Card for demonstration purposes.
    This card represents a "best-case scenario" output from the Mustang Sage bot.
    """

    @staticmethod
    def generate_demo_card() -> Dict[str, Any]:
        """Creates a comprehensive Quote Draft card with mock data."""
        
        # This mock data is based on the QuoteDraft model and the templates
        # found in the mustang_sage_v2_4_0_complete.md manifest.
        mock_quote_data = {
            "project_name": "Acme Corp. HQ - Freestanding Monument",
            "address": "123 Main St, Kennewick, WA",
            "project_type": "Monument Sign",
            "gross_margin_pct": 0.38,
            "travel_sku": "TRV-ZONE1",
            "quote_id": "SQ-DEMO-123"
        }

        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "emphasis",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"📋 QUOTE DRAFT: {mock_quote_data['project_name']}",
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"{mock_quote_data['address']} | {mock_quote_data['project_type']}",
                            "isSubtle": True,
                            "spacing": "None"
                        }
                    ],
                    "bleed": True
                },
                {
                    "type": "FactSet",
                    "spacing": "Large",
                    "facts": [
                        {
                            "title": "Compliance Checklist",
                            "value": "✅ All checks passed"
                        },
                        {
                            "title": "Max Height (KMC 18.24)",
                            "value": "10ft Limit / **8ft Actual**"
                        },
                        {
                            "title": "Setback (KMC 18.24)",
                            "value": "5ft from property line"
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "spacing": "Medium",
                    "facts": [
                        {
                            "title": "Margin Summary",
                            "value": f"**{mock_quote_data['gross_margin_pct'] * 100:.1f}%** (Healthy)"
                        },
                        {
                            "title": "Applied Fees",
                            "value": f"Travel SKU: {mock_quote_data['travel_sku']}"
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Approve & Send to Sandbox",
                    "style": "positive",
                    "data": {"action": "approve_quote", "quote_id": mock_quote_data['quote_id']}
                },
                {
                    "type": "Action.ShowCard",
                    "title": "Edit Scope",
                    "card": {
                        "type": "AdaptiveCard",
                        "body": [
                            {
                                "type": "Input.Text",
                                "id": "changes_requested",
                                "placeholder": "e.g., 'Change to a double-sided pylon sign.'",
                                "isMultiline": True
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.Submit",
                                "title": "Submit Changes"
                            }
                        ]
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "Dismiss",
                    "style": "destructive",
                    "data": {"action": "dismiss"}
                }
            ]
        }
        return card
