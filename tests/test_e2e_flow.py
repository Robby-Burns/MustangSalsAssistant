from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_pipeline_run():
    """
    Validates that the MS Teams HTTP endpoint successfully engages the 
    LangGraph `sage_graph` state machine through the HITL pause and resume.
    """
    # 1. Fresh Run payload targeting shopVOX lead mock
    payload1 = {"text": "LD-12345"}
    resp1 = client.post("/api/messages", json=payload1, headers={"Content-Type": "application/json"})
    assert resp1.status_code == 200
    
    # 2. Resume Run payload (Human-in-the-Loop "approve" command)
    payload2 = {"text": "approve"}
    resp2 = client.post("/api/messages", json=payload2, headers={"Content-Type": "application/json"})
    assert resp2.status_code == 200
