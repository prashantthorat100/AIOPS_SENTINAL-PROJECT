"""
Prometheus-compatible Time-Series Metrics Simulator for AIOps Sentinel.
Generates realistic container and application metrics across the microservice topology.
"""
import random
from typing import List, Dict, Optional
from datetime import datetime, timezone

from .config import SERVICE_TOPOLOGY, ServiceSpec
from .models import MetricPoint


class MetricsSimulator:
    def __init__(self, topology: Optional[Dict[str, ServiceSpec]] = None):
        self.topology = topology or SERVICE_TOPOLOGY
        # Dynamic state per service to track gradual changes (like memory leaks)
        self.state: Dict[str, Dict[str, float]] = {}
        self.reset_state()

    def reset_state(self):
        """Reset service dynamic metrics state to normal baselines."""
        for name, spec in self.topology.items():
            self.state[name] = {
                "memory_mb": spec.base_memory_mb,
                "cpu_percent": spec.base_cpu_percent,
                "p99_latency_ms": spec.base_p99_latency_ms,
                "p50_latency_ms": max(2.0, spec.base_p99_latency_ms * 0.35),
                "qps": spec.base_qps,
                "error_rate": spec.error_rate_baseline,
                "is_leaking": 0.0,  # growth rate in MB per tick
            }

    def apply_memory_leak(self, service_name: str, growth_mb_per_tick: float = 12.0):
        """Inject a progressive memory leak into a specific service."""
        if service_name in self.state:
            self.state[service_name]["is_leaking"] = growth_mb_per_tick

    def apply_cascading_latency(self, service_names: List[str], multiplier: float = 8.0):
        """Simulate cascading latency across dependent services."""
        for name in service_names:
            if name in self.state:
                spec = self.topology[name]
                self.state[name]["p99_latency_ms"] = spec.base_p99_latency_ms * multiplier
                self.state[name]["error_rate"] = min(0.65, spec.error_rate_baseline + 0.35)

    def generate_tick(self, timestamp: Optional[str] = None) -> List[MetricPoint]:
        """Generate one snapshot of metrics across all services in the topology."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        metrics: List[MetricPoint] = []

        for name, spec in self.topology.items():
            st = self.state[name]
            pod_id = f"{spec.pod_prefix}-{random.randint(100, 999)}"

            # 1. Memory Calculation
            if st["is_leaking"] > 0:
                st["memory_mb"] = min(spec.memory_limit_mb * 1.15, st["memory_mb"] + st["is_leaking"])
                # As memory approaches limit, GC thrashing causes latency and CPU increase
                memory_ratio = st["memory_mb"] / spec.memory_limit_mb
                if memory_ratio > 0.85:
                    st["p99_latency_ms"] = spec.base_p99_latency_ms * (1.0 + (memory_ratio - 0.85) * 35.0)
                    st["cpu_percent"] = min(98.0, spec.base_cpu_percent * 2.8)
                    st["error_rate"] = min(0.80, 0.05 + (memory_ratio - 0.85) * 2.5)
            else:
                # Normal minor jitter
                noise = random.uniform(-2.0, 2.0)
                st["memory_mb"] = max(50.0, min(spec.memory_limit_mb * 0.75, st["memory_mb"] + noise))

            # 2. CPU Calculation
            cpu_jitter = random.uniform(-2.5, 2.5)
            curr_cpu = max(1.0, min(99.0, st["cpu_percent"] + cpu_jitter))

            # 3. Latency Calculation
            lat_jitter = random.uniform(-1.5, 2.0)
            curr_p99 = max(3.0, st["p99_latency_ms"] + lat_jitter)
            curr_p50 = max(1.5, curr_p99 * 0.35)

            # 4. QPS Calculation
            qps_jitter = random.uniform(-5.0, 5.0)
            curr_qps = max(5.0, st["qps"] + qps_jitter)

            # 5. Error Rate
            curr_error_rate = max(0.0, min(1.0, st["error_rate"] + random.uniform(-0.0005, 0.0005)))

            labels = {
                "service": name,
                "tier": spec.tier,
                "namespace": spec.namespace,
            }

            # Emit MetricPoints
            metrics.append(
                MetricPoint(
                    timestamp=timestamp,
                    metric_name="container_memory_working_set_bytes",
                    service_name=name,
                    pod_id=pod_id,
                    metric_value=round(st["memory_mb"] * 1024 * 1024, 2),
                    unit="bytes",
                    labels=labels,
                )
            )
            metrics.append(
                MetricPoint(
                    timestamp=timestamp,
                    metric_name="container_cpu_usage_percent",
                    service_name=name,
                    pod_id=pod_id,
                    metric_value=round(curr_cpu, 2),
                    unit="percent",
                    labels=labels,
                )
            )
            metrics.append(
                MetricPoint(
                    timestamp=timestamp,
                    metric_name="http_request_duration_seconds_p99",
                    service_name=name,
                    pod_id=pod_id,
                    metric_value=round(curr_p99 / 1000.0, 4),
                    unit="seconds",
                    labels=labels,
                )
            )
            metrics.append(
                MetricPoint(
                    timestamp=timestamp,
                    metric_name="http_request_duration_seconds_p50",
                    service_name=name,
                    pod_id=pod_id,
                    metric_value=round(curr_p50 / 1000.0, 4),
                    unit="seconds",
                    labels=labels,
                )
            )
            metrics.append(
                MetricPoint(
                    timestamp=timestamp,
                    metric_name="http_requests_total_rate",
                    service_name=name,
                    pod_id=pod_id,
                    metric_value=round(curr_qps, 1),
                    unit="qps",
                    labels=labels,
                )
            )
            metrics.append(
                MetricPoint(
                    timestamp=timestamp,
                    metric_name="http_requests_error_ratio",
                    service_name=name,
                    pod_id=pod_id,
                    metric_value=round(curr_error_rate, 4),
                    unit="ratio",
                    labels=labels,
                )
            )

        return metrics
