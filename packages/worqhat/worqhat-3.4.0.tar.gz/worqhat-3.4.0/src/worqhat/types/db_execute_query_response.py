# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DBExecuteQueryResponse"]


class DBExecuteQueryResponse(BaseModel):
    data: Optional[List[object]] = None

    execution_time: Optional[int] = FieldInfo(alias="executionTime", default=None)
    """Query execution time in milliseconds"""

    query: Optional[str] = None
    """The executed SQL query"""

    success: Optional[bool] = None
