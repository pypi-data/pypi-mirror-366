# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import (
    MdmCreateDistanceMatrixResponse,
    MdmGetDistanceMatrixStatusResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMdm:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_distance_matrix(self, client: NextbillionSDK) -> None:
        mdm = client.mdm.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
        )
        assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_distance_matrix_with_all_params(self, client: NextbillionSDK) -> None:
        mdm = client.mdm.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
            spliter="od_number_spliter",
            area="singapore",
            avoid="toll",
            cross_border=True,
            departure_time=0,
            destinations="destinations",
            destinations_approach="unrestricted",
            hazmat_type="general",
            mode="car",
            origins_approach="unrestricted",
            route_type="fastest",
            truck_axle_load=0,
            truck_size='"truck_size"=200,210,600',
            truck_weight=0,
        )
        assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_distance_matrix(self, client: NextbillionSDK) -> None:
        response = client.mdm.with_raw_response.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mdm = response.parse()
        assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_distance_matrix(self, client: NextbillionSDK) -> None:
        with client.mdm.with_streaming_response.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mdm = response.parse()
            assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_distance_matrix_status(self, client: NextbillionSDK) -> None:
        mdm = client.mdm.get_distance_matrix_status(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(MdmGetDistanceMatrixStatusResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_distance_matrix_status(self, client: NextbillionSDK) -> None:
        response = client.mdm.with_raw_response.get_distance_matrix_status(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mdm = response.parse()
        assert_matches_type(MdmGetDistanceMatrixStatusResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_distance_matrix_status(self, client: NextbillionSDK) -> None:
        with client.mdm.with_streaming_response.get_distance_matrix_status(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mdm = response.parse()
            assert_matches_type(MdmGetDistanceMatrixStatusResponse, mdm, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMdm:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_distance_matrix(self, async_client: AsyncNextbillionSDK) -> None:
        mdm = await async_client.mdm.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
        )
        assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_distance_matrix_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        mdm = await async_client.mdm.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
            spliter="od_number_spliter",
            area="singapore",
            avoid="toll",
            cross_border=True,
            departure_time=0,
            destinations="destinations",
            destinations_approach="unrestricted",
            hazmat_type="general",
            mode="car",
            origins_approach="unrestricted",
            route_type="fastest",
            truck_axle_load=0,
            truck_size='"truck_size"=200,210,600',
            truck_weight=0,
        )
        assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_distance_matrix(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.mdm.with_raw_response.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mdm = await response.parse()
        assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_distance_matrix(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.mdm.with_streaming_response.create_distance_matrix(
            key="key=API_KEY",
            option="flexible",
            origins="origins",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mdm = await response.parse()
            assert_matches_type(MdmCreateDistanceMatrixResponse, mdm, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_distance_matrix_status(self, async_client: AsyncNextbillionSDK) -> None:
        mdm = await async_client.mdm.get_distance_matrix_status(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(MdmGetDistanceMatrixStatusResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_distance_matrix_status(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.mdm.with_raw_response.get_distance_matrix_status(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mdm = await response.parse()
        assert_matches_type(MdmGetDistanceMatrixStatusResponse, mdm, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_distance_matrix_status(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.mdm.with_streaming_response.get_distance_matrix_status(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mdm = await response.parse()
            assert_matches_type(MdmGetDistanceMatrixStatusResponse, mdm, path=["response"])

        assert cast(Any, response.is_closed) is True
