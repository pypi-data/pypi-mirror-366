# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import (
    NamespacedApikeyCreateResponse,
    NamespacedApikeyDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNamespacedApikeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        namespaced_apikey = client.skynet.namespaced_apikeys.create(
            key="key=API_KEY",
            namespace="namespace=test_name",
        )
        assert_matches_type(NamespacedApikeyCreateResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.skynet.namespaced_apikeys.with_raw_response.create(
            key="key=API_KEY",
            namespace="namespace=test_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        namespaced_apikey = response.parse()
        assert_matches_type(NamespacedApikeyCreateResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.skynet.namespaced_apikeys.with_streaming_response.create(
            key="key=API_KEY",
            namespace="namespace=test_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            namespaced_apikey = response.parse()
            assert_matches_type(NamespacedApikeyCreateResponse, namespaced_apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        namespaced_apikey = client.skynet.namespaced_apikeys.delete(
            key="key=API_KEY",
            key_to_delete="key_to_delete",
            namespace="namespace",
        )
        assert_matches_type(NamespacedApikeyDeleteResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.skynet.namespaced_apikeys.with_raw_response.delete(
            key="key=API_KEY",
            key_to_delete="key_to_delete",
            namespace="namespace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        namespaced_apikey = response.parse()
        assert_matches_type(NamespacedApikeyDeleteResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.skynet.namespaced_apikeys.with_streaming_response.delete(
            key="key=API_KEY",
            key_to_delete="key_to_delete",
            namespace="namespace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            namespaced_apikey = response.parse()
            assert_matches_type(NamespacedApikeyDeleteResponse, namespaced_apikey, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNamespacedApikeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        namespaced_apikey = await async_client.skynet.namespaced_apikeys.create(
            key="key=API_KEY",
            namespace="namespace=test_name",
        )
        assert_matches_type(NamespacedApikeyCreateResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.namespaced_apikeys.with_raw_response.create(
            key="key=API_KEY",
            namespace="namespace=test_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        namespaced_apikey = await response.parse()
        assert_matches_type(NamespacedApikeyCreateResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.namespaced_apikeys.with_streaming_response.create(
            key="key=API_KEY",
            namespace="namespace=test_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            namespaced_apikey = await response.parse()
            assert_matches_type(NamespacedApikeyCreateResponse, namespaced_apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        namespaced_apikey = await async_client.skynet.namespaced_apikeys.delete(
            key="key=API_KEY",
            key_to_delete="key_to_delete",
            namespace="namespace",
        )
        assert_matches_type(NamespacedApikeyDeleteResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.namespaced_apikeys.with_raw_response.delete(
            key="key=API_KEY",
            key_to_delete="key_to_delete",
            namespace="namespace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        namespaced_apikey = await response.parse()
        assert_matches_type(NamespacedApikeyDeleteResponse, namespaced_apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.namespaced_apikeys.with_streaming_response.delete(
            key="key=API_KEY",
            key_to_delete="key_to_delete",
            namespace="namespace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            namespaced_apikey = await response.parse()
            assert_matches_type(NamespacedApikeyDeleteResponse, namespaced_apikey, path=["response"])

        assert cast(Any, response.is_closed) is True
