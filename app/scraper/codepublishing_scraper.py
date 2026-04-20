import requests
from bs4 import BeautifulSoup
import hashlib
import json
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

# Configured Target URLs
CITY_CODES = {
    "KMC": "https://www.codepublishing.com/WA/Kennewick/html/Kennewick18/Kennewick1824.html",
    "RMC": "https://www.codepublishing.com/WA/Richland/html/Richland27/Richland27.html",
    "PMC": "https://www.codepublishing.com/WA/Pasco/html/Pasco20/Pasco2084.html"
}

def fetch_code_text(url: str) -> str:
    """Fetches the raw text from the CodePublishing endpoint with timeout and retries.
    """
    @retry(
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
    )
    def _get():
        headers = {"User-Agent": "Mustang-Sage-Scraper/1.0"}
        logger.info(f"Fetching regulatory data from {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text

    raw_html = _get()
    soup = BeautifulSoup(raw_html, "html.parser")
    text_content = soup.get_text(separator=' ', strip=True)
    return text_content

def calculate_hash(content: str) -> str:
    """Returns SHA-256 hash to detect changes."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def scrape_all_cities(return_text: bool = False):
    """Iterates through all cities and returns their current state hash or full text."""
    results = {}
    for city, url in CITY_CODES.items():
        try:
            content = fetch_code_text(url)
            content_hash = calculate_hash(content)
            results[city] = {
                "hash": content_hash,
                "length": len(content),
                # Storing snippet just for debug
                "snippet": content[:200]
            }
            if return_text:
                results[city]["raw_text"] = content
        except Exception as e:
            logger.error(f"Failed to scrape {city} at {url}: {e}")
            results[city] = {"error": str(e)}
            
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(scrape_all_cities(), indent=2))
