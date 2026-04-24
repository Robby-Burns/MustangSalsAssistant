from __future__ import annotations

import sys
import traceback
import os
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException, Security
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from app.config import config
from app.demo_runtime import apply_demo_action, create_demo_session, get_demo_session
from app.graph import sage_graph

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

app = FastAPI(title="The Mustang Sage")


class NudgeRequest(BaseModel):
    quote_id: str


class DemoSessionCreateRequest(BaseModel):
    lead_id: str
    overrides: dict = {}


class DemoActionRequest(BaseModel):
    action: str
    feedback: str = ""
    payload: dict = {}

# --- Telemetry Configuration ---
resource = Resource.create({"service.name": "mustang-whisper-api"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
FastAPIInstrumentor.instrument_app(app)

# --- Platform Integrations (Conditionally Enabled) ---

if config.platforms.teams_enabled:
    from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, ActivityHandler
    from botbuilder.schema import Activity, ActivityTypes
    from app.ui.adaptive_cards import AdaptiveCardGenerator

    APP_ID = os.getenv("MICROSOFT_APP_ID", "")
    APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
    adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
    adapter = BotFrameworkAdapter(adapter_settings)

    async def on_error(context: TurnContext, error: Exception):
        print(f"\n[on_turn_error] unhandled error: {error}", file=sys.stderr)
        traceback.print_exc()
        await context.send_activity("The bot encountered an error or bug.")
    adapter.on_turn_error = on_error

    class SageBot(ActivityHandler):
        async def on_message_activity(self, turn_context: TurnContext):
            lead_id = turn_context.activity.text
            thread_id = turn_context.activity.conversation.id
            graph_config = {"configurable": {"thread_id": thread_id}}
            final_state = sage_graph.invoke({"lead_id": lead_id}, graph_config)
            
            card_json = AdaptiveCardGenerator.generate_quote_draft_card(final_state["quote_draft"].model_dump()) if final_state.get("quote_draft") else None
            if card_json:
                reply_activity = Activity(type=ActivityTypes.message, attachments=[{"contentType": "application/vnd.microsoft.card.adaptive", "content": card_json}])
                await turn_context.send_activity(reply_activity)
            else:
                await turn_context.send_activity("I'm not sure how to handle that request.")

    bot = SageBot()

    def _demo_message_response(message_text: str, thread_id: str):
        graph_config = {"configurable": {"thread_id": thread_id}}
        final_state = sage_graph.invoke({"lead_id": message_text}, graph_config)
        if final_state.get("quote_draft"):
            return AdaptiveCardGenerator.generate_quote_draft_card(final_state["quote_draft"].model_dump())
        if final_state.get("comm_draft"):
            return {"type": "comm_draft", "subject": final_state["comm_draft"].Subject, "body": final_state["comm_draft"].Body}
        return {"message": "I'm not sure how to handle that request."}

    @app.post("/api/messages")
    async def messages(req: Request):
        if "application/json" not in req.headers["Content-Type"]:
            return Response(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        body = await req.json()
        if "type" not in body:
            message_text = body.get("text", "")
            card = _demo_message_response(message_text, body.get("thread_id", "demo-thread"))
            return {"ok": True, "content": card}
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        response = await adapter.process(auth_header, activity, bot.on_turn)
        if response:
            return Response(content=response.body, status_code=response.status)
        return Response(status_code=status.HTTP_202_ACCEPTED)

if config.platforms.slack_enabled and os.environ.get("SLACK_BOT_TOKEN") and os.environ.get("SLACK_SIGNING_SECRET"):
    from slack_bolt.async_app import AsyncApp
    from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
    from app.ui.block_kit_builder import BlockKitBuilder

    slack_app = AsyncApp(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))
    slack_handler = AsyncSlackRequestHandler(slack_app)

    @slack_app.message(".*")
    async def handle_slack_message(message, say):
        lead_id = message['text']
        thread_id = message['channel']
        graph_config = {"configurable": {"thread_id": thread_id}}
        final_state = sage_graph.invoke({"lead_id": lead_id}, graph_config)
        
        blocks = BlockKitBuilder.generate_quote_draft_card(final_state["quote_draft"].model_dump()) if final_state.get("quote_draft") else None
        if blocks:
            await say(blocks=blocks, text=f"Quote Draft for {lead_id}")
        else:
            await say("I'm not sure how to handle that request.")

    @app.post("/slack/events")
    async def slack_events(req: Request):
        return await slack_handler.handle(req)

# --- Generic Endpoints ---
@app.get("/")
def read_root():
    return {"status": "The Mustang Sage API is online."}

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}

# --- Demo Endpoints ---
from app.ui.demo_card import DemoCardGenerator
from app.ui.demo_page import DemoPageBuilder

@app.get("/demo/card", tags=["Demo"])
def get_demo_card():
    """
    Returns the JSON for a high-quality, detailed Adaptive Card for demos.
    You can paste this JSON into the Adaptive Card Designer to visualize it.
    """
    return DemoCardGenerator.generate_demo_card()

@app.get("/demo", response_class=HTMLResponse, tags=["Demo"])
def get_demo_page():
    return DemoPageBuilder.render()

@app.post("/demo/api/session", tags=["Demo"])
def create_demo_api_session(payload: DemoSessionCreateRequest):
    return create_demo_session(payload.lead_id, payload.overrides)

@app.get("/demo/api/session/{session_id}", tags=["Demo"])
def get_demo_api_session(session_id: str):
    return get_demo_session(session_id)

@app.post("/demo/api/session/{session_id}/quote", tags=["Demo"])
def run_demo_quote(session_id: str):
    from app.demo_runtime import run_quote_workflow

    return run_quote_workflow(session_id)

@app.post("/demo/api/session/{session_id}/action", tags=["Demo"])
def run_demo_action(session_id: str, payload: DemoActionRequest):
    return apply_demo_action(session_id, payload.action, payload.feedback, payload.payload)

# ... (The rest of your endpoints remain the same)
from app.skills.audit_system import run_bi_annual_audit, run_weekly_cve
audit_api_key_header = APIKeyHeader(name="X-Audit-Key", auto_error=False)

def verify_audit_key(api_key: str = Security(audit_api_key_header)):
    expected_key = os.getenv("AUDIT_API_KEY")
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")
    return api_key

@app.post("/audit/run")
def trigger_audit_run(api_key: str = Depends(verify_audit_key)):
    return run_bi_annual_audit()

@app.post("/audit/cve-check")
def trigger_cve_check(api_key: str = Depends(verify_audit_key)):
    return run_weekly_cve()

@app.post("/teams/nudge", tags=["UI Integration"])
def trigger_teams_nudge(payload: NudgeRequest):
    graph_config = {"configurable": {"thread_id": f"nudge-{payload.quote_id}"}}
    sage_graph.invoke({"lead_id": payload.quote_id, "current_human_feedback": "send follow-up"}, graph_config)
    return {"status": "nudge dispatched", "quote_id": payload.quote_id}

@app.post("/teams/card", tags=["UI Integration"])
def generate_teams_card(quote_data: dict):
    from app.ui.adaptive_cards import AdaptiveCardGenerator
    return AdaptiveCardGenerator.generate_quote_draft_card(quote_data)

@app.post("/resume", tags=["Human-in-the-Loop"])
def resume_workflow(thread_id: str, action: str):
    graph_config = {"configurable": {"thread_id": thread_id}}
    sage_graph.update_state(graph_config, {"current_human_feedback": action})
    result = sage_graph.invoke(None, graph_config)
    return {"status": "resumed"}
