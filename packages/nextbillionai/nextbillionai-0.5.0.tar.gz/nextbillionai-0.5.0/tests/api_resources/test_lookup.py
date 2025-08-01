# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import LookupByIDResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLookup:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_by_id(self, client: NextbillionSDK) -> None:
        lookup = client.lookup.by_id(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(LookupByIDResponse, lookup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_by_id(self, client: NextbillionSDK) -> None:
        response = client.lookup.with_raw_response.by_id(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lookup = response.parse()
        assert_matches_type(LookupByIDResponse, lookup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_by_id(self, client: NextbillionSDK) -> None:
        with client.lookup.with_streaming_response.by_id(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lookup = response.parse()
            assert_matches_type(LookupByIDResponse, lookup, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLookup:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_by_id(self, async_client: AsyncNextbillionSDK) -> None:
        lookup = await async_client.lookup.by_id(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(LookupByIDResponse, lookup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_by_id(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.lookup.with_raw_response.by_id(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lookup = await response.parse()
        assert_matches_type(LookupByIDResponse, lookup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_by_id(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.lookup.with_streaming_response.by_id(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lookup = await response.parse()
            assert_matches_type(LookupByIDResponse, lookup, path=["response"])

        assert cast(Any, response.is_closed) is True
