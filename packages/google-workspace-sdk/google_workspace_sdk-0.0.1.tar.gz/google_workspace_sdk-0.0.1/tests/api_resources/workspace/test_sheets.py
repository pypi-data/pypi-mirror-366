# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from google_workspace_sdk import GoogleWorkspaceSDK, AsyncGoogleWorkspaceSDK
from google_workspace_sdk.types.workspace import SheetRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSheets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: GoogleWorkspaceSDK) -> None:
        sheet = client.workspace.sheets.create(
            session_id="sessionId",
            name="Budget 2024",
        )
        assert sheet is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: GoogleWorkspaceSDK) -> None:
        sheet = client.workspace.sheets.create(
            session_id="sessionId",
            name="Budget 2024",
            data=[["Name", "Amount"], ["Office Supplies", "500"], ["Software", "1200"]],
        )
        assert sheet is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.sheets.with_raw_response.create(
            session_id="sessionId",
            name="Budget 2024",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert sheet is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.sheets.with_streaming_response.create(
            session_id="sessionId",
            name="Budget 2024",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert sheet is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.sheets.with_raw_response.create(
                session_id="",
                name="Budget 2024",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        sheet = client.workspace.sheets.retrieve(
            sheet_id="sheetId",
            session_id="sessionId",
        )
        assert_matches_type(SheetRetrieveResponse, sheet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.sheets.with_raw_response.retrieve(
            sheet_id="sheetId",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert_matches_type(SheetRetrieveResponse, sheet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.sheets.with_streaming_response.retrieve(
            sheet_id="sheetId",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert_matches_type(SheetRetrieveResponse, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.sheets.with_raw_response.retrieve(
                sheet_id="sheetId",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.workspace.sheets.with_raw_response.retrieve(
                sheet_id="",
                session_id="sessionId",
            )


class TestAsyncSheets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        sheet = await async_client.workspace.sheets.create(
            session_id="sessionId",
            name="Budget 2024",
        )
        assert sheet is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        sheet = await async_client.workspace.sheets.create(
            session_id="sessionId",
            name="Budget 2024",
            data=[["Name", "Amount"], ["Office Supplies", "500"], ["Software", "1200"]],
        )
        assert sheet is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.sheets.with_raw_response.create(
            session_id="sessionId",
            name="Budget 2024",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert sheet is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.sheets.with_streaming_response.create(
            session_id="sessionId",
            name="Budget 2024",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert sheet is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.sheets.with_raw_response.create(
                session_id="",
                name="Budget 2024",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        sheet = await async_client.workspace.sheets.retrieve(
            sheet_id="sheetId",
            session_id="sessionId",
        )
        assert_matches_type(SheetRetrieveResponse, sheet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.sheets.with_raw_response.retrieve(
            sheet_id="sheetId",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert_matches_type(SheetRetrieveResponse, sheet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.sheets.with_streaming_response.retrieve(
            sheet_id="sheetId",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert_matches_type(SheetRetrieveResponse, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.sheets.with_raw_response.retrieve(
                sheet_id="sheetId",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.workspace.sheets.with_raw_response.retrieve(
                sheet_id="",
                session_id="sessionId",
            )
