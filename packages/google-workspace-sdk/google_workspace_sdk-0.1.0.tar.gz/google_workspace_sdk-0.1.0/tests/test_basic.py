"""
Basic tests for the Google Workspace SDK.
"""

import pytest
from google_workspace_sdk import WorkspaceClient, WorkspaceInfo
from google_workspace_sdk.exceptions import WorkspaceSDKError


def test_workspace_client_init():
    """Test WorkspaceClient initialization."""
    client = WorkspaceClient()
    assert client.manager_url == "http://localhost:5001"
    assert client.timeout == 30.0


def test_workspace_client_custom_url():
    """Test WorkspaceClient with custom URL."""
    client = WorkspaceClient(manager_url="http://example.com:8080")
    assert client.manager_url == "http://example.com:8080"


def test_workspace_info_model():
    """Test WorkspaceInfo model."""
    info = WorkspaceInfo(
        session_id="test-123",
        api_url="http://localhost:8000",
        mcp_url="http://localhost:3000/mcp",
        api_port=8000,
        mcp_port=3000
    )
    assert info.session_id == "test-123"
    assert info.status == "running"  # default value


def test_exceptions():
    """Test custom exceptions."""
    with pytest.raises(WorkspaceSDKError):
        raise WorkspaceSDKError("Test error")