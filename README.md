# The Mustang Sage (Agentic Sales Co-Pilot)

## Overview
The Mustang Sage is a LangGraph-orchestrated system that maps routing intents, vector-searches regulatory sandbox compliance rules in a serverless `pgvector` database, and pulls direct historical S3 Legacy jobs via dynamic Retrieval-Augmented Generation (RAG).

The system architecture spans 10 comprehensive layers, featuring advanced Dual-LLM intent verification, deterministic Pydantic guardrails, Multi-Container Orchestration, and Bi-Annual Scheduled Auditing.

## 🚀 Quickstart (Container Execution)
The repository formally packages all layers within a Multi-Container Docker architecture.
```bash
docker compose up --build
```
This stands up:
1. **mustang-whisper**: The primary FastAPI Agentic logic endpoint (Port `8000`).
2. **db**: PostgreSQL instance handling Vector storage/RAG logic mapping (Port `5432`).
3. **redis**: Broker handling background worker tasks where applicable (Port `6379`).
4. **jaeger**: OpenTelemetry log mapping and monitoring UI frontend (Port `16686`).

## 🎛️ Configuration & Controls

The repository runs completely decoupled from raw-string inputs, operating via a safe "Master Control" design:

1. **`config/scale.yaml` (Behavioral Tuning)**: Defines deployment tiers, truncation strategies, audit dispatch locations, and the primary Target Language Provider (e.g. `gemini`, `openai`, `anthropic`).
2. **Runtime Flags**: `ENABLE_NEW_AGENTS` toggle limits API execution allowing secure rollbacks to mocked API boundaries during critical outages.
3. **`.env` (Secured Keys)**: Holds absolute secrets (`GOOGLE_API_KEY`, `SHOPVOX_API_KEY`, `AUDIT_API_KEY`, and internal `NEON_DATABASE_URL` routing). Safe references exist in `.env.example`.

## 📍 Project Execution Map
- **`app/main.py`**: Web API binding handling external Microsoft BotFramework triggers and exposing specific `/teams/card` & `/resume` UI bounds.
- **`app/db.py`**: Intersects Postgres Vector schema mappings.
- **`app/graph.py`**: Dictates the state machine looping data models securely over nodes.
- **`app/agents/`**: Houses independent LangGraph actors (`liaison.py`, `archivist.py`, `auditor.py`, `merchant.py`).
- **`app/ui/adaptive_cards.py`**: Generates cleanly formatted MS Teams UI layouts using standardized schema logic.
- **`app/scraper/rag_ingestion.py`**: Executes KMC/PMC Code Scraping, chunks the strings, and drops them sequentially into vectors.
- **`app/skills/audit_system.py`**: Dispatches the CVEMonitor and spec drift diagnostics.

## 🧪 Testing & Automation
All system layers enforce structural guardrails testing Token-Bucket constraints, Margin dropouts, Geolocation routing boundaries, and Audit security hooks safely!

```bash
uv run pytest
```
