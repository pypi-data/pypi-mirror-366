# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DBProcessNlQueryParams"]


class DBProcessNlQueryParams(TypedDict, total=False):
    question: Required[str]
    """Natural language question"""

    table: Required[str]
    """Table name to query"""
