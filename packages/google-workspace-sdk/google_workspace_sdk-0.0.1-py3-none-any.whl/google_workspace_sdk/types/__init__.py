# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from . import workspace
from .. import _compat
from .workspace_info import WorkspaceInfo as WorkspaceInfo
from .workspace_search_params import WorkspaceSearchParams as WorkspaceSearchParams
from .workspace_delete_response import WorkspaceDeleteResponse as WorkspaceDeleteResponse
from .workspace_search_response import WorkspaceSearchResponse as WorkspaceSearchResponse

# Rebuild cyclical models only after all modules are imported.
# This ensures that, when building the deferred (due to cyclical references) model schema,
# Pydantic can resolve the necessary references.
# See: https://github.com/pydantic/pydantic/issues/11250 for more context.
if _compat.PYDANTIC_V2:
    workspace.drive_tree.DriveTree.model_rebuild(_parent_namespace_depth=0)
else:
    workspace.drive_tree.DriveTree.update_forward_refs()  # type: ignore
