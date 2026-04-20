# 📚 MUSTANG SAGE PROJECT MANIFEST
**Complete Reference Library for Building & Operating Mustang Sage**

---

## 🚀 START HERE

You are building **The Mustang Sage** — a sales co-pilot for Mustang Sign Company that runs in Teams and uses Antigravity orchestration.

**Everything you need is in this manifest.** Reference files as needed during building. Nothing is hidden.

---

## 📦 WHAT'S IN THIS PROJECT

### Core System
- **`mustang_sage_v2_4_0_complete.md`** — The system prompt (what Mustang Sage does)
- **`agent.md`** — Kernel directives (how AI tools read system prompts)
- **Role Skills (12 core + 2 advisory)** — Who owns what decision

### Framework Guides (10-Part)
- **`00_START_HERE.md`** — Entry point, risk scoring, 6 decisions
- **`01_QUICK_REFERENCE.md`** — Formulas, checklists, matrices
- **`02_COMPLETE_GUIDE.md`** — Deep methodology, 8-step process
- **`03_DEPENDENCY_MANAGEMENT.md`** — Python deps, reproducible builds
- **`04_AI_ASSISTANT_INTEGRATION.md`** — Guide AI tools, prompt patterns
- **`05_BUILD_CONTEXT_AND_BUGS.md`** — Memory file templates
- **`06_INFRASTRUCTURE_AS_CODE.md`** — Docker, Terraform, deployment
- **`07_CONFIGURATION_CONTROL.md`** — `scale.yaml` cost controls
- **`08_AGNOSTIC_FACTORIES.md`** — Swap dependencies via config
- **`09_AUDIT_AND_MAINTENANCE.md`** — Scheduled audits, HITL sign-off

### Governance (12 Roles + 2 Advisory)
**Core Roles (Blocking Authority):**
1. Product Manager — Mission, success metrics, go/no-go
2. Architect — Patterns, vendor lock-in prevention
3. Database Manager — Schema, encryption, backups
4. Infosec Lead — Audits, kill switch, breach prevention
5. DevOps Manager — Deployment, costs, reliability
6. AI Engineer — Agent implementation, code quality
7. QA Engineer — Tests, coverage, quality gates
8. Data Analyst — Metrics, dashboards, anomalies
9. Compliance Officer — GDPR/CCPA, legal risk
10. Marketing Manager — Brand rules, final approval
11. UX/UI Designer — Interfaces, accessibility
12. Project Lead — Team coordination, blockers

**Advisory Roles (Challenge & Inform):**
- Red Team Hacker — Attack surfaces, vulnerability discovery
- Devil's Advocate — Assumptions, pre-mortems, failure analysis

### Orchestration Patterns
- **`DUAL-LLM-PHASE-CYCLE.md`** — Builder + Checker LLM structure (if using 2 LLMs)
- **`MASTER_AGENT_DISCOVERY_PROMPT.md`** — Interview prompt for architecture (use before building)
- **`MASTER_DOCS_PROMPT.md`** — Post-build documentation generator

---

## 🗂️ FILE ORGANIZATION

