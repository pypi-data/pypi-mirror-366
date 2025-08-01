# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types import (
    GeocodeRetrieveResponse,
    GeocodeBatchCreateResponse,
    GeocodeStructuredRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGeocode:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        geocode = client.geocode.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )
        assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        geocode = client.geocode.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
            at="at=52.5308,13.3856",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
            limit=0,
        )
        assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.geocode.with_raw_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode = response.parse()
        assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.geocode.with_streaming_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode = response.parse()
            assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_batch_create(self, client: NextbillionSDK) -> None:
        geocode = client.geocode.batch_create(
            key="key=API_KEY",
            body=[{"q": '"q":"125, Berliner, berlin"'}],
        )
        assert_matches_type(GeocodeBatchCreateResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_batch_create(self, client: NextbillionSDK) -> None:
        response = client.geocode.with_raw_response.batch_create(
            key="key=API_KEY",
            body=[{"q": '"q":"125, Berliner, berlin"'}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode = response.parse()
        assert_matches_type(GeocodeBatchCreateResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_batch_create(self, client: NextbillionSDK) -> None:
        with client.geocode.with_streaming_response.batch_create(
            key="key=API_KEY",
            body=[{"q": '"q":"125, Berliner, berlin"'}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode = response.parse()
            assert_matches_type(GeocodeBatchCreateResponse, geocode, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_structured_retrieve(self, client: NextbillionSDK) -> None:
        geocode = client.geocode.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
        )
        assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_structured_retrieve_with_all_params(self, client: NextbillionSDK) -> None:
        geocode = client.geocode.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
            at="at=52.5308,13.3856",
            city="city",
            county="county",
            house_number="houseNumber",
            in_="in=circle:52.53,13.38;r=10000",
            limit=0,
            postal_code="postalCode",
            state="state",
            street="street",
        )
        assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_structured_retrieve(self, client: NextbillionSDK) -> None:
        response = client.geocode.with_raw_response.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode = response.parse()
        assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_structured_retrieve(self, client: NextbillionSDK) -> None:
        with client.geocode.with_streaming_response.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode = response.parse()
            assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGeocode:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        geocode = await async_client.geocode.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )
        assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        geocode = await async_client.geocode.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
            at="at=52.5308,13.3856",
            in_="in=countryCode:CAN,MEX,USA",
            lang="lang=en",
            limit=0,
        )
        assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geocode.with_raw_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode = await response.parse()
        assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geocode.with_streaming_response.retrieve(
            key="key=API_KEY",
            q="q=125, Berliner, berlin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode = await response.parse()
            assert_matches_type(GeocodeRetrieveResponse, geocode, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_batch_create(self, async_client: AsyncNextbillionSDK) -> None:
        geocode = await async_client.geocode.batch_create(
            key="key=API_KEY",
            body=[{"q": '"q":"125, Berliner, berlin"'}],
        )
        assert_matches_type(GeocodeBatchCreateResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_batch_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geocode.with_raw_response.batch_create(
            key="key=API_KEY",
            body=[{"q": '"q":"125, Berliner, berlin"'}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode = await response.parse()
        assert_matches_type(GeocodeBatchCreateResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_batch_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geocode.with_streaming_response.batch_create(
            key="key=API_KEY",
            body=[{"q": '"q":"125, Berliner, berlin"'}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode = await response.parse()
            assert_matches_type(GeocodeBatchCreateResponse, geocode, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_structured_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        geocode = await async_client.geocode.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
        )
        assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_structured_retrieve_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        geocode = await async_client.geocode.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
            at="at=52.5308,13.3856",
            city="city",
            county="county",
            house_number="houseNumber",
            in_="in=circle:52.53,13.38;r=10000",
            limit=0,
            postal_code="postalCode",
            state="state",
            street="street",
        )
        assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_structured_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.geocode.with_raw_response.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode = await response.parse()
        assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_structured_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.geocode.with_streaming_response.structured_retrieve(
            country_code="countryCode",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode = await response.parse()
            assert_matches_type(GeocodeStructuredRetrieveResponse, geocode, path=["response"])

        assert cast(Any, response.is_closed) is True
