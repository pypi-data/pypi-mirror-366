"""
Exceptions for the Google Workspace SDK.
"""


class WorkspaceSDKError(Exception):
    """Base exception for all workspace SDK errors."""
    pass


class WorkspaceNotFoundError(WorkspaceSDKError):
    """Raised when a workspace cannot be found."""
    pass


class WorkspaceCreationError(WorkspaceSDKError):
    """Raised when workspace creation fails."""
    pass


class ConnectionError(WorkspaceSDKError):
    """Raised when connection to manager fails."""
    pass