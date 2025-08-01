# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import (
    RichGroupResponse,
    RestrictionListResponse,
    RestrictionDeleteResponse,
    RestrictionListByBboxResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRestrictions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
            latlon=True,
            comment="comment",
            direction="forward",
            end_time=0,
            geofence=[[0]],
            height=0,
            length=0,
            mode=["0w"],
            repeat_on='repeatOn="Mo-Fr 07:00-09:00,17:00-19:00"',
            segments=[
                {
                    "from": 0,
                    "to": 0,
                }
            ],
            speed=0,
            speed_limit=0,
            start_time=0,
            tracks=[[0]],
            turns=[
                {
                    "from": 0,
                    "to": 0,
                    "via": 0,
                }
            ],
            weight=0,
            width=0,
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.retrieve(
            id=0,
            key="key=API_KEY",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.retrieve(
            id=0,
            key="key=API_KEY",
            transform=True,
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.retrieve(
            id=0,
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.retrieve(
            id=0,
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
            latlon=True,
            comment="comment",
            direction="forward",
            end_time=0,
            geofence=[[0]],
            height=0,
            length=0,
            mode=["0w"],
            repeat_on='repeatOn="Mo-Fr 07:00-09:00,17:00-19:00"',
            segments=[
                {
                    "from": 0,
                    "to": 0,
                }
            ],
            speed=0,
            speed_limit=0,
            start_time=0,
            tracks=[[0]],
            turns=[
                {
                    "from": 0,
                    "to": 0,
                    "via": 0,
                }
            ],
            weight=0,
            width=0,
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
        )
        assert_matches_type(RestrictionListResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
            mode="0w",
            name="name",
            restriction_type="turn",
            source="rrt",
            state="enabled",
            status="active",
            transform=True,
        )
        assert_matches_type(RestrictionListResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RestrictionListResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RestrictionListResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.delete(
            id=0,
            key="key=API_KEY",
        )
        assert_matches_type(RestrictionDeleteResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.delete(
            id=0,
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RestrictionDeleteResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.delete(
            id=0,
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RestrictionDeleteResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_by_bbox(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )
        assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_by_bbox_with_all_params(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
            mode=["0w"],
            restriction_type="turn",
            source="rrt",
            state="enabled",
            status="active",
            transform=True,
        )
        assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_by_bbox(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_by_bbox(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_set_state(self, client: NextbillionSDK) -> None:
        restriction = client.restrictions.set_state(
            id=0,
            key="key=API_KEY",
            state="enabled",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_set_state(self, client: NextbillionSDK) -> None:
        response = client.restrictions.with_raw_response.set_state(
            id=0,
            key="key=API_KEY",
            state="enabled",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_set_state(self, client: NextbillionSDK) -> None:
        with client.restrictions.with_streaming_response.set_state(
            id=0,
            key="key=API_KEY",
            state="enabled",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRestrictions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
            latlon=True,
            comment="comment",
            direction="forward",
            end_time=0,
            geofence=[[0]],
            height=0,
            length=0,
            mode=["0w"],
            repeat_on='repeatOn="Mo-Fr 07:00-09:00,17:00-19:00"',
            segments=[
                {
                    "from": 0,
                    "to": 0,
                }
            ],
            speed=0,
            speed_limit=0,
            start_time=0,
            tracks=[[0]],
            turns=[
                {
                    "from": 0,
                    "to": 0,
                    "via": 0,
                }
            ],
            weight=0,
            width=0,
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.create(
            restriction_type="turn",
            key="key=API_KEY",
            area="area",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.retrieve(
            id=0,
            key="key=API_KEY",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.retrieve(
            id=0,
            key="key=API_KEY",
            transform=True,
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.retrieve(
            id=0,
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.retrieve(
            id=0,
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
            latlon=True,
            comment="comment",
            direction="forward",
            end_time=0,
            geofence=[[0]],
            height=0,
            length=0,
            mode=["0w"],
            repeat_on='repeatOn="Mo-Fr 07:00-09:00,17:00-19:00"',
            segments=[
                {
                    "from": 0,
                    "to": 0,
                }
            ],
            speed=0,
            speed_limit=0,
            start_time=0,
            tracks=[[0]],
            turns=[
                {
                    "from": 0,
                    "to": 0,
                    "via": 0,
                }
            ],
            weight=0,
            width=0,
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.update(
            id=0,
            key="key=API_KEY",
            area="area",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
        )
        assert_matches_type(RestrictionListResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
            mode="0w",
            name="name",
            restriction_type="turn",
            source="rrt",
            state="enabled",
            status="active",
            transform=True,
        )
        assert_matches_type(RestrictionListResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RestrictionListResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.list(
            area="area",
            key="key=API_KEY",
            limit=0,
            offset=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RestrictionListResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.delete(
            id=0,
            key="key=API_KEY",
        )
        assert_matches_type(RestrictionDeleteResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.delete(
            id=0,
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RestrictionDeleteResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.delete(
            id=0,
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RestrictionDeleteResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_by_bbox(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )
        assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_by_bbox_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
            mode=["0w"],
            restriction_type="turn",
            source="rrt",
            state="enabled",
            status="active",
            transform=True,
        )
        assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_by_bbox(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_by_bbox(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.list_by_bbox(
            key="key=API_KEY",
            max_lat=0,
            max_lon=0,
            min_lat=0,
            min_lon=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RestrictionListByBboxResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_state(self, async_client: AsyncNextbillionSDK) -> None:
        restriction = await async_client.restrictions.set_state(
            id=0,
            key="key=API_KEY",
            state="enabled",
        )
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_set_state(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.restrictions.with_raw_response.set_state(
            id=0,
            key="key=API_KEY",
            state="enabled",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        restriction = await response.parse()
        assert_matches_type(RichGroupResponse, restriction, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_set_state(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.restrictions.with_streaming_response.set_state(
            id=0,
            key="key=API_KEY",
            state="enabled",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            restriction = await response.parse()
            assert_matches_type(RichGroupResponse, restriction, path=["response"])

        assert cast(Any, response.is_closed) is True
