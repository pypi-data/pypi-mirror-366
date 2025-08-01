# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from nextbillionai import NextbillionSDK, AsyncNextbillionSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMap:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_segment(self, client: NextbillionSDK) -> None:
        map = client.map.create_segment()
        assert map is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_segment(self, client: NextbillionSDK) -> None:
        response = client.map.with_raw_response.create_segment()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        map = response.parse()
        assert map is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_segment(self, client: NextbillionSDK) -> None:
        with client.map.with_streaming_response.create_segment() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            map = response.parse()
            assert map is None

        assert cast(Any, response.is_closed) is True


class TestAsyncMap:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_segment(self, async_client: AsyncNextbillionSDK) -> None:
        map = await async_client.map.create_segment()
        assert map is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_segment(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.map.with_raw_response.create_segment()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        map = await response.parse()
        assert map is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_segment(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.map.with_streaming_response.create_segment() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            map = await response.parse()
            assert map is None

        assert cast(Any, response.is_closed) is True
