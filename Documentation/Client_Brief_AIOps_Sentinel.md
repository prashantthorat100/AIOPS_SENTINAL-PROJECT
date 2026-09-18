# Client Brief — AIOps Sentinel: Self-Healing Cloud Platform

**Prepared for:** Engineering Capstone Team (4-member group)
**Prepared by:** Client Requirements Desk (simulated client brief)
**Date:** September 2026
**Project Type:** B2B Observability Intelligence Platform — AI/ML + MLOps Capstone

---

## 1. Client Background

Our organization is a mid-size SaaS company running production workloads on Kubernetes across
dozens of microservices. Over the last year, our Site Reliability Engineering (SRE) team has been
overwhelmed by alert fatigue, slow root-cause diagnosis, and inconsistent incident response. We are
commissioning a capstone engineering team to design and build a working prototype of an AI-driven
"self-healing cloud" platform — internally referred to as **AIOps Sentinel** — that can detect, explain,
and (within safe limits) automatically remediate infrastructure incidents.

We are not asking you to replace our existing monitoring stack (Prometheus, Grafana, Datadog). We want
a layer that sits **above** these tools, ingests their telemetry, and closes the loop from raw signal to
resolved incident.

## 2. Business Problem

- Engineers are paged **after** customers notice outages, not before.
- A single root cause can trigger hundreds of disconnected alerts across dependent services (alert storms).
- Root-cause diagnosis currently takes 30–60 minutes of manual dashboard correlation.
- Remediation requires a human to log in and manually run commands — slow and error-prone.
- Postmortems are written manually, days after the incident, from memory and scattered logs.

## 3. Project Objectives

1. Reduce Mean Time to Resolution (MTTR) by **40–50%** versus the current manual baseline.
2. Compress alert-storm volume by **>90%** through intelligent clustering.
3. Automatically identify the true root-cause service with **≥85% top-1 accuracy**.
4. Produce human-readable, plain-English incident explanations (replacing ~45 minutes of dashboard
   review with a 10-second read).
5. Enable safe, policy-gated automated remediation with a **false remediation rate below 5%**.

## 4. Scope of Work

### In Scope
- Ingestion pipeline for metrics, logs, traces, and Kubernetes events.
- Multi-modal anomaly detection (metrics + logs + traces).
- Graph-based root-cause analysis using a live service-dependency graph.
- LLM-powered natural-language incident explanations grounded via RAG.
- Policy-gated (OPA-based) safe remediation execution.
- A 7-page web dashboard ("Mission Control") for SREs and engineering managers.
- A PostgreSQL/Supabase backend with vector search support for RAG.
- Evaluation against target metrics using public AIOps benchmark datasets.

### Out of Scope
- Building a new metrics/logging/tracing collection agent (we already use Prometheus/Loki/Jaeger).
- Full multi-tenant SaaS billing or customer onboarding flows.
- Mobile app version of the dashboard.
- Training foundation-scale LLMs from scratch (use existing LLM APIs via RAG/prompting).

## 5. Target Users / Personas

| Persona | Core Need |
|---|---|
| Site Reliability Engineer (SRE) | One clear "situation" instead of hundreds of alerts |
| DevOps Engineer | Instant signal on whether a new deployment caused a regression |
| Platform Team | Cross-team visibility into hidden dependency failures |
| Incident Response / NOC Team | A single Situation Room instead of ten dashboards |
| Engineering Manager / VP Eng | Auto-generated incident timelines for postmortems and SLA reporting |

## 6. Required System Capabilities (Functional Requirements)

1. **Telemetry Ingestion** — Consume metrics, logs, traces, and K8s events via Kafka + Flink.
2. **AI Incident Clustering** — Group correlated alerts into one Situation using embedding + topology similarity.
3. **Root-Cause Graph Engine** — GNN-based causal ranking over a live service-dependency graph.
4. **LLM Situation Room** — RAG-grounded natural-language explanation of what broke, why, and the fix.
5. **Predictive Failure Scoring** — Leading-indicator risk scores per service (proactive maintenance).
6. **Policy-Gated Remediation** — OPA-based safety layer evaluating blast radius, service tier, and risk before auto-executing or requesting human approval.
7. **Postmortem Learning Loop** — Every resolved incident feeds back into training/tuning data.

## 7. Technical Constraints & Preferences

- **Frontend:** React + Tailwind CSS (dark "Mission Control" design system).
- **Backend:** FastAPI (ML-serving) + Node.js (real-time events).
- **ML Stack:** PyTorch Geometric (GNN), Scikit-learn (baseline anomaly detection), LangChain (RAG).
- **Streaming:** Apache Kafka + Apache Flink.
- **Database:** Supabase (PostgreSQL + pgvector) — chosen over Firebase for relational graph queries and native vector search.
- **Orchestration/Deployment target:** Kubernetes.
- **Safety:** Open Policy Agent (OPA) for all remediation gating — no action bypasses policy evaluation.

## 8. Success Metrics (Acceptance Criteria)

| Metric | Target |
|---|---|
| Anomaly Detection F1-Score | ≥ 0.90 |
| Anomaly Detection AUC-ROC | ≥ 0.95 |
| MTTR Reduction | 40–50% vs. manual baseline |
| False Remediation Rate | < 5% |
| Incident Clustering Compression Ratio | > 90% alert volume reduction |
| Root Cause Top-1 Accuracy | ≥ 85% |

## 9. Key Risks the Client Wants Addressed

- Bad automation making an outage worse (mitigated by confidence thresholds + mandatory human approval on tier-0 services).
- Over-trusting full autonomy too early (mitigated by a "shadow mode" launch phase — recommend only, never execute — before graduating to auto-execution).
- LLM hallucination in incident narratives (mitigated by grounding every explanation in retrieved structured evidence, never free-generation).
- Alert-fatigue from false positives (mitigated by continuous threshold tuning and engineer feedback loops).
- Multi-tenant data isolation (row-level security in Supabase, isolated Kafka topics per namespace).

## 10. Deliverables Expected from the Team

1. Working end-to-end prototype covering all four architecture layers (Telemetry → Ingestion → Intelligence → Action).
2. A populated database schema with sample incidents, alerts, and remediation playbooks.
3. A functioning 7-page dashboard demonstrating the full incident lifecycle (as in the example scenario).
4. An evaluation report showing performance against the Section 8 metrics on the chosen benchmark datasets.
5. Documentation suitable for an IEEE-style paper submission (see Research Gap in the technical blueprint).
6. A final presentation/pitch suitable for recruiters, framed around real-world MTTR and alert-reduction impact.

## 11. Timeline Expectation

The client expects the capstone team to work in clearly defined phases (see accompanying `todos.md`),
with regular checkpoints, so that all four contributors can work in parallel without blocking each other.

---
*This brief translates the AIOps Sentinel Technical Blueprint into a client-facing requirements document, for use as the reference point when planning and dividing work.*
