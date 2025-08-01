# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["SlideRetrieveResponse", "Slide"]


class Slide(BaseModel):
    id: Optional[str] = None

    content: Optional[str] = None

    title: Optional[str] = None


class SlideRetrieveResponse(BaseModel):
    id: Optional[str] = None
    """Presentation identifier"""

    content: Optional[str] = None
    """Presentation content"""

    created_at: Optional[datetime] = None

    modified_at: Optional[datetime] = None

    name: Optional[str] = None
    """Presentation name"""

    slides: Optional[List[Slide]] = None
    """Individual slides"""

    url: Optional[str] = None
    """Presentation URL"""
