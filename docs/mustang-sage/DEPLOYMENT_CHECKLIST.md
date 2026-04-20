# 🚀 MUSTANG SAGE — PHASE 6 DEPLOYMENT CHECKLIST

**Date:** 2026-04-20
**Project Phase:** 6 (Deployment / Go-Live)
**Status:** APPROVED FOR MVP ROLLOUT

---

## 💰 1. Cost Estimate & Budget Bounds

The system has been architected to adhere strictly to serverless/scale-to-zero compute models to ensure low overhead for the MVP Phase. 

- **Database (Neon Serverless Postgres):** ~$0 - $15 / month (Scale to zero enabled, minimal pgvector storage).
- **In-Memory Cache (Redis):** ~$5 / month (or $0 if using a lightweight swappable container).
- **LLM API Usage (Gemini/OpenAI):** < $10 / month (Based on estimated ~500 quote requests/month, with context window optimization).
- **Container Hosting (Agnostic - e.g., Fly.io / AWS ECS / Swarm):** ~$10 - $15 / month for base app & worker containers.

**TOTAL TARGET BUDGET:** **< $50.00 / month**

> [!NOTE] 
> Usage will be audited monthly. If LLM context scaling causes prices to increase unexpectedly, `scale.yaml` supports instantly toggling models down to cheaper variants.

---

## 🔄 2. Rollback & Swap Plan

Mustang Sage uses a highly decoupled, agnostic container architecture.

### Swappable Hosting Targets
The primary deployment vehicle is `docker-compose`. Deployment is kept agnostic but built to swap seamlessly across generic runners:
1. **Fly.io:** Utilizing `fly.toml` for edge-network distribution and quick rollback.
2. **AWS (ECS/Fargate):** Built to be cleanly pushed to ECR and run immutably.

### Failure State Playbooks
- **LLM API Saturation / Hallucination Spike:** 
  - *Action:* Change `ENABLE_NEW_AGENTS=false` in the environment to halt new routing.
  - *Action:* Update `scale.yaml` to enforce strict model fallbacks and restart the application container.
- **Database Corruption / pgvector Desync:**
  - *Action:* Restore from the latest point-in-time Neon snapshot via the Dashboard.
  - *Action:* Roll back to the previous known-good Docker image tag.
- **ShopVOX Integration Issues / 429 Rate Limits:**
  - *Action:* Hard-stop the container via `docker-compose down`.
  - *Action:* Reps fall back to manual quoting in shopVOX until the token-bucket rate limiter configuration is addressed.

---

## 🛡️ 3. Audit & Monitoring Confirmations

- ✅ **Observability:** OpenTelemetry and Jaeger containers are actively attached and reporting traces (Phase 7).
- ✅ **CVEMonitor & DepScanner:** Automated security scans are configured inside the `app/skills/audit_system.py` background tasks (Phase 8).
- ✅ **Guardrails:** HITL (Human in the loop), GeoLock boundaries, and 35% margin floor flags have successfully passed QA tests.

---

## ✍️ 4. 12-Role Governance Sign-Off

The following project governance roles have officially verified the MVP limits and authorize the production deployment.

- `[X]` **Product Manager:** MVP Scope met.
- `[X]` **Architect:** Agnostic factory boundaries and swappable targets confirmed.
- `[X]` **Database Manager:** Neon/pgvector schema and encryption verified.
- `[X]` **Infosec Lead:** HITL Kill switch verified.
- `[X]` **DevOps Manager:** Host-agnostic setup and cost limits approved.
- `[X]` **AI Engineer:** Agent logic, grounding, and fallbacks passing.
- `[X]` **QA Engineer:** End-to-end trace pipelines passing >80% coverage.
- `[X]` **Data Analyst:** Telemetry hooks operational.
- `[X]` **Compliance Officer:** Address locking and KMC/RMC/PMC zoning accurate.
- `[X]` **Marketing Manager:** Comm. card templates reviewed for branding.
- `[X]` **UX/UI Designer:** Adaptive Cards UI mapping properly to MS Teams.
- `[X]` **Project Lead:** All blockers cleared. Go-Live approved.

**Advisory Checks Cleared:**
- `[X]` **Red Team Hacker:** No unmitigated SEV-0 findings.
- `[X]` **Devil's Advocate:** Rollback and cost-overrun risks documented and accepted.
