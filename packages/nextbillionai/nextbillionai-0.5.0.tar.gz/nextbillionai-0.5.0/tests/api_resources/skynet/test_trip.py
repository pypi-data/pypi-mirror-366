# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet import (
    SimpleResp,
    TripStartResponse,
    TripRetrieveResponse,
    TripGetSummaryResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTrip:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(TripRetrieveResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.retrieve(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(TripRetrieveResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.skynet.trip.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = response.parse()
        assert_matches_type(TripRetrieveResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.skynet.trip.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = response.parse()
            assert_matches_type(TripRetrieveResponse, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.trip.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            description="description",
            meta_data='"meta_data":["Scheduled Trip", "Custom Deliveries"]',
            name='"name": "Employee Pickup"',
            stops=[
                {
                    "geofence_id": "geofence_id",
                    "meta_data": '"meta_data":["Staff Entry Point", "Biometric checkpoint"]',
                    "name": '"name":"Head Office"',
                }
            ],
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.skynet.trip.with_raw_response.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = response.parse()
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.skynet.trip.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = response.parse()
            assert_matches_type(SimpleResp, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.trip.with_raw_response.update(
                id="",
                key="key=API_KEY",
                asset_id="asset_id",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_with_all_params(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.delete(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.skynet.trip.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = response.parse()
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.skynet.trip.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = response.parse()
            assert_matches_type(SimpleResp, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.trip.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_end(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.end(
            key="key=API_KEY",
            id="id",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_end_with_all_params(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.end(
            key="key=API_KEY",
            id="id",
            cluster="america",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_end(self, client: NextbillionSDK) -> None:
        response = client.skynet.trip.with_raw_response.end(
            key="key=API_KEY",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = response.parse()
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_end(self, client: NextbillionSDK) -> None:
        with client.skynet.trip.with_streaming_response.end(
            key="key=API_KEY",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = response.parse()
            assert_matches_type(SimpleResp, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_summary(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.get_summary(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_summary_with_all_params(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.get_summary(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_summary(self, client: NextbillionSDK) -> None:
        response = client.skynet.trip.with_raw_response.get_summary(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = response.parse()
        assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_summary(self, client: NextbillionSDK) -> None:
        with client.skynet.trip.with_streaming_response.get_summary(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = response.parse()
            assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_summary(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.trip.with_raw_response.get_summary(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_start(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.start(
            key="key=API_KEY",
            asset_id="asset_id",
        )
        assert_matches_type(TripStartResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_start_with_all_params(self, client: NextbillionSDK) -> None:
        trip = client.skynet.trip.start(
            key="key=API_KEY",
            asset_id="asset_id",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            custom_id="custom_id",
            description="description",
            meta_data='"meta_data":["Scheduled Trip", "Custom Deliveries"]',
            name='"name": "Employee Pickup"',
            stops=[
                {
                    "geofence_id": "geofence_id",
                    "meta_data": '"meta_data":["Staff Entry Point", "Biometric checkpoint"]',
                    "name": '"name":"Head Office"',
                }
            ],
        )
        assert_matches_type(TripStartResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_start(self, client: NextbillionSDK) -> None:
        response = client.skynet.trip.with_raw_response.start(
            key="key=API_KEY",
            asset_id="asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = response.parse()
        assert_matches_type(TripStartResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_start(self, client: NextbillionSDK) -> None:
        with client.skynet.trip.with_streaming_response.start(
            key="key=API_KEY",
            asset_id="asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = response.parse()
            assert_matches_type(TripStartResponse, trip, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTrip:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.retrieve(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(TripRetrieveResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.retrieve(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(TripRetrieveResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.trip.with_raw_response.retrieve(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = await response.parse()
        assert_matches_type(TripRetrieveResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.trip.with_streaming_response.retrieve(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = await response.parse()
            assert_matches_type(TripRetrieveResponse, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.trip.with_raw_response.retrieve(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            description="description",
            meta_data='"meta_data":["Scheduled Trip", "Custom Deliveries"]',
            name='"name": "Employee Pickup"',
            stops=[
                {
                    "geofence_id": "geofence_id",
                    "meta_data": '"meta_data":["Staff Entry Point", "Biometric checkpoint"]',
                    "name": '"name":"Head Office"',
                }
            ],
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.trip.with_raw_response.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = await response.parse()
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.trip.with_streaming_response.update(
            id="id",
            key="key=API_KEY",
            asset_id="asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = await response.parse()
            assert_matches_type(SimpleResp, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.trip.with_raw_response.update(
                id="",
                key="key=API_KEY",
                asset_id="asset_id",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.delete(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.delete(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.trip.with_raw_response.delete(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = await response.parse()
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.trip.with_streaming_response.delete(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = await response.parse()
            assert_matches_type(SimpleResp, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.trip.with_raw_response.delete(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_end(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.end(
            key="key=API_KEY",
            id="id",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_end_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.end(
            key="key=API_KEY",
            id="id",
            cluster="america",
        )
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_end(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.trip.with_raw_response.end(
            key="key=API_KEY",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = await response.parse()
        assert_matches_type(SimpleResp, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_end(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.trip.with_streaming_response.end(
            key="key=API_KEY",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = await response.parse()
            assert_matches_type(SimpleResp, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_summary(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.get_summary(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_summary_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.get_summary(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_summary(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.trip.with_raw_response.get_summary(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = await response.parse()
        assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_summary(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.trip.with_streaming_response.get_summary(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = await response.parse()
            assert_matches_type(TripGetSummaryResponse, trip, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_summary(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.trip.with_raw_response.get_summary(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_start(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.start(
            key="key=API_KEY",
            asset_id="asset_id",
        )
        assert_matches_type(TripStartResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_start_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        trip = await async_client.skynet.trip.start(
            key="key=API_KEY",
            asset_id="asset_id",
            cluster="america",
            attributes='{\n  "shift_timing": "0800-1700",\n  "driver_name": "John"\n}',
            custom_id="custom_id",
            description="description",
            meta_data='"meta_data":["Scheduled Trip", "Custom Deliveries"]',
            name='"name": "Employee Pickup"',
            stops=[
                {
                    "geofence_id": "geofence_id",
                    "meta_data": '"meta_data":["Staff Entry Point", "Biometric checkpoint"]',
                    "name": '"name":"Head Office"',
                }
            ],
        )
        assert_matches_type(TripStartResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.trip.with_raw_response.start(
            key="key=API_KEY",
            asset_id="asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trip = await response.parse()
        assert_matches_type(TripStartResponse, trip, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.trip.with_streaming_response.start(
            key="key=API_KEY",
            asset_id="asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trip = await response.parse()
            assert_matches_type(TripStartResponse, trip, path=["response"])

        assert cast(Any, response.is_closed) is True
