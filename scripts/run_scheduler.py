import time
import schedule
import logging
import os
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_stale_quotes():
    logger.info("Scheduler: Scanning for QuoteDrafts older than 72 hours...")
    # Mocking database connection logic for API safety over sandbox
    # Ideally: db.execute("SELECT quote_id FROM quote_drafts WHERE updated_at < NOW() - INTERVAL '3 days'")
    stale_quotes = ["SQ-10023", "SQ-10024"]
    
    for qid in stale_quotes:
        logger.info(f"Triggering Nudge for Quote {qid}")
        try:
            requests.post(
                "http://mustang-whisper:8000/teams/nudge",
                json={"quote_id": qid},
                timeout=5
            )
        except Exception as e:
            logger.error(f"Failed triggering nudge for {qid}: {e}")

if __name__ == "__main__":
    logger.info("Mustang Whisper Scheduler initialized.")
    # For Phase 2 sandbox testing, we will run it every 1 minute instead of every 24 hours.
    schedule.every(1).minutes.do(check_stale_quotes)
    
    while True:
        schedule.run_pending()
        time.sleep(5)
