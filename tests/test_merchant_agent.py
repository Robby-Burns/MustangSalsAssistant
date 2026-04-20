import pytest
from app.agents.merchant import merchant_node

class MockState:
    pass

def test_merchant_quoting_margin():
    res = merchant_node(MockState())
    assert "draft_margin" in res
    assert res["draft_margin"] > 0
