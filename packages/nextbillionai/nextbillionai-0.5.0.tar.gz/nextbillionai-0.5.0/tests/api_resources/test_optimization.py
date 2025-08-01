# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import (
    PostResponse,
    OptimizationComputeResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOptimization:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_compute(self, client: NextbillionSDK) -> None:
        optimization = client.optimization.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
        )
        assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_compute_with_all_params(self, client: NextbillionSDK) -> None:
        optimization = client.optimization.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
            approaches="unrestricted",
            destination="any",
            geometries="polyline",
            mode="car",
            roundtrip=True,
            source="any",
            with_geometry=True,
        )
        assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_compute(self, client: NextbillionSDK) -> None:
        response = client.optimization.with_raw_response.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        optimization = response.parse()
        assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_compute(self, client: NextbillionSDK) -> None:
        with client.optimization.with_streaming_response.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            optimization = response.parse()
            assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_re_optimize(self, client: NextbillionSDK) -> None:
        optimization = client.optimization.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
        )
        assert_matches_type(PostResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_re_optimize_with_all_params(self, client: NextbillionSDK) -> None:
        optimization = client.optimization.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
            job_changes={
                "add": [
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
                "modify": [
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
                "remove": ["string"],
            },
            locations=["string"],
            shipment_changes={
                "add": [
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
                "modify": [
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
                "remove": ["string"],
            },
            vehicle_changes={
                "add": [
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
                "modify": {
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
                },
                "remove": ["string"],
            },
        )
        assert_matches_type(PostResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_re_optimize(self, client: NextbillionSDK) -> None:
        response = client.optimization.with_raw_response.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        optimization = response.parse()
        assert_matches_type(PostResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_re_optimize(self, client: NextbillionSDK) -> None:
        with client.optimization.with_streaming_response.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            optimization = response.parse()
            assert_matches_type(PostResponse, optimization, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOptimization:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_compute(self, async_client: AsyncNextbillionSDK) -> None:
        optimization = await async_client.optimization.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
        )
        assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_compute_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        optimization = await async_client.optimization.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
            approaches="unrestricted",
            destination="any",
            geometries="polyline",
            mode="car",
            roundtrip=True,
            source="any",
            with_geometry=True,
        )
        assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_compute(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.optimization.with_raw_response.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        optimization = await response.parse()
        assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_compute(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.optimization.with_streaming_response.compute(
            coordinates="coordinates=41.35544869444527,2.0747669962025292|41.37498154684205,2.103705 4530396886|41.38772862000152,2.1311887061315526",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            optimization = await response.parse()
            assert_matches_type(OptimizationComputeResponse, optimization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_re_optimize(self, async_client: AsyncNextbillionSDK) -> None:
        optimization = await async_client.optimization.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
        )
        assert_matches_type(PostResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_re_optimize_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        optimization = await async_client.optimization.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
            job_changes={
                "add": [
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
                "modify": [
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
                "remove": ["string"],
            },
            locations=["string"],
            shipment_changes={
                "add": [
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
                "modify": [
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
                "remove": ["string"],
            },
            vehicle_changes={
                "add": [
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
                "modify": {
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
                },
                "remove": ["string"],
            },
        )
        assert_matches_type(PostResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_re_optimize(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.optimization.with_raw_response.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        optimization = await response.parse()
        assert_matches_type(PostResponse, optimization, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_re_optimize(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.optimization.with_streaming_response.re_optimize(
            key="key=API_KEY",
            existing_request_id="existing_request_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            optimization = await response.parse()
            assert_matches_type(PostResponse, optimization, path=["response"])

        assert cast(Any, response.is_closed) is True
