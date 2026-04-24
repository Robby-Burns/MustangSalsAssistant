from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from app.agents.archivist import archivist_node
from app.agents.auditor import auditor_node
from app.agents.merchant import merchant_node
from app.factories.comm_template_engine import CommTemplateEngine
from app.factories.geo_logistics_factory import GeoLogisticsFactory
from app.factories.shopvox_factory import ShopvoxFactory
from app.models.core import CommDraft, LeadContext, QuoteDraft
from app.ui.adaptive_cards import AdaptiveCardGenerator
from app.ui.demo_card import DemoCardGenerator

_DEMO_SESSIONS: dict[str, dict[str, Any]] = {}


def list_demo_leads() -> list[dict[str, str]]:
    return [
        {
            "lead_id": "LD-123",
            "company": "Acme Corp",
            "project_type": "Monument Sign",
            "address": "123 Main St, Kennewick, WA",
            "contact_name": "John Smith",
        },
        {
            "lead_id": "LD-456",
            "company": "Pylon Inc.",
            "project_type": "Pylon Sign",
            "address": "456 Industrial Way, Richland, WA",
            "contact_name": "Jane Doe",
        },
    ]


def create_demo_session(lead_id: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    lead_context = _build_lead_context(lead_id, overrides or {})
    session_id = str(uuid4())
    session = {
        "session_id": session_id,
        "lead_context": lead_context,
        "recipe_found": False,
        "project_recipe": None,
        "compliance_rules": [],
        "travel_sku": "",
        "quote_draft": None,
        "comm_draft": None,
        "code_review": [],
        "source_context": [],
        "field_sources": {},
        "locked_fields": set(),
        "send_status": "not_sent",
        "current_view": {"kind": "welcome", "payload": DemoCardGenerator.generate_demo_card()},
        "messages": [],
        "events": [],
    }
    _seed_session_metadata(session)
    _append_message(
        session,
        "sage",
        (
            f"Loaded {lead_context.Company} into the Mustang Sage workspace. "
            "Add request details, review retrieved context, then run the quote workflow."
        ),
    )
    _append_event(session, "SESSION_CREATED", f"Workspace opened for {lead_context.Lead_ID}.")
    _DEMO_SESSIONS[session_id] = session
    return _serialize_session(session)


def get_demo_session(session_id: str) -> dict[str, Any]:
    return _serialize_session(_DEMO_SESSIONS[session_id])


def run_quote_workflow(session_id: str) -> dict[str, Any]:
    session = _DEMO_SESSIONS[session_id]
    _run_quote_pipeline(session)
    return _serialize_session(session)


def apply_demo_action(
    session_id: str,
    action: str,
    feedback: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = _DEMO_SESSIONS[session_id]
    action = action.lower().strip()
    payload = payload or {}

    if action == "append_note":
        if feedback:
            session["lead_context"].Open_Notes = feedback
            _set_field_source(session, "Open_Notes", "User edited")
            _append_message(session, "rep", feedback)
            _append_event(session, "NOTE_CAPTURED", feedback)
        return _serialize_session(session)

    if action == "save_lead":
        lead_payload = payload.get("lead_context", {})
        _update_lead_context(session, lead_payload)
        _append_event(session, "LEAD_UPDATED", "Lead and scope details updated in workspace.")
        return _serialize_session(session)

    if action == "save_quote":
        quote_payload = payload.get("quote_draft", {})
        _update_quote_draft(session, quote_payload)
        _append_event(session, "QUOTE_UPDATED", "Rep adjusted quote values and line items.")
        return _serialize_session(session)

    if action == "set_code_status":
        _update_code_review(session, payload.get("code_review", []))
        _append_event(session, "CODE_REVIEW_UPDATED", "Municipal code review states updated.")
        return _serialize_session(session)

    if action == "regenerate_quote":
        _append_event(session, "QUOTE_REGEN_REQUESTED", "Regeneration requested for untouched fields.")
        _run_quote_pipeline(session, preserve_user_quote=True)
        return _serialize_session(session)

    if action == "approve_quote":
        quote = session.get("quote_draft")
        if quote:
            quote.Status = "approved_pending_submission"
            quote.Last_Updated = datetime.utcnow()
        session["current_view"] = {
            "kind": "confirmation",
            "payload": {
                "title": "Quote approved for customer follow-up",
                "subtitle": quote.Quote_ID if quote else session["lead_context"].Lead_ID,
                "body": "The quote is approved in the demo workspace. The follow-up email can now be prepared.",
            },
        }
        _append_message(session, "sage", "Quote approved. You can now prepare the customer email.")
        _append_event(session, "QUOTE_APPROVED", "Quote approved by rep.")
        return _serialize_session(session)

    if action in {"edit_scope", "request_changes"}:
        if feedback:
            session["lead_context"].Open_Notes = feedback
            _set_field_source(session, "Open_Notes", "User edited")
            _append_message(session, "rep", feedback)
        _append_event(session, "QUOTE_CHANGE_REQUESTED", feedback or "Rep requested changes.")
        _run_quote_pipeline(session, preserve_user_quote=True)
        return _serialize_session(session)

    if action == "dismiss":
        session["current_view"] = {
            "kind": "dismissed",
            "payload": {
                "title": "Current card dismissed",
                "subtitle": session["lead_context"].Lead_ID,
                "body": "The workspace remains open for more edits or another regeneration.",
            },
        }
        _append_message(session, "sage", "Dismissed the current card. The workspace state is still available.")
        _append_event(session, "CARD_DISMISSED", "Rep dismissed current card view.")
        return _serialize_session(session)

    if action == "trigger_nudge":
        _build_follow_up_draft(session)
        _append_event(session, "EMAIL_PREP_STARTED", "Customer follow-up draft prepared.")
        return _serialize_session(session)

    if action == "save_email":
        _update_email_draft(session, payload.get("comm_draft", {}))
        _append_event(session, "EMAIL_UPDATED", "Rep updated the draft email.")
        return _serialize_session(session)

    if action == "approve_nudge":
        _build_follow_up_draft(session)
        session["current_view"] = {
            "kind": "email_card",
            "payload": {
                "title": "Customer Email Ready",
                "subtitle": session["lead_context"].Company,
                "subject": session["comm_draft"].Subject if session["comm_draft"] else "",
                "body": session["comm_draft"].Body if session["comm_draft"] else "",
            },
        }
        _append_message(session, "sage", "Email draft expanded and ready for final confirmation.")
        _append_event(session, "EMAIL_READY", "Email draft approved for send preview.")
        return _serialize_session(session)

    if action == "confirm_send":
        if not session.get("comm_draft"):
            _build_follow_up_draft(session)
        comm_draft: CommDraft = session["comm_draft"]
        comm_draft.Status = "sent_by_rep"
        session["send_status"] = "sent"
        session["current_view"] = {
            "kind": "sent",
            "payload": {
                "title": "Email sent in demo mode",
                "subtitle": session["lead_context"].Company,
                "body": comm_draft.Body,
            },
        }
        _append_message(session, "sage", "Email send simulated. Final copy has been logged in the workspace.")
        _append_event(session, "EMAIL_SENT", f"Simulated send for {session['lead_context'].Lead_ID}.")
        return _serialize_session(session)

    _append_event(session, "UNKNOWN_ACTION", f"Unhandled action '{action}'.")
    return _serialize_session(session)


def _run_quote_pipeline(session: dict[str, Any], preserve_user_quote: bool = False) -> None:
    lead_context: LeadContext = session["lead_context"]
    preserved_quote = deepcopy(session["quote_draft"].model_dump(mode="json")) if preserve_user_quote and session.get("quote_draft") else None
    locked_fields = set(session.get("locked_fields", set()))

    geo = GeoLogisticsFactory.geocode_address(lead_context.Address_Input)
    lead_context.Address_Geo_Lock = geo
    _set_field_source(session, "Address_Geo_Lock", "Inferred")

    if not geo:
        session["current_view"] = {
            "kind": "address_block",
            "payload": {
                "title": "Address verification required",
                "subtitle": "Mustang Sage could not verify the site address.",
                "body": lead_context.Address_Input,
            },
        }
        _append_message(session, "sage", "Address verification failed. Update the site address and retry.")
        _append_event(session, "ADDRESS_BLOCKED", f"Could not geocode '{lead_context.Address_Input}'.")
        return

    state = SimpleNamespace(
        lead_id=lead_context.Lead_ID,
        lead_context=lead_context,
        address_verified=True,
    )

    archivist_result = archivist_node(state)
    state.recipe_found = archivist_result.get("recipe_found", False)
    state.project_recipe = archivist_result.get("project_recipe")
    session["recipe_found"] = state.recipe_found
    session["project_recipe"] = state.project_recipe

    auditor_result = auditor_node(state)
    state.compliance_rules = auditor_result.get("compliance_rules", [])
    state.travel_sku = auditor_result.get("travel_sku", "")
    session["compliance_rules"] = state.compliance_rules
    session["travel_sku"] = state.travel_sku
    session["code_review"] = _merge_code_review(session.get("code_review", []), state.compliance_rules)

    merchant_result = merchant_node(state)
    generated_quote = merchant_result.get("quote_draft")
    if generated_quote and preserved_quote:
        generated_quote = _merge_locked_quote_fields(generated_quote, preserved_quote, locked_fields)
    session["quote_draft"] = generated_quote
    session["source_context"] = _build_source_context(session)
    _refresh_field_sources(session)

    if generated_quote:
        session["current_view"] = {
            "kind": "quote_card",
            "payload": AdaptiveCardGenerator.generate_quote_draft_card(generated_quote.model_dump(mode="json")),
        }
        _append_message(
            session,
            "sage",
            (
                f"Drafted a quote for {lead_context.Company}. "
                f"Travel zone {session['travel_sku'] or 'N/A'} and {len(session['compliance_rules'])} municipal rule set(s) were applied."
            ),
        )
        _append_event(session, "QUOTE_DRAFTED", f"Quote refreshed for {lead_context.Lead_ID}.")
    else:
        session["current_view"] = {
            "kind": "no_quote",
            "payload": {
                "title": "No quote generated",
                "subtitle": lead_context.Lead_ID,
                "body": "The workflow did not return a draft quote.",
            },
        }
        _append_event(session, "QUOTE_FAILED", f"No quote generated for {lead_context.Lead_ID}.")


def _build_lead_context(lead_id: str, overrides: dict[str, Any]) -> LeadContext:
    raw = ShopvoxFactory().get_lead_context(lead_id)
    raw.update({key: value for key, value in overrides.items() if value not in ("", None)})
    if "Last_Activity_Date" not in raw:
        raw["Last_Activity_Date"] = datetime.utcnow().isoformat()
    if "Pipeline_Stage" not in raw:
        raw["Pipeline_Stage"] = "Discovery"
    if "Open_Notes" not in raw:
        raw["Open_Notes"] = ""
    return LeadContext(**raw)


def _seed_session_metadata(session: dict[str, Any]) -> None:
    _refresh_field_sources(session)
    session["source_context"] = _build_source_context(session)


def _refresh_field_sources(session: dict[str, Any]) -> None:
    lead = session["lead_context"]
    now = _now_iso()
    field_sources = session.setdefault("field_sources", {})
    field_sources.setdefault("Lead_ID", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Contact_Name", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Company", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Project_Type", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Address_Input", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Pipeline_Stage", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Last_Activity_Date", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Open_Notes", _field_source("Retrieved", "shopVOX notes", now))
    if lead.Address_Geo_Lock:
        field_sources["Address_Geo_Lock"] = _field_source("Inferred", "GeoLogisticsFactory geocode", now)
    if session.get("project_recipe"):
        field_sources["Recipe"] = _field_source("Retrieved", "Archivist recipe retrieval", now)
    if session.get("compliance_rules"):
        field_sources["Compliance"] = _field_source("Retrieved", "Auditor jurisdiction lookup", now)
    if session.get("quote_draft"):
        field_sources["Quote"] = _field_source("Inferred", "Merchant quote assembly", now)
    if session.get("comm_draft"):
        field_sources["Email"] = _field_source("Inferred", "CommTemplateEngine draft", now)


def _field_source(status: str, source: str, timestamp: str) -> dict[str, str]:
    return {"status": status, "source": source, "timestamp": timestamp}


def _set_field_source(session: dict[str, Any], field_name: str, status: str, source: str | None = None) -> None:
    session.setdefault("field_sources", {})[field_name] = _field_source(status, source or status, _now_iso())


def _build_source_context(session: dict[str, Any]) -> list[dict[str, str]]:
    items = [
        {
            "label": "Lead record",
            "source": "shopVOX demo lead context",
            "status": "Retrieved",
            "timestamp": _now_iso(),
        }
    ]
    if session.get("project_recipe"):
        items.append(
            {
                "label": "Recipe match",
                "source": session["project_recipe"].Recipe_ID,
                "status": "Retrieved",
                "timestamp": _now_iso(),
            }
        )
    if session.get("compliance_rules"):
        items.append(
            {
                "label": "Municipal code",
                "source": session["compliance_rules"][0].Code_Citation,
                "status": "Retrieved",
                "timestamp": _now_iso(),
            }
        )
    if session.get("quote_draft"):
        items.append(
            {
                "label": "Quote assembly",
                "source": session["quote_draft"].Quote_ID,
                "status": "Inferred",
                "timestamp": _now_iso(),
            }
        )
    return items


def _merge_code_review(existing: list[dict[str, Any]], rules: list[Any]) -> list[dict[str, Any]]:
    existing_map = {item["Code_Citation"]: item for item in existing if "Code_Citation" in item}
    merged = []
    for rule in rules:
        current = existing_map.get(rule.Code_Citation, {})
        merged.append(
            {
                "Code_Citation": rule.Code_Citation,
                "Jurisdiction": rule.Jurisdiction,
                "Jurisdiction_Name": rule.Jurisdiction_Name,
                "status": current.get("status", "acknowledged"),
                "note": current.get("note", ""),
            }
        )
    return merged


def _update_code_review(session: dict[str, Any], code_review: list[dict[str, Any]]) -> None:
    if code_review:
        session["code_review"] = code_review


def _update_lead_context(session: dict[str, Any], lead_payload: dict[str, Any]) -> None:
    lead_context: LeadContext = session["lead_context"]
    editable_fields = {
        "Lead_ID",
        "Contact_Name",
        "Company",
        "Project_Type",
        "Pipeline_Stage",
        "Last_Activity_Date",
        "Open_Notes",
        "Address_Input",
    }
    for field, value in lead_payload.items():
        if field in editable_fields and value is not None:
            if field == "Last_Activity_Date" and isinstance(value, str) and value:
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            setattr(lead_context, field, value)
            session["locked_fields"].add(field)
            _set_field_source(session, field, "User edited")
    lead_context.Address_Geo_Lock = None


def _update_quote_draft(session: dict[str, Any], quote_payload: dict[str, Any]) -> None:
    quote = session.get("quote_draft")
    if not quote:
        return

    editable_fields = {
        "Project_Name",
        "Travel_SKU",
        "Travel_Fee_Amount",
        "Permit_Fees",
        "Gross_Margin_Pct",
        "Margin_Alert",
        "Status",
    }
    for field, value in quote_payload.items():
        if field == "Line_Items" and isinstance(value, list):
            quote.Line_Items = value
            session["locked_fields"].add("Line_Items")
            _set_field_source(session, "Line_Items", "User edited")
            continue
        if field in editable_fields and value is not None:
            setattr(quote, field, value)
            session["locked_fields"].add(field)
            _set_field_source(session, field, "User edited")
    quote.Last_Updated = datetime.utcnow()


def _merge_locked_quote_fields(generated_quote: QuoteDraft, preserved_quote: dict[str, Any], locked_fields: set[str]) -> QuoteDraft:
    if "Project_Name" in locked_fields and preserved_quote.get("Project_Name"):
        generated_quote.Project_Name = preserved_quote["Project_Name"]
    if "Line_Items" in locked_fields and preserved_quote.get("Line_Items") is not None:
        generated_quote.Line_Items = preserved_quote["Line_Items"]
    if "Travel_SKU" in locked_fields and preserved_quote.get("Travel_SKU"):
        generated_quote.Travel_SKU = preserved_quote["Travel_SKU"]
    if "Travel_Fee_Amount" in locked_fields and preserved_quote.get("Travel_Fee_Amount") is not None:
        generated_quote.Travel_Fee_Amount = preserved_quote["Travel_Fee_Amount"]
    if "Permit_Fees" in locked_fields and preserved_quote.get("Permit_Fees") is not None:
        generated_quote.Permit_Fees = preserved_quote["Permit_Fees"]
    if "Gross_Margin_Pct" in locked_fields and preserved_quote.get("Gross_Margin_Pct") is not None:
        generated_quote.Gross_Margin_Pct = preserved_quote["Gross_Margin_Pct"]
    if "Margin_Alert" in locked_fields and preserved_quote.get("Margin_Alert") is not None:
        generated_quote.Margin_Alert = preserved_quote["Margin_Alert"]
    if "Status" in locked_fields and preserved_quote.get("Status"):
        generated_quote.Status = preserved_quote["Status"]
    generated_quote.Last_Updated = datetime.utcnow()
    return generated_quote


def _build_follow_up_draft(session: dict[str, Any]) -> None:
    lead_context: LeadContext = session["lead_context"]
    quote = session.get("quote_draft")
    context = {
        "contact_name": lead_context.Contact_Name,
        "company": lead_context.Company,
        "project_type": lead_context.Project_Type,
        "lead_id": lead_context.Lead_ID,
        "open_notes": lead_context.Open_Notes,
        "quote_id": quote.Quote_ID if quote else lead_context.Lead_ID,
    }
    comm_draft = CommTemplateEngine.process_comm_intent(lead_context.Lead_ID, "follow_up_email", context)
    session["comm_draft"] = comm_draft
    session["send_status"] = "draft_ready"
    _set_field_source(session, "Email", "Inferred", "CommTemplateEngine follow-up draft")


def _update_email_draft(session: dict[str, Any], comm_payload: dict[str, Any]) -> None:
    if not session.get("comm_draft"):
        _build_follow_up_draft(session)
    comm_draft: CommDraft = session["comm_draft"]
    if "Subject" in comm_payload and comm_payload["Subject"] is not None:
        comm_draft.Subject = comm_payload["Subject"]
    if "Body" in comm_payload and comm_payload["Body"] is not None:
        comm_draft.Body = comm_payload["Body"]
    comm_draft.Status = "approved_not_sent"
    _set_field_source(session, "Email", "User edited", "Rep edited email draft")


def _serialize_session(session: dict[str, Any]) -> dict[str, Any]:
    lead_context: LeadContext = session["lead_context"]
    return {
        "session_id": session["session_id"],
        "lead_context": lead_context.model_dump(mode="json"),
        "recipe_found": session["recipe_found"],
        "project_recipe": session["project_recipe"].model_dump(mode="json") if session["project_recipe"] else None,
        "compliance_rules": [rule.model_dump(mode="json") for rule in session["compliance_rules"]],
        "code_review": session["code_review"],
        "travel_sku": session["travel_sku"],
        "quote_draft": session["quote_draft"].model_dump(mode="json") if session["quote_draft"] else None,
        "comm_draft": session["comm_draft"].model_dump(mode="json") if session["comm_draft"] else None,
        "field_sources": session["field_sources"],
        "source_context": session["source_context"],
        "send_status": session["send_status"],
        "current_view": session["current_view"],
        "messages": session["messages"],
        "events": session["events"],
        "available_leads": list_demo_leads(),
    }


def _append_message(session: dict[str, Any], role: str, text: str) -> None:
    session["messages"].append({"role": role, "text": text, "timestamp": _now_iso()})


def _append_event(session: dict[str, Any], event: str, details: str) -> None:
    session["events"].append({"time": _now_iso(), "event": event, "details": details})


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
