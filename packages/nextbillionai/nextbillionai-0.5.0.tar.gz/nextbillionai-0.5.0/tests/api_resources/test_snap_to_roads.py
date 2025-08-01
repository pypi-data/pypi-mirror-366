# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import SnapToRoadSnapResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSnapToRoads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_snap(self, client: NextbillionSDK) -> None:
        snap_to_road = client.snap_to_roads.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
        )
        assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_snap_with_all_params(self, client: NextbillionSDK) -> None:
        snap_to_road = client.snap_to_roads.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
            approaches="unrestricted",
            avoid="toll",
            geometry="polyline",
            mode="car",
            option="flexible",
            radiuses="radiuses=14|16|14",
            road_info="max_speed",
            timestamps="timestamps=1656570000|1656570015|1656570030",
            tolerate_outlier=True,
        )
        assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_snap(self, client: NextbillionSDK) -> None:
        response = client.snap_to_roads.with_raw_response.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snap_to_road = response.parse()
        assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_snap(self, client: NextbillionSDK) -> None:
        with client.snap_to_roads.with_streaming_response.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snap_to_road = response.parse()
            assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSnapToRoads:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_snap(self, async_client: AsyncNextbillionSDK) -> None:
        snap_to_road = await async_client.snap_to_roads.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
        )
        assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_snap_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        snap_to_road = await async_client.snap_to_roads.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
            approaches="unrestricted",
            avoid="toll",
            geometry="polyline",
            mode="car",
            option="flexible",
            radiuses="radiuses=14|16|14",
            road_info="max_speed",
            timestamps="timestamps=1656570000|1656570015|1656570030",
            tolerate_outlier=True,
        )
        assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_snap(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.snap_to_roads.with_raw_response.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snap_to_road = await response.parse()
        assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_snap(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.snap_to_roads.with_streaming_response.snap(
            key="key=API_KEY",
            path="path=41.38602272,2.17621539|41.38312885,2.17207083|41.38157854,2.17906668|41.38288511,2.18186215",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snap_to_road = await response.parse()
            assert_matches_type(SnapToRoadSnapResponse, snap_to_road, path=["response"])

        assert cast(Any, response.is_closed) is True
