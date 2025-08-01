# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DBExecuteQueryParams"]


class DBExecuteQueryParams(TypedDict, total=False):
    query: Required[str]
    """SQL query to execute"""
