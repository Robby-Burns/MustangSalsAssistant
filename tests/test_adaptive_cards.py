import pytest
import json
from jsonschema import validate
from app.ui.adaptive_cards import AdaptiveCardGenerator

def test_generate_quote_card():
    data = {"project_name": "Test Sign", "gross_margin": 0.40, "travel_sku": "TRV-1"}
    card = AdaptiveCardGenerator.generate_quote_draft_card(data)
    
    with open("schemas/adaptive_card_schema.json") as f:
        schema = json.load(f)
    validate(instance=card, schema=schema)
    
    assert card["type"] == "AdaptiveCard"
    assert "body" in card

def test_generate_margin_alert():
    card = AdaptiveCardGenerator.generate_margin_alert_card(0.20)
    assert card["type"] == "AdaptiveCard"
    assert "⚠️" in card["body"][0]["text"]
