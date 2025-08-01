"""
Data models for the Google Workspace SDK.
"""

from typing import Optional
from pydantic import BaseModel


class WorkspaceInfo(BaseModel):
    """Information about a workspace instance."""
    
    session_id: str
    api_url: str
    mcp_url: str
    api_port: int
    mcp_port: int
    db_path: Optional[str] = None
    status: str = "running"