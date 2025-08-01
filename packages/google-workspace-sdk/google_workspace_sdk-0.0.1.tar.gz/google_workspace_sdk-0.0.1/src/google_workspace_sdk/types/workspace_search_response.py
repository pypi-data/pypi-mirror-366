# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["WorkspaceSearchResponse", "Result"]


class Result(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the item"""

    content_preview: Optional[str] = None
    """Preview of the content"""

    created_at: Optional[datetime] = None
    """Creation timestamp"""

    modified_at: Optional[datetime] = None
    """Last modification timestamp"""

    name: Optional[str] = None
    """Name of the item"""

    type: Optional[Literal["document", "spreadsheet", "presentation", "folder"]] = None
    """Type of content"""

    url: Optional[str] = None
    """URL to access the item"""


class WorkspaceSearchResponse(BaseModel):
    results: Optional[List[Result]] = None

    total_count: Optional[int] = None
    """Total number of results found"""