```
project-root/
├── mustang_sage_v2_4_0_complete.md      ← THE SYSTEM PROMPT
├── agent.md                             ← Kernel (read first)
├── .build-context.md                    ← Project memory (AI reads this)
├── .bugs_tracker.md                     ← Bug tracking (AI reads this)
├── MUSTANG_SAGE_PROJECT_MANIFEST.md     ← You are here
│
├── docs/
│   ├── AgentSpec.md                     ← Arch spec (generated from discovery)
│   ├── mustang-sage/
│   │   ├── MISSION_AND_METRICS.md       ← Product Manager owns
│   │   ├── ARCHITECTURE.md              ← Architect owns
│   │   ├── SECURITY_AUDIT.md            ← Infosec Lead owns
│   │   ├── RED_TEAM_FINDINGS.md         ← Red Team Hacker owns
│   │   ├── RISK_REGISTER.md             ← Devil's Advocate owns
│   │   ├── DASHBOARD_CONFIG.yaml        ← Data Analyst owns
│   │   └── DEPLOYMENT_CHECKLIST.md      ← DevOps Manager owns
│   │
│   └── framework/
│       ├── 00_START_HERE.md
│       ├── 01_QUICK_REFERENCE.md
│       ├── 02_COMPLETE_GUIDE.md
│       ├── 03_DEPENDENCY_MANAGEMENT.md
│       ├── 04_AI_ASSISTANT_INTEGRATION.md
│       ├── 05_BUILD_CONTEXT_AND_BUGS.md
│       ├── 06_INFRASTRUCTURE_AS_CODE.md
│       ├── 07_CONFIGURATION_CONTROL.md
│       ├── 08_AGNOSTIC_FACTORIES.md
│       └── 09_AUDIT_AND_MAINTENANCE.md
│
├── roles/
│   ├── GENERIC-01-product-manager-role-skill.md
│   ├── GENERIC-02-architect-role-skill.md
│   ├── GENERIC-03-database-manager-role-skill.md
│   ├── GENERIC-04-infosec-lead-role-skill.md
│   ├── GENERIC-05-devops-manager-role-skill.md
│   ├── GENERIC-06-ai-engineer-role-skill.md
│   ├── GENERIC-07-qa-engineer-role-skill.md
│   ├── GENERIC-08-data-analyst-role-skill.md
│   ├── GENERIC-09-compliance-officer-role-skill.md
│   ├── GENERIC-10-marketing-manager-role-skill.md
│   ├── GENERIC-11-ux-ui-designer-role-skill.md
│   ├── GENERIC-12-project-lead-role-skill.md
│   ├── GENERIC-13-red-team-hacker-role-skill.md
│   ├── GENERIC-14-devils-advocate-role-skill.md
│   └── GENERIC-ROLES-MASTER-GUIDE.md
│
├── config/
│   ├── scale.yaml                       ← All configuration (AI reads this)
│   └── mustang_sage_brand_rules.txt     ← Marketing Manager rules
│
├── skills/
│   ├── geo-lock-guard/
│   │   ├── geo-lock-guard.yaml          ← Skill metadata
│   │   └── geo-lock-guard.py            ← Implementation
│   ├── distance-calculator/
│   ├── margin-validator/
│   ├── code-citer/
│   ├── comm-template-engine/
│   └── price-scrubber/
│
├── .agents/
│   ├── workflows/
│   │   └── mustang_sage/
│   │       ├── system_prompt.md         ← Antigravity reads this
│   │       ├── liaison_agent.py
│   │       ├── archivist_agent.py
│   │       ├── auditor_agent.py
│   │       └── merchant_agent.py
│   │
│   └── factories/
│       ├── shopvox_factory.py
│       ├── s3_vector_factory.py
│       ├── geo_logistics_factory.py
│       └── comm_factory.py
│
├── tests/
│   ├── test_liaison_agent.py
│   ├── test_archivist_agent.py
│   ├── test_auditor_agent.py
│   ├── test_merchant_agent.py
│   └── test_margin_validator.py
│
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── requirements.txt
└── requirements-lock.txt
```

---

## 🔍 HOW TO USE THIS MANIFEST

### I'm Building Agents (AI Engineer)

