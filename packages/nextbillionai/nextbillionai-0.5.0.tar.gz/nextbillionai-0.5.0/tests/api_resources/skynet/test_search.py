# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import SearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSearch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_around(self, client: NextbillionSDK) -> None:
        search = client.skynet.search.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_around_with_all_params(self, client: NextbillionSDK) -> None:
        search = client.skynet.search.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
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
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_around(self, client: NextbillionSDK) -> None:
        response = client.skynet.search.with_raw_response.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_around(self, client: NextbillionSDK) -> None:
        with client.skynet.search.with_streaming_response.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_bound(self, client: NextbillionSDK) -> None:
        search = client.skynet.search.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_bound_with_all_params(self, client: NextbillionSDK) -> None:
        search = client.skynet.search.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
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
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_bound(self, client: NextbillionSDK) -> None:
        response = client.skynet.search.with_raw_response.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_bound(self, client: NextbillionSDK) -> None:
        with client.skynet.search.with_streaming_response.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSearch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_around(self, async_client: AsyncNextbillionSDK) -> None:
        search = await async_client.skynet.search.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_around_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        search = await async_client.skynet.search.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
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
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_around(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.search.with_raw_response.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = await response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_around(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.search.with_streaming_response.around(
            center="56.597801,43.967836",
            key="key=API_KEY",
            radius=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = await response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_bound(self, async_client: AsyncNextbillionSDK) -> None:
        search = await async_client.skynet.search.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_bound_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        search = await async_client.skynet.search.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
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
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_bound(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.search.with_raw_response.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = await response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_bound(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.search.with_streaming_response.bound(
            bound="bounds=44.7664,-0.6941|44.9206,-0.4639",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = await response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True
