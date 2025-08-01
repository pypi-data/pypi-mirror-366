# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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
from ...types.workspace import sheet_create_params
from ...types.workspace.sheet_retrieve_response import SheetRetrieveResponse

__all__ = ["SheetsResource", "AsyncSheetsResource"]


class SheetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SheetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#accessing-raw-response-data-eg-headers
        """
        return SheetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SheetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#with_streaming_response
        """
        return SheetsResourceWithStreamingResponse(self)

    def create(
        self,
        session_id: str,
        *,
        name: str,
        data: Iterable[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new Google Sheets spreadsheet in the workspace

        Args:
          name: Name of the spreadsheet

          data: Initial data for the spreadsheet

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/workspace/{session_id}/sheets",
            body=maybe_transform(
                {
                    "name": name,
                    "data": data,
                },
                sheet_create_params.SheetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        sheet_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SheetRetrieveResponse:
        """
        Retrieve the content of a specific spreadsheet

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return self._get(
            f"/workspace/{session_id}/sheets/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SheetRetrieveResponse,
        )


class AsyncSheetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSheetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSheetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSheetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/metis-mantis/google-workspace-sdk#with_streaming_response
        """
        return AsyncSheetsResourceWithStreamingResponse(self)

    async def create(
        self,
        session_id: str,
        *,
        name: str,
        data: Iterable[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new Google Sheets spreadsheet in the workspace

        Args:
          name: Name of the spreadsheet

          data: Initial data for the spreadsheet

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/workspace/{session_id}/sheets",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "data": data,
                },
                sheet_create_params.SheetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        sheet_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SheetRetrieveResponse:
        """
        Retrieve the content of a specific spreadsheet

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return await self._get(
            f"/workspace/{session_id}/sheets/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SheetRetrieveResponse,
        )


class SheetsResourceWithRawResponse:
    def __init__(self, sheets: SheetsResource) -> None:
        self._sheets = sheets

        self.create = to_raw_response_wrapper(
            sheets.create,
        )
        self.retrieve = to_raw_response_wrapper(
            sheets.retrieve,
        )


class AsyncSheetsResourceWithRawResponse:
    def __init__(self, sheets: AsyncSheetsResource) -> None:
        self._sheets = sheets

        self.create = async_to_raw_response_wrapper(
            sheets.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            sheets.retrieve,
        )


class SheetsResourceWithStreamingResponse:
    def __init__(self, sheets: SheetsResource) -> None:
        self._sheets = sheets

        self.create = to_streamed_response_wrapper(
            sheets.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sheets.retrieve,
        )


class AsyncSheetsResourceWithStreamingResponse:
    def __init__(self, sheets: AsyncSheetsResource) -> None:
        self._sheets = sheets

        self.create = async_to_streamed_response_wrapper(
            sheets.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sheets.retrieve,
        )
