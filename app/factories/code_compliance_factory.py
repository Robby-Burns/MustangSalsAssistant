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
        
    def retrieve_codes(self, address_input: str) -> List[ComplianceRule]:
        self.logger.info(f"Retrieving vector compliance codes for: {address_input}")
        
        # For Phase 2 Sandbox, we mock the pgvector similarity lookup.
        # This accurately models what an NLP payload structure would return for the checklist UI.
        return [
            ComplianceRule(
                Jurisdiction="KMC",
                Max_Sq_Ft=40,
                Height_Limit_Ft=10,
                Setback_Ft=15,
                Illumination_Notes="No flashing or rotating lights. Must be statically illuminated.",
                Permit_Fee=150.0,
                Code_Citation="KMC 18.24.030",
                Code_Link="https://www.codepublishing.com/WA/Kennewick/html/Kennewick18/Kennewick1824.html",
                Verified_Geo={"lat": 46.2114, "lng": -119.1373},
                Jurisdiction_Name="Kennewick"
            )
        ]