1. Read: **`mustang_sage_v2_4_0_complete.md`** (what you're building)
2. Read: **`agent.md`** (how to use factories, patterns)
3. Read: **`GENERIC-06-ai-engineer-role-skill.md`** (your responsibilities)
4. Check: **`08_AGNOSTIC_FACTORIES.md`** (factory pattern for dependencies)
5. Build: Use **`GENERIC-AGENT-TEMPLATE-SKILL.md`** as template for each agent
6. Test: **`07_QA_ENGINEER_ROLE_SKILL.md`** defines test requirements
7. Reference: **`.build-context.md`** for decisions made so far

### I'm Reviewing Code (Architect)

1. Read: **`02-architect-role-skill.md`** (your blocking authority)
2. Check: **`08_AGNOSTIC_FACTORIES.md`** (enforcement checklist)
3. Review: Every PR uses factories, no hardcoded imports
4. Verify: **`vendor-swap-test`** passes (prove swappability)
5. Document: Add decision to **`docs/mustang-sage/ARCHITECTURE.md`**

### I'm Testing (QA Engineer)

1. Read: **`GENERIC-07-qa-engineer-role-skill.md`** (your authority)
2. Check: **`01_QUICK_REFERENCE.md`** (risk scoring, guardrails)
3. Verify: Tests >80% coverage, latency <10s
4. Run: **7-step troubleshooting protocol** for any bugs
5. Document: **`.bugs_tracker.md`** for patterns
6. Gate: Phase advance only after quality checkpoint cleared

### I'm Deploying (DevOps Manager)

1. Read: **`GENERIC-05-devops-manager-role-skill.md`** (your authority)
2. Check: **`06_INFRASTRUCTURE_AS_CODE.md`** (Dockerfile, Terraform)
3. Setup: **`07_CONFIGURATION_CONTROL.md`** (`scale.yaml`)
4. Monitor: **`08_DATA_ANALYST_ROLE_SKILL.md`** (what metrics to track)
5. Checklist: **`09_AUDIT_AND_MAINTENANCE.md`** (pre-deploy verification)

### I'm Doing Security (Infosec Lead)

1. Read: **`GENERIC-04-infosec-lead-role-skill.md`** (your authority)
2. Verify: HITL enforcement (no autonomous sends)
3. Test: Kill switch works instantly
4. Review: Red Team findings from **`docs/mustang-sage/RED_TEAM_FINDINGS.md`**
5. Audit: **`09_AUDIT_AND_MAINTENANCE.md`** (scheduled audits)
6. Gate: Kill switch tested and documented before deploy

### I'm Attacking It (Red Team Hacker)

1. Read: **`GENERIC-13-red-team-hacker-role-skill.md`** (your mission)
2. Map: Attack surfaces (Liaison → Archivist → Auditor → Merchant)
3. Test: Prompt injection, data exfiltration, privilege escalation
4. Document: Findings in **`docs/mustang-sage/RED_TEAM_FINDINGS.md`**
5. Deliver: Severity breakdown (critical, high, medium, low)
6. Retest: After Infosec Lead applies fixes

### I'm Challenging Assumptions (Devil's Advocate)

1. Read: **`GENERIC-14-devils-advocate-role-skill.md`** (your mission)
2. Run: Pre-mortem at start of each phase
3. Challenge: Every major architectural decision
4. Document: **`docs/mustang-sage/RISK_REGISTER.md`**
5. Force: Assumptions validated or risks accepted explicitly
6. Escalate: If concerns are being ignored

---

## 📊 PHASE GATES (What Blocks Advancement?)

### Phase 1: Planning
**Who approves:** Product Manager, Architect, Devil's Advocate
**Checklist:**
- [ ] Mission defined (MISSION_AND_METRICS.md)
- [ ] Success metrics locked
- [ ] Architecture approach approved
- [ ] Risk register created
- [ ] Assumptions listed and validated or accepted

### Phase 2: Build
**Who approves:** AI Engineer, Architect, QA Engineer
**Checklist:**
- [ ] All agents coded (4 agents: Liaison, Archivist, Auditor, Merchant)
- [ ] Factories used throughout (no hardcoded imports)
- [ ] Tests passing (>80% coverage)
- [ ] Code review approved
- [ ] Latency targets met (<10s full quote)

### Phase 3: Security
**Who approves:** Infosec Lead, Database Manager, Red Team Hacker
**Checklist:**
- [ ] HITL enforcement verified (quote approval logged)
- [ ] Kill switch tested (works <5 sec)
- [ ] Data encrypted at rest
- [ ] Red Team findings severity assessed
- [ ] Critical findings: 0 or fixed

### Phase 4: Quality
**Who approves:** QA Engineer, Data Analyst
**Checklist:**
- [ ] Code coverage >80%
- [ ] Margin validator logic tested
- [ ] 3-Day Nudge timing verified
- [ ] Dashboard ready to measure metrics
- [ ] Edge cases documented and handled

### Phase 5: Compliance & Brand
**Who approves:** Compliance Officer, Marketing Manager, UX Designer
**Checklist:**
- [ ] PII handling compliant
- [ ] Email templates on-brand
- [ ] Adaptive Cards accessible
- [ ] Legal review complete

### Phase 6: Deployment
**Who approves:** DevOps Manager, Project Lead (coordinates all)
**Checklist:**
- [ ] Cost estimate within budget
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Audit scheduler configured
- [ ] All 12 roles sign off

---

## 🎯 QUICK LOOKUPS

### "What does the Sage do?"
→ **`mustang_sage_v2_4_0_complete.md`**

### "How do I use factories?"
→ **`08_AGNOSTIC_FACTORIES.md`** + **`agent.md`** (factories section)

### "What are my responsibilities?"
→ **`GENERIC-[N]-[ROLE]-role-skill.md`** (find your role number)

### "How do I test this?"
→ **`GENERIC-07-qa-engineer-role-skill.md`** + **`01_QUICK_REFERENCE.md`** (7-step protocol)

### "What's the risk if something goes wrong?"
→ **`02_COMPLETE_GUIDE.md`** (risk assessment section) + **`GENERIC-14-devils-advocate-role-skill.md`**

### "How do I deploy this?"
→ **`06_INFRASTRUCTURE_AS_CODE.md`** + **`GENERIC-05-devops-manager-role-skill.md`**

### "What's the audit schedule?"
→ **`09_AUDIT_AND_MAINTENANCE.md`** + **`07_CONFIGURATION_CONTROL.md`** (`scale.yaml`)

### "How does this system handle [X]?"
→ Search **`mustang_sage_v2_4_0_complete.md`** for the component, then cross-reference with relevant role skill

---

## 📝 BEFORE YOU START BUILDING

### Step 1: Read This Manifest (5 min)
You're reading it now. ✅

### Step 2: Read the System Prompt (10 min)
Open **`mustang_sage_v2_4_0_complete.md`** and skim it. Understand what the four agents do.

### Step 3: Read Your Role Skill (10 min)
Find your role in the list above. Read that specific skill file. Understand your authority and responsibilities.

### Step 4: Read the Agent Kernel (5 min)
Open **`agent.md`**. It tells you (and the AI tools) how to follow the framework.

### Step 5: Assign Roles (5 min)
Create **`docs/mustang-sage/ROLE_ASSIGNMENTS.md`**:
```markdown
# Mustang Sage — Role Assignments

Product Manager: [Your Name] | slack: [@user]
Architect: [Your Name] | slack: [@user]
... (all 12 roles)
```

### Step 6: Create AgentSpec (30 min)
Use **`MASTER_AGENT_DISCOVERY_PROMPT.md`** with a strong LLM to lock down:
- MVP scope (Phase 1 only: Quoting + Compliance)
- Risk score (confirmed: 11/17)
- Orchestration (confirmed: Antigravity)
- Required guardrails (HITL, geo-lock, margin floor, estimate watermark)
- Success metrics
- Phase 1 implementation order

Output: **`docs/AgentSpec.md`** (the spec that Architect and AI Engineer follow)

### Step 7: Start Building
Hand **`docs/AgentSpec.md`** + **`mustang_sage_v2_4_0_complete.md`** to AI Engineer.

They build using:
- **`GENERIC-AGENT-TEMPLATE-SKILL.md`** (template for each agent)
- **`08_AGNOSTIC_FACTORIES.md`** (factory pattern)
- **`.build-context.md`** (to log decisions)

---

## 🚀 YOU'RE READY

Everything you need to build Mustang Sage is in this library.

**Nothing is hidden. Everything is referenced.**

When builders ask questions, they search this manifest first. If the answer isn't here, they create a new document and add it to the manifest.

---

## 📌 MANIFEST META

**Version:** 1.0.0  
**Created:** April 11, 2026  
**Purpose:** Single source of truth for Mustang Sage project  
**Update:** Add new docs to the manifest as they're created  
**Audience:** AI Engineer, Architect, all 12 roles, AI tools (Cursor, Claude Code, Antigravity)

---

## 🎯 THE GOLDEN RULE

> **"If it's not in the manifest, it doesn't exist yet. Create it, add it here, and reference it."**

This keeps the project organized, searchable, and handoff-ready.

---

*Everything below this line is reference material organized by role and phase. Start at the phase gate you're in and read what you need.*
