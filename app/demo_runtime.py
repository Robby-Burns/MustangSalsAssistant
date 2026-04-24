from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import re
import os
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from app.agents.archivist import archivist_node
from app.agents.auditor import auditor_node
from app.agents.merchant import merchant_node
from app.factories.comm_template_engine import CommTemplateEngine
from app.factories.code_compliance_factory import CodeComplianceFactory
from app.factories.geo_logistics_factory import GeoLogisticsFactory
from app.factories.shopvox_factory import ShopvoxFactory
from app.models.core import CommDraft, LeadContext, ProjectRecipe, QuoteDraft
from app.skills.distance_calculator import DistanceCalculator
from app.skills.margin_validator import MarginValidator
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
        "queue_status": "Draft",
        "request_brief": "",
        "pending_request_choice": None,
        "workflow_alert": None,
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
            "Fill the customer details on the right, then use the composer below to draft or revise the quote."
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
            _capture_request(session, feedback)
            _append_event(session, "REQUEST_CAPTURED", feedback)
        return _serialize_session(session)

    if action == "submit_request":
        mode = (payload.get("mode") or "").strip().lower()
        pending_request = session.get("pending_request_choice", {})
        effective_feedback = (feedback or pending_request.get("request") or "").strip()

        if session.get("quote_draft") and effective_feedback and mode not in {"update_existing", "create_new"}:
            session["pending_request_choice"] = {
                "request": effective_feedback,
                "created_at": _now_iso(),
            }
            session["current_view"] = {
                "kind": "intent_choice",
                "payload": {
                    "title": "Apply this request to the current draft?",
                    "body": effective_feedback,
                },
            }
            session["queue_status"] = "Draft"
            _append_message(session, "sage", "I found an existing draft. Choose whether to update it or create a new draft.")
            _append_event(session, "REQUEST_DECISION_REQUIRED", "Rep must choose update existing or create new.")
            return _serialize_session(session)

        if effective_feedback:
            _capture_request(session, effective_feedback)

        preserve_user_quote = mode == "update_existing"
        if mode == "create_new":
            session["quote_draft"] = None
            session["comm_draft"] = None

        session["pending_request_choice"] = None
        _append_event(session, "QUOTE_REQUESTED", feedback or "Quote requested from current workspace fields.")
        _run_quote_pipeline(session, preserve_user_quote=preserve_user_quote)
        return _serialize_session(session)

    if action == "save_lead":
        lead_payload = payload.get("lead_context", {})
        _update_lead_context(session, lead_payload)
        _sync_quote_identity(session)
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
        _build_follow_up_draft(session)
        session["queue_status"] = "Email Ready"
        session["current_view"] = {
            "kind": "email_card",
            "payload": {
                "title": "Quote approved and email drafted",
                "subtitle": quote.Quote_ID if quote else session["lead_context"].Lead_ID,
                "body": "The quote is approved in the demo workspace. The follow-up email is ready in the Email tab.",
            },
        }
        _append_message(session, "sage", "Quote approved. I drafted the customer follow-up email and loaded it into the Email tab.")
        _append_event(session, "QUOTE_APPROVED", "Quote approved by rep and follow-up email drafted.")
        return _serialize_session(session)

    if action in {"edit_scope", "request_changes"}:
        if feedback:
            _capture_request(session, feedback)
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
        session["queue_status"] = "Email Ready"
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
        session["queue_status"] = "Email Sent"
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
    session["workflow_alert"] = None

    missing_fields = _missing_required_fields(lead_context)
    if missing_fields:
        _append_message(session, "sage", f"I drafted with partial information. I still need: {', '.join(missing_fields)}.")
        _append_event(session, "MISSING_FIELDS", ", ".join(missing_fields))
        session["workflow_alert"] = {
            "kind": "missing_fields",
            "title": "More details needed",
            "subtitle": "The draft was created with partial information.",
            "body": ", ".join(missing_fields),
        }

    geo = GeoLogisticsFactory.geocode_address(lead_context.Address_Input)
    lead_context.Address_Geo_Lock = geo
    _set_field_source(session, "Address_Geo_Lock", "Inferred")
    address_verified = bool(geo)
    if not geo:
        _append_message(session, "sage", "Address verification did not complete. I drafted the quote without compliance and travel verification.")
        _append_event(session, "ADDRESS_PARTIAL", f"Could not geocode '{lead_context.Address_Input}'.")
        session["workflow_alert"] = {
            "kind": "address_block",
            "title": "Address verification required",
            "subtitle": "The draft was created without verified travel or code checks.",
            "body": lead_context.Address_Input or "Add a site address.",
        }

    state = SimpleNamespace(
        lead_id=lead_context.Lead_ID,
        lead_context=lead_context,
        address_verified=address_verified,
    )

    if _demo_offline_mode():
        archivist_result = _offline_archivist_result(state)
    else:
        try:
            archivist_result = archivist_node(state)
        except Exception as exc:
            _append_event(session, "ARCHIVIST_FALLBACK", f"Recipe lookup failed: {exc}")
            archivist_result = {"recipe_found": False, "project_recipe": None}
    state.recipe_found = archivist_result.get("recipe_found", False)
    state.project_recipe = archivist_result.get("project_recipe")
    session["recipe_found"] = state.recipe_found
    session["project_recipe"] = state.project_recipe

    if _demo_offline_mode():
        auditor_result = _offline_auditor_result(state)
    else:
        try:
            auditor_result = auditor_node(state)
        except Exception as exc:
            _append_event(session, "AUDITOR_FALLBACK", f"Compliance lookup failed: {exc}")
            auditor_result = {"compliance_rules": [], "travel_sku": ""}
    state.compliance_rules = auditor_result.get("compliance_rules", [])
    state.travel_sku = auditor_result.get("travel_sku", "")
    session["compliance_rules"] = state.compliance_rules
    session["travel_sku"] = state.travel_sku
    session["code_review"] = _merge_code_review(session.get("code_review", []), state.compliance_rules)

    if _demo_offline_mode():
        merchant_result = _offline_merchant_result(state)
    else:
        try:
            merchant_result = merchant_node(state)
        except Exception as exc:
            _append_event(session, "MERCHANT_FALLBACK", f"Quote assembly failed: {exc}")
            merchant_result = {"quote_draft": _build_fallback_quote(state), "draft_margin": 0.0}
    generated_quote = merchant_result.get("quote_draft")
    previous_quote_id = session["quote_draft"].Quote_ID if session.get("quote_draft") else None
    if generated_quote and preserved_quote:
        generated_quote = _merge_locked_quote_fields(generated_quote, preserved_quote, locked_fields)
    if generated_quote:
        generated_quote.Quote_ID = _generate_quote_id(session, previous_quote_id if preserve_user_quote else None)
        generated_quote.Project_Name = f"{lead_context.Company} {lead_context.Project_Type}".strip()
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
        session["queue_status"] = "Needs Info" if missing_fields or not address_verified else "Ready for Approval"
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
        session["queue_status"] = "Needs Info"


