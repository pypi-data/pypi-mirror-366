# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .._types import FileTypes

__all__ = ["FlowTriggerWithFileParams"]


class FlowTriggerWithFileParams(TypedDict, total=False):
    file: FileTypes
    """File to upload and process"""

    url: str
    """URL to a file to download and process"""
