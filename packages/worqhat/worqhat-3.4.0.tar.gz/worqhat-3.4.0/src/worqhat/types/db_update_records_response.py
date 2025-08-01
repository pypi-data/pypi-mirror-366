# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["DBUpdateRecordsResponse"]


class DBUpdateRecordsResponse(BaseModel):
    count: Optional[int] = None
    """Number of records updated"""

    data: Optional[List[object]] = None

    message: Optional[str] = None

    success: Optional[bool] = None
