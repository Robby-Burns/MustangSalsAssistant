import logging
from typing import Any
from datetime import datetime
from app.factories.shopvox_factory import ShopvoxFactory
from app.models.core import QuoteDraft

logger = logging.getLogger(__name__)

def merchant_node(state: Any):
    logger.info("MERCHANT: Quoting via ShopVOX API.")
    
    factory = ShopvoxFactory()
    lead_id = getattr(state, "lead_id", "LD-UNKNOWN")
    project_type = state.lead_context.Project_Type if state.lead_context else "Sign"
    
    products = []
    is_estimate = False
    try:
        products = factory.search_products(project_type)
    except Exception as e:
        logger.error(f"MERCHANT: ShopVOX API failed. Falling back to sandbox pricing. Error: {e}")
        is_estimate = True
        # Mocked historical pricing
        products = [{"sku": "TRV-ZONE2", "price": 150.0}, {"sku": "MONUMENT-8FT", "price": 4500.0}]

    line_items = []
    total_cost = 0.0
    total_price = 0.0
    
    for prod in products:
        price = float(prod.get("price", 100.0))
        cost = price * 0.75
        total_price += price
        total_cost += cost
        line_items.append({
            "sku": prod.get("sku", "UNKNOWN"),
            "price": price,
            "cost": cost
        })

    permit_fee = 150.0
    total_price += permit_fee
    
    travel_sku = getattr(state, "travel_sku", "TRV-ZONE1")
    travel_fee = 50.0
    total_price += travel_fee
    
    gross_profit = total_price - total_cost
    gross_margin_pct = (gross_profit / total_price) if total_price > 0 else 0.0
    
    margin_alert = gross_margin_pct < 0.35
    if margin_alert:
        logger.error(f"MERCHANT: Calculated margin {gross_margin_pct:.2%} falls below 35% floor!")
        
    quote_status = "estimate_only" if is_estimate else "draft"

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
        Status=quote_status,
        Created_At=datetime.now(),
        Last_Updated=datetime.now()
    )
    
    return {
        "quote_draft": quote_draft,
        "draft_margin": gross_margin_pct
    }
