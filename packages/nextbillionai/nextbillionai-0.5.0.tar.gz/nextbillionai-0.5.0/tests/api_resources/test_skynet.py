# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import SkynetSubscribeResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSkynet:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_subscribe(self, client: NextbillionSDK) -> None:
        skynet = client.skynet.subscribe(
            action="TRIP_SUBSCRIBE",
        )
        assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_subscribe_with_all_params(self, client: NextbillionSDK) -> None:
        skynet = client.skynet.subscribe(
            action="TRIP_SUBSCRIBE",
            id="id",
            params={"id": "id"},
        )
        assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_subscribe(self, client: NextbillionSDK) -> None:
        response = client.skynet.with_raw_response.subscribe(
            action="TRIP_SUBSCRIBE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        skynet = response.parse()
        assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_subscribe(self, client: NextbillionSDK) -> None:
        with client.skynet.with_streaming_response.subscribe(
            action="TRIP_SUBSCRIBE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            skynet = response.parse()
            assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSkynet:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_subscribe(self, async_client: AsyncNextbillionSDK) -> None:
        skynet = await async_client.skynet.subscribe(
            action="TRIP_SUBSCRIBE",
        )
        assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_subscribe_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        skynet = await async_client.skynet.subscribe(
            action="TRIP_SUBSCRIBE",
            id="id",
            params={"id": "id"},
        )
        assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_subscribe(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.with_raw_response.subscribe(
            action="TRIP_SUBSCRIBE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        skynet = await response.parse()
        assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_subscribe(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.with_streaming_response.subscribe(
            action="TRIP_SUBSCRIBE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            skynet = await response.parse()
            assert_matches_type(SkynetSubscribeResponse, skynet, path=["response"])

        assert cast(Any, response.is_closed) is True
