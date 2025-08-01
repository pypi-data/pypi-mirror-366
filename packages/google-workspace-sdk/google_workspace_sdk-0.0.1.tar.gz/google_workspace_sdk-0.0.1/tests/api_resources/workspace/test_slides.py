# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from google_workspace_sdk import GoogleWorkspaceSDK, AsyncGoogleWorkspaceSDK
from google_workspace_sdk.types.workspace import SlideRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSlides:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: GoogleWorkspaceSDK) -> None:
        slide = client.workspace.slides.create(
            session_id="sessionId",
            name="Q4 Review",
        )
        assert slide is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: GoogleWorkspaceSDK) -> None:
        slide = client.workspace.slides.create(
            session_id="sessionId",
            name="Q4 Review",
            content="Welcome to Q4 Review",
        )
        assert slide is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.slides.with_raw_response.create(
            session_id="sessionId",
            name="Q4 Review",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        slide = response.parse()
        assert slide is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.slides.with_streaming_response.create(
            session_id="sessionId",
            name="Q4 Review",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            slide = response.parse()
            assert slide is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.slides.with_raw_response.create(
                session_id="",
                name="Q4 Review",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        slide = client.workspace.slides.retrieve(
            slides_id="slidesId",
            session_id="sessionId",
        )
        assert_matches_type(SlideRetrieveResponse, slide, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.slides.with_raw_response.retrieve(
            slides_id="slidesId",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        slide = response.parse()
        assert_matches_type(SlideRetrieveResponse, slide, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.slides.with_streaming_response.retrieve(
            slides_id="slidesId",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            slide = response.parse()
            assert_matches_type(SlideRetrieveResponse, slide, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.slides.with_raw_response.retrieve(
                slides_id="slidesId",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slides_id` but received ''"):
            client.workspace.slides.with_raw_response.retrieve(
                slides_id="",
                session_id="sessionId",
            )


class TestAsyncSlides:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        slide = await async_client.workspace.slides.create(
            session_id="sessionId",
            name="Q4 Review",
        )
        assert slide is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        slide = await async_client.workspace.slides.create(
            session_id="sessionId",
            name="Q4 Review",
            content="Welcome to Q4 Review",
        )
        assert slide is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.slides.with_raw_response.create(
            session_id="sessionId",
            name="Q4 Review",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        slide = await response.parse()
        assert slide is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.slides.with_streaming_response.create(
            session_id="sessionId",
            name="Q4 Review",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            slide = await response.parse()
            assert slide is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.slides.with_raw_response.create(
                session_id="",
                name="Q4 Review",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        slide = await async_client.workspace.slides.retrieve(
            slides_id="slidesId",
            session_id="sessionId",
        )
        assert_matches_type(SlideRetrieveResponse, slide, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.slides.with_raw_response.retrieve(
            slides_id="slidesId",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        slide = await response.parse()
        assert_matches_type(SlideRetrieveResponse, slide, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.slides.with_streaming_response.retrieve(
            slides_id="slidesId",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            slide = await response.parse()
            assert_matches_type(SlideRetrieveResponse, slide, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.slides.with_raw_response.retrieve(
                slides_id="slidesId",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slides_id` but received ''"):
            await async_client.workspace.slides.with_raw_response.retrieve(
                slides_id="",
                session_id="sessionId",
            )
