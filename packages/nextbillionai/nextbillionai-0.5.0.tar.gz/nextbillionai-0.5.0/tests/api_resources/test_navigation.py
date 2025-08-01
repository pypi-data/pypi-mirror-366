# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import NavigationRetrieveRouteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNavigation:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_route(self, client: NextbillionSDK) -> None:
        navigation = client.navigation.retrieve_route(
            key="key=API_KEY",
        )
        assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_route_with_all_params(self, client: NextbillionSDK) -> None:
        navigation = client.navigation.retrieve_route(
            key="key=API_KEY",
            altcount=1,
            alternatives=True,
            approaches="unrestricted",
            avoid="toll",
            bearings="bearings=0,180;0,180",
            destination="destination=41.349302,2.136480",
            geometry="polyline",
            lang="lang=en",
            mode="car",
            origin="origin=41.349302,2.136480",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
            overview="full",
            waypoints="waypoints=41.349302,2.136480|41.349303,2.136481|41.349304,2.136482",
        )
        assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_route(self, client: NextbillionSDK) -> None:
        response = client.navigation.with_raw_response.retrieve_route(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        navigation = response.parse()
        assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_route(self, client: NextbillionSDK) -> None:
        with client.navigation.with_streaming_response.retrieve_route(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            navigation = response.parse()
            assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNavigation:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_route(self, async_client: AsyncNextbillionSDK) -> None:
        navigation = await async_client.navigation.retrieve_route(
            key="key=API_KEY",
        )
        assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_route_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        navigation = await async_client.navigation.retrieve_route(
            key="key=API_KEY",
            altcount=1,
            alternatives=True,
            approaches="unrestricted",
            avoid="toll",
            bearings="bearings=0,180;0,180",
            destination="destination=41.349302,2.136480",
            geometry="polyline",
            lang="lang=en",
            mode="car",
            origin="origin=41.349302,2.136480",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
            overview="full",
            waypoints="waypoints=41.349302,2.136480|41.349303,2.136481|41.349304,2.136482",
        )
        assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_route(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.navigation.with_raw_response.retrieve_route(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        navigation = await response.parse()
        assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_route(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.navigation.with_streaming_response.retrieve_route(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            navigation = await response.parse()
            assert_matches_type(NavigationRetrieveRouteResponse, navigation, path=["response"])

        assert cast(Any, response.is_closed) is True
