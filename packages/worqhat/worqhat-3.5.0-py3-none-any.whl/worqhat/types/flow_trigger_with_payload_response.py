# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["FlowTriggerWithPayloadResponse"]


class FlowTriggerWithPayloadResponse(BaseModel):
    analytics_id: Optional[str] = None

    data: Optional[Dict[str, object]] = None

    message: Optional[str] = None

    success: Optional[bool] = None

    timestamp: Optional[datetime] = None
