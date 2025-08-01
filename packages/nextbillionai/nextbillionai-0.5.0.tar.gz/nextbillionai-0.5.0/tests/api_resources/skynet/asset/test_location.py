# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.skynet.asset import (
    LocationListResponse,
    LocationGetLastResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLocation:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        location = client.skynet.asset.location.list(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(LocationListResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        location = client.skynet.asset.location.list(
            id="id",
            key="key=API_KEY",
            cluster="america",
            correction="correction=mapmatch=1,interpolate=0,mode=car",
            end_time=0,
            geometry_type="polyline",
            pn=0,
            ps=500,
            start_time=0,
        )
        assert_matches_type(LocationListResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.location.with_raw_response.list(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        location = response.parse()
        assert_matches_type(LocationListResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.location.with_streaming_response.list(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            location = response.parse()
            assert_matches_type(LocationListResponse, location, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.location.with_raw_response.list(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_last(self, client: NextbillionSDK) -> None:
        location = client.skynet.asset.location.get_last(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(LocationGetLastResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_last_with_all_params(self, client: NextbillionSDK) -> None:
        location = client.skynet.asset.location.get_last(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(LocationGetLastResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_last(self, client: NextbillionSDK) -> None:
        response = client.skynet.asset.location.with_raw_response.get_last(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        location = response.parse()
        assert_matches_type(LocationGetLastResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_last(self, client: NextbillionSDK) -> None:
        with client.skynet.asset.location.with_streaming_response.get_last(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            location = response.parse()
            assert_matches_type(LocationGetLastResponse, location, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_last(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.asset.location.with_raw_response.get_last(
                id="",
                key="key=API_KEY",
            )


class TestAsyncLocation:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        location = await async_client.skynet.asset.location.list(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(LocationListResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        location = await async_client.skynet.asset.location.list(
            id="id",
            key="key=API_KEY",
            cluster="america",
            correction="correction=mapmatch=1,interpolate=0,mode=car",
            end_time=0,
            geometry_type="polyline",
            pn=0,
            ps=500,
            start_time=0,
        )
        assert_matches_type(LocationListResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.location.with_raw_response.list(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        location = await response.parse()
        assert_matches_type(LocationListResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.location.with_streaming_response.list(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            location = await response.parse()
            assert_matches_type(LocationListResponse, location, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.location.with_raw_response.list(
                id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_last(self, async_client: AsyncNextbillionSDK) -> None:
        location = await async_client.skynet.asset.location.get_last(
            id="id",
            key="key=API_KEY",
        )
        assert_matches_type(LocationGetLastResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_last_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        location = await async_client.skynet.asset.location.get_last(
            id="id",
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(LocationGetLastResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_last(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.asset.location.with_raw_response.get_last(
            id="id",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        location = await response.parse()
        assert_matches_type(LocationGetLastResponse, location, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_last(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.asset.location.with_streaming_response.get_last(
            id="id",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            location = await response.parse()
            assert_matches_type(LocationGetLastResponse, location, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_last(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.asset.location.with_raw_response.get_last(
                id="",
                key="key=API_KEY",
            )
