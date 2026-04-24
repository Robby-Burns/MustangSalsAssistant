import logging
from typing import Any
from datetime import datetime
from app.factories.shopvox_factory import ShopvoxFactory
from app.models.core import QuoteDraft

logger = logging.getLogger(__name__)

from app.skills.margin_validator import MarginValidator

def merchant_node(state: Any):
    logger.info("MERCHANT: Quoting via ShopVOX API.")
    
    factory = ShopvoxFactory()
    lead_id = getattr(state, "lead_id", "LD-UNKNOWN")
    project_recipe = getattr(state, "project_recipe", None)
    compliance_rules = getattr(state, "compliance_rules", [])
    travel_sku = getattr(state, "travel_sku", "TRV-ZONE1")

    # Use recipe parts if available, else fallback to search
    line_items = []
    total_cost = 0.0
    total_price = 0.0
    project_type = state.lead_context.Project_Type if state.lead_context else "Sign"
    
    if project_recipe and project_recipe.Part_List:
        logger.info(f"MERCHANT: Building quote from Archivist recipe: {project_recipe.Recipe_ID}")
        price_lookup = {prod.get("sku"): float(prod.get("price", 0.0)) for prod in factory.search_products(project_type)}
        for part in project_recipe.Part_List:
            sku = part.get("SKU", "PART")
            qty = int(part.get("Qty", 1))
            unit_price = float(part.get("Price", 0.0)) or price_lookup.get(sku, 0.0)
            price = unit_price * qty
            cost = float(part.get("Cost", 0.0))
            if cost == 0.0:
                cost = price * 0.70
            total_price += price
            total_cost += cost
            line_items.append({"SKU": sku, "Qty": qty, "Description": part.get("Description", sku)})
    else:
        products = factory.search_products(project_type)
        for prod in products:
            price = float(prod.get("price", 100.0))
            cost = price * 0.70 # Default cost assumption for mock
            sku = prod.get("sku", "UNKNOWN")
            total_price += price
            total_cost += cost
            line_items.append({"SKU": sku, "Qty": 1, "Description": sku})

    # Use permit fee from compliance rules (Finding #6)
    permit_fee = 0.0
    if compliance_rules:
        permit_fee = sum(rule.Permit_Fee for rule in compliance_rules if rule.Permit_Fee)
    else:
        permit_fee = 150.0 # Fallback
    total_price += permit_fee
    
    # Travel Fee (Finding #5/6)
    travel_fee = 150.0 if "ZONE2" in travel_sku else 75.0
    total_price += travel_fee
    
    gross_profit = total_price - total_cost
    gross_margin_pct = (gross_profit / total_price) if total_price > 0 else 0.0
    
    # Use MarginValidator (Finding #6)
    margin_ok = MarginValidator.validate(gross_margin_pct)
    
    # Create real draft via factory
    draft_response = factory.create_quote_draft({
        "lead_id": lead_id,
        "total": total_price,
        "line_items": line_items
    }) or {}
    quote_id = draft_response.get("draft_id", f"SQ-{int(datetime.now().timestamp())}")

    quote_draft = QuoteDraft(
        Quote_ID=quote_id,
        Lead_ID=lead_id,
        Project_Name=f"Quote for {state.lead_context.Company if state.lead_context else 'Unknown'}",
        Line_Items=line_items,
        Travel_SKU=travel_sku,
        Travel_Fee_Amount=travel_fee,
        Permit_Fees=permit_fee,
        Gross_Margin_Pct=gross_margin_pct,
        Margin_Alert=not margin_ok,
        Status="draft",
        Created_At=datetime.now(),
        Last_Updated=datetime.now()
    )
    
    return {
        "quote_draft": quote_draft,
        "draft_margin": gross_margin_pct
    }
