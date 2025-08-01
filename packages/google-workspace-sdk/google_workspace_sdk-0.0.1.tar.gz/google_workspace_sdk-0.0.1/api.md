# Workspace

Types:

```python
from google_workspace_sdk.types import (
    WorkspaceInfo,
    WorkspaceDeleteResponse,
    WorkspaceSearchResponse,
)
```

Methods:

- <code title="post /workspace">client.workspace.<a href="./src/google_workspace_sdk/resources/workspace/workspace.py">create</a>() -> <a href="./src/google_workspace_sdk/types/workspace_info.py">WorkspaceInfo</a></code>
- <code title="get /workspace/{sessionId}">client.workspace.<a href="./src/google_workspace_sdk/resources/workspace/workspace.py">retrieve</a>(session_id) -> <a href="./src/google_workspace_sdk/types/workspace_info.py">WorkspaceInfo</a></code>
- <code title="delete /workspace/{sessionId}">client.workspace.<a href="./src/google_workspace_sdk/resources/workspace/workspace.py">delete</a>(session_id) -> <a href="./src/google_workspace_sdk/types/workspace_delete_response.py">WorkspaceDeleteResponse</a></code>
- <code title="post /workspace/{sessionId}/search">client.workspace.<a href="./src/google_workspace_sdk/resources/workspace/workspace.py">search</a>(session_id, \*\*<a href="src/google_workspace_sdk/types/workspace_search_params.py">params</a>) -> <a href="./src/google_workspace_sdk/types/workspace_search_response.py">WorkspaceSearchResponse</a></code>

## Drive

Types:

```python
from google_workspace_sdk.types.workspace import DriveTree
```

Methods:

- <code title="get /workspace/{sessionId}/drive/tree">client.workspace.drive.<a href="./src/google_workspace_sdk/resources/workspace/drive.py">retrieve_tree</a>(session_id) -> <a href="./src/google_workspace_sdk/types/workspace/drive_tree.py">DriveTree</a></code>

## Docs

Types:

```python
from google_workspace_sdk.types.workspace import DocRetrieveResponse
```

Methods:

- <code title="post /workspace/{sessionId}/docs">client.workspace.docs.<a href="./src/google_workspace_sdk/resources/workspace/docs.py">create</a>(session_id, \*\*<a href="src/google_workspace_sdk/types/workspace/doc_create_params.py">params</a>) -> None</code>
- <code title="get /workspace/{sessionId}/docs/{docId}">client.workspace.docs.<a href="./src/google_workspace_sdk/resources/workspace/docs.py">retrieve</a>(doc_id, \*, session_id) -> <a href="./src/google_workspace_sdk/types/workspace/doc_retrieve_response.py">DocRetrieveResponse</a></code>

## Sheets

Types:

```python
from google_workspace_sdk.types.workspace import SheetRetrieveResponse
```

Methods:

- <code title="post /workspace/{sessionId}/sheets">client.workspace.sheets.<a href="./src/google_workspace_sdk/resources/workspace/sheets.py">create</a>(session_id, \*\*<a href="src/google_workspace_sdk/types/workspace/sheet_create_params.py">params</a>) -> None</code>
- <code title="get /workspace/{sessionId}/sheets/{sheetId}">client.workspace.sheets.<a href="./src/google_workspace_sdk/resources/workspace/sheets.py">retrieve</a>(sheet_id, \*, session_id) -> <a href="./src/google_workspace_sdk/types/workspace/sheet_retrieve_response.py">SheetRetrieveResponse</a></code>

## Slides

Types:

```python
from google_workspace_sdk.types.workspace import SlideRetrieveResponse
```

Methods:

- <code title="post /workspace/{sessionId}/slides">client.workspace.slides.<a href="./src/google_workspace_sdk/resources/workspace/slides.py">create</a>(session_id, \*\*<a href="src/google_workspace_sdk/types/workspace/slide_create_params.py">params</a>) -> None</code>
- <code title="get /workspace/{sessionId}/slides/{slidesId}">client.workspace.slides.<a href="./src/google_workspace_sdk/resources/workspace/slides.py">retrieve</a>(slides_id, \*, session_id) -> <a href="./src/google_workspace_sdk/types/workspace/slide_retrieve_response.py">SlideRetrieveResponse</a></code>
