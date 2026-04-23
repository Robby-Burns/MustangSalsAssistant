# The Mustang Sage (Agentic Sales Co-Pilot)

## Overview
The Mustang Sage is a LangGraph-orchestrated, multi-platform sales co-pilot that assists sales reps by automating quoting, compliance checks, and communication drafts within Microsoft Teams and Slack.

A key feature is its robust, user-friendly process for managing municipal compliance data via a central Excel file, which is automatically monitored and ingested by the application. The project also includes a comprehensive, self-contained demo mode for testing and presentations.

## 🚀 Quickstart (Container Execution)
The repository is packaged as a multi-container Docker application.

```bash
# 1. Create your environment file from the example
cp .env.example .env

# 2. Fill in your API keys for production, or leave them blank for demo mode.

# 3. Build and run the services with Docker Compose
docker compose up --build -d
```

## 🎛️ Configuration & Controls
The application's behavior is controlled through two main files:

1.  **`.env` (Application Mode & Secrets)**: This file is the primary control for switching between modes.
    -   **`APP_MODE`**: Set to `production` to use live API keys and data paths. Set to `demo` to activate the self-contained demo environment with mock data.
    -   **API Keys**: Holds all necessary secrets for production services.

2.  **`config/scale.yaml` (Behavioral Tuning)**: This file fine-tunes the application's behavior.
    -   Enable or disable bot platforms (Teams and Slack).
    -   Configure the path to the **production** compliance data Excel file.
    -   Swap out LLM and vector database providers.

## 🎬 Running in Demo Mode
To run the application in a self-contained demo mode without any live API keys:

1.  **Set the Mode:** In your `.env` file, set `APP_MODE=demo`.
2.  **Run the App:** Start the application with `docker compose up -d`.
3.  **Seed the Demo Database:** Run the one-time seeder script to populate the local ChromaDB with realistic fake project data:
    ```bash
    docker compose exec mustang-whisper python -m scripts.demo.seed_demo_database
    ```
The application will now use the mock ShopVOX factory and the demo compliance Excel file automatically.

## 📍 Project Structure
- **`app/`**: Core application logic.
- **`config/`**: Contains `scale.yaml` and the **live** `compliance_data.xlsx`.
- **`docs/`**: Project manifests, architectural documents, and playbooks.
- **`scripts/demo/`**: Contains all tools for the demo environment, including the seeder script and the demo Excel file.
