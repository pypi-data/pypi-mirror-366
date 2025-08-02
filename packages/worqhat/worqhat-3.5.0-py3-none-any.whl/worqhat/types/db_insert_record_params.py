# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DBInsertRecordParams"]


class DBInsertRecordParams(TypedDict, total=False):
    data: Required[object]
    """Data to insert"""

    table: Required[str]
    """Table name to insert into"""
