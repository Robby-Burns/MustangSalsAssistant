import logging

logger = logging.getLogger(__name__)

class GeoLockGuard:
    """Ensures geographical location is established before quotes/compliance can proceed.
    # See mustang_whisper_system_prompt.md (Guardrails on Geo-Lock).
    """
    @staticmethod
    def verify(address_string: str) -> bool:
        """Validates if the provided address is a substantial string."""
        if not address_string or len(address_string) < 5:
            logger.warning(f"Geo-Lock failed for address: '{address_string}'")
            return False
            
        logger.info(f"Geo-Lock verified for: {address_string}")
        return True

    @staticmethod
    def verify_coordinates(coords: dict) -> bool:
        """Fully validate map bounding box math explicitly."""
        if not coords or "lat" not in coords or "lng" not in coords:
            return False
        lat_valid = -90.0 <= float(coords["lat"]) <= 90.0
        lng_valid = -180.0 <= float(coords["lng"]) <= 180.0
        return lat_valid and lng_valid
