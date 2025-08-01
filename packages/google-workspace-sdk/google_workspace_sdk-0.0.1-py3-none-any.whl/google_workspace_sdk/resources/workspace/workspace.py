# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .docs import (
    DocsResource,
    AsyncDocsResource,
    DocsResourceWithRawResponse,
    AsyncDocsResourceWithRawResponse,
    DocsResourceWithStreamingResponse,
    AsyncDocsResourceWithStreamingResponse,
)
from .drive import (
    DriveResource,
    AsyncDriveResource,
    DriveResourceWithRawResponse,
    AsyncDriveResourceWithRawResponse,
    DriveResourceWithStreamingResponse,
    AsyncDriveResourceWithStreamingResponse,
)
from .sheets import (
    SheetsResource,
    AsyncSheetsResource,
    SheetsResourceWithRawResponse,
    AsyncSheetsResourceWithRawResponse,
    SheetsResourceWithStreamingResponse,
    AsyncSheetsResourceWithStreamingResponse,
)
from .slides import (
    SlidesResource,
    AsyncSlidesResource,
    SlidesResourceWithRawResponse,
    AsyncSlidesResourceWithRawResponse,
    SlidesResourceWithStreamingResponse,
    AsyncSlidesResourceWithStreamingResponse,
)
from ...types import workspace_search_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.workspace_info import WorkspaceInfo
from ...types.workspace_delete_response import WorkspaceDeleteResponse
from ...types.workspace_search_response import WorkspaceSearchResponse

__all__ = ["WorkspaceResource", "AsyncWorkspaceResource"]


