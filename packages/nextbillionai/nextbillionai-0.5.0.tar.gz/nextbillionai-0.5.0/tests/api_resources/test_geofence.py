# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import (
    GeofenceListResponse,
    GeofenceCreateResponse,
    GeofenceContainsResponse,
    GeofenceRetrieveResponse,
)
from nextbillionai.types.skynet import SimpleResp

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGeofence:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.create(
            key="key=API_KEY",
            type="circle",
        )
        assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.create(
            key="key=API_KEY",
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
        assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.geofence.with_raw_response.create(
            key="key=API_KEY",
            type="circle",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = response.parse()
        assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.geofence.with_streaming_response.create(
            key="key=API_KEY",
            type="circle",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = response.parse()
            assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(GeofenceRetrieveResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.geofence.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = response.parse()
        assert_matches_type(GeofenceRetrieveResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.geofence.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = response.parse()
            assert_matches_type(GeofenceRetrieveResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.geofence.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.update(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.update(
            id="id",
            key="key=API_KEY",
            circle={
                "center": {
                    "lat": 0,
                    "lon": 0,
                },
                "radius": 0,
            },
            isochrone={
                "contours_meter": 0,
                "contours_minute": 0,
                "coordinates": '"coordinates": "13.25805884388484,77.91083661048299"',
                "denoise": 0,
                "departure_time": 0,
                "mode": "“mode”:”car”",
            },
            meta_data="",
            name='"name":"Los Angeles Downtown"',
            polygon={
                "geojson": {
                    "geometry": [[0]],
                    "type": "type",
                }
            },
            tags=['"tags":["tags_1", "O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7"]'],
            type="circle",
        )
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.geofence.with_raw_response.update(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = response.parse()
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.geofence.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = response.parse()
            assert_matches_type(SimpleResp, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.geofence.with_raw_response.update(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.list(
            key="key=API_KEY",
        )
        assert_matches_type(GeofenceListResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.list(
            key="key=API_KEY",
            pn=0,
            ps=100,
            tags="tags=tags_1,O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7",
        )
        assert_matches_type(GeofenceListResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.geofence.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = response.parse()
        assert_matches_type(GeofenceListResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.geofence.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = response.parse()
            assert_matches_type(GeofenceListResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.geofence.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = response.parse()
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.geofence.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = response.parse()
            assert_matches_type(SimpleResp, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.geofence.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_contains(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
        )
        assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_contains_with_all_params(self, client: NextbillionSDK) -> None:
        geofence = client.geofence.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
            geofences="geofences=80d1fa55-6287-4da0-93ac-2fc162d0a228,70d1fa55-1287-4da0-93ac-2fc162d0a228",
            verbose="verbose=true",
        )
        assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_contains(self, client: NextbillionSDK) -> None:
        response = client.geofence.with_raw_response.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = response.parse()
        assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_contains(self, client: NextbillionSDK) -> None:
        with client.geofence.with_streaming_response.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = response.parse()
            assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGeofence:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.create(
            key="key=API_KEY",
            type="circle",
        )
        assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.create(
            key="key=API_KEY",
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
        assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.with_raw_response.create(
            key="key=API_KEY",
            type="circle",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = await response.parse()
        assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.with_streaming_response.create(
            key="key=API_KEY",
            type="circle",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = await response.parse()
            assert_matches_type(GeofenceCreateResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(GeofenceRetrieveResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = await response.parse()
        assert_matches_type(GeofenceRetrieveResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = await response.parse()
            assert_matches_type(GeofenceRetrieveResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.geofence.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.update(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.update(
            id="id",
            key="key=API_KEY",
            circle={
                "center": {
                    "lat": 0,
                    "lon": 0,
                },
                "radius": 0,
            },
            isochrone={
                "contours_meter": 0,
                "contours_minute": 0,
                "coordinates": '"coordinates": "13.25805884388484,77.91083661048299"',
                "denoise": 0,
                "departure_time": 0,
                "mode": "“mode”:”car”",
            },
            meta_data="",
            name='"name":"Los Angeles Downtown"',
            polygon={
                "geojson": {
                    "geometry": [[0]],
                    "type": "type",
                }
            },
            tags=['"tags":["tags_1", "O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7"]'],
            type="circle",
        )
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.with_raw_response.update(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = await response.parse()
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = await response.parse()
            assert_matches_type(SimpleResp, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.geofence.with_raw_response.update(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.list(
            key="key=API_KEY",
        )
        assert_matches_type(GeofenceListResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.list(
            key="key=API_KEY",
            pn=0,
            ps=100,
            tags="tags=tags_1,O69Am2Y4KL8q5Y5JuD-Fy-tdtEpkTRQo_ZYIK7",
        )
        assert_matches_type(GeofenceListResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = await response.parse()
        assert_matches_type(GeofenceListResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = await response.parse()
            assert_matches_type(GeofenceListResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = await response.parse()
        assert_matches_type(SimpleResp, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = await response.parse()
            assert_matches_type(SimpleResp, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.geofence.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_contains(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
        )
        assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_contains_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        geofence = await async_client.geofence.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
            geofences="geofences=80d1fa55-6287-4da0-93ac-2fc162d0a228,70d1fa55-1287-4da0-93ac-2fc162d0a228",
            verbose="verbose=true",
        )
        assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_contains(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geofence.with_raw_response.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geofence = await response.parse()
        assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_contains(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geofence.with_streaming_response.contains(
            key="key=API_KEY",
            locations="13.25805884388484,77.91083661048299|13.25805884388484,77.91083661048299",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geofence = await response.parse()
            assert_matches_type(GeofenceContainsResponse, geofence, path=["response"])

        assert cast(Any, response.is_closed) is True
