# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import SimpleResp
from nextbillionai.types.geofence import (
    BatchListResponse,
    BatchCreateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        batch = client.geofence.batch.create(
            key="key=API_KEY",
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        batch = client.geofence.batch.create(
            key="key=API_KEY",
            geofences=[
                {
                    "type": "circle",
                    "circle": {
                        "center": {
                            "lat": 0,
                            "lon": 0,
                        },
                        "radius": 0,
                    },
                    "custom_id": "custom_id",
                    "isochrone": {
                        "coordinates": '"coordinates": "13.25805884,77.91083661"',
                        "contours_meter": 0,
                        "contours_minute": 0,
                        "denoise": 0,
                        "departure_time": 0,
                        "mode": "car",
                    },
                    "meta_data": '{\n  "country": "USA",\n  "state": "California"\n}',
                    "name": '"name":"Los Angeles Downtown"',
                    "polygon": {
                        "geojson": {
                            "coordinates": [[0]],
                            "type": "type",
                        }
                    },
                    "tags": ['"tags":["tags_1", "O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7"]'],
                }
            ],
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.geofence.batch.with_raw_response.create(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.geofence.batch.with_streaming_response.create(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(BatchCreateResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        batch = client.geofence.batch.list(
            ids="ids",
            key="key=API_KEY",
        )
        assert_matches_type(BatchListResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.geofence.batch.with_raw_response.list(
            ids="ids",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(BatchListResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.geofence.batch.with_streaming_response.list(
            ids="ids",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(BatchListResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        batch = client.geofence.batch.delete(
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_with_all_params(self, client: NextbillionSDK) -> None:
        batch = client.geofence.batch.delete(
            key="key=API_KEY",
            ids=["string"],
        )
        assert_matches_type(SimpleResp, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.geofence.batch.with_raw_response.delete(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(SimpleResp, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.geofence.batch.with_streaming_response.delete(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(SimpleResp, batch, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBatch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        batch = await async_client.geofence.batch.create(
            key="key=API_KEY",
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        batch = await async_client.geofence.batch.create(
            key="key=API_KEY",
            geofences=[
                {
                    "type": "circle",
                    "circle": {
                        "center": {
                            "lat": 0,
                            "lon": 0,
                        },
                        "radius": 0,
                    },
                    "custom_id": "custom_id",
                    "isochrone": {
                        "coordinates": '"coordinates": "13.25805884,77.91083661"',
                        "contours_meter": 0,
                        "contours_minute": 0,
                        "denoise": 0,
                        "departure_time": 0,
                        "mode": "car",
                    },
                    "meta_data": '{\n  "country": "USA",\n  "state": "California"\n}',
                    "name": '"name":"Los Angeles Downtown"',
                    "polygon": {
                        "geojson": {
                            "coordinates": [[0]],
                            "type": "type",
                        }
                    },
                    "tags": ['"tags":["tags_1", "O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7"]'],
                }
            ],
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.batch.with_raw_response.create(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.batch.with_streaming_response.create(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(BatchCreateResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        batch = await async_client.geofence.batch.list(
            ids="ids",
            key="key=API_KEY",
        )
        assert_matches_type(BatchListResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.batch.with_raw_response.list(
            ids="ids",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(BatchListResponse, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.batch.with_streaming_response.list(
            ids="ids",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(BatchListResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        batch = await async_client.geofence.batch.delete(
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        batch = await async_client.geofence.batch.delete(
            key="key=API_KEY",
            ids=["string"],
        )
        assert_matches_type(SimpleResp, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.batch.with_raw_response.delete(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(SimpleResp, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.batch.with_streaming_response.delete(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(SimpleResp, batch, path=["response"])

        assert cast(Any, response.is_closed) is True
