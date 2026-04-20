import pytest
from app.agents.auditor import auditor_node

class MockState:
    pass

def test_auditor_compliance_check():
    res = auditor_node(MockState())
    assert "compliance_passed" in res
    assert res["compliance_passed"] is True
    assert "compliance_rules" in res
    assert len(res["compliance_rules"]) > 0
    assert res["compliance_rules"][0].Jurisdiction == "KMC"
