# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import PostalcodeRetrieveCoordinatesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPostalcode:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_coordinates(self, client: NextbillionSDK) -> None:
        postalcode = client.postalcode.retrieve_coordinates(
            key="key=API_KEY",
        )
        assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_coordinates_with_all_params(self, client: NextbillionSDK) -> None:
        postalcode = client.postalcode.retrieve_coordinates(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            country="country",
            format="geojson",
            postalcode="postalcode",
        )
        assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_coordinates(self, client: NextbillionSDK) -> None:
        response = client.postalcode.with_raw_response.retrieve_coordinates(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        postalcode = response.parse()
        assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_coordinates(self, client: NextbillionSDK) -> None:
        with client.postalcode.with_streaming_response.retrieve_coordinates(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            postalcode = response.parse()
            assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPostalcode:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_coordinates(self, async_client: AsyncNextbillionSDK) -> None:
        postalcode = await async_client.postalcode.retrieve_coordinates(
            key="key=API_KEY",
        )
        assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_coordinates_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        postalcode = await async_client.postalcode.retrieve_coordinates(
            key="key=API_KEY",
            at={
                "lat": 0,
                "lng": 0,
            },
            country="country",
            format="geojson",
            postalcode="postalcode",
        )
        assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_coordinates(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.postalcode.with_raw_response.retrieve_coordinates(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        postalcode = await response.parse()
        assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_coordinates(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.postalcode.with_streaming_response.retrieve_coordinates(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            postalcode = await response.parse()
            assert_matches_type(PostalcodeRetrieveCoordinatesResponse, postalcode, path=["response"])

        assert cast(Any, response.is_closed) is True
