"""
Unit tests for AIOps Sentinel Telemetry Simulators.
"""
import pytest
import os
import sys
import json
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulators.config import SERVICE_TOPOLOGY, KAFKA_TOPICS
from simulators.models import MetricPoint, LogEntry, TraceSpan, K8sEvent, DeploymentEvent
from simulators.metrics_simulator import MetricsSimulator
from simulators.logs_simulator import LogsSimulator
from simulators.traces_simulator import TracesSimulator
from simulators.k8s_events_simulator import K8sEventsSimulator
from simulators.scenario_runner import ScenarioRunner


class TestTopologyAndConfig:
    def test_topology_has_required_services(self):
        assert "checkout-service" in SERVICE_TOPOLOGY
        assert "api-gateway" in SERVICE_TOPOLOGY
        assert "database-postgres" in SERVICE_TOPOLOGY
        assert len(SERVICE_TOPOLOGY) >= 10

    def test_kafka_topic_mapping(self):
        assert KAFKA_TOPICS["metrics"] == "metrics.raw"
        assert KAFKA_TOPICS["logs"] == "logs.raw"
        assert KAFKA_TOPICS["traces"] == "traces.raw"
        assert KAFKA_TOPICS["k8s_events"] == "events.k8s"


class TestDataModels:
    def test_metric_point_serialization(self):
        mp = MetricPoint(
            metric_name="container_memory_working_set_bytes",
            service_name="checkout-service",
            pod_id="checkout-service-7f9c-101",
            metric_value=256000000.0,
            unit="bytes",
        )
        data = mp.to_kafka_dict()
        assert data["service_name"] == "checkout-service"
        assert data["metric_value"] == 256000000.0
        assert "timestamp" in data

    def test_log_entry_serialization(self):
        log = LogEntry(
            level="ERROR",
            service_name="checkout-service",
            pod_id="checkout-service-7f9c-101",
            message="java.lang.OutOfMemoryError: Java heap space",
        )
        data = log.to_kafka_dict()
        assert data["level"] == "ERROR"
        assert "OutOfMemoryError" in data["message"]

    def test_trace_span_serialization(self):
        span = TraceSpan(
            trace_id="abc123def456",
            span_id="span001",
            service_name="api-gateway",
            operation_name="POST /api/v1/checkout",
            duration_ms=45.2,
        )
        data = span.to_kafka_dict()
        assert data["service_name"] == "api-gateway"
        assert data["duration_ms"] == 45.2


class TestMetricsSimulator:
    def test_generate_tick_generates_all_services(self):
        sim = MetricsSimulator()
        metrics = sim.generate_tick()
        assert len(metrics) == len(SERVICE_TOPOLOGY) * 6  # 6 metrics per service
        services = {m.service_name for m in metrics}
        assert "checkout-service" in services
        assert "api-gateway" in services

    def test_memory_leak_growth(self):
        sim = MetricsSimulator()
        sim.apply_memory_leak("checkout-service", growth_mb_per_tick=50.0)

        initial_m = [m for m in sim.generate_tick() if m.service_name == "checkout-service" and m.metric_name == "container_memory_working_set_bytes"][0]
        subsequent_m = [m for m in sim.generate_tick() if m.service_name == "checkout-service" and m.metric_name == "container_memory_working_set_bytes"][0]

        assert subsequent_m.metric_value > initial_m.metric_value


class TestLogsSimulator:
    def test_normal_logs(self):
        sim = LogsSimulator()
        logs = sim.generate_normal_logs(count_per_service=1)
        assert len(logs) == len(SERVICE_TOPOLOGY)
        assert all(l.level in ["INFO", "DEBUG"] for l in logs)

    def test_memory_leak_critical_logs(self):
        sim = LogsSimulator()
        logs = sim.generate_memory_leak_logs("checkout-service", severity="critical")
        assert len(logs) >= 3
        error_msgs = [l.message for l in logs if l.level in ["ERROR", "FATAL"]]
        assert any("OutOfMemoryError" in m for m in error_msgs)
        assert any("504" in m for m in error_msgs)


class TestTracesSimulator:
    def test_healthy_checkout_trace(self):
        sim = TracesSimulator()
        spans = sim.generate_checkout_trace(is_degraded=False, is_oom=False)
        assert len(spans) == 7
        root = [s for s in spans if s.parent_span_id is None][0]
        assert root.service_name == "api-gateway"
        assert root.status_code == "OK"

    def test_oom_checkout_trace(self):
        sim = TracesSimulator()
        spans = sim.generate_checkout_trace(is_degraded=False, is_oom=True)
        root = [s for s in spans if s.parent_span_id is None][0]
        assert root.http_status == 504
        assert root.status_code == "ERROR"
        checkout = [s for s in spans if s.service_name == "checkout-service"][0]
        assert checkout.status_code == "ERROR"
        assert checkout.http_status == 500


class TestK8sEventsSimulator:
    def test_oom_incident_events(self):
        sim = K8sEventsSimulator()
        events = sim.generate_oom_incident_events("checkout-service", "checkout-service-7f9c-554")
        reasons = [e.reason for e in events]
        assert "Unhealthy" in reasons
        assert "OOMKilled" in reasons
        assert "BackOff" in reasons


class TestScenarioRunner:
    def test_run_checkout_scenario(self, tmp_path):
        runner = ScenarioRunner()
        batches = runner.run_checkout_memory_leak_scenario()
        assert len(batches) == 7  # 1 normal + 1 deploy + 3 leak + 1 cascade + 1 oom

        counts = runner.export_scenario_to_disk(batches, output_dir=str(tmp_path))
        assert counts["metrics"] > 0
        assert counts["logs"] > 0
        assert counts["traces"] > 0
        assert counts["k8s_events"] > 0
        assert counts["deployments"] == 1

        assert os.path.exists(tmp_path / "metrics.ndjson")
        assert os.path.exists(tmp_path / "logs.ndjson")
        assert os.path.exists(tmp_path / "traces.ndjson")
        assert os.path.exists(tmp_path / "k8s_events.ndjson")
        assert os.path.exists(tmp_path / "deployments.ndjson")