def _build_lead_context(lead_id: str, overrides: dict[str, Any]) -> LeadContext:
    raw = ShopvoxFactory().get_lead_context(lead_id)
    raw.update({key: value for key, value in overrides.items() if value is not None})
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
    project_type_source = "Composer request inference" if session.get("request_brief") else "shopVOX lead record"
    project_type_status = "Inferred" if session.get("request_brief") else "Retrieved"
    field_sources.setdefault("Project_Type", _field_source(project_type_status, project_type_source, now))
    field_sources.setdefault("Address_Input", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Pipeline_Stage", _field_source("Retrieved", "shopVOX lead record", now))
    field_sources.setdefault("Last_Activity_Date", _field_source("Retrieved", "shopVOX lead record", now))
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
    _sync_quote_identity(session)


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
        "open_notes": session.get("request_brief", ""),
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
        "queue_status": session["queue_status"],
        "request_brief": session["request_brief"],
        "pending_request_choice": session["pending_request_choice"],
        "workflow_alert": session["workflow_alert"],
        "current_view": session["current_view"],
        "messages": session["messages"],
        "events": session["events"],
        "available_leads": list_demo_leads(),
        "queue": _serialize_queue(),
    }


def _append_message(session: dict[str, Any], role: str, text: str) -> None:
    session["messages"].append({"role": role, "text": text, "timestamp": _now_iso()})


def _append_event(session: dict[str, Any], event: str, details: str) -> None:
    session["events"].append({"time": _now_iso(), "event": event, "details": details})


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _capture_request(session: dict[str, Any], feedback: str) -> None:
    feedback = feedback.strip()
    if not feedback:
        return
    session["request_brief"] = feedback
    session["lead_context"].Open_Notes = feedback
    _append_message(session, "rep", feedback)
    _infer_from_request(session["lead_context"], feedback)
    _set_field_source(session, "Project_Type", "Inferred", "Composer request inference")


