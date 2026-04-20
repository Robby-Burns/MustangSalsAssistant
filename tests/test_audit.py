import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_audit_endpoints_unauthorized():
    """Ensure endpoints are protected via X-Audit-Key."""
    # Should fail with 403 Forbidden
    response_run = client.post("/audit/run")
    assert response_run.status_code == 403
    
    response_cve = client.post("/audit/cve-check")
    assert response_cve.status_code == 403

def test_audit_endpoints_authorized():
    """Ensure endpoints execute fully when authorized."""
    # Set fake audit key for the test env
    fake_key = "test_super_secret"
    os.environ["AUDIT_API_KEY"] = fake_key
    
    headers = {"X-Audit-Key": fake_key}
    
    response_run = client.post("/audit/run", headers=headers)
    assert response_run.status_code == 200
    assert "status" in response_run.json()
    assert response_run.json()["status"] == "completed"
    
    response_cve = client.post("/audit/cve-check", headers=headers)
    assert response_cve.status_code == 200
    assert "status" in response_cve.json()
    assert response_cve.json()["status"] == "completed"
