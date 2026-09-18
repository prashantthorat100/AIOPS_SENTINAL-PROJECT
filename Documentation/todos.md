# AIOps Sentinel — Project TODOs & Phase Plan

**Team size:** 4
**Roles (equal contribution, split by architecture layer):**
- **P1 — Data & Infra Engineer:** Telemetry ingestion, Kafka/Flink, datasets
- **P2 — ML Engineer (Detection & RCA):** Anomaly detection, Root-Cause GNN
- **P3 — AI/Platform Engineer (LLM & Safety):** LLM Explainer (RAG), OPA Policy Engine, Remediation Executor
- **P4 — Full-Stack Engineer:** Database (Supabase), FastAPI/Node backend APIs, React frontend

Each phase lists one task per person so contribution stays balanced. Check off tasks as you go.

---

## Phase 0 — Setup & Planning (Week 1)

- [x] **P1:** Set up shared GitHub repo, branching strategy, and project board (Kanban/Trello/GitHub Projects)
- [ ] **P2:** Research and shortlist candidate datasets (OpenTelemetry AIOps Benchmark, Microsoft Services Dataset, LO2 Microservice API Anomaly Dataset)
- [ ] **P3:** Draft the initial system architecture diagram (4 layers) and circulate for team review
- [ ] **P4:** Set up local dev environment: Docker Compose skeleton with placeholders for Kafka, Supabase/Postgres, FastAPI, React
- [x] **All:** Read the Client Brief and Technical Blueprint together; agree on scope boundaries and Definition of Done (P1 completed review)

**Milestone:** Repo live, environments running, datasets chosen, architecture agreed.

---

## Phase 1 — Data Foundation (Weeks 2–3)

- [ ] **P1:** Build telemetry ingestion simulators (synthetic metrics/logs/traces/K8s events) to feed the pipeline before real data is available
- [ ] **P2:** Preprocess and label anomaly data from chosen datasets; define train/val/test splits
- [ ] **P3:** Curate a small library of sample remediation playbooks (text runbooks) to later ground the LLM/RAG
- [ ] **P4:** Design and implement the Supabase/PostgreSQL schema (incidents, alerts, remediation_playbooks, telemetry_metrics) with pgvector enabled

**Milestone:** Database live with schema; sample/simulated telemetry flowing; labeled datasets ready.

---

## Phase 2 — Ingestion & Processing Layer (Weeks 3–4)

- [ ] **P1:** Stand up Kafka topics (metrics.raw, logs.raw, traces.raw, events.k8s) and Flink jobs for windowed aggregation + schema normalization
- [ ] **P2:** Build early feature extraction (rate-of-change, z-scores) consumed by the anomaly model
- [ ] **P3:** Define the event contract/schema between Ingestion → Intelligence Engine (what a "normalized feature vector" looks like)
- [ ] **P4:** Build API endpoints to write processed telemetry into Supabase (telemetry_metrics table)

**Milestone:** Raw → normalized telemetry pipeline working end-to-end into the database.

---

## Phase 3 — Intelligence Engine: Detection & Clustering (Weeks 5–6)

- [ ] **P1:** Support P2 with data pipelines for training/serving the anomaly models (batch + streaming inference paths)
- [ ] **P2:** Implement the Anomaly Engine — start with Isolation Forest baseline, then DAGMM / Transformer Autoencoder for metrics/logs/traces
- [ ] **P3:** Implement the AI Incident Clustering module (embedding similarity + temporal/topology clustering) to group alerts into Situations
- [ ] **P4:** Build the `alerts` and `incidents` write paths + basic API to fetch a Situation and its member alerts

**Milestone:** Raw alerts get automatically clustered into a single "Situation" record in the database.

---

## Phase 4 — Root Cause Graph Engine (Weeks 6–7)

- [ ] **P1:** Build/maintain the live service-dependency graph data structure (nodes = services/pods/DBs, edges = calls/dependencies)
- [ ] **P2:** Implement the GNN (PyTorch Geometric) for anomaly-score propagation and causal ranking of root-cause nodes
- [ ] **P3:** Validate RCA output against labeled root-cause data (Microsoft Services Dataset) and tune confidence scoring
- [ ] **P4:** Store root-cause results (root_cause_service, root_cause_confidence) back into the `incidents` table via API

**Milestone:** Given a Situation, the system returns a ranked root-cause node with a confidence score.

---

## Phase 5 — LLM Explainer & Predictive Scoring (Weeks 7–8)

