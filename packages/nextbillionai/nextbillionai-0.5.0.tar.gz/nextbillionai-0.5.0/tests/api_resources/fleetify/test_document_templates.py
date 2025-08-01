# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillionai import NextbillionSDK, AsyncNextbillionSDK
from nextbillionai.types.fleetify import (
    DocumentTemplateListResponse,
    DocumentTemplateCreateResponse,
    DocumentTemplateDeleteResponse,
    DocumentTemplateUpdateResponse,
    DocumentTemplateRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocumentTemplates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        document_template = client.fleetify.document_templates.create(
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                }
            ],
            name="name",
        )
        assert_matches_type(DocumentTemplateCreateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.fleetify.document_templates.with_raw_response.create(
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                }
            ],
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = response.parse()
        assert_matches_type(DocumentTemplateCreateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.fleetify.document_templates.with_streaming_response.create(
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                }
            ],
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = response.parse()
            assert_matches_type(DocumentTemplateCreateResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: NextbillionSDK) -> None:
        document_template = client.fleetify.document_templates.retrieve(
            id="id",
            key="key",
        )
        assert_matches_type(DocumentTemplateRetrieveResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: NextbillionSDK) -> None:
        response = client.fleetify.document_templates.with_raw_response.retrieve(
            id="id",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = response.parse()
        assert_matches_type(DocumentTemplateRetrieveResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: NextbillionSDK) -> None:
        with client.fleetify.document_templates.with_streaming_response.retrieve(
            id="id",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = response.parse()
            assert_matches_type(DocumentTemplateRetrieveResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fleetify.document_templates.with_raw_response.retrieve(
                id="",
                key="key",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: NextbillionSDK) -> None:
        document_template = client.fleetify.document_templates.update(
            id="id",
            key="key",
        )
        assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: NextbillionSDK) -> None:
        document_template = client.fleetify.document_templates.update(
            id="id",
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                    "meta": {
                        "options": [
                            {
                                "label": '"label": "Option 1"',
                                "value": '"value": "Car"',
                            }
                        ]
                    },
                    "name": '"name" : "Completion DateTime"',
                    "required": True,
                    "validation": {
                        "max": 0,
                        "max_items": 0,
                        "min": 0,
                        "min_items": 0,
                    },
                }
            ],
            name="name",
        )
        assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: NextbillionSDK) -> None:
        response = client.fleetify.document_templates.with_raw_response.update(
            id="id",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = response.parse()
        assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: NextbillionSDK) -> None:
        with client.fleetify.document_templates.with_streaming_response.update(
            id="id",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = response.parse()
            assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fleetify.document_templates.with_raw_response.update(
                id="",
                key="key",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        document_template = client.fleetify.document_templates.list(
            key="key",
        )
        assert_matches_type(DocumentTemplateListResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.fleetify.document_templates.with_raw_response.list(
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = response.parse()
        assert_matches_type(DocumentTemplateListResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.fleetify.document_templates.with_streaming_response.list(
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = response.parse()
            assert_matches_type(DocumentTemplateListResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: NextbillionSDK) -> None:
        document_template = client.fleetify.document_templates.delete(
            id="id",
            key="key",
        )
        assert_matches_type(DocumentTemplateDeleteResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: NextbillionSDK) -> None:
        response = client.fleetify.document_templates.with_raw_response.delete(
            id="id",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = response.parse()
        assert_matches_type(DocumentTemplateDeleteResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: NextbillionSDK) -> None:
        with client.fleetify.document_templates.with_streaming_response.delete(
            id="id",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = response.parse()
            assert_matches_type(DocumentTemplateDeleteResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fleetify.document_templates.with_raw_response.delete(
                id="",
                key="key",
            )


class TestAsyncDocumentTemplates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        document_template = await async_client.fleetify.document_templates.create(
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                }
            ],
            name="name",
        )
        assert_matches_type(DocumentTemplateCreateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.document_templates.with_raw_response.create(
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                }
            ],
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = await response.parse()
        assert_matches_type(DocumentTemplateCreateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.document_templates.with_streaming_response.create(
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                }
            ],
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = await response.parse()
            assert_matches_type(DocumentTemplateCreateResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        document_template = await async_client.fleetify.document_templates.retrieve(
            id="id",
            key="key",
        )
        assert_matches_type(DocumentTemplateRetrieveResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.document_templates.with_raw_response.retrieve(
            id="id",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = await response.parse()
        assert_matches_type(DocumentTemplateRetrieveResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.document_templates.with_streaming_response.retrieve(
            id="id",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = await response.parse()
            assert_matches_type(DocumentTemplateRetrieveResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fleetify.document_templates.with_raw_response.retrieve(
                id="",
                key="key",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncNextbillionSDK) -> None:
        document_template = await async_client.fleetify.document_templates.update(
            id="id",
            key="key",
        )
        assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        document_template = await async_client.fleetify.document_templates.update(
            id="id",
            key="key",
            content=[
                {
                    "label": '"label": "Specify Completion Time"',
                    "type": "string",
                    "meta": {
                        "options": [
                            {
                                "label": '"label": "Option 1"',
                                "value": '"value": "Car"',
                            }
                        ]
                    },
                    "name": '"name" : "Completion DateTime"',
                    "required": True,
                    "validation": {
                        "max": 0,
                        "max_items": 0,
                        "min": 0,
                        "min_items": 0,
                    },
                }
            ],
            name="name",
        )
        assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.document_templates.with_raw_response.update(
            id="id",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = await response.parse()
        assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.document_templates.with_streaming_response.update(
            id="id",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = await response.parse()
            assert_matches_type(DocumentTemplateUpdateResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fleetify.document_templates.with_raw_response.update(
                id="",
                key="key",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        document_template = await async_client.fleetify.document_templates.list(
            key="key",
        )
        assert_matches_type(DocumentTemplateListResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.document_templates.with_raw_response.list(
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = await response.parse()
        assert_matches_type(DocumentTemplateListResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.document_templates.with_streaming_response.list(
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = await response.parse()
            assert_matches_type(DocumentTemplateListResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncNextbillionSDK) -> None:
        document_template = await async_client.fleetify.document_templates.delete(
            id="id",
            key="key",
        )
        assert_matches_type(DocumentTemplateDeleteResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.fleetify.document_templates.with_raw_response.delete(
            id="id",
            key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document_template = await response.parse()
        assert_matches_type(DocumentTemplateDeleteResponse, document_template, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.fleetify.document_templates.with_streaming_response.delete(
            id="id",
            key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document_template = await response.parse()
            assert_matches_type(DocumentTemplateDeleteResponse, document_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fleetify.document_templates.with_raw_response.delete(
                id="",
                key="key",
            )
