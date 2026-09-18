"""
Scenario Runner & Pipeline Orchestrator for AIOps Sentinel.
Executes end-to-end incident scenarios and outputs synchronized multi-modal telemetry.
"""
from typing import Dict, List, Any, Generator, Optional
import time
from datetime import datetime, timezone, timedelta
import json
import os

from .config import SERVICE_TOPOLOGY, KAFKA_TOPICS
from .models import MetricPoint, LogEntry, TraceSpan, K8sEvent, DeploymentEvent
from .metrics_simulator import MetricsSimulator
from .logs_simulator import LogsSimulator
from .traces_simulator import TracesSimulator
from .k8s_events_simulator import K8sEventsSimulator


class TelemetryBatch:
    """A synchronized multi-modal slice of telemetry generated at a point in time."""
    def __init__(
        self,
        timestamp: str,
        phase_name: str,
        metrics: List[MetricPoint],
        logs: List[LogEntry],
        traces: List[TraceSpan],
        k8s_events: List[K8sEvent],
        deployment_events: Optional[List[DeploymentEvent]] = None,
    ):
        self.timestamp = timestamp
        self.phase_name = phase_name
        self.metrics = metrics
        self.logs = logs
        self.traces = traces
        self.k8s_events = k8s_events
        self.deployment_events = deployment_events or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "phase_name": self.phase_name,
            "metrics_count": len(self.metrics),
            "logs_count": len(self.logs),
            "traces_count": len(self.traces),
            "k8s_events_count": len(self.k8s_events),
            "deployment_events_count": len(self.deployment_events),
            KAFKA_TOPICS["metrics"]: [m.model_dump() for m in self.metrics],
            KAFKA_TOPICS["logs"]: [l.model_dump() for l in self.logs],
            KAFKA_TOPICS["traces"]: [t.model_dump() for t in self.traces],
            KAFKA_TOPICS["k8s_events"]: [e.model_dump() for e in self.k8s_events],
            KAFKA_TOPICS["deployments"]: [d.model_dump() for d in self.deployment_events],
        }


