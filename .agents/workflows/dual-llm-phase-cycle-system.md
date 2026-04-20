# Dual-LLM Phase Cycle System (v2.0)

## Human-Bridge & Agentic Integration Framework

This framework utilizes two distinct LLMs to eliminate self-rationalization bias, overseen by a Human Bridge who manages the handoff and maintains high-level situational awareness.

## 👥 The Two Teams

### 🔨 Builder Team (LLM 1 — e.g., Gemini)

Focused on implementation, construction, and creative problem-solving.

- **Primary Tooling:** Gemini 1.5 Pro / Ultra + Python Execution
- **Key Roles:** 
  - Product Manager
  - Architect
  - AI Engineer
  - Database Manager
  - DevOps

### 🔍 Checker Team (LLM 2 — e.g., Claude)

Focused on critique, security, and logic-chain verification.

- **Primary Tooling:** Claude 3.5 Sonnet / Opus + Claude Code / Antigravity
- **Key Roles:**
  - QA Engineer
  - Devil's Advocate
  - Red Team Hacker
  - Infosec Lead

### 🌉 The Human Bridge (The "Switch")

The human is the intentional friction in the system. You do not just move data; you audit the handoff.

- **Read-In:** Before switching models, you must read the current output to identify "hallucination loops."
- **Context Preservation:** You ensure the "Mission" defined by the PM role isn't lost in technical minutiae.
- **Manual Trigger:** The cycle only advances when you physically move the data from one environment to the other.

## 🔄 The 7-Round Cycle (Per Phase)

| Round | Action | Responsibility | The "Switch" |
|-------|--------|----------------|--------------|
| R1 | Plan & Build | Builder Team (Gemini) | Human reads the initial draft/code. |
| R2 | Root Cause Audit | Checker Team (Claude) | SWITCH: Human moves R1 output to Claude. |
| R3 | Iterative Build | Builder Team (Gemini) | SWITCH: Human moves Ranked Suggestions to Gemini. |
| R4 | Self-Fix Pass | Builder Team (Gemini) | Gemini performs internal cleanup. |
| R5 | Final Review | Checker Team (Claude) | SWITCH: Human moves R4 output to Claude. |
| R6 | Production Build | Builder Team (Gemini) | SWITCH: Human moves final clearance to Gemini. |
| R7 | Governance Gate | HUMAN + Gatekeeper | Final sign-off to advance to the next phase. |

## 🛠️ Checker Logic: Root Cause Analysis (RCA)

The Checker Team (Claude) never flags a symptom without tracing its origin.

### Example Workflow

**1. Surface Symptom:**
> "The database connection fails."

**2. Blast Radius:**
> "This breaks the user auth and the data ingestion pipeline."

**3. Root Cause Chain:**
- **Symptom:** Connection Fail
- **Link:** Invalid environment variable format
- **Root:** The Architect role in R1 used a legacy schema template

**4. Ranked Suggestions:**
Delivered as suggestions, not mandates. The Builder decides how to fix it.
