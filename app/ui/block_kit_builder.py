from typing import Dict, Any, List

class BlockKitBuilder:
    """Generates Slack Block Kit UI elements following strict JSON schema."""

    @staticmethod
    def _create_header(title: str) -> Dict[str, Any]:
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title,
                "emoji": True
            }
        }

    @staticmethod
    def _create_section(text: str) -> Dict[str, Any]:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }

    @staticmethod
    def _create_divider() -> Dict[str, Any]:
        return {"type": "divider"}

    @staticmethod
    def generate_quote_draft_card(quote_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Creates a Quote Draft Block Kit UI."""
        project_name = quote_data.get('project_name', 'Unknown')
        margin_pct = quote_data.get('gross_margin_pct', 0.0) * 100
        travel_sku = quote_data.get('travel_sku', 'N/A')
        quote_id = quote_data.get('quote_id')

        blocks = [
            BlockKitBuilder._create_header(f"📋 Quote Draft: {project_name}"),
            BlockKitBuilder._create_section(f"*Gross Margin:* {margin_pct:.1f}%\n*Travel SKU:* {travel_sku}"),
            BlockKitBuilder._create_divider(),
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve & Submit"
                        },
                        "style": "primary",
                        "value": quote_id,
                        "action_id": "approve_quote"
                    }
                ]
            }
        ]
        return blocks

    @staticmethod
    def generate_margin_alert_card(margin: float) -> List[Dict[str, Any]]:
        """Creates a Margin Alert Block Kit UI."""
        return [
            BlockKitBuilder._create_header("⚠️ Margin Floor Breached"),
            BlockKitBuilder._create_section(f"Proposed margin of *{margin * 100:.1f}%* is below the 35% minimum.")
        ]
