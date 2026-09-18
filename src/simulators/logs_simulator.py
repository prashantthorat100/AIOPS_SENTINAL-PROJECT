"""
Loki/Fluentd-compatible Structured Logs Simulator for AIOps Sentinel.
Emits standard microservice operational logs and incident error logs.
"""
import random
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timezone

from .config import SERVICE_TOPOLOGY, ServiceSpec
from .models import LogEntry


class LogsSimulator:
    def __init__(self, topology: Optional[Dict[str, ServiceSpec]] = None):
        self.topology = topology or SERVICE_TOPOLOGY

    def generate_normal_logs(self, count_per_service: int = 1, timestamp: Optional[str] = None) -> List[LogEntry]:
        """Generate typical operational logs across services."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        logs: List[LogEntry] = []
        normal_templates = {
            "api-gateway": [
                ("INFO", "Route match: {path} -> {service}:{port} in {lat}ms", {"path": "/api/v1/checkout", "lat": 4}),
                ("INFO", "Inbound request from {ip} status=200 size={bytes}B", {"ip": "192.168.1.42", "bytes": 1420}),
            ],
            "auth-service": [
                ("INFO", "JWT token validated for user_id={uid} in 2ms", {"uid": "usr_99182"}),
                ("DEBUG", "Session refreshed in cache ttl=3600s", {}),
            ],
            "checkout-service": [
                ("INFO", "Checkout initiated for cart_id={cid} total=${amt}", {"cid": "cart_821", "amt": 89.99}),
                ("INFO", "Order validation passed for customer={uid}", {"uid": "usr_99182"}),
            ],
            "payment-service": [
                ("INFO", "Payment intent pi_{pid} authorized with gateway 'stripe' amount=${amt}", {"pid": "8482", "amt": 89.99}),
            ],
            "order-service": [
                ("INFO", "Order ord_{oid} transitioned state to 'COMPLETED'", {"oid": "3910"}),
            ],
            "inventory-service": [
                ("INFO", "Inventory reservation confirmed for sku={sku} qty=1", {"sku": "SKU-PRO-42"}),
            ],
            "cart-service": [
                ("INFO", "Cart session retrieved cid={cid}", {"cid": "cart_821"}),
            ],
            "database-postgres": [
                ("INFO", "checkpoint complete: wrote 42 buffers (0.1%); 0 WAL file(s) added", {}),
            ],
        }

        for service_name, spec in self.topology.items():
            templates = normal_templates.get(service_name, [
                ("INFO", f"Heartbeat check healthy for {service_name} uptime=14201s", {})
            ])

            for _ in range(count_per_service):
                level, msg_tmpl, meta = random.choice(templates)
                trace_id = uuid.uuid4().hex
                span_id = uuid.uuid4().hex[:16]

                logs.append(
                    LogEntry(
                        timestamp=timestamp,
                        level=level,
                        service_name=service_name,
                        pod_id=f"{spec.pod_prefix}-{random.randint(100, 999)}",
                        message=msg_tmpl,
                        trace_id=trace_id,
                        span_id=span_id,
                        logger=f"com.sentinel.{service_name.replace('-', '.')}",
                        metadata=meta,
                    )
                )

        return logs

    def generate_memory_leak_logs(self, service_name: str = "checkout-service", severity: str = "warning", timestamp: Optional[str] = None) -> List[LogEntry]:
        """Generate error/fatal log storm when memory leak escalates or triggers OOM."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        spec = self.topology.get(service_name, ServiceSpec(name=service_name, tier="tier-0"))
        pod_id = f"{spec.pod_prefix}-7f9c"
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]

        logs: List[LogEntry] = []

        if severity == "warning":
            logs.append(
                LogEntry(
                    timestamp=timestamp,
                    level="WARN",
                    service_name=service_name,
                    pod_id=pod_id,
                    message="[GCWatcher] High memory occupancy: JVM old gen heap at 88.4% capacity (452MB / 512MB)",
                    trace_id=trace_id,
                    span_id=span_id,
                    logger="com.sentinel.runtime.GCWatcher",
                    metadata={"heap_used_mb": 452, "heap_max_mb": 512},
                )
            )
            logs.append(
                LogEntry(
                    timestamp=timestamp,
                    level="WARN",
                    service_name=service_name,
                    pod_id=pod_id,
                    message="[CartBuffer] Buffer backlog growing faster than drain rate; queued items: 12,490",
                    trace_id=trace_id,
                    span_id=span_id,
                    logger="com.sentinel.checkout.CartBuffer",
                    metadata={"queue_depth": 12490},
                )
            )
        elif severity == "critical":
            # OutOfMemory burst
            logs.append(
                LogEntry(
                    timestamp=timestamp,
                    level="ERROR",
                    service_name=service_name,
                    pod_id=pod_id,
                    message="java.lang.OutOfMemoryError: Java heap space at com.sentinel.checkout.service.CartBuffer.accumulate(CartBuffer.java:142)",
                    trace_id=trace_id,
                    span_id=span_id,
                    logger="com.sentinel.checkout.CartBuffer",
                    metadata={"exception_class": "java.lang.OutOfMemoryError", "stack_depth": 18},
                )
            )
            logs.append(
                LogEntry(
                    timestamp=timestamp,
                    level="FATAL",
                    service_name=service_name,
                    pod_id=pod_id,
                    message="[JVM CrashHandler] Unhandled OutOfMemoryError in worker thread 'epollEventLoopGroup-4-1'; container unhealthy",
                    trace_id=trace_id,
                    span_id=span_id,
                    logger="com.sentinel.runtime.CrashHandler",
                    metadata={"thread": "epollEventLoopGroup-4-1"},
                )
            )
            # Downstream caller timeouts
            for caller in ["api-gateway", "frontend-service", "cart-service"]:
                caller_spec = self.topology.get(caller, ServiceSpec(name=caller, tier="tier-1"))
                logs.append(
                    LogEntry(
                        timestamp=timestamp,
                        level="ERROR",
                        service_name=caller,
                        pod_id=f"{caller_spec.pod_prefix}-{random.randint(100, 999)}",
                        message=f"HTTP 504 Gateway Timeout connecting to http://{service_name}:8080/api/v1/checkout after 5000ms",
                        trace_id=trace_id,
                        span_id=uuid.uuid4().hex[:16],
                        logger=f"com.sentinel.{caller.replace('-', '.')}.HttpClient",
                        metadata={"target_service": service_name, "timeout_ms": 5000, "status": 504},
                    )
                )

        return logs
