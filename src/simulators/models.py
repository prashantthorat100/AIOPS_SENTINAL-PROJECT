"""
Data models for synthetic telemetry records in AIOps Sentinel.
Compatible with Prometheus, Loki, OpenTelemetry/Jaeger, and Kubernetes Event APIs.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetricPoint(BaseModel):
    """Prometheus-compatible time-series metric data point."""
    timestamp: str = Field(default_factory=utc_now_iso)
    metric_name: str
    service_name: str
    pod_id: str
    node_id: str = "node-worker-01"
    metric_value: float
    unit: str = "gauge"
    labels: Dict[str, str] = Field(default_factory=dict)

    def to_kafka_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class LogEntry(BaseModel):
    """Loki/Fluentd compatible structured log entry."""
    timestamp: str = Field(default_factory=utc_now_iso)
    level: str = "INFO"  # DEBUG, INFO, WARN, ERROR, FATAL
    service_name: str
    pod_id: str
    message: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    logger: str = "app.root"
    thread: str = "main-thread"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_kafka_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class TraceSpan(BaseModel):
    """OpenTelemetry / Jaeger distributed trace span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str
    operation_name: str
    start_time_iso: str = Field(default_factory=utc_now_iso)
    duration_ms: float
    status_code: str = "OK"  # OK, ERROR
    http_status: int = 200
    attributes: Dict[str, Any] = Field(default_factory=dict)

    def to_kafka_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class K8sInvolvedObject(BaseModel):
    kind: str = "Pod"
    name: str
    namespace: str = "production"
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class K8sEvent(BaseModel):
    """Kubernetes API Server Event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=utc_now_iso)
    type: str = "Normal"  # Normal, Warning
    reason: str  # Scheduled, Pulled, BackOff, OOMKilled, Unhealthy
    involved_object: K8sInvolvedObject
    message: str
    count: int = 1
    component: str = "kubelet"
    host: str = "node-worker-01"

    def to_kafka_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class DeploymentEvent(BaseModel):
    """CI/CD Deployment Webhook Event."""
    deployment_id: str = Field(default_factory=lambda: f"dep-{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=utc_now_iso)
    service_name: str
    version: str
    git_commit: str
    author: str
    status: str = "success"
    environment: str = "production"

    def to_kafka_dict(self) -> Dict[str, Any]:
        return self.model_dump()
