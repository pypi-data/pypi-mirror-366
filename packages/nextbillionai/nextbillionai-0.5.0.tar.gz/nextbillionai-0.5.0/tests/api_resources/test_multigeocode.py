# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import MultigeocodeSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMultigeocode:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: NextbillionSDK) -> None:
        multigeocode = client.multigeocode.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
        )
        assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_with_all_params(self, client: NextbillionSDK) -> None:
        multigeocode = client.multigeocode.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
            city="“city”: “Glendale”",
            country="“country”:”IND”",
            district="“district”: “City Center”",
            limit=0,
            radius="“radius”: “10m”",
            state="“state”: “California”",
            street="“street”: “Americana Way”",
            sub_district="“subDistrict”: “Golkonda”",
        )
        assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: NextbillionSDK) -> None:
        response = client.multigeocode.with_raw_response.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        multigeocode = response.parse()
        assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: NextbillionSDK) -> None:
        with client.multigeocode.with_streaming_response.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            multigeocode = response.parse()
            assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMultigeocode:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncNextbillionSDK) -> None:
        multigeocode = await async_client.multigeocode.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
        )
        assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        multigeocode = await async_client.multigeocode.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
            city="“city”: “Glendale”",
            country="“country”:”IND”",
            district="“district”: “City Center”",
            limit=0,
            radius="“radius”: “10m”",
            state="“state”: “California”",
            street="“street”: “Americana Way”",
            sub_district="“subDistrict”: “Golkonda”",
        )
        assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.multigeocode.with_raw_response.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        multigeocode = await response.parse()
        assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.multigeocode.with_streaming_response.search(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            query="“query”: “Taj Mahal”",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            multigeocode = await response.parse()
            assert_matches_type(MultigeocodeSearchResponse, multigeocode, path=["response"])

        assert cast(Any, response.is_closed) is True