class WorkspaceResource(SyncAPIResource):
    @cached_property
    def drive(self) -> DriveResource:
        return DriveResource(self._client)

    @cached_property
    def docs(self) -> DocsResource:
        return DocsResource(self._client)

    @cached_property
    def sheets(self) -> SheetsResource:
        return SheetsResource(self._client)

    @cached_property
    def slides(self) -> SlidesResource:
        return SlidesResource(self._client)

    @cached_property
    def with_raw_response(self) -> WorkspaceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#accessing-raw-response-data-eg-headers
        """
        return WorkspaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkspaceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#with_streaming_response
        """
        return WorkspaceResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceInfo:
        """Creates a new Google Workspace simulation instance with pre-populated data"""
        # Custom response handler for workspace manager format
        import httpx
        
        # Build the request manually to handle custom response format
        request_options = make_request_options(
            extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
        )
        
        # Get the raw HTTP response
        with httpx.Client(base_url=self._client.base_url, headers=self._client.default_headers, timeout=self._client.timeout) as http_client:
            http_response = http_client.post("/workspaces", json={})
            response_data = http_response.json()
        
        # Extract workspace data from nested response
        if isinstance(response_data, dict) and "workspace" in response_data:
            workspace_data = response_data["workspace"]
        else:
            workspace_data = response_data
            
        # Convert to WorkspaceInfo model
        return WorkspaceInfo.model_validate(workspace_data)

    def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceInfo:
        """
        Retrieve information about an existing workspace instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            f"/workspace/{session_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceInfo,
        )

    def delete(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceDeleteResponse:
        """
        Permanently delete a workspace instance and all its data

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        # Use the workspace manager's current workspace deletion endpoint
        import httpx
        
        # Build the request manually to handle workspace manager format
        try:
            with httpx.Client(base_url=self._client.base_url, headers=self._client.default_headers, timeout=self._client.timeout) as http_client:
                http_response = http_client.delete("/workspaces/current")
                response_data = http_response.json()
            
            # Return the response in expected format
            from ...types.workspace_delete_response import WorkspaceDeleteResponse
            return WorkspaceDeleteResponse.model_validate(response_data)
            
        except Exception as e:
            # Fallback: try the original endpoint with plural
            return self._delete(
                f"/workspaces/{session_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=WorkspaceDeleteResponse,
            )

    def search(
        self,
        session_id: str,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceSearchResponse:
        """
        Search across all content in the workspace including documents, sheets, and
        presentations

        Args:
          query: Search query string (empty string returns all content)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            f"/workspace/{session_id}/search",
            body=maybe_transform({"query": query}, workspace_search_params.WorkspaceSearchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceSearchResponse,
        )


class AsyncWorkspaceResource(AsyncAPIResource):
    @cached_property
    def drive(self) -> AsyncDriveResource:
        return AsyncDriveResource(self._client)

    @cached_property
    def docs(self) -> AsyncDocsResource:
        return AsyncDocsResource(self._client)

    @cached_property
    def sheets(self) -> AsyncSheetsResource:
        return AsyncSheetsResource(self._client)

    @cached_property
    def slides(self) -> AsyncSlidesResource:
        return AsyncSlidesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWorkspaceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkspaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkspaceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#with_streaming_response
        """
        return AsyncWorkspaceResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceInfo:
        """Creates a new Google Workspace simulation instance with pre-populated data"""
        # Custom response handler for workspace manager format
        import httpx
        
        # Build the request manually to handle custom response format
        request_options = make_request_options(
            extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
        )
        
        # Get the raw HTTP response
        async with httpx.AsyncClient(base_url=self._client.base_url, headers=self._client.default_headers, timeout=self._client.timeout) as http_client:
            http_response = await http_client.post("/workspaces", json={})
            response_data = http_response.json()
        
        # Extract workspace data from nested response
        if isinstance(response_data, dict) and "workspace" in response_data:
            workspace_data = response_data["workspace"]
        else:
            workspace_data = response_data
            
        # Convert to WorkspaceInfo model
        return WorkspaceInfo.model_validate(workspace_data)

    async def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceInfo:
        """
        Retrieve information about an existing workspace instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            f"/workspace/{session_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceInfo,
        )

    async def delete(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceDeleteResponse:
        """
        Permanently delete a workspace instance and all its data

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        # Use the workspace manager's current workspace deletion endpoint
        import httpx
        
        # Build the request manually to handle workspace manager format
        try:
            async with httpx.AsyncClient(base_url=self._client.base_url, headers=self._client.default_headers, timeout=self._client.timeout) as http_client:
                http_response = await http_client.delete("/workspaces/current")
                response_data = http_response.json()
            
            # Return the response in expected format
            from ...types.workspace_delete_response import WorkspaceDeleteResponse
            return WorkspaceDeleteResponse.model_validate(response_data)
            
        except Exception as e:
            # Fallback: try the original endpoint with plural
            return await self._delete(
                f"/workspaces/{session_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=WorkspaceDeleteResponse,
            )

    async def search(
        self,
        session_id: str,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkspaceSearchResponse:
        """
        Search across all content in the workspace including documents, sheets, and
        presentations

        Args:
          query: Search query string (empty string returns all content)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            f"/workspace/{session_id}/search",
            body=await async_maybe_transform({"query": query}, workspace_search_params.WorkspaceSearchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceSearchResponse,
        )


class WorkspaceResourceWithRawResponse:
    def __init__(self, workspace: WorkspaceResource) -> None:
        self._workspace = workspace

        self.create = to_raw_response_wrapper(
            workspace.create,
        )
        self.retrieve = to_raw_response_wrapper(
            workspace.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            workspace.delete,
        )
        self.search = to_raw_response_wrapper(
            workspace.search,
        )

    @cached_property
    def drive(self) -> DriveResourceWithRawResponse:
        return DriveResourceWithRawResponse(self._workspace.drive)

    @cached_property
    def docs(self) -> DocsResourceWithRawResponse:
        return DocsResourceWithRawResponse(self._workspace.docs)

    @cached_property
    def sheets(self) -> SheetsResourceWithRawResponse:
        return SheetsResourceWithRawResponse(self._workspace.sheets)

    @cached_property
    def slides(self) -> SlidesResourceWithRawResponse:
        return SlidesResourceWithRawResponse(self._workspace.slides)


class AsyncWorkspaceResourceWithRawResponse:
    def __init__(self, workspace: AsyncWorkspaceResource) -> None:
        self._workspace = workspace

        self.create = async_to_raw_response_wrapper(
            workspace.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            workspace.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            workspace.delete,
        )
        self.search = async_to_raw_response_wrapper(
            workspace.search,
        )

    @cached_property
    def drive(self) -> AsyncDriveResourceWithRawResponse:
        return AsyncDriveResourceWithRawResponse(self._workspace.drive)

    @cached_property
    def docs(self) -> AsyncDocsResourceWithRawResponse:
        return AsyncDocsResourceWithRawResponse(self._workspace.docs)

    @cached_property
    def sheets(self) -> AsyncSheetsResourceWithRawResponse:
        return AsyncSheetsResourceWithRawResponse(self._workspace.sheets)

    @cached_property
    def slides(self) -> AsyncSlidesResourceWithRawResponse:
        return AsyncSlidesResourceWithRawResponse(self._workspace.slides)


class WorkspaceResourceWithStreamingResponse:
    def __init__(self, workspace: WorkspaceResource) -> None:
        self._workspace = workspace

        self.create = to_streamed_response_wrapper(
            workspace.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            workspace.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            workspace.delete,
        )
        self.search = to_streamed_response_wrapper(
            workspace.search,
        )

    @cached_property
    def drive(self) -> DriveResourceWithStreamingResponse:
        return DriveResourceWithStreamingResponse(self._workspace.drive)

    @cached_property
    def docs(self) -> DocsResourceWithStreamingResponse:
        return DocsResourceWithStreamingResponse(self._workspace.docs)

    @cached_property
    def sheets(self) -> SheetsResourceWithStreamingResponse:
        return SheetsResourceWithStreamingResponse(self._workspace.sheets)

    @cached_property
    def slides(self) -> SlidesResourceWithStreamingResponse:
        return SlidesResourceWithStreamingResponse(self._workspace.slides)


class AsyncWorkspaceResourceWithStreamingResponse:
    def __init__(self, workspace: AsyncWorkspaceResource) -> None:
        self._workspace = workspace

        self.create = async_to_streamed_response_wrapper(
            workspace.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            workspace.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            workspace.delete,
        )
        self.search = async_to_streamed_response_wrapper(
            workspace.search,
        )

    @cached_property
    def drive(self) -> AsyncDriveResourceWithStreamingResponse:
        return AsyncDriveResourceWithStreamingResponse(self._workspace.drive)

    @cached_property
    def docs(self) -> AsyncDocsResourceWithStreamingResponse:
        return AsyncDocsResourceWithStreamingResponse(self._workspace.docs)

    @cached_property
    def sheets(self) -> AsyncSheetsResourceWithStreamingResponse:
        return AsyncSheetsResourceWithStreamingResponse(self._workspace.sheets)

    @cached_property
    def slides(self) -> AsyncSlidesResourceWithStreamingResponse:
        return AsyncSlidesResourceWithStreamingResponse(self._workspace.slides)
