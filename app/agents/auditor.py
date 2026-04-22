import logging
from typing import Any
from app.factories.code_compliance_factory import CodeComplianceFactory

logger = logging.getLogger(__name__)

def auditor_node(state: Any):
    logger.info("AUDITOR: Verifying compliance logic visually via RAG array payload.")
    
    address = state.lead_context.Address_Input if state.lead_context else "Unknown"
    
    factory = CodeComplianceFactory()
    compliance_rules = factory.retrieve_codes(address)
    
    passed = len(compliance_rules) > 0
    
    if not passed:
        logger.error("AUDITOR: Strict Compliance failure! No matching municipal rules found.")
        
    return {
        "compliance_passed": passed,
        "compliance_rules": compliance_rules
    }
