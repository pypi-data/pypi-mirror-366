# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["FlowGetMetricsParams"]


class FlowGetMetricsParams(TypedDict, total=False):
    end_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """End date for filtering (YYYY-MM-DD format)"""

    start_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """Start date for filtering (YYYY-MM-DD format)"""

    status: Literal["completed", "failed", "in_progress"]
    """Filter by workflow status"""

    user_id: str
    """Filter by specific user ID"""
