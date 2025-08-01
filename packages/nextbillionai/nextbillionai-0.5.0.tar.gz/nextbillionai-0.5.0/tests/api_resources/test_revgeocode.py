# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import RevgeocodeRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRevgeocode:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        revgeocode = client.revgeocode.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
        )
        assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        revgeocode = client.revgeocode.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
        )
        assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.revgeocode.with_raw_response.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        revgeocode = response.parse()
        assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.revgeocode.with_streaming_response.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            revgeocode = response.parse()
            assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRevgeocode:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        revgeocode = await async_client.revgeocode.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
        )
        assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        revgeocode = await async_client.revgeocode.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
        )
        assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.revgeocode.with_raw_response.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        revgeocode = await response.parse()
        assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.revgeocode.with_streaming_response.retrieve(
            at="at=52.5308,13.3856",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            revgeocode = await response.parse()
            assert_matches_type(RevgeocodeRetrieveResponse, revgeocode, path=["response"])

        assert cast(Any, response.is_closed) is True
