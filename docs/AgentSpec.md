# Mustang Sage v2.4 - Agent Specification

## Executive Summary & ROI
**Mustang Sage** is a consultative sales co-pilot serving as a "Shadow Collaborator", embedded seamlessly into Microsoft Teams. Its primary value proposition is eliminating "tab fatigue" for sales reps by aggregating shopVOX CRM data, localized municipal code compliance, and legacy institutional project memory into actionable, interactive Adaptive Cards. The projected ROI stems from radically accelerated quote generation, zero compliance violation reworks, and strict adherence to a 35% gross margin floor.

## Agent Architecture
**Orchestration Pattern:** Antigravity orchestrating LangGraph.
**Rationale:** LangGraph is chosen over simpler async pipelines or CrewAI because the complex routing constraints and mandatory Human-In-The-Loop (HITL) gate require a robust State Graph design with strict memory checkpoints (`MemorySaver`). The system utilizes four specialized agents (Liaison, Archivist, Auditor, Merchant) connected via specific graph nodes.

## Risk Score & Guardrails
**Risk Score:** 11 / 17 (Medium-High)
**Required Guardrails:**
1. **HITL Only:** No autonomous actions permitted. All commits or drafts require a human click.
2. **Sandbox Restricted:** Live writes are locked strictly to the shopVOX Sandbox environment.
3. **Geo-Lock Mandatory:** Zero compliance checks will fire without validated `{lat, lng}` coordinates.
4. **Margin Floor:** Any quote falling below a 35% gross margin must surface a prominent ⚠️ Alert Card.
5. **Estimate-Only Watermarks:** If the live API fails, cached Sandbox prices must be heavily watermarked to prevent accidental sends.

## Agnostic Factories 
The pipeline avoids vendor lock-in by executing external calls via:
- **ShopvoxFactory:** `get_lead_context()`, `search_products()`, `create_quote_draft()` (Requires token-bucket limiting).
- **S3VectorFactory:** `semantic_search()`, handling Neon pgvector connections.
- **GeoLogisticsFactory:** `geocode_address()`, bounded by Google Maps quota thresholds.
- **CommFactory:** `build_lead_context()`, handles intent translation.

## Data Models & State Triggers
**Core Models (Pydantic schema constraints):**
- `LeadContext` (shopVOX identifier layer)
- `ProjectRecipe` (Part lists stripped of prices)
- `ComplianceRule` (KMC/RMC/PMC zoning requirements)
- `QuoteDraft` (Unified itemized outputs)
- `CommDraft` (String-based message generation)

## Non-Functional Requirements
- **Fault Tolerance:** All factory calls must implement try/except hooks. If `ShopvoxFactory` hits 429s due to 100/min caps, it executes exponential backoffs (1s → 2s → 4s → 8s). The system must never surface a blank state.
- **Container Defensiveness:** No ephemeral disk I/O. 
- **Strict UI Timeouts:** Adaptive Cards must render progress indicators if time constraints are breached (e.g., Geo-lock >3s, Recipe lookup >5s, Full Draft >10s).

## Maintenance Plan
- **Audit Notifications:** Escalate automated alerts directly to `#sage-ops-alerts` in Slack.
- **HITL Reviewer:** Designated Production Manager handles secondary reviews.
- **Schedule:** Monthly review over margin override logs. Quarterly triggers for PriceScrubber Lambda execution and Sandbox retraining.

## Skills Identification
Repeating operations are decoupled from agents into `app/skills/`:
- `GeoLockGuard`: Validates syntax of map routes.
- `DistanceCalculator`: Calculates distances to emit Travel SKUs.
- `MarginValidator`: Mathematical boolean checks.
- `CommTemplateEngine`: Pre-processors to safely template email intent.

## Phase 1 Implementation Steps
1. Lock AgentSpec.md and define `AdaptiveCardTemplates.md`.
2. Apply Python dependencies pinned securely (`adaptivecards`/`jinja2`).
3. Construct `app/models/core.py`.
4. Replace existing hollow state nodes with configured LangGraph agents (`liaison.py`, `archivist.py`, etc.).
5. Elevate Skills to production validity.
6. Assemble `/teams/card` endpoints with FastApi and QA Test coverage thresholds (>80%).
