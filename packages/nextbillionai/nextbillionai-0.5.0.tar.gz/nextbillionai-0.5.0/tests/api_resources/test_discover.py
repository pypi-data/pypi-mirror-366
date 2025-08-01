# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import DiscoverRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDiscover:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        discover = client.discover.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )
        assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        discover = client.discover.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
            at="at=52.5308,13.3856",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
            limit=0,
        )
        assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.discover.with_raw_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        discover = response.parse()
        assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.discover.with_streaming_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            discover = response.parse()
            assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDiscover:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        discover = await async_client.discover.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )
        assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        discover = await async_client.discover.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
            at="at=52.5308,13.3856",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
            limit=0,
        )
        assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.discover.with_raw_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        discover = await response.parse()
        assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.discover.with_streaming_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            discover = await response.parse()
            assert_matches_type(DiscoverRetrieveResponse, discover, path=["response"])

        assert cast(Any, response.is_closed) is True
