# The Mustang Sage (Agentic Sales Co-Pilot)

## Overview
The Mustang Sage is a LangGraph-orchestrated, multi-platform sales co-pilot. It assists sales reps by automating quoting, compliance checks, and communication drafts within Microsoft Teams and Slack. The system uses Retrieval-Augmented Generation (RAG) to query compliance rules and historical project data.

A key feature of this system is its robust, user-friendly process for managing municipal compliance data via a central Excel file, which is automatically monitored and ingested by the application.

## 🚀 Quickstart (Container Execution)
The repository is packaged as a multi-container Docker application. To get started, run:
```bash
# 1. Create your environment file from the example
cp .env.example .env

# 2. Fill in your API keys and secrets in the .env file

# 3. Build and run the services with Docker Compose
docker compose up --build
```
This stands up the following services:
- **mustang-whisper**: The primary FastAPI application serving the bot endpoints.
- **db**: A PostgreSQL instance for local development.
- **redis**: A Redis broker for potential background tasks.
- **jaeger**: An OpenTelemetry collector for tracing and monitoring.

## 🎛️ Configuration & Controls
The application's behavior is controlled through two main files:

1.  **`config/scale.yaml` (Behavioral Tuning)**: This file is the master control for the application's features.
    -   Enable or disable bot platforms (Teams and Slack).
    -   Configure the path to the compliance data Excel file.
    -   Swap out the LLM and vector database providers.

2.  **`.env` (Secrets & API Keys)**: This file holds all necessary secrets. Create it by copying `.env.example` and filling in your credentials.

## 📍 Project Structure
- **`app/main.py`**: The main FastAPI application.
- **`app/graph.py`**: Defines the core agentic workflow using LangGraph.
- **`app/agents/`**: Contains the specialized agents.
- **`app/factories/`**: Provides agnostic factories for connecting to external services.
- **`app/scraper/`**: Contains the automated scripts for monitoring and ingesting compliance data from the Excel file.
- **`app/ui/`**: Contains UI builders for Teams Adaptive Cards and Slack Block Kit.
- **`docs/`**: Project manifests, architectural documents, and playbooks, including the `Compliance_Data_Playbook.md`.

## 🧪 Testing
To run the project's test suite, use the following command:
```bash
uv run pytest
```