def _infer_from_request(lead_context: LeadContext, feedback: str) -> None:
    text = feedback.lower()
    if any(token in text for token in {"channel letter", "channel letters", "letters"}):
        lead_context.Project_Type = "Channel Letters"
    elif any(token in text for token in {"pylon", "pole sign"}):
        lead_context.Project_Type = "Pylon Sign"
    elif any(token in text for token in {"monument", "freestanding", "ground sign"}):
        lead_context.Project_Type = "Monument Sign"
    elif any(token in text for token in {"cabinet", "wall sign", "storefront", "sign"}):
        lead_context.Project_Type = "Custom Sign"
    elif not lead_context.Project_Type.strip():
        lead_context.Project_Type = "Custom Sign"


def _missing_required_fields(lead_context: LeadContext) -> list[str]:
    required = {
        "company name": lead_context.Company,
        "contact name": lead_context.Contact_Name,
        "site address": lead_context.Address_Input,
    }
    return [label for label, value in required.items() if not value or not str(value).strip()]


def _sync_quote_identity(session: dict[str, Any]) -> None:
    quote = session.get("quote_draft")
    if not quote:
        return
    quote.Quote_ID = _generate_quote_id(session, quote.Quote_ID)
    quote.Project_Name = f"{session['lead_context'].Company} {session['lead_context'].Project_Type}".strip()
    quote.Last_Updated = datetime.utcnow()


def _generate_quote_id(session: dict[str, Any], existing_quote_id: str | None = None) -> str:
    if existing_quote_id:
        return existing_quote_id
    company = session["lead_context"].Company or "QUOTE"
    prefix = re.sub(r"[^A-Z0-9]", "", company.upper())[:8] or "QUOTE"
    month_year = datetime.utcnow().strftime("%m-%Y")
    count = sum(
        1
        for current in _DEMO_SESSIONS.values()
        if current.get("quote_draft") and str(current["quote_draft"].Quote_ID).startswith(f"{prefix}-")
    )
    return f"{prefix}-{count + 1}-{month_year}"


def _serialize_queue() -> list[dict[str, str]]:
    items = []
    for session_id, session in _DEMO_SESSIONS.items():
        lead = session["lead_context"]
        items.append(
            {
                "session_id": session_id,
                "lead_id": lead.Lead_ID,
                "company": lead.Company,
                "project_type": lead.Project_Type,
                "address": lead.Address_Input,
                "status": session.get("queue_status", "Draft"),
                "quote_id": session["quote_draft"].Quote_ID if session.get("quote_draft") else "",
            }
        )
    return sorted(items, key=lambda item: (item["status"], item["company"], item["lead_id"]))


def _build_fallback_quote(state: Any) -> QuoteDraft:
    lead_context = state.lead_context
    project_type = lead_context.Project_Type.strip() if lead_context and lead_context.Project_Type else "Custom Sign"
    company = lead_context.Company.strip() if lead_context and lead_context.Company else "Untitled Quote"
    line_items = [{"SKU": "CUSTOM", "Qty": 1, "Description": project_type}]
    travel_sku = getattr(state, "travel_sku", "") or "TRV-ZONE1"
    travel_fee = 150.0 if "ZONE2" in travel_sku else 75.0
    permit_fees = 0.0
    gross_margin_pct = 0.35

    return QuoteDraft(
        Quote_ID=f"TMP-{int(datetime.utcnow().timestamp())}",
        Lead_ID=lead_context.Lead_ID if lead_context else "LD-UNKNOWN",
        Project_Name=f"{company} {project_type}".strip(),
        Line_Items=line_items,
        Travel_SKU=travel_sku,
        Travel_Fee_Amount=travel_fee,
        Permit_Fees=permit_fees,
        Gross_Margin_Pct=gross_margin_pct,
        Margin_Alert=False,
        Status="draft",
        Created_At=datetime.utcnow(),
        Last_Updated=datetime.utcnow(),
    )


def _demo_offline_mode() -> bool:
    return True


