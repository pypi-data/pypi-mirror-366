# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import (
    SimpleResp,
    AssetListResponse,
    AssetCreateResponse,
    AssetRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAsset:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.create(
            key="key=API_KEY",
        )
        assert_matches_type(AssetCreateResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.create(
            key="key=API_KEY",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            custom_id="custom_id",
            description="description",
            meta_data={},
            name="name",
            tags=["string"],
        )
        assert_matches_type(AssetCreateResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.create(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(AssetCreateResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.create(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(AssetCreateResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.retrieve(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.update(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.update(
            id="id",
            key="key=API_KEY",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            description="description",
            meta_data={},
            name="name",
            tags=["string"],
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.update(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.with_raw_response.update(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.list(
            key="key=API_KEY",
        )
        assert_matches_type(AssetListResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.list(
            key="key=API_KEY",
            cluster="america",
            include_all_of_attributes="include_all_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            include_any_of_attributes="include_any_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            pn=0,
            ps=100,
            sort="updated_at:desc",
            tags="tags=tag_1,tag_2",
        )
        assert_matches_type(AssetListResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(AssetListResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(AssetListResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_with_all_params(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.delete(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_bind(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_bind(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_bind(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_bind(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.with_raw_response.bind(
                id="",
                key="key=API_KEY",
                device_id="device_id",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_track(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
            },
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_track_with_all_params(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
                "accuracy": 0,
                "altitude": 0,
                "battery_level": 0,
                "bearing": 0,
                "meta_data": '{\n  "driver_name": "Tyler Durden",\n  "type": "parcel"\n}',
                "speed": 0,
                "tracking_mode": "tracking_mode",
            },
            cluster="america",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_track(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_track(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_track(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.with_raw_response.track(
                id="",
                key="key=API_KEY",
                device_id="device_id",
                locations={
                    "location": {
                        "lat": 0,
                        "lon": 0,
                    },
                    "timestamp": 0,
                },
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_attributes(self, client: NextbillionSDK) -> None:
        asset = client.skynet.asset.update_attributes(
            id="id",
            key="key=API_KEY",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_attributes(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.with_raw_response.update_attributes(
            id="id",
            key="key=API_KEY",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_attributes(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.with_streaming_response.update_attributes(
            id="id",
            key="key=API_KEY",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_attributes(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.with_raw_response.update_attributes(
                id="",
                key="key=API_KEY",
                attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            )


class TestAsyncAsset:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.create(
            key="key=API_KEY",
        )
        assert_matches_type(AssetCreateResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.create(
            key="key=API_KEY",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            custom_id="custom_id",
            description="description",
            meta_data={},
            name="name",
            tags=["string"],
        )
        assert_matches_type(AssetCreateResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.create(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AssetCreateResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.create(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AssetCreateResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.retrieve(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AssetRetrieveResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.update(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.update(
            id="id",
            key="key=API_KEY",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            description="description",
            meta_data={},
            name="name",
            tags=["string"],
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.update(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.with_raw_response.update(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.list(
            key="key=API_KEY",
        )
        assert_matches_type(AssetListResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.list(
            key="key=API_KEY",
            cluster="america",
            include_all_of_attributes="include_all_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            include_any_of_attributes="include_any_of_attributes=vehicle_type:pickup_truck|driver_name:John",
            pn=0,
            ps=100,
            sort="updated_at:desc",
            tags="tags=tag_1,tag_2",
        )
        assert_matches_type(AssetListResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AssetListResponse, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AssetListResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.delete(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_bind(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_bind(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_bind(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_bind(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.with_raw_response.bind(
                id="",
                key="key=API_KEY",
                device_id="device_id",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_track(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
            },
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_track_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
                "accuracy": 0,
                "altitude": 0,
                "battery_level": 0,
                "bearing": 0,
                "meta_data": '{\n  "driver_name": "Tyler Durden",\n  "type": "parcel"\n}',
                "speed": 0,
                "tracking_mode": "tracking_mode",
            },
            cluster="america",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_track(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_track(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.track(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
            locations={
                "location": {
                    "lat": 0,
                    "lon": 0,
                },
                "timestamp": 0,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_track(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.with_raw_response.track(
                id="",
                key="key=API_KEY",
                device_id="device_id",
                locations={
                    "location": {
                        "lat": 0,
                        "lon": 0,
                    },
                    "timestamp": 0,
                },
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_attributes(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.asset.update_attributes(
            id="id",
            key="key=API_KEY",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_attributes(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.with_raw_response.update_attributes(
            id="id",
            key="key=API_KEY",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_attributes(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.with_streaming_response.update_attributes(
            id="id",
            key="key=API_KEY",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_attributes(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.with_raw_response.update_attributes(
                id="",
                key="key=API_KEY",
                attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            )
