# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["SheetRetrieveResponse"]


class SheetRetrieveResponse(BaseModel):
    id: Optional[str] = None
    """Spreadsheet identifier"""

    created_at: Optional[datetime] = None

    data: Optional[List[List[str]]] = None
    """Spreadsheet data as array of rows"""

    modified_at: Optional[datetime] = None

    name: Optional[str] = None
    """Spreadsheet name"""

    url: Optional[str] = None
    """Spreadsheet URL"""
