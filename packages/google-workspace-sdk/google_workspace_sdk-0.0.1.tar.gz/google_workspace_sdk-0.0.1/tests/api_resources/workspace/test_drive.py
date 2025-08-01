# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from google_workspace_sdk import GoogleWorkspaceSDK, AsyncGoogleWorkspaceSDK
from google_workspace_sdk.types.workspace import DriveTree

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDrive:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_tree(self, client: GoogleWorkspaceSDK) -> None:
        drive = client.workspace.drive.retrieve_tree(
            "sessionId",
        )
        assert_matches_type(DriveTree, drive, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_tree(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.drive.with_raw_response.retrieve_tree(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drive = response.parse()
        assert_matches_type(DriveTree, drive, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_tree(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.drive.with_streaming_response.retrieve_tree(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drive = response.parse()
            assert_matches_type(DriveTree, drive, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_tree(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.drive.with_raw_response.retrieve_tree(
                "",
            )


class TestAsyncDrive:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_tree(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        drive = await async_client.workspace.drive.retrieve_tree(
            "sessionId",
        )
        assert_matches_type(DriveTree, drive, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_tree(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.drive.with_raw_response.retrieve_tree(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drive = await response.parse()
        assert_matches_type(DriveTree, drive, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_tree(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.drive.with_streaming_response.retrieve_tree(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drive = await response.parse()
            assert_matches_type(DriveTree, drive, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_tree(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.drive.with_raw_response.retrieve_tree(
                "",
            )
