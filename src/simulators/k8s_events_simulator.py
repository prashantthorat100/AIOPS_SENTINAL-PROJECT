"""
Kubernetes API Server & Deployment Events Simulator for AIOps Sentinel.
Simulates container lifecycle, health probe failures, OOMKills, and CI/CD deployment events.
"""
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from .models import K8sEvent, K8sInvolvedObject, DeploymentEvent


class K8sEventsSimulator:
    def __init__(self):
        pass

    def generate_pod_healthy_event(self, service_name: str, pod_name: str, timestamp: Optional[str] = None) -> K8sEvent:
        """Emits a standard healthy Kubernetes lifecycle event."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        return K8sEvent(
            timestamp=timestamp,
            type="Normal",
            reason="Started",
            involved_object=K8sInvolvedObject(name=pod_name, namespace="production"),
            message=f"Started container {service_name} in pod {pod_name}",
            count=1,
            component="kubelet",
        )

    def generate_oom_incident_events(self, service_name: str = "checkout-service", pod_name: str = "checkout-service-7f9c-554", timestamp: Optional[str] = None) -> List[K8sEvent]:
        """
        Emits the cascade of Kubernetes warning events when a pod breaches memory limits and is OOMKilled.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        events: List[K8sEvent] = []

        # 1. Liveness probe failure
        events.append(
            K8sEvent(
                timestamp=timestamp,
                type="Warning",
                reason="Unhealthy",
                involved_object=K8sInvolvedObject(name=pod_name, namespace="production"),
                message=f"Liveness probe failed: HTTP probe failed with statuscode: 500 on port 8080",
                count=3,
                component="kubelet",
            )
        )

        # 2. OOMKilled event from node kernel / cgroups
        events.append(
            K8sEvent(
                timestamp=timestamp,
                type="Warning",
                reason="OOMKilled",
                involved_object=K8sInvolvedObject(name=pod_name, namespace="production"),
                message=f"Container '{service_name}' exceeded memory limit of 512Mi (cgroup limit exceeded). Process killed by Linux OOM killer.",
                count=1,
                component="kernel/kubelet",
            )
        )

        # 3. CrashLoopBackOff event
        events.append(
            K8sEvent(
                timestamp=timestamp,
                type="Warning",
                reason="BackOff",
                involved_object=K8sInvolvedObject(name=pod_name, namespace="production"),
                message=f"Back-off 10s restarting failed container '{service_name}' in pod '{pod_name}'",
                count=1,
                component="kubelet",
            )
        )

        return events

    def generate_deployment_event(
        self,
        service_name: str = "checkout-service",
        version: str = "v2.115",
        author: str = "sarah.dev",
        git_commit: str = "7f9ca12",
        timestamp: Optional[str] = None,
    ) -> DeploymentEvent:
        """Simulates a CI/CD deployment webhook event."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        return DeploymentEvent(
            timestamp=timestamp,
            service_name=service_name,
            version=version,
            git_commit=git_commit,
            author=author,
            status="success",
            environment="production",
        )
