# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DBUpdateRecordsParams"]


class DBUpdateRecordsParams(TypedDict, total=False):
    data: Required[object]
    """Data to update"""

    table: Required[str]
    """Table name to update"""

    where: Required[object]
    """Where conditions"""
