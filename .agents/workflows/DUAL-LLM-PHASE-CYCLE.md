# Dual-LLM Phase Cycle System (v2.1)
### Human-Bridge & Agentic Integration Framework

This framework utilizes two distinct LLMs to eliminate self-rationalization bias, overseen by a **Human Bridge** who manages the handoff and maintains high-level situational awareness.

---

## 👥 The Two Teams

### 🔨 Builder Team (LLM 1 — e.g., Gemini)
*Focused on implementation, construction, and creative problem-solving.*

- **Primary Tooling:** Gemini 1.5 Pro / Ultra + Python Execution
- **Key Roles:** Product Manager, Architect, AI Engineer, Database Manager, DevOps Manager, UX/UI Designer, Data Analyst

### 🔍 Checker Team (LLM 2 — e.g., Claude)
*Focused on critique, security, and logic-chain verification.*

- **Primary Tooling:** Claude 3.5 Sonnet / Opus + Claude Code / Antigravity
- **Key Roles:** QA Engineer, Devil's Advocate, Red Team Hacker, Infosec Lead, Project Lead

### 🏛️ Governance Gate
*Focused on phase sign-off. Not a builder or checker — asks one question: is this phase done and safe to advance?*

- **Key Roles:** Compliance Officer, Marketing Manager (if user-facing), Project Lead

---

## 🌉 The Human Bridge

The human is the **intentional friction** in the system. You do not just move data between LLMs — you audit the handoff.

- **Read-In:** Before switching models, read the current output and identify any hallucination loops, mission drift, or issues the LLM didn't catch about itself.
- **Context Preservation:** Ensure the mission defined by the Product Manager role isn't lost in technical minutiae as rounds progress.
- **Manual Trigger:** The cycle only advances when you physically move data from one environment to the other. There is no automation between LLMs. You are the circuit breaker.

---

## 🔄 The 7-Round Cycle (Per Phase)

| Round | Action | Responsibility | Human Bridge Action |
| :--- | :--- | :--- | :--- |
| **R1** | Plan & Build | Builder Team | Read the output. Check for mission drift before switching. |
| **R2** | Root Cause Audit | Checker Team | **SWITCH:** Move R1 output to Checker LLM. |
| **R3** | Iterative Build | Builder Team | **SWITCH:** Move ranked suggestions to Builder LLM. |
| **R4** | Self-Fix Pass | Builder Team | Builder resolves internal conflicts, tightens loose ends, makes output coherent before next review. No switch needed. |
| **R5** | Final Review | Checker Team | **SWITCH:** Move R4 output to Checker LLM. |
| **R6** | Production Build | Builder Team | **SWITCH:** Move final clearance to Builder LLM. |
| **R7** | Governance Gate | Human + Gate Roles | Final sign-off. Approve to advance, loop back, or override. |

---

## 🔍 Checker Logic: Root Cause Analysis (RCA)

The Checker Team never flags a symptom without tracing its origin. Chains have no depth limit — go as deep as the problem requires.

**Process:**

1. **Flag the surface symptom** — "The database connection fails."
2. **Trace the blast radius** — "This breaks user auth and the data ingestion pipeline."
3. **Find the root cause chain:**
   ```
   Symptom:   Connection fails
   Link:      Invalid environment variable format
   Link:      Variable set using a legacy schema template
   Root:      Architect role in R1 pulled an outdated config pattern
   ```
4. **Deliver ranked suggestions** — Prioritized by criticality, presented as suggestions. The Builder Team decides *how* to fix it.

**Format:**
```
ISSUE FOUND: [Surface symptom]

ROOT CAUSE CHAIN:
└─ Root cause: [Why it happened]
   └─ Breaks: [What that affects]
      └─ Breaks: [What that affects]
         └─ Surface symptom: [What you see]

RANKED SUGGESTIONS:
1. [Most critical fix] — because [reasoning]
2. [Second priority] — because [reasoning]
3. [Third priority] — because [reasoning]

Note: These are suggestions. Builder Team decides what to implement and how.
```

---

## 📋 The Handoff Template

Use this when moving data between LLMs to preserve context across the switch.

```markdown
### HANDOFF: [Phase Name] — Round [#]
**FROM:** [Builder / Checker / Governance]
**TO:** [Builder / Checker / Governance]
**OBJECTIVE:** [Current phase goal]

**CONTEXT SUMMARY:**
- What was attempted: [Summary]
- Critical files / code: [Paths or snippets]
- Key decisions made: [Any architectural or scope decisions]

**FEEDBACK / INSTRUCTIONS:**
1. [Suggestion — Priority: High]
2. [Suggestion — Priority: Medium]
3. [Suggestion — Priority: Low]

**HUMAN BRIDGE NOTE:**
[Your personal observation — where the model is drifting, succeeding,
or where you're overriding a suggestion and why]
```

---

## 🏛️ Round 7: Governance Gate

The final manual check before the cycle repeats for the next phase.

| Decision | Condition | Action |
| :--- | :--- | :--- |
| **Approved** | Phase is safe, functional, and documented | Advance to next phase |
| **Loop Back** | Security or logic flaw discovered | Return to Round 3 with root cause report |
| **User Override** | LLM is flagging a non-issue | Human advances despite warnings — log reasoning |
| **Escalation** | Gate has looped back 2+ times on same issue | Tier 4 escalation — human breaks the deadlock directly |

**Tier 4 Escalation format:**
```
🔴 CROSS-LLM ESCALATION
Round: [N]
Issue: [Description]
Root cause chain: [Full chain]
Loop count: [N times flagged]

Options:
  A) Builder Team addresses [specific fix]
  B) User accepts risk and advances
  C) Phase scope reduced to exclude unresolved issue

Human decides. Decision logged in .build-context.md.
```

---

## 📌 Key Principles

- **Depth has no limit.** Tracing the root cause is more important than the timeline. The goal is to solve issues before deployment, not timebox the analysis.
- **Suggestions, not mandates.** The Checker Team and Governance Gate deliver ranked suggestions. The Builder Team owns the implementation decision.
- **The Human Bridge is the only automation.** There is no pipeline between LLMs. You switch manually, you read before you switch, and you note what you observe. This is a feature, not a limitation.
- **Mission over minutiae.** The Product Manager's mission definition from Round 1 is the anchor. If technical rounds are drifting from it, the Human Bridge catches it and resets.
- **The Governance Gate is not the Checker.** The Gate's only question is: *is this phase done and safe to advance?* It does not re-do the Checker's work.
