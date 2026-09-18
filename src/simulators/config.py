"""
Configuration and Service Topology Definitions for AIOps Sentinel Telemetry Simulators.
"""
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ServiceSpec:
    name: str
    tier: str  # tier-0 (revenue-critical), tier-1 (core), tier-2 (supporting)
    namespace: str = "production"
    pod_prefix: str = ""
    port: int = 8080
    dependencies: List[str] = field(default_factory=list)
    base_cpu_percent: float = 15.0
    base_memory_mb: float = 256.0
    memory_limit_mb: float = 512.0
    base_p99_latency_ms: float = 25.0
    base_qps: float = 120.0
    error_rate_baseline: float = 0.001

    def __post_init__(self):
        if not self.pod_prefix:
            self.pod_prefix = f"{self.name}-pod"


# Service topology replicating a modern e-commerce microservices mesh on Kubernetes
SERVICE_TOPOLOGY: Dict[str, ServiceSpec] = {
    "api-gateway": ServiceSpec(
        name="api-gateway",
        tier="tier-0",
        pod_prefix="api-gateway-5c8f",
        port=80,
        dependencies=["auth-service", "frontend-service", "checkout-service", "catalog-service"],
        base_cpu_percent=25.0,
        base_memory_mb=320.0,
        memory_limit_mb=1024.0,
        base_p99_latency_ms=15.0,
        base_qps=850.0,
    ),
    "auth-service": ServiceSpec(
        name="auth-service",
        tier="tier-0",
        pod_prefix="auth-service-6b4d",
        dependencies=["database-postgres"],
        base_cpu_percent=18.0,
        base_memory_mb=210.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=12.0,
        base_qps=500.0,
    ),
    "frontend-service": ServiceSpec(
        name="frontend-service",
        tier="tier-1",
        pod_prefix="frontend-service-89da",
        dependencies=["cart-service", "catalog-service", "recommendation-service"],
        base_cpu_percent=20.0,
        base_memory_mb=280.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=30.0,
        base_qps=600.0,
    ),
    "checkout-service": ServiceSpec(
        name="checkout-service",
        tier="tier-0",
        pod_prefix="checkout-service-7f9c",
        dependencies=["cart-service", "payment-service", "order-service", "inventory-service", "discount-service"],
        base_cpu_percent=30.0,
        base_memory_mb=256.0,
        memory_limit_mb=512.0,  # Max memory before OOM
        base_p99_latency_ms=45.0,
        base_qps=220.0,
    ),
    "cart-service": ServiceSpec(
        name="cart-service",
        tier="tier-1",
        pod_prefix="cart-service-3e1b",
        dependencies=["database-postgres"],
        base_cpu_percent=15.0,
        base_memory_mb=180.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=18.0,
        base_qps=310.0,
    ),
    "payment-service": ServiceSpec(
        name="payment-service",
        tier="tier-0",
        pod_prefix="payment-service-1c4a",
        dependencies=["database-postgres"],
        base_cpu_percent=22.0,
        base_memory_mb=240.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=55.0,
        base_qps=180.0,
    ),
    "order-service": ServiceSpec(
        name="order-service",
        tier="tier-1",
        pod_prefix="order-service-9a7f",
        dependencies=["inventory-service", "shipping-service", "notification-service", "database-postgres"],
        base_cpu_percent=20.0,
        base_memory_mb=220.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=40.0,
        base_qps=190.0,
    ),
    "inventory-service": ServiceSpec(
        name="inventory-service",
        tier="tier-1",
        pod_prefix="inventory-service-4d8e",
        dependencies=["database-postgres"],
        base_cpu_percent=14.0,
        base_memory_mb=190.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=22.0,
        base_qps=280.0,
    ),
    "catalog-service": ServiceSpec(
        name="catalog-service",
        tier="tier-1",
        pod_prefix="catalog-service-52fd",
        dependencies=["database-postgres"],
        base_cpu_percent=16.0,
        base_memory_mb=210.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=20.0,
        base_qps=450.0,
    ),
    "recommendation-service": ServiceSpec(
        name="recommendation-service",
        tier="tier-2",
        pod_prefix="recommendation-service-77fa",
        dependencies=["catalog-service"],
        base_cpu_percent=35.0,
        base_memory_mb=380.0,
        memory_limit_mb=1024.0,
        base_p99_latency_ms=65.0,
        base_qps=150.0,
    ),
    "shipping-service": ServiceSpec(
        name="shipping-service",
        tier="tier-2",
        pod_prefix="shipping-service-2a8b",
        dependencies=[],
        base_cpu_percent=10.0,
        base_memory_mb=160.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=28.0,
        base_qps=90.0,
    ),
    "notification-service": ServiceSpec(
        name="notification-service",
        tier="tier-2",
        pod_prefix="notification-service-66dc",
        dependencies=[],
        base_cpu_percent=12.0,
        base_memory_mb=170.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=35.0,
        base_qps=120.0,
    ),
    "discount-service": ServiceSpec(
        name="discount-service",
        tier="tier-2",
        pod_prefix="discount-service-33ef",
        dependencies=[],
        base_cpu_percent=8.0,
        base_memory_mb=140.0,
        memory_limit_mb=256.0,
        base_p99_latency_ms=10.0,
        base_qps=200.0,
    ),
    "review-service": ServiceSpec(
        name="review-service",
        tier="tier-2",
        pod_prefix="review-service-81cc",
        dependencies=["database-postgres"],
        base_cpu_percent=11.0,
        base_memory_mb=160.0,
        memory_limit_mb=512.0,
        base_p99_latency_ms=25.0,
        base_qps=110.0,
    ),
    "database-postgres": ServiceSpec(
        name="database-postgres",
        tier="tier-0",
        pod_prefix="postgres-statefulset-0",
        port=5432,
        dependencies=[],
        base_cpu_percent=28.0,
        base_memory_mb=580.0,
        memory_limit_mb=2048.0,
        base_p99_latency_ms=8.0,
        base_qps=1200.0,
    ),
}

# Kafka topic mapping for Phase 2 readiness
KAFKA_TOPICS = {
    "metrics": "metrics.raw",
    "logs": "logs.raw",
    "traces": "traces.raw",
    "k8s_events": "events.k8s",
    "deployments": "events.deployments",
}
