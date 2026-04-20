import time
import logging
import threading
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

class RateLimitExceededException(Exception):
    pass

class ShopvoxFactory:
    """
    Handles ShopVOX API connections, enforcing rate limits 
    (300 calls / 5 mins -> <= 1 call/sec).
    """

    def __init__(self):
        # Thread-safe rate limiter (Token bucket analogue)
        self._lock = threading.Lock()
        self._last_call_time = 0.0
        self._min_interval = 1.05  # >1 sec to stay under 300 / 300 seconds

    def _block_until_ready(self):
        """Enforces < 1 call per second globally across this instance using a thread lock.
        # See mustang_whisper_system_prompt.md (Guardrails on Target Endpoints & Rate Limits)
        """
        with self._lock:
            now = time.time()
            elapsed = now - self._last_call_time
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_call_time = time.time()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(RateLimitExceededException)
    )
    def search_products(self, query: str):
        self._block_until_ready()
        
        import requests, os
        api_key = os.getenv("SHOPVOX_API_KEY")
        if not api_key:
            logger.info(f"Mocking ShopVOX search for: {query}")
            return [{"sku": "TRV-ZONE2", "price": 150.0}, {"sku": "MONUMENT-8FT", "price": 4500.0}]
            
        logger.info(f"Live ShopVOX search: {query}")
        resp = requests.get(
            "https://api.shopvox.com/v1/products", 
            params={"q": query},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 429: raise RateLimitExceededException()
        resp.raise_for_status()
        return resp.json().get("data", [])

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(RateLimitExceededException)
    )
    def create_quote_draft(self, draft_data: dict):
        self._block_until_ready()
        
        import requests, os
        api_key = os.getenv("SHOPVOX_API_KEY")
        if not api_key:
            logger.info("Mocking Quote Draft Creation in Sandbox.")
            return {"status": "success", "draft_id": "SQ-99238"}
            
        resp = requests.post(
            "https://api.shopvox.com/v1/quotes",
            json=draft_data,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 429: raise RateLimitExceededException()
        resp.raise_for_status()
        return resp.json()
        
    def get_lead_context(self, lead_id: str):
        self._block_until_ready()
        import requests, os
        api_key = os.getenv("SHOPVOX_API_KEY")
        if not api_key:
            logger.info(f"Pulling mockup lead context for {lead_id}")
            return {"Lead_ID": lead_id, "Address_Geo_Lock": None, "Pipeline_Stage": "Quoting"}
            
        resp = requests.get(
            f"https://api.shopvox.com/v1/leads/{lead_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 429: raise RateLimitExceededException()
        resp.raise_for_status()
        return resp.json()
