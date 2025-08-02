# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FlowGetMetricsResponse", "Metrics", "MetricsMetricsByUser", "Workflow"]


class MetricsMetricsByUser(BaseModel):
    completed: Optional[int] = None

    failed: Optional[int] = None

    in_progress: Optional[int] = None

    total: Optional[int] = None


class Metrics(BaseModel):
    avg_duration_ms: Optional[float] = None

    completed_workflows: Optional[int] = None

    failed_workflows: Optional[int] = None

    in_progress_workflows: Optional[int] = None

    metrics_by_user: Optional[Dict[str, MetricsMetricsByUser]] = None

    total_workflows: Optional[int] = None


class Workflow(BaseModel):
    id: Optional[str] = None

    end_timestamp: Optional[datetime] = None

    org_id: Optional[str] = None

    start_timestamp: Optional[datetime] = None

    status: Optional[Literal["completed", "failed", "in_progress"]] = None

    user_id: Optional[str] = None

    workflow_id: Optional[str] = None


class FlowGetMetricsResponse(BaseModel):
    metrics: Optional[Metrics] = None

    workflows: Optional[List[Workflow]] = None
