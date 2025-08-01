# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["DocRetrieveResponse"]


class DocRetrieveResponse(BaseModel):
    id: Optional[str] = None
    """Document identifier"""

    content: Optional[str] = None
    """Document content in Markdown format"""

    created_at: Optional[datetime] = None

    modified_at: Optional[datetime] = None

    name: Optional[str] = None
    """Document name"""

    url: Optional[str] = None
    """Document URL"""
