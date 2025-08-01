# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import BrowseSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBrowse:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: NextbillionSDK) -> None:
        browse = client.browse.search(
            key="key=API_KEY",
        )
        assert_matches_type(BrowseSearchResponse, browse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_with_all_params(self, client: NextbillionSDK) -> None:
        browse = client.browse.search(
            key="key=API_KEY",
            at="at=52.5308,13.3856",
            categories="categories: schools",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
            limit=0,
        )
        assert_matches_type(BrowseSearchResponse, browse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: NextbillionSDK) -> None:
        response = client.browse.with_raw_response.search(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browse = response.parse()
        assert_matches_type(BrowseSearchResponse, browse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: NextbillionSDK) -> None:
        with client.browse.with_streaming_response.search(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browse = response.parse()
            assert_matches_type(BrowseSearchResponse, browse, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBrowse:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncNextbillionSDK) -> None:
        browse = await async_client.browse.search(
            key="key=API_KEY",
        )
        assert_matches_type(BrowseSearchResponse, browse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        browse = await async_client.browse.search(
            key="key=API_KEY",
            at="at=52.5308,13.3856",
            categories="categories: schools",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
            limit=0,
        )
        assert_matches_type(BrowseSearchResponse, browse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.browse.with_raw_response.search(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browse = await response.parse()
        assert_matches_type(BrowseSearchResponse, browse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.browse.with_streaming_response.search(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browse = await response.parse()
            assert_matches_type(BrowseSearchResponse, browse, path=["response"])

        assert cast(Any, response.is_closed) is True
