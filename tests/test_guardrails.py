import pytest
from app.factories.geo_logistics_factory import GeoLogisticsFactory
from app.skills.geo_lock_guard import GeoLockGuard
from app.skills.margin_validator import MarginValidator
from app.factories.shopvox_factory import ShopvoxFactory
import threading
import time

def test_geolock_guard():
    # Valid address
    assert GeoLockGuard.verify("123 Richland Ave") is True
    # Invalid empty address
    assert GeoLockGuard.verify("") is False
    # Invalid short address
    assert GeoLockGuard.verify("WA") is False

def test_geocode_address_uses_mock_geocoder_in_demo_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "invalid-demo-key")

    coords = GeoLogisticsFactory.geocode_address("123 Main St, Kennewick, WA")

    assert coords == {"lat": 46.2114, "lng": -119.1373}

def test_margin_validator():
    # Healthy margin
    assert MarginValidator.validate(0.38) is True
    assert MarginValidator.validate(0.50) is True
    # Low margin
    assert MarginValidator.validate(0.34) is False
    assert MarginValidator.validate(0.10) is False

def test_shopvox_rate_limiter_concurrency():
    factory = ShopvoxFactory()
    stints = []
    
    def worker():
        start = time.time()
        # This will securely bottleneck across threads if lock works
        factory.search_products("test")
        stints.append(time.time() - start)
        
    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # At least one of the threads should have waited > 1 second due to the limit
    assert max(stints) >= 1.0, "Rate limiter failed to block concurrent threads adequately"
