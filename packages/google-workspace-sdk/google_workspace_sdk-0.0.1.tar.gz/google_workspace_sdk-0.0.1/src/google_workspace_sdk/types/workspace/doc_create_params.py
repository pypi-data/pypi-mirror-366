# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DocCreateParams"]


class DocCreateParams(TypedDict, total=False):
    name: Required[str]
    """Name of the document"""

    content: str
    """Initial content of the document (Markdown format)"""
