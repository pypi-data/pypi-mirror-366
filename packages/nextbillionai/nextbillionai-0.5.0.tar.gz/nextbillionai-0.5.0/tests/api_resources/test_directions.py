# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import DirectionComputeRouteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDirections:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_compute_route(self, client: NextbillionSDK) -> None:
        direction = client.directions.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
        )
        assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_compute_route_with_all_params(self, client: NextbillionSDK) -> None:
        direction = client.directions.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
            altcount=1,
            alternatives=True,
            approaches="unrestricted;;curb;",
            avoid="toll",
            bearings="0,180;0,180",
            cross_border=True,
            departure_time=0,
            drive_time_limits="500,400,400",
            emission_class="euro0",
            exclude="toll",
            geometry="polyline",
            hazmat_type="general",
            mode="car",
            option="fast",
            overview="full",
            rest_times="500,300,100",
            road_info="max_speed",
            route_type="fastest",
            steps=True,
            truck_axle_load=0,
            truck_size="200,210,600",
            truck_weight=1,
            turn_angle_range=0,
            waypoints="41.349302,2.136480|41.349303,2.136481|41.349304,2.136482",
        )
        assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_compute_route(self, client: NextbillionSDK) -> None:
        response = client.directions.with_raw_response.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        direction = response.parse()
        assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_compute_route(self, client: NextbillionSDK) -> None:
        with client.directions.with_streaming_response.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            direction = response.parse()
            assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDirections:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_compute_route(self, async_client: AsyncNextbillionSDK) -> None:
        direction = await async_client.directions.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
        )
        assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_compute_route_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        direction = await async_client.directions.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
            altcount=1,
            alternatives=True,
            approaches="unrestricted;;curb;",
            avoid="toll",
            bearings="0,180;0,180",
            cross_border=True,
            departure_time=0,
            drive_time_limits="500,400,400",
            emission_class="euro0",
            exclude="toll",
            geometry="polyline",
            hazmat_type="general",
            mode="car",
            option="fast",
            overview="full",
            rest_times="500,300,100",
            road_info="max_speed",
            route_type="fastest",
            steps=True,
            truck_axle_load=0,
            truck_size="200,210,600",
            truck_weight=1,
            turn_angle_range=0,
            waypoints="41.349302,2.136480|41.349303,2.136481|41.349304,2.136482",
        )
        assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_compute_route(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.directions.with_raw_response.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        direction = await response.parse()
        assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_compute_route(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.directions.with_streaming_response.compute_route(
            destination="41.349302,2.136480",
            origin="41.349302,2.136480",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            direction = await response.parse()
            assert_matches_type(DirectionComputeRouteResponse, direction, path=["response"])

        assert cast(Any, response.is_closed) is True
