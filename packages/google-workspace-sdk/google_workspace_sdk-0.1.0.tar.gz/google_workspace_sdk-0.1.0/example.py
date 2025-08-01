#!/usr/bin/env python3
"""
Example usage of the Google Workspace SDK.
"""

import asyncio
from google_workspace_sdk import WorkspaceClient


async def main():
    """Demonstrate basic SDK usage."""
    
    print("🏗️  Google Workspace SDK Example")
    print("=" * 40)
    
    # Connect to workspace manager
    client = WorkspaceClient(manager_url="http://3.18.135.213:5001")
    
    try:
        # Create workspace  
        print("1. Creating workspace...")
        workspace = await client.create_workspace()
        print(f"   ✅ Created: {workspace.session_id}")
        print(f"   📡 MCP URL: {workspace.mcp_url}")
        
        # Get MCP client
        print("\n2. Setting up MCP client...")
        mcp = client.get_mcp_client()
        print("   ✅ MCP client ready")
        
        # Search content
        print("\n3. Searching workspace...")
        results = await mcp.search("")
        print(f"   📄 Found {len(results)} total items")
        
        # Create document
        print("\n4. Creating document...")
        doc = await mcp.create_doc(
            name="SDK Example Document",
            content="# Created with SDK\n\nThis document was created using the Google Workspace SDK."
        )
        print(f"   ✅ Document created")
        
        print("\n🎉 SDK example complete!")
        print(f"📡 Your workspace MCP URL: {workspace.mcp_url}")
        
        # Keep running until Ctrl+C
        print("\n⏳ Workspace running... Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Clean up
        print("🧹 Cleaning up...")
        await client.delete_workspace()
        print("✅ Done")


if __name__ == "__main__":
    asyncio.run(main())