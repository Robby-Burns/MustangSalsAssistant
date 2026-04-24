import logging
from typing import Any
from app.factories.code_compliance_factory import CodeComplianceFactory
from app.factories.geo_logistics_factory import GeoLogisticsFactory
from app.skills.distance_calculator import DistanceCalculator

logger = logging.getLogger(__name__)

def auditor_node(state: Any):
    logger.info("AUDITOR: Verifying compliance logic via RAG array payload.")
    
    if not getattr(state, "address_verified", False):
        logger.error("AUDITOR: Mandatory Geo-Lock check failed! Address not verified.")
        return {"compliance_passed": False, "compliance_rules": []}

    address = state.lead_context.Address_Input if state.lead_context else "Unknown"
    
    lat_lng = state.lead_context.Address_Geo_Lock if state.lead_context else None
    if not lat_lng and address != "Unknown":
        lat_lng = GeoLogisticsFactory.geocode_address(address)

    travel_sku = "TRV-ZONE1"
    jurisdiction = "KMC"
    if lat_lng:
        travel_info = DistanceCalculator.get_travel_sku(lat_lng["lat"], lat_lng["lng"])
        travel_sku = travel_info.get("sku", "TRV-ZONE1")
        logger.info(f"AUDITOR: Travel SKU calculated: {travel_sku}")
        jurisdiction = GeoLogisticsFactory.lookup_jurisdiction(lat_lng["lat"], lat_lng["lng"])
        logger.info(f"AUDITOR: Jurisdiction resolved to: {jurisdiction}")


    factory = CodeComplianceFactory()
    compliance_rules = factory.retrieve_codes(address, jurisdiction_filter=jurisdiction)
    
    passed = len(compliance_rules) > 0
    
    if not passed:
        logger.error("AUDITOR: Strict Compliance failure! No matching municipal rules found.")
        
    return {
        "compliance_passed": passed, 
        "compliance_rules": compliance_rules,
        "travel_sku": travel_sku
    }
