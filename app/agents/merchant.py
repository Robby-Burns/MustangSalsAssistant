import logging
from typing import Any
from datetime import datetime
from app.factories.shopvox_factory import ShopvoxFactory
from app.models.core import QuoteDraft

logger = logging.getLogger(__name__)

def merchant_node(state: Any):
    logger.info("MERCHANT: Quoting via ShopVOX API.")
    
    # 1. Hit the ShopVOX Factory for real or mocked sandbox pricing
    factory = ShopvoxFactory()
    lead_id = getattr(state, "lead_id", "LD-UNKNOWN") if hasattr(state, "lead_id") else (state.get("lead_id", "LD-UNKNOWN") if isinstance(state, dict) else "LD-UNKNOWN")
    
    # Use project type from state if available, else fallback to 'Sign'
    project_type = getattr(state, "project_type", "Sign") if hasattr(state, "project_type") else (state.get("project_type", "Sign") if isinstance(state, dict) else "Sign")
    products = factory.search_products(project_type)
    
    # 2. Extract SKU and simulated costs & prices
    line_items = []
    total_cost = 0.0
    total_price = 0.0
    
    for prod in products:
        price = float(prod.get("price", 100.0))
        # Simulated 75% COGS for testing typical margins (1 - 0.75 = 0.25 margin)
        # This will deliberately trip the margin_alert flag to prove HITL works.
        cost = price * 0.75
        total_price += price
        total_cost += cost
        line_items.append({
            "sku": prod.get("sku", "UNKNOWN"),
            "price": price,
            "cost": cost
        })

    # 3. Add Permit Fees (Extracted from Auditors in production)
    permit_fee = 150.0
    total_price += permit_fee
    
    # 4. Add Travel Fee
    travel_sku = getattr(state, "travel_sku", "TRV-ZONE1") if hasattr(state, "travel_sku") else (state.get("travel_sku", "TRV-ZONE1") if isinstance(state, dict) else "TRV-ZONE1")
    travel_fee = 50.0
    total_price += travel_fee
    
    # 5. Calculate True Gross Margin mathematically ensuring no false float scaling
    gross_profit = total_price - total_cost
    gross_margin_pct = (gross_profit / total_price) if total_price > 0 else 0.0
    
    # 6. Flag if below arbitrary floor 35%
    margin_alert = gross_margin_pct < 0.35
    if margin_alert:
        logger.error(f"MERCHANT: Calculated margin {gross_margin_pct:.2%} falls below 35% floor! Generating ⚠️ flags mapping explicitly back to Pydantic states.")
        
    quote_draft = QuoteDraft(
        Quote_ID=f"SQ-{int(datetime.now().timestamp())}",
        Lead_ID=lead_id,
        Project_Name="Live ShopVOX Quote Prototype",
        Line_Items=line_items,
        Travel_SKU=travel_sku,
        Travel_Fee_Amount=travel_fee,
        Permit_Fees=permit_fee,
        Gross_Margin_Pct=gross_margin_pct,
        Margin_Alert=margin_alert,
        Status="draft",
        Created_At=datetime.now(),
        Last_Updated=datetime.now()
    )
    
    return {
        "quote_draft": quote_draft,
        "draft_margin": gross_margin_pct
    }