def _offline_archivist_result(state: Any) -> dict[str, Any]:
    project_type = (state.lead_context.Project_Type or "").strip() or "Custom Sign"
    recipe_catalog = {
        "Monument Sign": {
            "Recipe_ID": "REC-MONUMENT-LOCAL",
            "Project_Type": "Monument Sign",
            "Part_List": [{"SKU": "MONUMENT-8FT", "Qty": 1, "Description": "8ft monument sign"}],
            "Labor_Hours": 24,
            "Zoning_Tags": ["KMC"],
            "Source_Bucket": "Sandbox",
        },
        "Pylon Sign": {
            "Recipe_ID": "REC-PYLON-LOCAL",
            "Project_Type": "Pylon Sign",
            "Part_List": [{"SKU": "PYLON-20FT", "Qty": 1, "Description": "20ft pylon sign"}],
            "Labor_Hours": 40,
            "Zoning_Tags": ["RMC"],
            "Source_Bucket": "Sandbox",
        },
        "Channel Letters": {
            "Recipe_ID": "REC-CHANNEL-LOCAL",
            "Project_Type": "Channel Letters",
            "Part_List": [{"SKU": "CHANNEL-LED", "Qty": 10, "Description": "LED channel letters"}],
            "Labor_Hours": 16,
            "Zoning_Tags": ["PMC"],
            "Source_Bucket": "Sandbox",
        },
        "Custom Sign": {
            "Recipe_ID": "REC-CUSTOM-LOCAL",
            "Project_Type": "Custom Sign",
            "Part_List": [{"SKU": "CUSTOM-SIGN", "Qty": 1, "Description": "Custom sign package"}],
            "Labor_Hours": 20,
            "Zoning_Tags": ["KMC"],
            "Source_Bucket": "Sandbox",
        },
    }
    recipe_data = recipe_catalog.get(project_type, recipe_catalog["Custom Sign"])
    return {"recipe_found": True, "project_recipe": ProjectRecipe(**recipe_data)}


def _offline_auditor_result(state: Any) -> dict[str, Any]:
    lat_lng = state.lead_context.Address_Geo_Lock if state.lead_context else None
    if lat_lng:
        travel_info = DistanceCalculator.get_travel_sku(lat_lng["lat"], lat_lng["lng"])
        travel_sku = travel_info.get("sku", "TRV-ZONE1")
        jurisdiction = GeoLogisticsFactory.lookup_jurisdiction(lat_lng["lat"], lat_lng["lng"])
        compliance_rules = CodeComplianceFactory().retrieve_codes(state.lead_context.Address_Input, jurisdiction_filter=jurisdiction)
        return {"compliance_rules": compliance_rules, "travel_sku": travel_sku}
    return {"compliance_rules": [], "travel_sku": "TRV-ZONE1"}


def _offline_merchant_result(state: Any) -> dict[str, Any]:
    factory = ShopvoxFactory()
    lead_context = state.lead_context
    project_type = (lead_context.Project_Type or "").strip() or "Custom Sign"
    project_recipe = getattr(state, "project_recipe", None)
    compliance_rules = getattr(state, "compliance_rules", []) or []
    travel_sku = getattr(state, "travel_sku", "") or "TRV-ZONE1"

    line_items = []
    total_cost = 0.0
    total_price = 0.0

    if project_recipe and project_recipe.Part_List:
        price_lookup = {prod.get("sku"): float(prod.get("price", 0.0)) for prod in factory.search_products(project_type)}
        for part in project_recipe.Part_List:
            sku = part.get("SKU", "PART")
            qty = int(part.get("Qty", 1))
            unit_price = float(part.get("Price", 0.0)) or price_lookup.get(sku, 0.0) or 1000.0
            price = unit_price * qty
            cost = price * 0.70
            total_price += price
            total_cost += cost
            line_items.append({"SKU": sku, "Qty": qty, "Description": part.get("Description", sku)})
    else:
        for prod in factory.search_products(project_type) or [{"sku": "CUSTOM-SIGN", "price": 2500.0}]:
            price = float(prod.get("price", 2500.0))
            cost = price * 0.70
            total_price += price
            total_cost += cost
            line_items.append({"SKU": prod.get("sku", "CUSTOM-SIGN"), "Qty": 1, "Description": prod.get("sku", "CUSTOM-SIGN")})

    permit_fee = sum(rule.Permit_Fee for rule in compliance_rules if rule.Permit_Fee) if compliance_rules else 0.0
    travel_fee = 150.0 if "ZONE2" in travel_sku else 75.0
    total_price += permit_fee + travel_fee
    gross_profit = total_price - total_cost
    gross_margin_pct = (gross_profit / total_price) if total_price > 0 else 0.0
    margin_ok = MarginValidator.validate(gross_margin_pct)

    quote_draft = QuoteDraft(
        Quote_ID=f"TMP-{int(datetime.utcnow().timestamp())}",
        Lead_ID=lead_context.Lead_ID,
        Project_Name=f"{lead_context.Company or 'Untitled Quote'} {project_type}".strip(),
        Line_Items=line_items,
        Travel_SKU=travel_sku,
        Travel_Fee_Amount=travel_fee,
        Permit_Fees=permit_fee,
        Gross_Margin_Pct=gross_margin_pct,
        Margin_Alert=not margin_ok,
        Status="draft",
        Created_At=datetime.utcnow(),
        Last_Updated=datetime.utcnow(),
    )
    return {"quote_draft": quote_draft, "draft_margin": gross_margin_pct}
