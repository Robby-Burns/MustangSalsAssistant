import time
import logging
import threading
import os
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

class RateLimitExceededException(Exception):
    pass

# --- Mock Data for Demo Mode ---
_MOCK_LEADS = {
    "LD-123": {
        "Lead_ID": "LD-123", 
        "Contact_Name": "John Smith", 
        "Company": "Acme Corp", 
        "Project_Type": "Monument Sign", 
        "Address_Input": "123 Main St, Kennewick, WA",
        "Pipeline_Stage": "Discovery",
        "Last_Activity_Date": "2026-04-20T10:00:00",
        "Open_Notes": "Customer wants a backlit monument sign."
    },
    "LD-456": {
        "Lead_ID": "LD-456", 
        "Contact_Name": "Jane Doe", 
        "Company": "Pylon Inc.", 
        "Project_Type": "Pylon Sign", 
        "Address_Input": "456 Industrial Way, Richland, WA",
        "Pipeline_Stage": "Quoting",
        "Last_Activity_Date": "2026-04-21T14:30:00",
        "Open_Notes": "Interested in a 20ft pylon."
    },
}
_MOCK_PRODUCTS = {
    "monument sign": [{"sku": "MONUMENT-8FT", "price": 4500.0}],
    "pylon sign": [{"sku": "PYLON-20FT", "price": 12500.0}],
}
# --- End Mock Data ---

class ShopvoxFactory:
    """
    Handles ShopVOX API connections. If APP_MODE is 'demo' or the API key is missing,
    it operates in a dynamic "demo mode" using a local dictionary of mock data.
    """
    def __init__(self):
        self._is_demo_mode = os.getenv("APP_MODE", "production").lower() == 'demo' or not os.getenv("SHOPVOX_API_KEY")
        if self._is_demo_mode:
            logger.warning("ShopvoxFactory is running in DEMO MODE.")
        self._lock = threading.Lock()
        self._last_call_time = 0.0
        self._min_interval = 1.05

    def _block_until_ready(self):
        with self._lock:
            now = time.time()
            elapsed = now - self._last_call_time
            wait_time = self._min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            self._last_call_time = time.time()

    def get_lead_context(self, lead_id: str):
        self._block_until_ready()
        if self._is_demo_mode:
            logger.info(f"DEMO MODE: Pulling mock lead context for '{lead_id}'")
            return _MOCK_LEADS.get(
                lead_id.upper(),
                {
                    "Lead_ID": lead_id,
                    "Contact_Name": "Demo Customer",
                    "Company": "Unknown Lead",
                    "Project_Type": "Monument Sign",
                    "Address_Input": "123 Main St, Kennewick, WA",
                    "Pipeline_Stage": "Discovery",
                    "Last_Activity_Date": "2026-04-20T10:00:00",
                    "Open_Notes": "Demo fallback lead context.",
                },
            )
        # Real API call logic...
        pass

    def search_products(self, query: str):
        self._block_until_ready()
        if self._is_demo_mode:
            logger.info(f"DEMO MODE: Searching mock products for '{query}'")
            return _MOCK_PRODUCTS.get(query.lower(), [])
        # Real API call logic...
        pass

    def create_quote_draft(self, draft_data: dict):
        self._block_until_ready()
        if self._is_demo_mode:
            logger.info("DEMO MODE: Mocking Quote Draft Creation.")
            return {"status": "success", "draft_id": f"SQ-DEMO-{int(time.time())}"}
        # Real API call logic...
        pass
