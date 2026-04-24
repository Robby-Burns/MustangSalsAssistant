import logging
from typing import List, Dict
from app.models.core import ComplianceRule

logger = logging.getLogger(__name__)

class CodeComplianceFactory:
    """
    Factory for retrieving and structuring municipal code compliance 
    from pgvector sandbox embeddings or static Fallback payload for RAG logic.
    """
    
    def __init__(self):
        self.logger = logger
        
    def retrieve_codes(self, address_input: str, jurisdiction_filter: str = "KMC") -> List[ComplianceRule]:
        self.logger.info(f"Retrieving vector compliance codes for: {address_input} with jurisdiction: {jurisdiction_filter}")
        
        # Mock RAG payloads for each jurisdiction
        _MOCK_RULES = {
            "KMC": ComplianceRule(Jurisdiction="KMC", Max_Sq_Ft=40, Height_Limit_Ft=10, Setback_Ft=15, Illumination_Notes="No flashing lights.", Permit_Fee=150.0, Code_Citation="KMC 18.24", Code_Link="https://example.com/kmc", Verified_Geo={"lat": 46.21, "lng": -119.13}, Jurisdiction_Name="Kennewick"),
            "RMC": ComplianceRule(Jurisdiction="RMC", Max_Sq_Ft=80, Height_Limit_Ft=25, Setback_Ft=10, Illumination_Notes="Shielded lighting required.", Permit_Fee=250.0, Code_Citation="RMC 9.1", Code_Link="https://example.com/rmc", Verified_Geo={"lat": 46.28, "lng": -119.27}, Jurisdiction_Name="Richland"),
            "PMC": ComplianceRule(Jurisdiction="PMC", Max_Sq_Ft=60, Height_Limit_Ft=20, Setback_Ft=20, Illumination_Notes="Full cutoff fixtures.", Permit_Fee=200.0, Code_Citation="PMC 22.5", Code_Link="https://example.com/pmc", Verified_Geo={"lat": 46.23, "lng": -119.10}, Jurisdiction_Name="Pasco"),
        }
        
        rule = _MOCK_RULES.get(jurisdiction_filter.upper())
        return [rule] if rule else []
