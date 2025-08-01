# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.fleetify.routes import (
    StepCreateResponse,
    StepDeleteResponse,
    StepUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSteps:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
        )
        assert_matches_type(StepCreateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
            address='"address": "503, Dublin Drive, Los Angeles, California - 500674",',
            completion_mode="manual",
            document_template_id="document_template_id",
            duration=0,
            geofence_config={
                "radius": 0,
                "type": "circle",
            },
            meta={
                "customer_name": '"customer_name": "Chandler Bing"',
                "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                "instructions": '"instructions": "Customer asked not to ring the doorbell."',
            },
        )
        assert_matches_type(StepCreateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.fleetify.routes.steps.with_raw_response.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(StepCreateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.fleetify.routes.steps.with_streaming_response.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = response.parse()
            assert_matches_type(StepCreateResponse, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.create(
                route_id="",
                key="key",
                arrival=0,
                location=[0],
                position=0,
                type="start",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
        )
        assert_matches_type(StepUpdateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
            address='"address": "503, Dublin Drive, Los Angeles, California - 500674",',
            completion_mode="manual",
            document_template_id="document_template_id",
            duration=0,
            geofence_config={
                "radius": 0,
                "type": "circle",
            },
            location=[0],
            meta={
                "customer_name": '"customer_name": "Chandler Bing"',
                "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                "instructions": '"instructions": "Customer asked not to ring the doorbell."',
            },
            type="start",
        )
        assert_matches_type(StepUpdateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.fleetify.routes.steps.with_raw_response.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(StepUpdateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.fleetify.routes.steps.with_streaming_response.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = response.parse()
            assert_matches_type(StepUpdateResponse, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.update(
                step_id="stepID",
                route_id="",
                key="key",
                arrival=0,
                position=0,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.update(
                step_id="",
                route_id="routeID",
                key="key",
                arrival=0,
                position=0,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.delete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )
        assert_matches_type(StepDeleteResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.fleetify.routes.steps.with_raw_response.delete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(StepDeleteResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.fleetify.routes.steps.with_streaming_response.delete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = response.parse()
            assert_matches_type(StepDeleteResponse, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.delete(
                step_id="stepID",
                route_id="",
                key="key",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.delete(
                step_id="",
                route_id="routeID",
                key="key",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_complete(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )
        assert step is None

    @pytest.mark.skip()
    @parametrize
    def test_method_complete_with_all_params(self, client: NextbillionSDK) -> None:
        step = client.fleetify.routes.steps.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
            document={},
            mode="mode",
            status="status",
        )
        assert step is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_complete(self, client: NextbillionSDK) -> None:
        response = client.fleetify.routes.steps.with_raw_response.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert step is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_complete(self, client: NextbillionSDK) -> None:
        with client.fleetify.routes.steps.with_streaming_response.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = response.parse()
            assert step is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_complete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.complete(
                step_id="stepID",
                route_id="",
                key="key",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step_id` but received ''"):
            client.fleetify.routes.steps.with_raw_response.complete(
                step_id="",
                route_id="routeID",
                key="key",
            )


class TestAsyncSteps:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
        )
        assert_matches_type(StepCreateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
            address='"address": "503, Dublin Drive, Los Angeles, California - 500674",',
            completion_mode="manual",
            document_template_id="document_template_id",
            duration=0,
            geofence_config={
                "radius": 0,
                "type": "circle",
            },
            meta={
                "customer_name": '"customer_name": "Chandler Bing"',
                "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                "instructions": '"instructions": "Customer asked not to ring the doorbell."',
            },
        )
        assert_matches_type(StepCreateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.routes.steps.with_raw_response.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = await response.parse()
        assert_matches_type(StepCreateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.routes.steps.with_streaming_response.create(
            route_id="routeID",
            key="key",
            arrival=0,
            location=[0],
            position=0,
            type="start",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = await response.parse()
            assert_matches_type(StepCreateResponse, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.create(
                route_id="",
                key="key",
                arrival=0,
                location=[0],
                position=0,
                type="start",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
        )
        assert_matches_type(StepUpdateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
            address='"address": "503, Dublin Drive, Los Angeles, California - 500674",',
            completion_mode="manual",
            document_template_id="document_template_id",
            duration=0,
            geofence_config={
                "radius": 0,
                "type": "circle",
            },
            location=[0],
            meta={
                "customer_name": '"customer_name": "Chandler Bing"',
                "customer_phone_number": '"customer_phone_number": "+1 707 234 1234"',
                "instructions": '"instructions": "Customer asked not to ring the doorbell."',
            },
            type="start",
        )
        assert_matches_type(StepUpdateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.routes.steps.with_raw_response.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = await response.parse()
        assert_matches_type(StepUpdateResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.routes.steps.with_streaming_response.update(
            step_id="stepID",
            route_id="routeID",
            key="key",
            arrival=0,
            position=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = await response.parse()
            assert_matches_type(StepUpdateResponse, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.update(
                step_id="stepID",
                route_id="",
                key="key",
                arrival=0,
                position=0,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.update(
                step_id="",
                route_id="routeID",
                key="key",
                arrival=0,
                position=0,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.delete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )
        assert_matches_type(StepDeleteResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.routes.steps.with_raw_response.delete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = await response.parse()
        assert_matches_type(StepDeleteResponse, step, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.routes.steps.with_streaming_response.delete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = await response.parse()
            assert_matches_type(StepDeleteResponse, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.delete(
                step_id="stepID",
                route_id="",
                key="key",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.delete(
                step_id="",
                route_id="routeID",
                key="key",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_complete(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )
        assert step is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_complete_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        step = await async_client.fleetify.routes.steps.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
            document={},
            mode="mode",
            status="status",
        )
        assert step is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_complete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.routes.steps.with_raw_response.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = await response.parse()
        assert step is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_complete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.routes.steps.with_streaming_response.complete(
            step_id="stepID",
            route_id="routeID",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = await response.parse()
            assert step is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_complete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `route_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.complete(
                step_id="stepID",
                route_id="",
                key="key",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step_id` but received ''"):
            await async_client.fleetify.routes.steps.with_raw_response.complete(
                step_id="",
                route_id="routeID",
                key="key",
            )
