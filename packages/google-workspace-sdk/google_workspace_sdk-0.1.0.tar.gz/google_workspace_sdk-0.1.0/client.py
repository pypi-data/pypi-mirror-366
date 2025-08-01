"""
Google Workspace SDK Client.
"""

import httpx
import asyncio
import json
from typing import Optional, Any
from mcp import Client

from .models import WorkspaceInfo
from .exceptions import (
    WorkspaceSDKError, 
    WorkspaceNotFoundError,
    WorkspaceCreationError,
    ConnectionError
)


class MCPClient:
    """MCP client for interacting with workspace tools."""
    
    def __init__(self, mcp_url: str):
        self.mcp_url = mcp_url
        self._client = None
    
    async def _ensure_connected(self):
        """Ensure MCP client is connected."""
        if self._client is None:
            self._client = Client(self.mcp_url)
            await self._client.connect()
    
    async def search(self, query: str = "") -> list:
        """Search across workspace content."""
        await self._ensure_connected()
        result = await self._client.call_tool("search", {"query": query})
        return result.get("results", [])
    
    async def drive_tree(self) -> dict:
        """Get drive folder structure."""
        await self._ensure_connected()
        result = await self._client.call_tool("drive_tree", {})
        return result
    
    async def get_doc(self, doc_id: str) -> dict:
        """Get document content."""
        await self._ensure_connected()
        result = await self._client.call_tool("get_doc", {"doc_id": doc_id})
        return result
    
    async def create_doc(self, name: str, content: str = "") -> dict:
        """Create a new document."""
        await self._ensure_connected()
        result = await self._client.call_tool("create_doc", {
            "name": name,
            "content": content
        })
        return result
    
    async def get_sheet(self, sheet_id: str) -> dict:
        """Get spreadsheet content."""
        await self._ensure_connected()
        result = await self._client.call_tool("get_sheet", {"sheet_id": sheet_id})
        return result
    
    async def create_sheet(self, name: str, data: list = None) -> dict:
        """Create a new spreadsheet."""
        await self._ensure_connected()
        result = await self._client.call_tool("create_sheet", {
            "name": name,
            "data": data or []
        })
        return result
    
    async def get_slides(self, slides_id: str) -> dict:
        """Get presentation content."""
        await self._ensure_connected()
        result = await self._client.call_tool("get_slides", {"slides_id": slides_id})
        return result
    
    async def create_slides(self, name: str, content: str = "") -> dict:
        """Create a new presentation."""
        await self._ensure_connected()
        result = await self._client.call_tool("create_slides", {
            "name": name,
            "content": content
        })
        return result
    
    async def close(self):
        """Close the MCP connection."""
        if self._client:
            await self._client.close()


class WorkspaceClient:
    """
    Client for managing Google Workspace Simulation instances.
    
    This client connects to a workspace manager to create, manage,
    and interact with workspace instances.
    """
    
    def __init__(self, manager_url: str = "http://localhost:5001", timeout: float = 30.0):
        """
        Initialize the workspace client.
        
        Args:
            manager_url: URL of the workspace manager service
            timeout: Request timeout in seconds  
        """
        self.manager_url = manager_url.rstrip('/')
        self.timeout = timeout
        self._workspace_info: Optional[WorkspaceInfo] = None
        self._mcp_client: Optional[MCPClient] = None
    
    async def create_workspace(self) -> WorkspaceInfo:
        """
        Create a new workspace instance.
        
        Returns:
            WorkspaceInfo with connection details
            
        Raises:
            WorkspaceCreationError: If workspace creation fails
            ConnectionError: If cannot connect to manager
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.manager_url}/workspace")
                response.raise_for_status()
                
                data = response.json()
                self._workspace_info = WorkspaceInfo(**data)
                return self._workspace_info
                
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to manager: {e}")
        except httpx.HTTPStatusError as e:
            raise WorkspaceCreationError(f"Workspace creation failed: {e}")
        except Exception as e:
            raise WorkspaceSDKError(f"Unexpected error: {e}")
    
    async def get_workspace(self) -> Optional[WorkspaceInfo]:
        """
        Get current workspace information.
        
        Returns:
            WorkspaceInfo if workspace exists, None otherwise
        """
        if not self._workspace_info:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.manager_url}/workspace/{self._workspace_info.session_id}"
                )
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                data = response.json()
                self._workspace_info = WorkspaceInfo(**data)
                return self._workspace_info
                
        except httpx.RequestError:
            return None
        except Exception:
            return None
    
    async def delete_workspace(self) -> bool:
        """
        Delete the current workspace.
        
        Returns:
            True if successfully deleted, False otherwise
        """
        if not self._workspace_info:
            return False
            
        try:
            # Close MCP client first
            if self._mcp_client:
                await self._mcp_client.close()
                self._mcp_client = None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.manager_url}/workspace/{self._workspace_info.session_id}"
                )
                response.raise_for_status()
                
            self._workspace_info = None
            return True
            
        except Exception:
            return False
    
    def get_mcp_client(self) -> MCPClient:
        """
        Get an MCP client for the current workspace.
        
        Returns:
            MCPClient instance
            
        Raises:
            WorkspaceNotFoundError: If no workspace is active
        """
        if not self._workspace_info:
            raise WorkspaceNotFoundError("No active workspace. Call create_workspace() first.")
        
        if not self._mcp_client:
            self._mcp_client = MCPClient(self._workspace_info.mcp_url)
        
        return self._mcp_client