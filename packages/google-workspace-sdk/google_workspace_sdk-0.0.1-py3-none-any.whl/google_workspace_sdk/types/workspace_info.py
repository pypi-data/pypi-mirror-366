# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["WorkspaceInfo"]


class WorkspaceInfo(BaseModel):
    api_port: int
    """Port number for API access"""

    api_url: str
    """URL for API access"""

    mcp_port: int
    """Port number for MCP access"""

    mcp_url: str
    """URL for MCP protocol access"""

    session_id: str
    """Unique session identifier"""

    status: Literal["running", "stopped", "error", "ready"]
    """Current status of the workspace"""

    db_path: Optional[str] = None
    """Path to the workspace database"""
