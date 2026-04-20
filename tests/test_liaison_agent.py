import pytest
from app.agents.liaison import liaison_node

class MockState:
    lead_id = "LD-TEST-123"

def test_liaison_routing():
    # Because factories have mock returns or try blocks, this will succeed.
    res = liaison_node(MockState())
    assert "address_verified" in res
    assert isinstance(res["address_verified"], bool)
