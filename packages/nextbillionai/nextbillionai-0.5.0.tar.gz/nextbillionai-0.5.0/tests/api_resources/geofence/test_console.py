# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.geofence import (
    ConsoleSearchResponse,
    ConsolePreviewResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConsole:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_preview(self, client: NextbillionSDK) -> None:
        console = client.geofence.console.preview(
            type="circle",
        )
        assert_matches_type(ConsolePreviewResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_preview_with_all_params(self, client: NextbillionSDK) -> None:
        console = client.geofence.console.preview(
            type="circle",
            circle={
                "center": {
                    "lat": 0,
                    "lon": 0,
                },
                "radius": 0,
            },
            custom_id="custom_id",
            isochrone={
                "coordinates": '"coordinates": "13.25805884,77.91083661"',
                "contours_meter": 0,
                "contours_minute": 0,
                "denoise": 0,
                "departure_time": 0,
                "mode": "car",
            },
            meta_data='{\n  "country": "USA",\n  "state": "California"\n}',
            name='"name":"Los Angeles Downtown"',
            polygon={
                "geojson": {
                    "coordinates": [[0]],
                    "type": "type",
                }
            },
            tags=['"tags":["tags_1", "O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7"]'],
        )
        assert_matches_type(ConsolePreviewResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_preview(self, client: NextbillionSDK) -> None:
        response = client.geofence.console.with_raw_response.preview(
            type="circle",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        console = response.parse()
        assert_matches_type(ConsolePreviewResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_preview(self, client: NextbillionSDK) -> None:
        with client.geofence.console.with_streaming_response.preview(
            type="circle",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            console = response.parse()
            assert_matches_type(ConsolePreviewResponse, console, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: NextbillionSDK) -> None:
        console = client.geofence.console.search(
            query="query",
        )
        assert_matches_type(ConsoleSearchResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: NextbillionSDK) -> None:
        response = client.geofence.console.with_raw_response.search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        console = response.parse()
        assert_matches_type(ConsoleSearchResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: NextbillionSDK) -> None:
        with client.geofence.console.with_streaming_response.search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            console = response.parse()
            assert_matches_type(ConsoleSearchResponse, console, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConsole:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_preview(self, async_client: AsyncNextbillionSDK) -> None:
        console = await async_client.geofence.console.preview(
            type="circle",
        )
        assert_matches_type(ConsolePreviewResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_preview_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        console = await async_client.geofence.console.preview(
            type="circle",
            circle={
                "center": {
                    "lat": 0,
                    "lon": 0,
                },
                "radius": 0,
            },
            custom_id="custom_id",
            isochrone={
                "coordinates": '"coordinates": "13.25805884,77.91083661"',
                "contours_meter": 0,
                "contours_minute": 0,
                "denoise": 0,
                "departure_time": 0,
                "mode": "car",
            },
            meta_data='{\n  "country": "USA",\n  "state": "California"\n}',
            name='"name":"Los Angeles Downtown"',
            polygon={
                "geojson": {
                    "coordinates": [[0]],
                    "type": "type",
                }
            },
            tags=['"tags":["tags_1", "O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7"]'],
        )
        assert_matches_type(ConsolePreviewResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_preview(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.console.with_raw_response.preview(
            type="circle",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        console = await response.parse()
        assert_matches_type(ConsolePreviewResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_preview(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.console.with_streaming_response.preview(
            type="circle",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            console = await response.parse()
            assert_matches_type(ConsolePreviewResponse, console, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncNextbillionSDK) -> None:
        console = await async_client.geofence.console.search(
            query="query",
        )
        assert_matches_type(ConsoleSearchResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.console.with_raw_response.search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        console = await response.parse()
        assert_matches_type(ConsoleSearchResponse, console, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.console.with_streaming_response.search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            console = await response.parse()
            assert_matches_type(ConsoleSearchResponse, console, path=["response"])

        assert cast(Any, response.is_closed) is True