- [ ] **P1:** Prepare historical incident + telemetry snapshots as retrievable context (chunking, embedding pipeline)
- [ ] **P2:** Implement Predictive Failure Scoring (trend/slope-based risk model per service)
- [ ] **P3:** Build the LLM Explainer using LangChain + RAG — retrieve grounded context (causal graph output, runbooks, telemetry) and generate the plain-English narrative
- [ ] **P4:** Store LLM narrative + embedding (narrative_summary, narrative_embedding) and expose it via API

**Milestone:** Every Situation has an auto-generated, grounded, plain-English explanation.

---

## Phase 6 — Safety & Remediation Layer (Weeks 8–9)

- [ ] **P1:** Provide historical action-success data to feed policy trust weights
- [ ] **P2:** Support root-cause → remediation-type mapping (which failure patterns map to which action types)
- [ ] **P3:** Implement the OPA Policy Engine (Rego policies) for blast-radius, service-tier, and risk-based gating; implement the Remediation Executor (Kubernetes API calls: rollback/restart/scale/circuit-break)
- [ ] **P4:** Build API + UI hooks for "Approve & Execute" / "Deny" actions, and log outcomes back to `remediation_playbooks`

**Milestone:** A proposed remediation action can be safely approved (or auto-executed if low-risk) and applied.

---

## Phase 7 — Frontend: Mission Control Dashboard (Weeks 9–11, can run in parallel with Phases 3–6)

- [ ] **P4 (lead):** Build the 7 pages in React + Tailwind — Login, Mission Control Dashboard, Situation Room, Alert Clustering View, Root Cause Graph Explorer, Remediation Playbooks, Settings & Policies
- [ ] **P1:** Wire up the dashboard's live data feeds (deployment metadata, active situation count)
- [ ] **P2:** Build the interactive Root Cause Graph Explorer visualization (graph canvas, anomaly heat overlay)
- [ ] **P3:** Build the Situation Room's "Explain" and "Approve/Deny" interactive components tied to the LLM/Policy APIs

**Milestone:** Full clickable dashboard demonstrating the Sarah/checkout-service example scenario end-to-end.

---

## Phase 8 — Postmortem Learning Loop & Feedback (Week 11)

- [ ] **P1:** Pipe resolved-incident outcomes back into the historical dataset store
- [ ] **P2:** Use feedback (thumbs up/down on Situations) as a retraining signal for the anomaly/clustering models
- [ ] **P3:** Auto-generate the structured incident timeline (detection → clustering → RCA → approval → remediation → recovery) that seeds postmortems
- [ ] **P4:** Build the postmortem view/export in the dashboard

**Milestone:** Every resolved Situation automatically produces a postmortem-ready timeline.

---

## Phase 9 — Evaluation Against Target Metrics (Week 12)

- [ ] **P1:** Set up the evaluation harness/test-scenario injector (synthetic alert storms, injected root causes)
- [ ] **P2:** Measure Anomaly Detection F1-Score (≥0.90) and AUC-ROC (≥0.95); measure Root Cause Top-1 Accuracy (≥85%)
- [ ] **P3:** Measure False Remediation Rate (<5%) and validate Safety Guardrail behavior under edge cases
- [ ] **P4:** Measure Incident Clustering Compression Ratio (>90%) and estimated MTTR Reduction (40–50%); compile results into charts/tables

**Milestone:** A results report showing performance against every Section 8 target metric from the Client Brief.

---

## Phase 10 — Documentation, Report & PPO Pitch (Week 13)

- [ ] **P1:** Write up the Data/Ingestion sections of the final report (datasets, Kafka/Flink pipeline)
- [ ] **P2:** Write up the ML/RCA sections (anomaly detection, GNN, evaluation results)
- [ ] **P3:** Write up the LLM/Safety sections (RAG explainer, OPA policy, risk mitigation) and draft the IEEE-style research-gap angle
- [ ] **P4:** Assemble the final report/slide deck, record the demo walkthrough, and prepare the recruiter pitch (lead with quantified MTTR/alert-reduction impact per the Client Brief)
- [ ] **All:** Rehearse the pitch together — each person should be able to explain any layer if asked

**Milestone:** Final report, demo video, and pitch deck ready for submission/PPO interviews.

---

## Notes on Working Together

- Use short weekly syncs (even 20 minutes) to unblock cross-layer dependencies (e.g., P4's API contracts affect everyone).
- Agree on API/data contracts *before* building each phase (see "Inter-Layer Interaction Summary" in the blueprint) so people don't build against assumptions.
- Keep a shared `CHANGELOG.md` or use PR descriptions so no one duplicates work.
- If a task blocks another person, flag it immediately rather than waiting for the next sync.
