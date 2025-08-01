# Google Workspace SDK - Update Guide

## How to Update and Reinstall the SDK

### Current Installation
You're currently using the SDK installed from Git:
```bash
pip install git+ssh://git@github.com/stainless-sdks/google-workspace-sdk-python.git
```

### To Update After Making Changes

#### 1. Uninstall Current Version
```bash
pip uninstall google-workspace-sdk -y
```

#### 2. Install Updated Version

**Option A: Install from Local Directory (for development)**
```bash
pip install -e /path/to/google-workspace-sdk-python
```

**Option B: Install from Git (after pushing changes)**
```bash
pip install git+ssh://git@github.com/stainless-sdks/google-workspace-sdk-python.git --force-reinstall
```

**Option C: Install from Git with Upgrade**
```bash
pip install --upgrade --force-reinstall git+ssh://git@github.com/stainless-sdks/google-workspace-sdk-python.git
```

### Recent Fixes Applied

1. **Fixed Endpoint Path**: Changed `/workspace` → `/workspaces`
2. **Fixed Response Parsing**: Handle nested `{"workspace": {...}}` response format  
3. **Updated Status Values**: Added `"ready"` to allowed status values

### Changes Made to Fix Compatibility

#### `/src/google_workspace_sdk/resources/workspace/workspace.py`
- Updated both sync and async `create()` methods
- Changed endpoint from `/workspace` to `/workspaces` 
- Added custom response handling for workspace manager's nested JSON format
- Extract `workspace` data from `{"workspace": {...}}` response

#### `/src/google_workspace_sdk/types/workspace_info.py`
- Added `"ready"` to status literal type: `["running", "stopped", "error", "ready"]`

### Testing the Updated SDK

```python
from google_workspace_sdk import GoogleWorkspaceSDK

client = GoogleWorkspaceSDK(
    api_key="dummy-api-key",  # Your manager doesn't validate this
    base_url="http://3.18.135.213:5001",  # Your manager URL
)

workspace_info = client.workspace.create()
print(workspace_info.session_id)  # Should print session ID
print(workspace_info.mcp_url)     # Should print MCP URL
```

### Workflow for Future Updates

1. **Make changes** to the SDK code
2. **Commit and push** to the GitHub repository  
3. **Uninstall** current version: `pip uninstall google-workspace-sdk -y`
4. **Reinstall** with force: `pip install --force-reinstall git+ssh://git@github.com/stainless-sdks/google-workspace-sdk-python.git`
5. **Test** your changes

### Development Workflow

For active development, use editable install:
```bash
git clone git@github.com:stainless-sdks/google-workspace-sdk-python.git
cd google-workspace-sdk-python
pip install -e .
```

This way changes are immediately reflected without reinstalling.