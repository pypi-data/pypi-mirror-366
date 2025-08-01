# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import IsochroneComputeResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIsochrone:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_compute(self, client: NextbillionSDK) -> None:
        isochrone = client.isochrone.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
        )
        assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_compute_with_all_params(self, client: NextbillionSDK) -> None:
        isochrone = client.isochrone.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
            contours_colors="contours_colors=ff0000,bf4040",
            denoise=0,
            departure_time=0,
            generalize=0,
            mode="car",
            polygons=True,
        )
        assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_compute(self, client: NextbillionSDK) -> None:
        response = client.isochrone.with_raw_response.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        isochrone = response.parse()
        assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_compute(self, client: NextbillionSDK) -> None:
        with client.isochrone.with_streaming_response.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            isochrone = response.parse()
            assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncIsochrone:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_compute(self, async_client: AsyncNextbillionSDK) -> None:
        isochrone = await async_client.isochrone.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
        )
        assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_compute_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        isochrone = await async_client.isochrone.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
            contours_colors="contours_colors=ff0000,bf4040",
            denoise=0,
            departure_time=0,
            generalize=0,
            mode="car",
            polygons=True,
        )
        assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_compute(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.isochrone.with_raw_response.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        isochrone = await response.parse()
        assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_compute(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.isochrone.with_streaming_response.compute(
            contours_meters=0,
            contours_minutes=0,
            coordinates="coordinates=1.29363713,103.8383112",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            isochrone = await response.parse()
            assert_matches_type(IsochroneComputeResponse, isochrone, path=["response"])

        assert cast(Any, response.is_closed) is True
