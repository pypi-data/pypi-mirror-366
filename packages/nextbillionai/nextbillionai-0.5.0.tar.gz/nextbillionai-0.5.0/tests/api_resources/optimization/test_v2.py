# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import PostResponse
from nextbillionai.types.optimization import V2RetrieveResultResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestV2:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_result(self, client: NextbillionSDK) -> None:
        v2 = client.optimization.v2.retrieve_result(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(V2RetrieveResultResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_result(self, client: NextbillionSDK) -> None:
        response = client.optimization.v2.with_raw_response.retrieve_result(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v2 = response.parse()
        assert_matches_type(V2RetrieveResultResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_result(self, client: NextbillionSDK) -> None:
        with client.optimization.v2.with_streaming_response.retrieve_result(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v2 = response.parse()
            assert_matches_type(V2RetrieveResultResponse, v2, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: NextbillionSDK) -> None:
        v2 = client.optimization.v2.submit(
            key="key=API_KEY",
            locations={"location": ["string"]},
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )
        assert_matches_type(PostResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_with_all_params(self, client: NextbillionSDK) -> None:
        v2 = client.optimization.v2.submit(
            key="key=API_KEY",
            locations={
                "location": ["string"],
                "id": 0,
                "approaches": ["unrestricted"],
            },
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
            cost_matrix=[[0]],
            depots=[
                {
                    "id": '"id":"depot 1"',
                    "location_index": 0,
                    "description": "“description”:”Los_Angeles_depot”",
                    "service": 0,
                    "time_windows": [[0]],
                }
            ],
            description='"description": "Sample Optimization"',
            distance_matrix=[[0]],
            duration_matrix=[[0]],
            existing_solution_id="existing_solution_id",
            jobs=[
                {
                    "id": '"id":"Job 1"',
                    "location_index": 0,
                    "delivery": [0],
                    "depot_ids": ["string"],
                    "description": "description",
                    "follow_lifo_order": True,
                    "incompatible_load_types": ["string"],
                    "joint_order": 0,
                    "load_types": ["string"],
                    "max_visit_lateness": 0,
                    "metadata": '{\n  "contact": "212-456-7890",\n  "metaId": 1234\n}',
                    "outsourcing_cost": 0,
                    "pickup": [0],
                    "priority": 0,
                    "revenue": 0,
                    "sequence_order": 0,
                    "service": 0,
                    "setup": 0,
                    "skills": [1],
                    "time_windows": [[0]],
                    "volume": {
                        "alignment": "strict",
                        "depth": 0,
                        "height": 0,
                        "width": 0,
                    },
                    "zones": [0],
                }
            ],
            options={
                "constraint": {
                    "max_activity_waiting_time": 0,
                    "max_vehicle_overtime": 0,
                    "max_visit_lateness": 0,
                },
                "grouping": {
                    "order_grouping": {"grouping_diameter": 0},
                    "proximity_factor": 0,
                    "route_grouping": {
                        "penalty_factor": 0,
                        "zone_diameter": 0,
                        "zone_source": "system_generated",
                    },
                },
                "objective": {
                    "allow_early_arrival": True,
                    "custom": {
                        "type": "min",
                        "value": "vehicles",
                    },
                    "minimise_num_depots": True,
                    "solver_mode": "flexible",
                    "solving_time_limit": 0,
                    "travel_cost": "duration",
                },
                "routing": {
                    "allow": ["taxi"],
                    "avoid": ["toll"],
                    "context": "avgspeed",
                    "cross_border": True,
                    "disable_cache": True,
                    "hazmat_type": ["general"],
                    "mode": "car",
                    "profiles": '"profiles":{\n    "mini-van":{\n        "mode": "car",\n        "avoid":["highway, toll"]\n        },\n    "trailer":{\n        "mode": "truck",\n        "truck_weight":12000,\n        "truck_size":"200, 210, 600",\n        "hazmat_type": ["general", "harmful_to_water"]\n        }\n    }\n',
                    "traffic_timestamp": 0,
                    "truck_axle_load": 0,
                    "truck_size": '"truck_size":"200,210,600"',
                    "truck_weight": 0,
                },
            },
            relations=[
                {
                    "steps": [
                        {
                            "type": "start",
                            "id": '"id":"Job 1"',
                        }
                    ],
                    "type": "in_same_route",
                    "id": 0,
                    "max_duration": 0,
                    "min_duration": 0,
                    "vehicle": '"vehicle": "Vehicle 10"',
                }
            ],
            shipments=[
                {
                    "delivery": {
                        "id": '"id":"Shipment Delivery 1"',
                        "location_index": 0,
                        "description": "description",
                        "max_visit_lateness": 0,
                        "metadata": '{\n  "notes": "dropoff at the patio",\n  "contact": "212-456-7890",\n  "metaId": 1234\n}',
                        "sequence_order": 0,
                        "service": 0,
                        "setup": 0,
                        "time_windows": [[0]],
                    },
                    "pickup": {
                        "id": '"id": "Shipment Pickup 1"',
                        "location_index": 0,
                        "description": "description",
                        "max_visit_lateness": 0,
                        "metadata": '{\n  "notes": "involves fragile items",\n  "contact": "212-456-7890",\n  "metaId": 1234\n}',
                        "sequence_order": 0,
                        "service": 0,
                        "setup": 0,
                        "time_windows": [[0]],
                    },
                    "amount": [0],
                    "follow_lifo_order": True,
                    "incompatible_load_types": ["string"],
                    "joint_order": 0,
                    "load_types": ["string"],
                    "max_time_in_vehicle": 0,
                    "outsourcing_cost": 0,
                    "priority": 0,
                    "revenue": 0,
                    "skills": [0],
                    "volume": {
                        "alignment": "strict",
                        "depth": 0,
                        "height": 0,
                        "width": 0,
                    },
                    "zones": [0],
                }
            ],
            solution=[
                {
                    "cost": 0,
                    "steps": [
                        {
                            "id": '"id": "Job 10"',
                            "arrival": 0,
                            "type": "start",
                            "description": "description",
                            "distance": 0,
                            "duration": 0,
                            "load": [0],
                            "location": [0],
                            "location_index": 0,
                            "service": 0,
                            "setup": 0,
                            "waiting_time": 0,
                        }
                    ],
                    "vehicle": "vehicle",
                    "delivery": [0],
                    "description": "description",
                    "distance": 0,
                    "duration": 0,
                    "geometry": '"geometry": "}ebGgcsxRE?CuDOYCYAG???"',
                    "pickup": [0],
                    "priority": 0,
                    "service": 0,
                    "setup": 0,
                    "waiting_time": 0,
                }
            ],
            unassigned={
                "jobs": ["string"],
                "shipments": [["string"]],
            },
            zones=[
                {
                    "id": 0,
                    "geofence_id": "geofence_id",
                    "geometry": {
                        "coordinates": [[0]],
                        "description": "description",
                        "type": "Polygon",
                    },
                }
            ],
        )
        assert_matches_type(PostResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: NextbillionSDK) -> None:
        response = client.optimization.v2.with_raw_response.submit(
            key="key=API_KEY",
            locations={"location": ["string"]},
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v2 = response.parse()
        assert_matches_type(PostResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: NextbillionSDK) -> None:
        with client.optimization.v2.with_streaming_response.submit(
            key="key=API_KEY",
            locations={"location": ["string"]},
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v2 = response.parse()
            assert_matches_type(PostResponse, v2, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncV2:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_result(self, async_client: AsyncNextbillionSDK) -> None:
        v2 = await async_client.optimization.v2.retrieve_result(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(V2RetrieveResultResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_result(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.optimization.v2.with_raw_response.retrieve_result(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v2 = await response.parse()
        assert_matches_type(V2RetrieveResultResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_result(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.optimization.v2.with_streaming_response.retrieve_result(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v2 = await response.parse()
            assert_matches_type(V2RetrieveResultResponse, v2, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncNextbillionSDK) -> None:
        v2 = await async_client.optimization.v2.submit(
            key="key=API_KEY",
            locations={"location": ["string"]},
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )
        assert_matches_type(PostResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        v2 = await async_client.optimization.v2.submit(
            key="key=API_KEY",
            locations={
                "location": ["string"],
                "id": 0,
                "approaches": ["unrestricted"],
            },
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
            cost_matrix=[[0]],
            depots=[
                {
                    "id": '"id":"depot 1"',
                    "location_index": 0,
                    "description": "“description”:”Los_Angeles_depot”",
                    "service": 0,
                    "time_windows": [[0]],
                }
            ],
            description='"description": "Sample Optimization"',
            distance_matrix=[[0]],
            duration_matrix=[[0]],
            existing_solution_id="existing_solution_id",
            jobs=[
                {
                    "id": '"id":"Job 1"',
                    "location_index": 0,
                    "delivery": [0],
                    "depot_ids": ["string"],
                    "description": "description",
                    "follow_lifo_order": True,
                    "incompatible_load_types": ["string"],
                    "joint_order": 0,
                    "load_types": ["string"],
                    "max_visit_lateness": 0,
                    "metadata": '{\n  "contact": "212-456-7890",\n  "metaId": 1234\n}',
                    "outsourcing_cost": 0,
                    "pickup": [0],
                    "priority": 0,
                    "revenue": 0,
                    "sequence_order": 0,
                    "service": 0,
                    "setup": 0,
                    "skills": [1],
                    "time_windows": [[0]],
                    "volume": {
                        "alignment": "strict",
                        "depth": 0,
                        "height": 0,
                        "width": 0,
                    },
                    "zones": [0],
                }
            ],
            options={
                "constraint": {
                    "max_activity_waiting_time": 0,
                    "max_vehicle_overtime": 0,
                    "max_visit_lateness": 0,
                },
                "grouping": {
                    "order_grouping": {"grouping_diameter": 0},
                    "proximity_factor": 0,
                    "route_grouping": {
                        "penalty_factor": 0,
                        "zone_diameter": 0,
                        "zone_source": "system_generated",
                    },
                },
                "objective": {
                    "allow_early_arrival": True,
                    "custom": {
                        "type": "min",
                        "value": "vehicles",
                    },
                    "minimise_num_depots": True,
                    "solver_mode": "flexible",
                    "solving_time_limit": 0,
                    "travel_cost": "duration",
                },
                "routing": {
                    "allow": ["taxi"],
                    "avoid": ["toll"],
                    "context": "avgspeed",
                    "cross_border": True,
                    "disable_cache": True,
                    "hazmat_type": ["general"],
                    "mode": "car",
                    "profiles": '"profiles":{\n    "mini-van":{\n        "mode": "car",\n        "avoid":["highway, toll"]\n        },\n    "trailer":{\n        "mode": "truck",\n        "truck_weight":12000,\n        "truck_size":"200, 210, 600",\n        "hazmat_type": ["general", "harmful_to_water"]\n        }\n    }\n',
                    "traffic_timestamp": 0,
                    "truck_axle_load": 0,
                    "truck_size": '"truck_size":"200,210,600"',
                    "truck_weight": 0,
                },
            },
            relations=[
                {
                    "steps": [
                        {
                            "type": "start",
                            "id": '"id":"Job 1"',
                        }
                    ],
                    "type": "in_same_route",
                    "id": 0,
                    "max_duration": 0,
                    "min_duration": 0,
                    "vehicle": '"vehicle": "Vehicle 10"',
                }
            ],
            shipments=[
                {
                    "delivery": {
                        "id": '"id":"Shipment Delivery 1"',
                        "location_index": 0,
                        "description": "description",
                        "max_visit_lateness": 0,
                        "metadata": '{\n  "notes": "dropoff at the patio",\n  "contact": "212-456-7890",\n  "metaId": 1234\n}',
                        "sequence_order": 0,
                        "service": 0,
                        "setup": 0,
                        "time_windows": [[0]],
                    },
                    "pickup": {
                        "id": '"id": "Shipment Pickup 1"',
                        "location_index": 0,
                        "description": "description",
                        "max_visit_lateness": 0,
                        "metadata": '{\n  "notes": "involves fragile items",\n  "contact": "212-456-7890",\n  "metaId": 1234\n}',
                        "sequence_order": 0,
                        "service": 0,
                        "setup": 0,
                        "time_windows": [[0]],
                    },
                    "amount": [0],
                    "follow_lifo_order": True,
                    "incompatible_load_types": ["string"],
                    "joint_order": 0,
                    "load_types": ["string"],
                    "max_time_in_vehicle": 0,
                    "outsourcing_cost": 0,
                    "priority": 0,
                    "revenue": 0,
                    "skills": [0],
                    "volume": {
                        "alignment": "strict",
                        "depth": 0,
                        "height": 0,
                        "width": 0,
                    },
                    "zones": [0],
                }
            ],
            solution=[
                {
                    "cost": 0,
                    "steps": [
                        {
                            "id": '"id": "Job 10"',
                            "arrival": 0,
                            "type": "start",
                            "description": "description",
                            "distance": 0,
                            "duration": 0,
                            "load": [0],
                            "location": [0],
                            "location_index": 0,
                            "service": 0,
                            "setup": 0,
                            "waiting_time": 0,
                        }
                    ],
                    "vehicle": "vehicle",
                    "delivery": [0],
                    "description": "description",
                    "distance": 0,
                    "duration": 0,
                    "geometry": '"geometry": "}ebGgcsxRE?CuDOYCYAG???"',
                    "pickup": [0],
                    "priority": 0,
                    "service": 0,
                    "setup": 0,
                    "waiting_time": 0,
                }
            ],
            unassigned={
                "jobs": ["string"],
                "shipments": [["string"]],
            },
            zones=[
                {
                    "id": 0,
                    "geofence_id": "geofence_id",
                    "geometry": {
                        "coordinates": [[0]],
                        "description": "description",
                        "type": "Polygon",
                    },
                }
            ],
        )
        assert_matches_type(PostResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.optimization.v2.with_raw_response.submit(
            key="key=API_KEY",
            locations={"location": ["string"]},
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v2 = await response.parse()
        assert_matches_type(PostResponse, v2, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.optimization.v2.with_streaming_response.submit(
            key="key=API_KEY",
            locations={"location": ["string"]},
            vehicles=[
                {
                    "id": "id",
                    "location": {},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v2 = await response.parse()
            assert_matches_type(PostResponse, v2, path=["response"])

        assert cast(Any, response.is_closed) is True
