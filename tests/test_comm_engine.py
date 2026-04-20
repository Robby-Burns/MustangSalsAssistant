import pytest
from app.graph import SageState, comm_node
from app.agents.liaison import liaison_node

@pytest.mark.parametrize("feedback, expected_intent, expected_subject", [
    ("Please draft an intro email for this client", "intro_email", "Welcome to Mustang Signs!"),
    ("Ask them for a vector logo", "vector_request", "Artwork Request for Your Signage Project"),
    ("Schedule the install for next week", "install_schedule", "Scheduling Your Sign Installation"),
    ("Write a design brief", "design_brief", "Design Brief"),
    ("Follow up with them", "follow_up_email", "Following Up on Your Quote"),
])
def test_comm_engine_dynamic_intents(feedback, expected_intent, expected_subject):
    # 1. Instantiate SageState with human feedback
    state = SageState(lead_id="L123", current_human_feedback=feedback)
    
    # 2. Execute liaison_node and verify current_intent
    result_state_dict = liaison_node(state)
    assert result_state_dict.get("current_intent") == expected_intent
    
    # Update state with liaison's output (simulating graph execution)
    state.current_intent = result_state_dict.get("current_intent")
    
    # 3. Call comm_node and assert CommDraft correctness
    comm_result = comm_node(state)
    draft = comm_result.get("comm_draft")
    
    assert draft is not None
    assert draft.Draft_Type == expected_intent
    assert expected_subject in draft.Subject
    assert "[L123]" in draft.Subject
    assert draft.Body is not None
    assert len(draft.Body) > 0
    assert draft.Review_Required is True
    assert draft.Status == "draft"
