# Telemetry Ingestion Simulators (Phase 1 — P1)

This module provides high-fidelity synthetic telemetry generators for **AIOps Sentinel**, producing realistic multi-modal data streams across a 15-microservice Kubernetes mesh before real cluster telemetry is attached.

## Architecture & Topic Mapping

The output schemas align directly with the Phase 2 Kafka ingestion pipeline:

| Telemetry Modality | Generator Class | Emitted Format | Target Kafka Topic |
|---|---|---|---|
| **Metrics** | `MetricsSimulator` | Prometheus Exporter Time-Series | `metrics.raw` |
| **Logs** | `LogsSimulator` | Loki / Fluentd Structured JSON | `logs.raw` |
| **Traces** | `TracesSimulator` | OpenTelemetry / Jaeger Spans | `traces.raw` |
| **K8s Events** | `K8sEventsSimulator` | Kubernetes API Server Events | `events.k8s` |
| **Deployments** | `K8sEventsSimulator` | CI/CD Webhook JSON | `events.deployments` |

---

## Simulated Scenarios

### 1. `checkout_leak` (The Flagship Incident Scenario)
Faithfully implements the Sarah / `checkout-service` memory leak scenario described in Section 5 of the *AIOps Sentinel Technical Blueprint*:
1. **Normal Baseline**: Healthy steady-state metrics and distributed traces.
2. **Deployment Webhook**: CI/CD logs a deployment of `checkout-service:v2.115` by `sarah.dev`.
3. **Progressive Memory Leak**: Old gen heap climbs linearly while request traffic remains flat (differentiating a leak from a traffic spike).
4. **Cascading Latency**: Severe GC pauses in `checkout-service` cause p99 latency to spike to >1200ms and cascade into upstream callers (`api-gateway`, `frontend-service`, `cart-service`).
5. **OOMKill & Alert Storm**: Pod exceeds 512Mi memory limit, Linux kernel issues OOMKill, Kubernetes fires `Unhealthy`, `OOMKilled`, and `BackOff` events, and log streams burst with `java.lang.OutOfMemoryError` and HTTP 504 Gateway Timeouts.

### 2. `steady_state`
Generates continuous healthy telemetry across all 15 services with realistic Gaussian noise and diurnal fluctuation.

---

## Quickstart

### Run the Incident Scenario:
```bash
python run_simulator.py --scenario checkout_leak --output-dir data/simulated
```

### Run Steady State Telemetry:
```bash
python run_simulator.py --scenario steady_state --ticks 10 --output-dir data/simulated
```

### Run Automated Tests:
```bash
python -m pytest tests/ -v
```

---

## Data Schema Reference

- **Metrics**: `timestamp`, `service_name`, `pod_id`, `metric_name`, `metric_value`, `unit`, `labels` (tier, namespace).
- **Logs**: `timestamp`, `level` (INFO, WARN, ERROR, FATAL), `service_name`, `pod_id`, `trace_id`, `span_id`, `message`, `logger`, `metadata`.
- **Traces**: `trace_id`, `span_id`, `parent_span_id`, `service_name`, `operation_name`, `duration_ms`, `status_code` (OK, ERROR), `http_status`, `attributes`.
- **K8s Events**: `event_id`, `timestamp`, `type` (Normal, Warning), `reason` (Started, Unhealthy, OOMKilled, BackOff), `involved_object`, `message`, `component`.
