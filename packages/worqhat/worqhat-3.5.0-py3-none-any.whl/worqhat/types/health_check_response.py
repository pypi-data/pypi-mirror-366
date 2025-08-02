# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["HealthCheckResponse", "Services"]


class Services(BaseModel):
    database: Optional[Literal["ok", "degraded", "down"]] = None


class HealthCheckResponse(BaseModel):
    status: Literal["ok", "degraded", "maintenance", "down"]
    """Current health status of the API"""

    uptime: float
    """Server uptime in seconds"""

    environment: Optional[Literal["development", "staging", "production"]] = None
    """Current environment"""

    services: Optional[Services] = None
    """Status of dependent services"""

    timestamp: Optional[datetime] = None
    """Current server time"""

    version: Optional[str] = None
    """Current API version"""
