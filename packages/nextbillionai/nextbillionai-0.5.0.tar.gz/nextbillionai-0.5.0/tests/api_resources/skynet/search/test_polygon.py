# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import SearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPolygon:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        polygon = client.skynet.search.polygon.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        polygon = client.skynet.search.polygon.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
            filter='"tag:delivery,truck"',
            match_filter={
                "include_all_of_attributes": '"shift_timing": "0800-1700","driver_name": "John"',
                "include_any_of_attributes": "include_any_of_attributes",
            },
            max_search_limit=True,
            pn=0,
            ps=0,
            sort={
                "sort_by": "distance",
                "sort_destination": {
                    "lat": 0,
                    "lon": 0,
                },
                "sort_driving_mode": "car",
            },
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.skynet.search.polygon.with_raw_response.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        polygon = response.parse()
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.skynet.search.polygon.with_streaming_response.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            polygon = response.parse()
            assert_matches_type(SearchResponse, polygon, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: NextbillionSDK) -> None:
        polygon = client.skynet.search.polygon.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_with_all_params(self, client: NextbillionSDK) -> None:
        polygon = client.skynet.search.polygon.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
            filter="filter=tag:delivery,truck",
            include_all_of_attributes="include_all_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            include_any_of_attributes="include_any_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            max_search_limit=True,
            pn=0,
            ps=100,
            sort_by="distance",
            sort_destination="sort_destination= 34.0241,-118.2550",
            sort_driving_mode="car",
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: NextbillionSDK) -> None:
        response = client.skynet.search.polygon.with_raw_response.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        polygon = response.parse()
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: NextbillionSDK) -> None:
        with client.skynet.search.polygon.with_streaming_response.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            polygon = response.parse()
            assert_matches_type(SearchResponse, polygon, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPolygon:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        polygon = await async_client.skynet.search.polygon.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        polygon = await async_client.skynet.search.polygon.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
            filter='"tag:delivery,truck"',
            match_filter={
                "include_all_of_attributes": '"shift_timing": "0800-1700","driver_name": "John"',
                "include_any_of_attributes": "include_any_of_attributes",
            },
            max_search_limit=True,
            pn=0,
            ps=0,
            sort={
                "sort_by": "distance",
                "sort_destination": {
                    "lat": 0,
                    "lon": 0,
                },
                "sort_driving_mode": "car",
            },
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.search.polygon.with_raw_response.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        polygon = await response.parse()
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.search.polygon.with_streaming_response.create(
            key="key=API_KEY",
            polygon={
                "coordinates": [0],
                "type": "type",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            polygon = await response.parse()
            assert_matches_type(SearchResponse, polygon, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncNextbillionSDK) -> None:
        polygon = await async_client.skynet.search.polygon.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        polygon = await async_client.skynet.search.polygon.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
            filter="filter=tag:delivery,truck",
            include_all_of_attributes="include_all_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            include_any_of_attributes="include_any_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            max_search_limit=True,
            pn=0,
            ps=100,
            sort_by="distance",
            sort_destination="sort_destination= 34.0241,-118.2550",
            sort_driving_mode="car",
        )
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.search.polygon.with_raw_response.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        polygon = await response.parse()
        assert_matches_type(SearchResponse, polygon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.search.polygon.with_streaming_response.get(
            key="key=API_KEY",
            polygon="polygon=17.4239,78.4590|17.4575,78.4624|17.4547,78.5483|17.4076,78.5527|17.4239,78.4590",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            polygon = await response.parse()
            assert_matches_type(SearchResponse, polygon, path=["response"])

        assert cast(Any, response.is_closed) is True
