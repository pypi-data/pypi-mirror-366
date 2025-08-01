# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["GetServerInfoResponse"]


class GetServerInfoResponse(BaseModel):
    environment: Optional[str] = None

    name: Optional[str] = None

    version: Optional[str] = None
