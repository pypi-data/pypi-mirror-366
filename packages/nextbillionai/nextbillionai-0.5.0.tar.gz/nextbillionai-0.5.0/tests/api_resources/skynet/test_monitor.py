# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import (
    SimpleResp,
    MonitorListResponse,
    MonitorCreateResponse,
    MonitorRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMonitor:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
        )
        assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
            cluster="america",
            custom_id="custom_id",
            description="description",
            geofence_config={"geofence_ids": ["string"]},
            geofence_ids=["string"],
            idle_config={
                "distance_tolerance": 0,
                "time_tolerance": 0,
            },
            match_filter={
                "include_all_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
                "include_any_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
            },
            meta_data={},
            name="name",
            speeding_config={
                "customer_speed_limit": 0,
                "time_tolerance": 0,
                "use_admin_speed_limit": True,
            },
        )
        assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.skynet.monitor.with_raw_response.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = response.parse()
        assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.skynet.monitor.with_streaming_response.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = response.parse()
            assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(MonitorRetrieveResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.skynet.monitor.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = response.parse()
        assert_matches_type(MonitorRetrieveResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.skynet.monitor.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = response.parse()
            assert_matches_type(MonitorRetrieveResponse, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.monitor.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.update(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.update(
            id="id",
            key="key=API_KEY",
            description="description",
            geofence_config={"geofence_ids": ["string"]},
            geofence_ids=["string"],
            idle_config={
                "distance_tolerance": 0,
                "time_tolerance": 0,
            },
            match_filter={
                "include_all_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
                "include_any_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
            },
            meta_data={},
            name='"name":"warehouse_exit"',
            speeding_config={
                "customer_speed_limit": '"customer_speed_limit":8',
                "time_tolerance": 0,
                "use_admin_speed_limit": True,
            },
            tags=["string"],
            type="enter",
        )
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.skynet.monitor.with_raw_response.update(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = response.parse()
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.skynet.monitor.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = response.parse()
            assert_matches_type(SimpleResp, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.monitor.with_raw_response.update(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.list(
            key="key=API_KEY",
        )
        assert_matches_type(MonitorListResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.list(
            key="key=API_KEY",
            cluster="america",
            pn=0,
            ps=100,
            sort="updated_at:desc",
            tags="tags=tag_1,tag_2",
        )
        assert_matches_type(MonitorListResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.skynet.monitor.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = response.parse()
        assert_matches_type(MonitorListResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.skynet.monitor.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = response.parse()
            assert_matches_type(MonitorListResponse, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        monitor = client.skynet.monitor.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.skynet.monitor.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = response.parse()
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.skynet.monitor.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = response.parse()
            assert_matches_type(SimpleResp, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.monitor.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )


class TestAsyncMonitor:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
        )
        assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
            cluster="america",
            custom_id="custom_id",
            description="description",
            geofence_config={"geofence_ids": ["string"]},
            geofence_ids=["string"],
            idle_config={
                "distance_tolerance": 0,
                "time_tolerance": 0,
            },
            match_filter={
                "include_all_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
                "include_any_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
            },
            meta_data={},
            name="name",
            speeding_config={
                "customer_speed_limit": 0,
                "time_tolerance": 0,
                "use_admin_speed_limit": True,
            },
        )
        assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.monitor.with_raw_response.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = await response.parse()
        assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.monitor.with_streaming_response.create(
            key="key=API_KEY",
            tags=["string"],
            type="enter",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = await response.parse()
            assert_matches_type(MonitorCreateResponse, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(MonitorRetrieveResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.monitor.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = await response.parse()
        assert_matches_type(MonitorRetrieveResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.monitor.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = await response.parse()
            assert_matches_type(MonitorRetrieveResponse, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.monitor.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.update(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.update(
            id="id",
            key="key=API_KEY",
            description="description",
            geofence_config={"geofence_ids": ["string"]},
            geofence_ids=["string"],
            idle_config={
                "distance_tolerance": 0,
                "time_tolerance": 0,
            },
            match_filter={
                "include_all_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
                "include_any_of_attributes": '{\n  "asset_type": "delivery",\n  "area": "Los Angeles downtown"\n}',
            },
            meta_data={},
            name='"name":"warehouse_exit"',
            speeding_config={
                "customer_speed_limit": '"customer_speed_limit":8',
                "time_tolerance": 0,
                "use_admin_speed_limit": True,
            },
            tags=["string"],
            type="enter",
        )
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.monitor.with_raw_response.update(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = await response.parse()
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.monitor.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = await response.parse()
            assert_matches_type(SimpleResp, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.monitor.with_raw_response.update(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.list(
            key="key=API_KEY",
        )
        assert_matches_type(MonitorListResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.list(
            key="key=API_KEY",
            cluster="america",
            pn=0,
            ps=100,
            sort="updated_at:desc",
            tags="tags=tag_1,tag_2",
        )
        assert_matches_type(MonitorListResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.monitor.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = await response.parse()
        assert_matches_type(MonitorListResponse, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.monitor.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = await response.parse()
            assert_matches_type(MonitorListResponse, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        monitor = await async_client.skynet.monitor.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.monitor.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        monitor = await response.parse()
        assert_matches_type(SimpleResp, monitor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.monitor.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            monitor = await response.parse()
            assert_matches_type(SimpleResp, monitor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.monitor.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )
