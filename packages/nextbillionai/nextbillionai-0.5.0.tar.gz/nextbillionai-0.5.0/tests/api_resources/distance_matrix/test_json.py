# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.distance_matrix import JsonRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestJson:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        json = client.distance_matrix.json.create()
        assert json is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.distance_matrix.json.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        json = response.parse()
        assert json is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.distance_matrix.json.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            json = response.parse()
            assert json is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        json = client.distance_matrix.json.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
        )
        assert_matches_type(JsonRetrieveResponse, json, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        json = client.distance_matrix.json.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            approaches="unrestricted",
            avoid="toll",
            bearings="bearings=0,180;0,180",
            mode="car",
            route_failed_prompt=True,
        )
        assert_matches_type(JsonRetrieveResponse, json, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.distance_matrix.json.with_raw_response.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        json = response.parse()
        assert_matches_type(JsonRetrieveResponse, json, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.distance_matrix.json.with_streaming_response.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            json = response.parse()
            assert_matches_type(JsonRetrieveResponse, json, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncJson:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        json = await async_client.distance_matrix.json.create()
        assert json is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.distance_matrix.json.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        json = await response.parse()
        assert json is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.distance_matrix.json.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            json = await response.parse()
            assert json is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        json = await async_client.distance_matrix.json.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
        )
        assert_matches_type(JsonRetrieveResponse, json, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        json = await async_client.distance_matrix.json.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            approaches="unrestricted",
            avoid="toll",
            bearings="bearings=0,180;0,180",
            mode="car",
            route_failed_prompt=True,
        )
        assert_matches_type(JsonRetrieveResponse, json, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.distance_matrix.json.with_raw_response.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        json = await response.parse()
        assert_matches_type(JsonRetrieveResponse, json, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.distance_matrix.json.with_streaming_response.retrieve(
            destinations="destinations=41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
            key="key=API_KEY",
            origins="origins:41.349302,2.136480|41.389925,2.136258|41.357961,2.097878",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            json = await response.parse()
            assert_matches_type(JsonRetrieveResponse, json, path=["response"])

        assert cast(Any, response.is_closed) is True
