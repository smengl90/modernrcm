# Company Vision: Building the AI-Native RCM OS

## 1. Vision

We envision a world where healthcare providers never lose a dollar they're owed and revenue cycle management (RCM) becomes fully programmable, AI-driven, and human-assisted only when necessary. Our platform will be the **AI-native RCM Operating System (OS)** — orchestrating every step of the revenue cycle with a blend of browser agents, clearinghouse integrations, and large language models (LLMs).

Ultimately, we aim to be the **financial OS of healthcare**, replacing manual billing operations with a self-healing, predictive system that ensures providers get paid faster, more accurately, and with less overhead.

---

## 2. Mission

To transform RCM from a labor-intensive, error-prone process into an autonomous, transparent, and efficient system powered by AI and reinforced by human expertise.

---

## 3. The Problem Today

- **Manual bottlenecks**: 20–30% of revenue cycle tasks still require humans logging into payer portals, uploading documents, or re-coding claims
- **Inefficient automation**: Clearinghouses handle the basics (eligibility, submissions), but exceptions and denials still need costly staff
- **High cost of collections**: RCM can cost 4–10% of collections, with average days in A/R (DSO) often exceeding 40
- **Burnout & turnover**: Billing staff face repetitive, low-value tasks that are hard to scale

**The result**: leakage, delays, and rising costs, especially for mid-market providers.

---

## 4. Our Solution

We're building the **AI-Native, Human-Assisted RCM OS**:

### 4.1 Browser Agent Spine
- Automates payer portal workflows where APIs/EDI fail
- Executes tasks (eligibility, claim status, appeals, posting) via declarative YAML flows
- Generates structured JSON outputs + artifacts for auditability

### 4.2 Recorder for Ops
- Ops staff record new workflows → system exports YAML flows automatically
- Democratizes automation; engineers focus only on hard edge cases

### 4.3 Human-in-the-Loop (HITL)
- Operators resolve MFA, CAPTCHA, ambiguous denials
- Corrections become training data, improving automation over time

### 4.4 LLM Augmentation Layer
- LLMs parse unstructured data (EOBs, denial PDFs)
- Draft appeals, coding suggestions, and flow fixes
- Ops supervise/approve, ensuring safety and correctness

### 4.5 Autonomous RCM OS
- **Predictive**: denial prediction and proactive claim optimization
- **Self-healing**: agents + LLMs detect portal drift and patch flows automatically
- **Exposed as APIs**: programmable financial infrastructure for healthtech builders

---

## 5. Roadmap

### Phase 0 – Browser Agent Foundations (Now)

**Goal**: Prove payer portal automation works.

- Build browser agent runtime (Playwright + DSL + YAML)
- Recorder for ops → capture flows, export YAML
- Launch Availity eligibility & UHC claim status
- Normalize into JSON (EligibilityResponse, ClaimStatus)
- HITL hooks for MFA, CAPTCHA, layout drift

**Success metric**: ≥70% automation on pilot flows, p95 < 3 min

---

### Phase 1 – Full RCM Service With Hybrid Automation (6–12 months)

**Goal**: Operate as RCM vendor with BPO + AI agents.

- Expand portal coverage (BCBS, Aetna, Medicare)
- Add workflows (claim submission validation, EOB parsing, appeals)
- Clearinghouse integration where possible; browser agent fills gaps
- Ops console with HITL dashboard & automation coverage reporting

**Success metric**: 20–30% lower cost vs. traditional RCM; automation ≥50%

---

### Phase 2 – Human-Assisted LLM Layer (12–24 months)

**Goal**: LLMs augment portal agents; humans supervise.

- LLM parsers for denial reasons & EOBs
- Draft appeals & coding suggestions
- LLM proposes YAML fixes for broken flows; ops approve
- Every correction becomes training data → proprietary dataset moat

**Success metric**: HITL rate <20%; LLM correctness ≥80% with ops approvals

---

### Phase 3 – Autonomous RCM OS (24–36 months)

**Goal**: Be the category-defining financial OS.

- All RCM tasks = typed, composable workflows
- Self-healing portal automation
- Predictive denials, coding optimization, proactive routing
- Lightweight PMS spine (scheduler, charge capture)
- Expose APIs to other builders

**Success metric**: 85–90% automation; HITL only for true edge cases; DSO reduced 30–40%

---

## 6. Strategic Positioning

- **Today**: "We're proving payer portal automation with a browser agent + recorder."
- **12 months**: "We're the AI-powered RCM vendor, delivering superior economics."
- **24 months**: "We're building the AI-native RCM OS, where humans supervise and LLMs do the work."
- **36 months**: "We're the category owner: programmable, autonomous revenue cycle infrastructure for healthcare."

---

## 7. Example Metrics by Phase

| Phase | Automation Coverage | HITL % | Avg Run Time | Provider ROI |
|-------|-------------------|--------|--------------|--------------|
| Phase 0 | ~70% (pilot flows) | <10% | <3 min | Feasibility + automation |
| Phase 1 | 50–60% (multi-payer) | 20–30% | <2 min | 20–30% lower ops cost |
| Phase 2 | 70–80% | <20% | <90 sec | 30–40% faster collections |
| Phase 3 | 85–90% | <10% | <60 sec | 30–40% DSO reduction |

---

## 8. Why Us / Moat

- **Data exhaust**: Every claim, denial, portal scrape, and human correction feeds our LLMs
- **Composable OS**: Typed workflows and schemas create a programmable system others can build on
- **Ops + AI synergy**: Recorder + HITL makes ops a training function, not just cost center
- **First-mover advantage**: Payer portal automation + LLM + RCM vertical focus = differentiated moat

---

## Summary

Phase 0 (browser agent + recorder) is the spine. It creates the workflow language, automation rails, and data exhaust that make Phases 1–3 possible. Over 3 years, this evolves into the **AI-native, human-assisted, autonomous RCM OS** — the financial operating system for healthcare.