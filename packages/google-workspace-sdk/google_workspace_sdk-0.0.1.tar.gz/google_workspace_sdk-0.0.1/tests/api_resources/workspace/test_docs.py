# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from google_workspace_sdk import GoogleWorkspaceSDK, AsyncGoogleWorkspaceSDK
from google_workspace_sdk.types.workspace import DocRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: GoogleWorkspaceSDK) -> None:
        doc = client.workspace.docs.create(
            session_id="sessionId",
            name="Meeting Notes",
        )
        assert doc is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: GoogleWorkspaceSDK) -> None:
        doc = client.workspace.docs.create(
            session_id="sessionId",
            name="Meeting Notes",
            content="# Meeting Notes\n\nDiscussion points...",
        )
        assert doc is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.docs.with_raw_response.create(
            session_id="sessionId",
            name="Meeting Notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert doc is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.docs.with_streaming_response.create(
            session_id="sessionId",
            name="Meeting Notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.docs.with_raw_response.create(
                session_id="",
                name="Meeting Notes",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        doc = client.workspace.docs.retrieve(
            doc_id="docId",
            session_id="sessionId",
        )
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        response = client.workspace.docs.with_raw_response.retrieve(
            doc_id="docId",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with client.workspace.docs.with_streaming_response.retrieve(
            doc_id="docId",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert_matches_type(DocRetrieveResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: GoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.workspace.docs.with_raw_response.retrieve(
                doc_id="docId",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.workspace.docs.with_raw_response.retrieve(
                doc_id="",
                session_id="sessionId",
            )


class TestAsyncDocs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        doc = await async_client.workspace.docs.create(
            session_id="sessionId",
            name="Meeting Notes",
        )
        assert doc is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        doc = await async_client.workspace.docs.create(
            session_id="sessionId",
            name="Meeting Notes",
            content="# Meeting Notes\n\nDiscussion points...",
        )
        assert doc is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.docs.with_raw_response.create(
            session_id="sessionId",
            name="Meeting Notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert doc is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.docs.with_streaming_response.create(
            session_id="sessionId",
            name="Meeting Notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.docs.with_raw_response.create(
                session_id="",
                name="Meeting Notes",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        doc = await async_client.workspace.docs.retrieve(
            doc_id="docId",
            session_id="sessionId",
        )
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        response = await async_client.workspace.docs.with_raw_response.retrieve(
            doc_id="docId",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        async with async_client.workspace.docs.with_streaming_response.retrieve(
            doc_id="docId",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert_matches_type(DocRetrieveResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGoogleWorkspaceSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.workspace.docs.with_raw_response.retrieve(
                doc_id="docId",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.workspace.docs.with_raw_response.retrieve(
                doc_id="",
                session_id="sessionId",
            )
