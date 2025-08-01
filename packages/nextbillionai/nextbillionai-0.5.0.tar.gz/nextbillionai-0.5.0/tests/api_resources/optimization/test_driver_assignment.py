# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.optimization import DriverAssignmentAssignResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDriverAssignment:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_assign(self, client: NextbillionSDK) -> None:
        driver_assignment = client.optimization.driver_assignment.assign(
            key="key=API_KEY",
            filter={},
            orders=[
                {
                    "id": "id",
                    "pickup": {},
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )
        assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_assign_with_all_params(self, client: NextbillionSDK) -> None:
        driver_assignment = client.optimization.driver_assignment.assign(
            key="key=API_KEY",
            filter={
                "driving_distance": 0,
                "pickup_eta": 0,
                "radius": 0,
            },
            orders=[
                {
                    "id": "id",
                    "pickup": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "attributes": {},
                    "dropoffs": [
                        {
                            "lat": 0,
                            "lng": 0,
                        }
                    ],
                    "priority": 0,
                    "service_time": 0,
                    "vehicle_preferences": {
                        "exclude_all_of_attributes": [
                            {
                                "attribute": '"attribute": "driver_rating"',
                                "operator": '"operator":"<"',
                                "value": '"value": "4"',
                            }
                        ],
                        "required_all_of_attributes": [
                            {
                                "attribute": '"attribute": "driver_rating"',
                                "operator": '"operator":"=="',
                                "value": '"value": "4"',
                            }
                        ],
                        "required_any_of_attributes": [
                            {
                                "attribute": '"attribute": "driver_rating"',
                                "operator": '"operator":">"',
                                "value": '"value": "4"',
                            }
                        ],
                    },
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "attributes": '"attributes":{\n    "driver_rating": "4.0",\n    "trip_types": "premium"\n  }',
                    "priority": 0,
                    "remaining_waypoints": [
                        {
                            "lat": -90,
                            "lon": -180,
                        }
                    ],
                }
            ],
            options={
                "alternate_assignments": 0,
                "dropoff_details": True,
                "order_attribute_priority_mappings": [
                    {
                        "attribute": '"attribute": "driver_rating"',
                        "operator": '"operator":"=="',
                        "priority": "priority",
                        "value": '"value": "4"',
                    }
                ],
                "travel_cost": "driving_eta",
                "vehicle_attribute_priority_mappings": [
                    {
                        "attribute": '"attribute": "driver_rating"',
                        "operator": '"operator":"=="',
                        "priority": "priority",
                        "value": '"value": "4"',
                    }
                ],
            },
        )
        assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_assign(self, client: NextbillionSDK) -> None:
        response = client.optimization.driver_assignment.with_raw_response.assign(
            key="key=API_KEY",
            filter={},
            orders=[
                {
                    "id": "id",
                    "pickup": {},
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        driver_assignment = response.parse()
        assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_assign(self, client: NextbillionSDK) -> None:
        with client.optimization.driver_assignment.with_streaming_response.assign(
            key="key=API_KEY",
            filter={},
            orders=[
                {
                    "id": "id",
                    "pickup": {},
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            driver_assignment = response.parse()
            assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDriverAssignment:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_assign(self, async_client: AsyncNextbillionSDK) -> None:
        driver_assignment = await async_client.optimization.driver_assignment.assign(
            key="key=API_KEY",
            filter={},
            orders=[
                {
                    "id": "id",
                    "pickup": {},
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )
        assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_assign_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        driver_assignment = await async_client.optimization.driver_assignment.assign(
            key="key=API_KEY",
            filter={
                "driving_distance": 0,
                "pickup_eta": 0,
                "radius": 0,
            },
            orders=[
                {
                    "id": "id",
                    "pickup": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "attributes": {},
                    "dropoffs": [
                        {
                            "lat": 0,
                            "lng": 0,
                        }
                    ],
                    "priority": 0,
                    "service_time": 0,
                    "vehicle_preferences": {
                        "exclude_all_of_attributes": [
                            {
                                "attribute": '"attribute": "driver_rating"',
                                "operator": '"operator":"<"',
                                "value": '"value": "4"',
                            }
                        ],
                        "required_all_of_attributes": [
                            {
                                "attribute": '"attribute": "driver_rating"',
                                "operator": '"operator":"=="',
                                "value": '"value": "4"',
                            }
                        ],
                        "required_any_of_attributes": [
                            {
                                "attribute": '"attribute": "driver_rating"',
                                "operator": '"operator":">"',
                                "value": '"value": "4"',
                            }
                        ],
                    },
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "attributes": '"attributes":{\n    "driver_rating": "4.0",\n    "trip_types": "premium"\n  }',
                    "priority": 0,
                    "remaining_waypoints": [
                        {
                            "lat": -90,
                            "lon": -180,
                        }
                    ],
                }
            ],
            options={
                "alternate_assignments": 0,
                "dropoff_details": True,
                "order_attribute_priority_mappings": [
                    {
                        "attribute": '"attribute": "driver_rating"',
                        "operator": '"operator":"=="',
                        "priority": "priority",
                        "value": '"value": "4"',
                    }
                ],
                "travel_cost": "driving_eta",
                "vehicle_attribute_priority_mappings": [
                    {
                        "attribute": '"attribute": "driver_rating"',
                        "operator": '"operator":"=="',
                        "priority": "priority",
                        "value": '"value": "4"',
                    }
                ],
            },
        )
        assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_assign(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.optimization.driver_assignment.with_raw_response.assign(
            key="key=API_KEY",
            filter={},
            orders=[
                {
                    "id": "id",
                    "pickup": {},
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        driver_assignment = await response.parse()
        assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_assign(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.optimization.driver_assignment.with_streaming_response.assign(
            key="key=API_KEY",
            filter={},
            orders=[
                {
                    "id": "id",
                    "pickup": {},
                }
            ],
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            driver_assignment = await response.parse()
            assert_matches_type(DriverAssignmentAssignResponse, driver_assignment, path=["response"])

        assert cast(Any, response.is_closed) is True
