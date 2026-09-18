"""
OpenTelemetry / Jaeger-compatible Distributed Trace Simulator for AIOps Sentinel.
Simulates call graphs and propagation of trace context across microservices.
"""
import uuid
import random
from typing import List, Optional
from datetime import datetime, timezone

from .models import TraceSpan


class TracesSimulator:
    def __init__(self):
        pass

    def generate_checkout_trace(self, is_degraded: bool = False, is_oom: bool = False, timestamp: Optional[str] = None) -> List[TraceSpan]:
        """
        Simulate a distributed trace for a user checkout transaction.
        Call graph:
        api-gateway
          ├── auth-service
          └── checkout-service
                ├── cart-service
                ├── payment-service
                ├── inventory-service
                └── order-service
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        trace_id = uuid.uuid4().hex
        spans: List[TraceSpan] = []

        # 1. Root span: api-gateway
        root_span_id = uuid.uuid4().hex[:16]
        auth_span_id = uuid.uuid4().hex[:16]
        checkout_span_id = uuid.uuid4().hex[:16]

        if is_oom:
            # Complete failure scenario
            root_duration = 5025.0
            root_status = "ERROR"
            root_http = 504

            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=root_span_id,
                    parent_span_id=None,
                    service_name="api-gateway",
                    operation_name="POST /api/v1/checkout",
                    start_time_iso=timestamp,
                    duration_ms=root_duration,
                    status_code=root_status,
                    http_status=root_http,
                    attributes={"http.method": "POST", "http.status_code": 504, "error": True},
                )
            )
            # auth succeeded fast
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=auth_span_id,
                    parent_span_id=root_span_id,
                    service_name="auth-service",
                    operation_name="POST /auth/verify",
                    start_time_iso=timestamp,
                    duration_ms=5.4,
                    status_code="OK",
                    http_status=200,
                    attributes={"http.method": "POST", "http.status_code": 200},
                )
            )
            # checkout-service crashed / timed out
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=checkout_span_id,
                    parent_span_id=root_span_id,
                    service_name="checkout-service",
                    operation_name="POST /checkout/process",
                    start_time_iso=timestamp,
                    duration_ms=5015.0,
                    status_code="ERROR",
                    http_status=500,
                    attributes={
                        "http.method": "POST",
                        "http.status_code": 500,
                        "error.type": "java.lang.OutOfMemoryError",
                        "error.message": "Java heap space",
                    },
                )
            )
            return spans

        elif is_degraded:
            # Memory pressure leading to GC pauses and high latency
            checkout_lat = random.uniform(1100.0, 1800.0)
            root_lat = checkout_lat + 25.0

            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=root_span_id,
                    parent_span_id=None,
                    service_name="api-gateway",
                    operation_name="POST /api/v1/checkout",
                    start_time_iso=timestamp,
                    duration_ms=round(root_lat, 2),
                    status_code="OK",
                    http_status=200,
                    attributes={"http.method": "POST", "http.status_code": 200, "degraded": True},
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=auth_span_id,
                    parent_span_id=root_span_id,
                    service_name="auth-service",
                    operation_name="POST /auth/verify",
                    start_time_iso=timestamp,
                    duration_ms=6.1,
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=checkout_span_id,
                    parent_span_id=root_span_id,
                    service_name="checkout-service",
                    operation_name="POST /checkout/process",
                    start_time_iso=timestamp,
                    duration_ms=round(checkout_lat, 2),
                    status_code="OK",
                    http_status=200,
                    attributes={"gc.pause_ms": 950.0},
                )
            )
            return spans

        else:
            # Healthy normal trace
            cart_span_id = uuid.uuid4().hex[:16]
            pay_span_id = uuid.uuid4().hex[:16]
            inv_span_id = uuid.uuid4().hex[:16]
            ord_span_id = uuid.uuid4().hex[:16]

            checkout_dur = random.uniform(32.0, 48.0)
            root_dur = checkout_dur + 12.0

            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=root_span_id,
                    parent_span_id=None,
                    service_name="api-gateway",
                    operation_name="POST /api/v1/checkout",
                    start_time_iso=timestamp,
                    duration_ms=round(root_dur, 2),
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=auth_span_id,
                    parent_span_id=root_span_id,
                    service_name="auth-service",
                    operation_name="POST /auth/verify",
                    start_time_iso=timestamp,
                    duration_ms=5.0,
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=checkout_span_id,
                    parent_span_id=root_span_id,
                    service_name="checkout-service",
                    operation_name="POST /checkout/process",
                    start_time_iso=timestamp,
                    duration_ms=round(checkout_dur, 2),
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=cart_span_id,
                    parent_span_id=checkout_span_id,
                    service_name="cart-service",
                    operation_name="GET /cart/items",
                    start_time_iso=timestamp,
                    duration_ms=7.5,
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=pay_span_id,
                    parent_span_id=checkout_span_id,
                    service_name="payment-service",
                    operation_name="POST /payment/charge",
                    start_time_iso=timestamp,
                    duration_ms=16.2,
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=inv_span_id,
                    parent_span_id=checkout_span_id,
                    service_name="inventory-service",
                    operation_name="POST /inventory/reserve",
                    start_time_iso=timestamp,
                    duration_ms=9.1,
                    status_code="OK",
                    http_status=200,
                )
            )
            spans.append(
                TraceSpan(
                    trace_id=trace_id,
                    span_id=ord_span_id,
                    parent_span_id=checkout_span_id,
                    service_name="order-service",
                    operation_name="POST /order/create",
                    start_time_iso=timestamp,
                    duration_ms=11.4,
                    status_code="OK",
                    http_status=200,
                )
            )
            return spans
