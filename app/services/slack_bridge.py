import os
import logging
import requests

logger = logging.getLogger(__name__)

class SlackBridge:
    """Wrapper for routing high-priority system alerts and 
    Teams backup messages successfully to Slack."""
    
    @staticmethod
    def send_notification(message: str) -> bool:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        # In sandboxes where SLACK_WEBHOOK_URL is not set, we playfully mock the success.
        if not webhook_url:
            logger.info(f"Mocking Slack Notification: {message}")
            return True
            
        try:
            payload = {"text": message}
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info("Successfully pushed notification to Slack.")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to push to Slack webhook: {e}")
            return False
