# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import RestrictionsItemListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRestrictionsItems:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        restrictions_item = client.restrictions_items.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )
        assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        restrictions_item = client.restrictions_items.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
            group_id=0,
            mode="0w",
            restriction_type="turn",
            source="source",
            state="enabled",
            status="active",
        )
        assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.restrictions_items.with_raw_response.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restrictions_item = response.parse()
        assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.restrictions_items.with_streaming_response.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restrictions_item = response.parse()
            assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRestrictionsItems:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        restrictions_item = await async_client.restrictions_items.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )
        assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        restrictions_item = await async_client.restrictions_items.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
            group_id=0,
            mode="0w",
            restriction_type="turn",
            source="source",
            state="enabled",
            status="active",
        )
        assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions_items.with_raw_response.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restrictions_item = await response.parse()
        assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions_items.with_streaming_response.list(
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restrictions_item = await response.parse()
            assert_matches_type(RestrictionsItemListResponse, restrictions_item, path=["response"])

        assert cast(Any, response.is_closed) is True
