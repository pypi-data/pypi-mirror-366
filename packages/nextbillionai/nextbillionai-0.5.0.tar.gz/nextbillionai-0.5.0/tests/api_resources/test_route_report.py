# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import RouteReportCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRouteReport:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        route_report = client.route_report.create(
            key="key=API_KEY",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
        )
        assert_matches_type(RouteReportCreateResponse, route_report, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.route_report.with_raw_response.create(
            key="key=API_KEY",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        route_report = response.parse()
        assert_matches_type(RouteReportCreateResponse, route_report, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.route_report.with_streaming_response.create(
            key="key=API_KEY",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            route_report = response.parse()
            assert_matches_type(RouteReportCreateResponse, route_report, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRouteReport:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        route_report = await async_client.route_report.create(
            key="key=API_KEY",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
        )
        assert_matches_type(RouteReportCreateResponse, route_report, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.route_report.with_raw_response.create(
            key="key=API_KEY",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        route_report = await response.parse()
        assert_matches_type(RouteReportCreateResponse, route_report, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.route_report.with_streaming_response.create(
            key="key=API_KEY",
            original_shape="original_shape=sbp}_AlmgpFnLuToKmKviB{eDlcGhpFvj@qbAwoA_mA",
            original_shape_type="polyline",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            route_report = await response.parse()
            assert_matches_type(RouteReportCreateResponse, route_report, path=["response"])

        assert cast(Any, response.is_closed) is True
