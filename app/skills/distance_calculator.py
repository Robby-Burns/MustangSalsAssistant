import math

class DistanceCalculator:
    """
    Computes direct spatial distance and outputs relevant shopVOX Travel SKUs.
    """
    # Shop origin (Kennewick HQ approximation)
    SHOP_LAT = 46.2114
    SHOP_LNG = -119.1373
    
    @classmethod
    def calculate_distance(cls, target_lat: float, target_lng: float) -> float:
        """Calculate generalized Haversine distance in miles."""
        R = 3958.8 # Radius of Earth in miles
        
        lat1, lon1 = math.radians(cls.SHOP_LAT), math.radians(cls.SHOP_LNG)
        lat2, lon2 = math.radians(target_lat), math.radians(target_lng)
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def get_travel_sku(cls, target_lat: float, target_lng: float) -> dict:
        distance = cls.calculate_distance(target_lat, target_lng)
        
        if distance < 10:
            return {"sku": "TRV-ZONE1", "fee": 50.00, "distance_miles": round(distance, 2)}
        elif distance < 30:
            return {"sku": "TRV-ZONE2", "fee": 150.00, "distance_miles": round(distance, 2)}
        else:
            return {"sku": "TRV-CUSTOM", "fee": 0.00, "distance_miles": round(distance, 2)}