class ScenarioRunner:
    def __init__(self):
        self.metrics_sim = MetricsSimulator(SERVICE_TOPOLOGY)
        self.logs_sim = LogsSimulator(SERVICE_TOPOLOGY)
        self.traces_sim = TracesSimulator()
        self.k8s_sim = K8sEventsSimulator()

    def run_steady_state(self, num_ticks: int = 5, tick_interval_sec: float = 1.0) -> List[TelemetryBatch]:
        """Runs normal steady-state telemetry generation."""
        self.metrics_sim.reset_state()
        batches: List[TelemetryBatch] = []
        base_time = datetime.now(timezone.utc)

        for i in range(num_ticks):
            ts = (base_time + timedelta(seconds=i * 10)).isoformat()
            metrics = self.metrics_sim.generate_tick(timestamp=ts)
            logs = self.logs_sim.generate_normal_logs(count_per_service=1, timestamp=ts)
            traces = self.traces_sim.generate_checkout_trace(is_degraded=False, is_oom=False, timestamp=ts)
            k8s_events = [
                self.k8s_sim.generate_pod_healthy_event("checkout-service", "checkout-service-7f9c-554", timestamp=ts)
            ]

            batches.append(
                TelemetryBatch(
                    timestamp=ts,
                    phase_name="steady_state",
                    metrics=metrics,
                    logs=logs,
                    traces=traces,
                    k8s_events=k8s_events,
                )
            )

        return batches

    def run_checkout_memory_leak_scenario(self) -> List[TelemetryBatch]:
        """
        Executes the flagship Sarah / checkout-service memory leak incident scenario
        from the AIOps Sentinel Technical Blueprint (Section 5).

        Lifecycle:
        1. Baseline Normal (00:00)
        2. Deployment Event (checkout-service v2.115 introduced)
        3. Progressive Memory Leak (memory climbing, requests flat)
        4. Memory Pressure & Cascading Latency (GC pauses, downstream p99 spike)
        5. OutOfMemoryKill & Error Storm (K8s OOMKill, 504 timeouts, 500 errors)
        """
        self.metrics_sim.reset_state()
        batches: List[TelemetryBatch] = []
        base_time = datetime.now(timezone.utc)
        tick_idx = 0

        def current_ts():
            nonlocal tick_idx
            ts = (base_time + timedelta(seconds=tick_idx * 30)).isoformat()
            tick_idx += 1
            return ts

        # --- Step 1: Baseline Normal ---
        ts1 = current_ts()
        batches.append(
            TelemetryBatch(
                timestamp=ts1,
                phase_name="1_normal_baseline",
                metrics=self.metrics_sim.generate_tick(timestamp=ts1),
                logs=self.logs_sim.generate_normal_logs(count_per_service=1, timestamp=ts1),
                traces=self.traces_sim.generate_checkout_trace(is_degraded=False, is_oom=False, timestamp=ts1),
                k8s_events=[self.k8s_sim.generate_pod_healthy_event("checkout-service", "checkout-service-7f9c-554", ts1)],
            )
        )

        # --- Step 2: Deployment Event ---
        ts2 = current_ts()
        deploy_ev = self.k8s_sim.generate_deployment_event(
            service_name="checkout-service",
            version="v2.115",
            author="sarah.dev",
            git_commit="7f9ca12",
            timestamp=ts2,
        )
        batches.append(
            TelemetryBatch(
                timestamp=ts2,
                phase_name="2_service_deployment",
                metrics=self.metrics_sim.generate_tick(timestamp=ts2),
                logs=self.logs_sim.generate_normal_logs(count_per_service=1, timestamp=ts2),
                traces=self.traces_sim.generate_checkout_trace(is_degraded=False, is_oom=False, timestamp=ts2),
                k8s_events=[self.k8s_sim.generate_pod_healthy_event("checkout-service", "checkout-service-7f9c-554", ts2)],
                deployment_events=[deploy_ev],
            )
        )

        # --- Step 3: Progressive Memory Leak Injected ---
        # Inject fast leak of 60MB per 30-sec tick
        self.metrics_sim.apply_memory_leak("checkout-service", growth_mb_per_tick=65.0)

        for leak_tick in range(3):
            ts_leak = current_ts()
            leak_logs = self.logs_sim.generate_normal_logs(count_per_service=1, timestamp=ts_leak)
            if leak_tick >= 1:
                leak_logs.extend(self.logs_sim.generate_memory_leak_logs("checkout-service", severity="warning", timestamp=ts_leak))

            batches.append(
                TelemetryBatch(
                    timestamp=ts_leak,
                    phase_name=f"3_memory_leak_growth_{leak_tick+1}",
                    metrics=self.metrics_sim.generate_tick(timestamp=ts_leak),
                    logs=leak_logs,
                    traces=self.traces_sim.generate_checkout_trace(is_degraded=False, is_oom=False, timestamp=ts_leak),
                    k8s_events=[],
                )
            )

        # --- Step 4: Memory Pressure & Cascading Latency ---
        # Cascading degradation to dependent services (api-gateway, frontend-service)
        self.metrics_sim.apply_cascading_latency(["api-gateway", "frontend-service", "cart-service"], multiplier=7.5)
        ts4 = current_ts()
        batches.append(
            TelemetryBatch(
                timestamp=ts4,
                phase_name="4_cascading_latency_pressure",
                metrics=self.metrics_sim.generate_tick(timestamp=ts4),
                logs=self.logs_sim.generate_memory_leak_logs("checkout-service", severity="warning", timestamp=ts4),
                traces=self.traces_sim.generate_checkout_trace(is_degraded=True, is_oom=False, timestamp=ts4),
                k8s_events=[],
            )
        )

        # --- Step 5: OOMKill & Error Storm ---
        ts5 = current_ts()
        oom_k8s = self.k8s_sim.generate_oom_incident_events("checkout-service", "checkout-service-7f9c-554", timestamp=ts5)
        oom_logs = self.logs_sim.generate_memory_leak_logs("checkout-service", severity="critical", timestamp=ts5)
        oom_traces = self.traces_sim.generate_checkout_trace(is_degraded=False, is_oom=True, timestamp=ts5)

        batches.append(
            TelemetryBatch(
                timestamp=ts5,
                phase_name="5_oomkill_and_alert_storm",
                metrics=self.metrics_sim.generate_tick(timestamp=ts5),
                logs=oom_logs,
                traces=oom_traces,
                k8s_events=oom_k8s,
            )
        )

        return batches

    def export_scenario_to_disk(self, batches: List[TelemetryBatch], output_dir: str = "data/simulated") -> Dict[str, int]:
        """
        Exports all telemetry streams into dedicated NDJSON files partitioned by Kafka topic.
        """
        os.makedirs(output_dir, exist_ok=True)
        counts = {"metrics": 0, "logs": 0, "traces": 0, "k8s_events": 0, "deployments": 0}

        metrics_file = os.path.join(output_dir, "metrics.ndjson")
        logs_file = os.path.join(output_dir, "logs.ndjson")
        traces_file = os.path.join(output_dir, "traces.ndjson")
        k8s_file = os.path.join(output_dir, "k8s_events.ndjson")
        deploy_file = os.path.join(output_dir, "deployments.ndjson")

        with open(metrics_file, "w") as fm, \
             open(logs_file, "w") as fl, \
             open(traces_file, "w") as ft, \
             open(k8s_file, "w") as fk, \
             open(deploy_file, "w") as fd:

            for batch in batches:
                for m in batch.metrics:
                    fm.write(json.dumps(m.model_dump()) + "\n")
                    counts["metrics"] += 1
                for l in batch.logs:
                    fl.write(json.dumps(l.model_dump()) + "\n")
                    counts["logs"] += 1
                for t in batch.traces:
                    ft.write(json.dumps(t.model_dump()) + "\n")
                    counts["traces"] += 1
                for k in batch.k8s_events:
                    fk.write(json.dumps(k.model_dump()) + "\n")
                    counts["k8s_events"] += 1
                for d in batch.deployment_events:
                    fd.write(json.dumps(d.model_dump()) + "\n")
                    counts["deployments"] += 1

        return counts
