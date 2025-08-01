# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from google_workspace_sdk import GoogleWorkspaceSDK, AsyncGoogleWorkspaceSDK
from google_workspace_sdk.types import (
    WorkspaceInfo,
    WorkspaceDeleteResponse,
    WorkspaceSearchResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkspace:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: GoogleWorkspaceSDK) -> None:
        workspace = client.workspace.create()
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceInfo, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        workspace = client.workspace.retrieve(
            "sessionId",
        )
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.with_raw_response.retrieve(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.with_streaming_response.retrieve(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceInfo, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: GoogleWorkspaceSDK) -> None:
        workspace = client.workspace.delete(
            "sessionId",
        )
        assert_matches_type(WorkspaceDeleteResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.with_raw_response.delete(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceDeleteResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.with_streaming_response.delete(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceDeleteResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: GoogleWorkspaceSDK) -> None:
        workspace = client.workspace.search(
            session_id="sessionId",
            query="meeting notes",
        )
        assert_matches_type(WorkspaceSearchResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.with_raw_response.search(
            session_id="sessionId",
            query="meeting notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceSearchResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.with_streaming_response.search(
            session_id="sessionId",
            query="meeting notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceSearchResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_search(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.with_raw_response.search(
                session_id="",
                query="meeting notes",
            )


class TestAsyncWorkspace:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        workspace = await async_client.workspace.create()
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceInfo, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        workspace = await async_client.workspace.retrieve(
            "sessionId",
        )
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.with_raw_response.retrieve(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceInfo, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.with_streaming_response.retrieve(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceInfo, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        workspace = await async_client.workspace.delete(
            "sessionId",
        )
        assert_matches_type(WorkspaceDeleteResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.with_raw_response.delete(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceDeleteResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.with_streaming_response.delete(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceDeleteResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        workspace = await async_client.workspace.search(
            session_id="sessionId",
            query="meeting notes",
        )
        assert_matches_type(WorkspaceSearchResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.with_raw_response.search(
            session_id="sessionId",
            query="meeting notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceSearchResponse, workspace, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.with_streaming_response.search(
            session_id="sessionId",
            query="meeting notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceSearchResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_search(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.with_raw_response.search(
                session_id="",
                query="meeting notes",
            )
