from fastapi import FastAPI, Request, Response, status, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
import sys
import traceback
import os
from app.graph import sage_graph

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

app = FastAPI(title="The Mustang Sage")

# Telemetry Configuration
resource = Resource.create({"service.name": "mustang-whisper-api"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

FastAPIInstrumentor.instrument_app(app)

# Load Bot Framework credentials from environment (do not hard‑code secrets)
APP_ID = os.getenv("MICROSOFT_APP_ID", "PLACEHOLDER_APP_ID")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "PLACEHOLDER_APP_PASSWORD")

# NOTE: See citation in mustang_whisper_system_prompt.md line 40 for guardrail on secret handling.
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Catch-all for errors
async def on_error(context, error):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error or bug.")

adapter.on_turn_error = on_error

# --- Audit Endpoints ---
from app.skills.audit_system import run_bi_annual_audit, run_weekly_cve

audit_api_key_header = APIKeyHeader(name="X-Audit-Key", auto_error=False)

def verify_audit_key(api_key: str = Security(audit_api_key_header)):
    expected_key = os.getenv("AUDIT_API_KEY")
    if not expected_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    return api_key

@app.post("/audit/run")
def trigger_audit_run(api_key: str = Depends(verify_audit_key)):
    result = run_bi_annual_audit()
    return result

@app.post("/audit/cve-check")
def trigger_cve_check(api_key: str = Depends(verify_audit_key)):
    result = run_weekly_cve()
    return result
# --- End Audit Endpoints ---

@app.get("/")
def read_root():
    return {"status": "The Mustang Sage API is online."}

@app.get("/health", tags=["System"])
def health_check():
    """Endpoint explicitly for Docker container healthchecks."""
    return {"status": "healthy"}

@app.post("/api/messages")
async def messages(req: Request) -> Response:
    """Main endpoint for Microsoft Teams Bot Framework"""
    # Defensive header check – avoid KeyError
    content_type = req.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        return Response(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    try:
        body = await req.json()
        # Security: Strip PII. Never log raw MS Teams chat objects direct to logger!
    except Exception as e:
        # Return 400 for malformed JSON
        return Response(content=f"Invalid JSON payload: {e}", status_code=status.HTTP_400_BAD_REQUEST)

    # Bridge `body` into LangGraph/Liaison node (see citation in mustang_whisper_system_prompt.md)
    # Using a static thread_id for mock testing purposes
    graph_config = {"configurable": {"thread_id": "teams-session-1"}}
    state = sage_graph.get_state(graph_config)
    
    # If the workflow is stuck in the HITL (human_bridge), we update state and continue
    if len(state.next) > 0 and state.next[0] == 'human_bridge':
        human_text = body.get("text", "approve").lower()
        sage_graph.update_state(graph_config, {"current_human_feedback": human_text})
        # Resume the queue
        sage_graph.invoke(None, graph_config)
    else:
        # Fresh Run
        lead_id = body.get("text", "LD-UNKNOWN")
        sage_graph.invoke({"lead_id": lead_id}, graph_config)

    return Response(status_code=status.HTTP_200_OK)

from pydantic import BaseModel

class NudgeRequest(BaseModel):
    quote_id: str

@app.post("/teams/nudge", tags=["UI Integration"])
def trigger_teams_nudge(payload: NudgeRequest):
    """
    Endpoint triggered by the background scheduler to fire off follow-up nudges.
    In Phase 2, this will route the nudge directly into the Liaison node.
    """
    graph_config = {"configurable": {"thread_id": f"nudge-{payload.quote_id}"}}
    
    # We simulate a "follow_up_email" human intent trigger to leverage Phase 2 Comm Engine!
    sage_graph.invoke(
        {
            "lead_id": payload.quote_id, 
            "current_human_feedback": "send follow-up"
        }, 
        graph_config
    )
    return {"status": "nudge dispatched", "quote_id": payload.quote_id}

@app.post("/teams/card", tags=["UI Integration"])
def generate_teams_card(quote_data: dict):
    """
    Generates the strict Microsoft Teams Adaptive Card JSON from a QuoteDraft dictionary.
    """
    from app.ui.adaptive_cards import AdaptiveCardGenerator
    return AdaptiveCardGenerator.generate_quote_draft_card(quote_data)

@app.post("/resume", tags=["Human-in-the-Loop"])
def resume_workflow(thread_id: str, action: str):
    """
    Resumes a LangGraph checkpoint explicitly bridging the HITL pause state.
    """
    from app.graph import sage_graph
    graph_config = {"configurable": {"thread_id": thread_id}}
    sage_graph.update_state(graph_config, {"current_human_feedback": action})
    result = sage_graph.invoke(None, graph_config)
    return {"status": "resumed"}
