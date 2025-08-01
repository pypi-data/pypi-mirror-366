# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DriveTree"]


class DriveTree(BaseModel):
    id: Optional[str] = None
    """Unique identifier"""

    children: Optional[List["DriveTree"]] = None
    """Child folders and files"""

    name: Optional[str] = None
    """Folder name"""

    type: Optional[Literal["folder", "file"]] = None
