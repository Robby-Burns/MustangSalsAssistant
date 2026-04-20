import pytest
from app.agents.archivist import archivist_node

class MockState:
    lead_id = "LD-TEST-123"

def test_archivist_vector_query():
    res = archivist_node(MockState())
    assert "recipe_found" in res
    assert isinstance(res["recipe_found"], bool)
