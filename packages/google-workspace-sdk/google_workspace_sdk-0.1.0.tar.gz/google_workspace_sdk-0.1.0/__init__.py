"""
Google Workspace SDK - Connect to Google Workspace Simulation Manager.

A lightweight SDK for creating and managing Google Workspace simulation instances
with MCP (Model Context Protocol) support.
"""

from .client import WorkspaceClient
from .models import WorkspaceInfo
from .exceptions import WorkspaceSDKError, WorkspaceNotFoundError

__version__ = "0.1.0"

__all__ = [
    'WorkspaceClient',
    'WorkspaceInfo', 
    'WorkspaceSDKError',
    'WorkspaceNotFoundError'
]