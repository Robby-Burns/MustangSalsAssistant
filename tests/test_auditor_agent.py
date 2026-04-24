import pytest
from types import SimpleNamespace
from app.agents.auditor import auditor_node

def test_auditor_compliance_check():
    state = SimpleNamespace(
        address_verified=True,
        lead_context=SimpleNamespace(
            Address_Input="123 Main St, Kennewick, WA",
            Address_Geo_Lock={"lat": 46.2114, "lng": -119.1373},
        ),
    )
    res = auditor_node(state)
    assert "compliance_passed" in res
    assert res["compliance_passed"] is True
    assert "compliance_rules" in res
    assert len(res["compliance_rules"]) > 0
    assert res["compliance_rules"][0].Jurisdiction == "KMC"
    assert res["travel_sku"].startswith("TRV-")
