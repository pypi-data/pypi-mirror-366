# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SlideCreateParams"]


class SlideCreateParams(TypedDict, total=False):
    name: Required[str]
    """Name of the presentation"""

    content: str
    """Initial content for the presentation"""
