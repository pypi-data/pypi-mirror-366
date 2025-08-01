# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.multigeocode import (
    PlaceCreateResponse,
    PlaceDeleteResponse,
    PlaceUpdateResponse,
    PlaceRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPlace:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        place = client.multigeocode.place.create(
            key="key=API_KEY",
            place=[{"geopoint": {}}],
        )
        assert_matches_type(PlaceCreateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        place = client.multigeocode.place.create(
            key="key=API_KEY",
            place=[
                {
                    "geopoint": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "address": "address",
                    "building": "building",
                    "city": "city",
                    "country": '"country":"IND"',
                    "district": "district",
                    "house": "house",
                    "poi": {"title": "title"},
                    "postal_code": "postalCode",
                    "state": "state",
                    "street": "street",
                    "sub_district": "subDistrict",
                }
            ],
            data_source={
                "ref_id": "refId",
                "source": "source",
                "status": "enable",
            },
            force=True,
            score=0,
        )
        assert_matches_type(PlaceCreateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.multigeocode.place.with_raw_response.create(
            key="key=API_KEY",
            place=[{"geopoint": {}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = response.parse()
        assert_matches_type(PlaceCreateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.multigeocode.place.with_streaming_response.create(
            key="key=API_KEY",
            place=[{"geopoint": {}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = response.parse()
            assert_matches_type(PlaceCreateResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        place = client.multigeocode.place.retrieve(
            doc_id="docId",
            key="key=API_KEY",
        )
        assert_matches_type(PlaceRetrieveResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.multigeocode.place.with_raw_response.retrieve(
            doc_id="docId",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = response.parse()
        assert_matches_type(PlaceRetrieveResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.multigeocode.place.with_streaming_response.retrieve(
            doc_id="docId",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = response.parse()
            assert_matches_type(PlaceRetrieveResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.multigeocode.place.with_raw_response.retrieve(
                doc_id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        place = client.multigeocode.place.update(
            doc_id="docId",
            key="key=API_KEY",
        )
        assert_matches_type(PlaceUpdateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        place = client.multigeocode.place.update(
            doc_id="docId",
            key="key=API_KEY",
            data_source={
                "ref_id": "refId",
                "source": "source",
                "status": "enable",
            },
            place=[
                {
                    "address": "address",
                    "building": "building",
                    "city": "city",
                    "country": "country",
                    "district": "district",
                    "geopoint": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "house": "house",
                    "poi": {"title": "title"},
                    "postal_code": "postalCode",
                    "state": "state",
                    "street": "street",
                    "sub_district": "subDistrict",
                }
            ],
            score=0,
        )
        assert_matches_type(PlaceUpdateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.multigeocode.place.with_raw_response.update(
            doc_id="docId",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = response.parse()
        assert_matches_type(PlaceUpdateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.multigeocode.place.with_streaming_response.update(
            doc_id="docId",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = response.parse()
            assert_matches_type(PlaceUpdateResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.multigeocode.place.with_raw_response.update(
                doc_id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        place = client.multigeocode.place.delete(
            doc_id="docId",
            key="key=API_KEY",
        )
        assert_matches_type(PlaceDeleteResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.multigeocode.place.with_raw_response.delete(
            doc_id="docId",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = response.parse()
        assert_matches_type(PlaceDeleteResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.multigeocode.place.with_streaming_response.delete(
            doc_id="docId",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = response.parse()
            assert_matches_type(PlaceDeleteResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.multigeocode.place.with_raw_response.delete(
                doc_id="",
                key="key=API_KEY",
            )


class TestAsyncPlace:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        place = await async_client.multigeocode.place.create(
            key="key=API_KEY",
            place=[{"geopoint": {}}],
        )
        assert_matches_type(PlaceCreateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        place = await async_client.multigeocode.place.create(
            key="key=API_KEY",
            place=[
                {
                    "geopoint": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "address": "address",
                    "building": "building",
                    "city": "city",
                    "country": '"country":"IND"',
                    "district": "district",
                    "house": "house",
                    "poi": {"title": "title"},
                    "postal_code": "postalCode",
                    "state": "state",
                    "street": "street",
                    "sub_district": "subDistrict",
                }
            ],
            data_source={
                "ref_id": "refId",
                "source": "source",
                "status": "enable",
            },
            force=True,
            score=0,
        )
        assert_matches_type(PlaceCreateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.multigeocode.place.with_raw_response.create(
            key="key=API_KEY",
            place=[{"geopoint": {}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = await response.parse()
        assert_matches_type(PlaceCreateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.multigeocode.place.with_streaming_response.create(
            key="key=API_KEY",
            place=[{"geopoint": {}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = await response.parse()
            assert_matches_type(PlaceCreateResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        place = await async_client.multigeocode.place.retrieve(
            doc_id="docId",
            key="key=API_KEY",
        )
        assert_matches_type(PlaceRetrieveResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.multigeocode.place.with_raw_response.retrieve(
            doc_id="docId",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = await response.parse()
        assert_matches_type(PlaceRetrieveResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.multigeocode.place.with_streaming_response.retrieve(
            doc_id="docId",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = await response.parse()
            assert_matches_type(PlaceRetrieveResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.multigeocode.place.with_raw_response.retrieve(
                doc_id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        place = await async_client.multigeocode.place.update(
            doc_id="docId",
            key="key=API_KEY",
        )
        assert_matches_type(PlaceUpdateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        place = await async_client.multigeocode.place.update(
            doc_id="docId",
            key="key=API_KEY",
            data_source={
                "ref_id": "refId",
                "source": "source",
                "status": "enable",
            },
            place=[
                {
                    "address": "address",
                    "building": "building",
                    "city": "city",
                    "country": "country",
                    "district": "district",
                    "geopoint": {
                        "lat": 0,
                        "lng": 0,
                    },
                    "house": "house",
                    "poi": {"title": "title"},
                    "postal_code": "postalCode",
                    "state": "state",
                    "street": "street",
                    "sub_district": "subDistrict",
                }
            ],
            score=0,
        )
        assert_matches_type(PlaceUpdateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.multigeocode.place.with_raw_response.update(
            doc_id="docId",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = await response.parse()
        assert_matches_type(PlaceUpdateResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.multigeocode.place.with_streaming_response.update(
            doc_id="docId",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = await response.parse()
            assert_matches_type(PlaceUpdateResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.multigeocode.place.with_raw_response.update(
                doc_id="",
                key="key=API_KEY",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        place = await async_client.multigeocode.place.delete(
            doc_id="docId",
            key="key=API_KEY",
        )
        assert_matches_type(PlaceDeleteResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.multigeocode.place.with_raw_response.delete(
            doc_id="docId",
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        place = await response.parse()
        assert_matches_type(PlaceDeleteResponse, place, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.multigeocode.place.with_streaming_response.delete(
            doc_id="docId",
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            place = await response.parse()
            assert_matches_type(PlaceDeleteResponse, place, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.multigeocode.place.with_raw_response.delete(
                doc_id="",
                key="key=API_KEY",
            )
