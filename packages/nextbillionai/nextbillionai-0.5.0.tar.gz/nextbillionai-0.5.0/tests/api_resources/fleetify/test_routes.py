# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.fleetify import (
    RouteCreateResponse,
    RouteRedispatchResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRoutes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        route = client.fleetify.routes.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                }
            ],
        )
        assert_matches_type(RouteCreateResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        route = client.fleetify.routes.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                    "address": '"address": "503, Dublin Drive, Los Angeles, California - 500674",',
                    "completion_mode": "manual",
                    "document_template_id": "document_template_id",
                    "duration": 0,
                    "geofence_config": {
                        "radius": 0,
                        "type": "circle",
                    },
                    "meta": {
                        "customer_name": '"customer_name": "Chandler Bing"',
                        "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                        "instructions": '"instructions": "Customer asked not to ring the doorbell."',
                    },
                }
            ],
            distance=0,
            document_template_id='"document_template_id": "bfbc4799-bc2f-4515-9054-d888560909bf"',
            ro_request_id="ro_request_id",
            routing={
                "approaches": "unrestricted",
                "avoid": "toll",
                "hazmat_type": "general",
                "mode": "car",
                "truck_axle_load": 0,
                "truck_size": '"truck_size": "200, 210, 600"',
                "truck_weight": 0,
            },
        )
        assert_matches_type(RouteCreateResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.fleetify.routes.with_raw_response.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        route = response.parse()
        assert_matches_type(RouteCreateResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.fleetify.routes.with_streaming_response.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            route = response.parse()
            assert_matches_type(RouteCreateResponse, route, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_redispatch(self, client: NextbillionSDK) -> None:
        route = client.fleetify.routes.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {},
                    "operation": "create",
                }
            ],
        )
        assert_matches_type(RouteRedispatchResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_redispatch_with_all_params(self, client: NextbillionSDK) -> None:
        route = client.fleetify.routes.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {
                        "completion_mode": "manual",
                        "document_template_id": "document_template_id",
                        "step": {
                            "arrival": 0,
                            "location": [0],
                            "type": "start",
                            "address": '"address": "503, Dublin Drive, Los Angeles, California - 500674",',
                            "completion_mode": "manual",
                            "document_template_id": "document_template_id",
                            "duration": 0,
                            "geofence_config": {
                                "radius": 0,
                                "type": "circle",
                            },
                            "meta": {
                                "customer_name": '"customer_name": "Chandler Bing"',
                                "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                                "instructions": '"instructions": "Customer asked not to ring the doorbell."',
                            },
                        },
                        "step_id": "step_id",
                    },
                    "operation": "create",
                }
            ],
            distance=0,
        )
        assert_matches_type(RouteRedispatchResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_redispatch(self, client: NextbillionSDK) -> None:
        response = client.fleetify.routes.with_raw_response.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {},
                    "operation": "create",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        route = response.parse()
        assert_matches_type(RouteRedispatchResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_redispatch(self, client: NextbillionSDK) -> None:
        with client.fleetify.routes.with_streaming_response.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {},
                    "operation": "create",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            route = response.parse()
            assert_matches_type(RouteRedispatchResponse, route, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_redispatch(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            client.fleetify.routes.with_raw_response.redispatch(
                route_id="",
                key="key",
                operations=[
                    {
                        "data": {},
                        "operation": "create",
                    }
                ],
            )


class TestAsyncRoutes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        route = await async_client.fleetify.routes.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                }
            ],
        )
        assert_matches_type(RouteCreateResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        route = await async_client.fleetify.routes.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                    "address": '"address": "503, Dublin Drive, Los Angeles, California - 500674",',
                    "completion_mode": "manual",
                    "document_template_id": "document_template_id",
                    "duration": 0,
                    "geofence_config": {
                        "radius": 0,
                        "type": "circle",
                    },
                    "meta": {
                        "customer_name": '"customer_name": "Chandler Bing"',
                        "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                        "instructions": '"instructions": "Customer asked not to ring the doorbell."',
                    },
                }
            ],
            distance=0,
            document_template_id='"document_template_id": "bfbc4799-bc2f-4515-9054-d888560909bf"',
            ro_request_id="ro_request_id",
            routing={
                "approaches": "unrestricted",
                "avoid": "toll",
                "hazmat_type": "general",
                "mode": "car",
                "truck_axle_load": 0,
                "truck_size": '"truck_size": "200, 210, 600"',
                "truck_weight": 0,
            },
        )
        assert_matches_type(RouteCreateResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.routes.with_raw_response.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        route = await response.parse()
        assert_matches_type(RouteCreateResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.routes.with_streaming_response.create(
            key="key",
            driver_email="johndoe@abc.com",
            steps=[
                {
                    "arrival": 0,
                    "location": [0],
                    "type": "start",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            route = await response.parse()
            assert_matches_type(RouteCreateResponse, route, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_redispatch(self, async_client: AsyncNextbillionSDK) -> None:
        route = await async_client.fleetify.routes.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {},
                    "operation": "create",
                }
            ],
        )
        assert_matches_type(RouteRedispatchResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_redispatch_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        route = await async_client.fleetify.routes.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {
                        "completion_mode": "manual",
                        "document_template_id": "document_template_id",
                        "step": {
                            "arrival": 0,
                            "location": [0],
                            "type": "start",
                            "address": '"address": "503, Dublin Drive, Los Angeles, California - 500674",',
                            "completion_mode": "manual",
                            "document_template_id": "document_template_id",
                            "duration": 0,
                            "geofence_config": {
                                "radius": 0,
                                "type": "circle",
                            },
                            "meta": {
                                "customer_name": '"customer_name": "Chandler Bing"',
                                "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                                "instructions": '"instructions": "Customer asked not to ring the doorbell."',
                            },
                        },
                        "step_id": "step_id",
                    },
                    "operation": "create",
                }
            ],
            distance=0,
        )
        assert_matches_type(RouteRedispatchResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_redispatch(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.routes.with_raw_response.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {},
                    "operation": "create",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        route = await response.parse()
        assert_matches_type(RouteRedispatchResponse, route, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_redispatch(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.routes.with_streaming_response.redispatch(
            route_id="routeID",
            key="key",
            operations=[
                {
                    "data": {},
                    "operation": "create",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            route = await response.parse()
            assert_matches_type(RouteRedispatchResponse, route, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_redispatch(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            await async_client.fleetify.routes.with_raw_response.redispatch(
                route_id="",
                key="key",
                operations=[
                    {
                        "data": {},
                        "operation": "create",
                    }
                ],
            )
