# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["SheetCreateParams"]


class SheetCreateParams(TypedDict, total=False):
    name: Required[str]
    """Name of the spreadsheet"""

    data: Iterable[List[str]]
    """Initial data for the spreadsheet"""
