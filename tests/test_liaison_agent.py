import pytest
from app.agents.liaison import liaison_node

class MockState:
    def __init__(self, lead_id):
        self.lead_id = lead_id
    
    def get(self, key, default=None):
        return getattr(self, key, default)

def test_liaison_success_with_mock_lead():
    # LD-123 is a valid mock lead in shopvox_factory.py
    state = MockState("LD-123")
    res = liaison_node(state)
    
    assert res["lead_context"] is not None
    assert res["lead_context"].Lead_ID == "LD-123"
    assert res["lead_context"].Company == "Acme Corp"
    assert res["address_verified"] is True
    assert res["current_intent"] == ""

def test_liaison_failure_with_invalid_lead():
    state = MockState("LD-INVALID")
    res = liaison_node(state)
    
    assert res["lead_context"] is None
    assert res["address_verified"] is False
    assert res["current_intent"] == "error_halt"
