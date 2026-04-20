import pytest
from scripts.run_scheduler import check_stale_quotes
from unittest.mock import patch

@patch('scripts.run_scheduler.requests.post')
def test_check_stale_quotes(mock_post):
    # Execute the mock script
    check_stale_quotes()
    
    # Assert that requests.post was called twice (for the 2 mock stale quotes)
    assert mock_post.call_count == 2
    
    # Assert the endpoint hit was correct
    mock_post.assert_any_call(
        "http://mustang-whisper:8000/teams/nudge",
        json={"quote_id": "SQ-10023"},
        timeout=5
    )
    mock_post.assert_any_call(
        "http://mustang-whisper:8000/teams/nudge",
        json={"quote_id": "SQ-10024"},
        timeout=5
    )
