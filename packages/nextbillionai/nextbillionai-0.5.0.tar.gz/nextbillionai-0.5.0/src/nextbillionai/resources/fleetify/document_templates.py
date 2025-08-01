# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.fleetify import (
    document_template_list_params,
    document_template_create_params,
    document_template_delete_params,
    document_template_update_params,
    document_template_retrieve_params,
)
from ...types.fleetify.document_template_list_response import DocumentTemplateListResponse
from ...types.fleetify.document_template_create_response import DocumentTemplateCreateResponse
from ...types.fleetify.document_template_delete_response import DocumentTemplateDeleteResponse
from ...types.fleetify.document_template_update_response import DocumentTemplateUpdateResponse
from ...types.fleetify.document_template_retrieve_response import DocumentTemplateRetrieveResponse
from ...types.fleetify.document_template_content_request_param import DocumentTemplateContentRequestParam

__all__ = ["DocumentTemplatesResource", "AsyncDocumentTemplatesResource"]


class DocumentTemplatesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentTemplatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return DocumentTemplatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentTemplatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return DocumentTemplatesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        content: Iterable[DocumentTemplateContentRequestParam],
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateCreateResponse:
        """
        Create Document template

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          content: A form field that drivers must complete when executing a route step. Defines the
              data structure and validation rules for collecting required information during
              route execution.

          name: Specify a name for the document template to be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/fleetify/document_templates",
            body=maybe_transform(
                {
                    "content": content,
                    "name": name,
                },
                document_template_create_params.DocumentTemplateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, document_template_create_params.DocumentTemplateCreateParams),
            ),
            cast_to=DocumentTemplateCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateRetrieveResponse:
        """
        Retrieve template by ID

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/fleetify/document_templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, document_template_retrieve_params.DocumentTemplateRetrieveParams),
            ),
            cast_to=DocumentTemplateRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        key: str,
        content: Iterable[DocumentTemplateContentRequestParam] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateUpdateResponse:
        """
        Update a document template

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          content: An object to collect the details of form fields to be updated - data structures,
              validation rules. Please note that the details provided here will overwrite any
              existing document fields in the given template.

          name: Specify the document template name to be updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/fleetify/document_templates/{id}",
            body=maybe_transform(
                {
                    "content": content,
                    "name": name,
                },
                document_template_update_params.DocumentTemplateUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, document_template_update_params.DocumentTemplateUpdateParams),
            ),
            cast_to=DocumentTemplateUpdateResponse,
        )

    def list(
        self,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateListResponse:
        """
        Get all document templates

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/fleetify/document_templates",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, document_template_list_params.DocumentTemplateListParams),
            ),
            cast_to=DocumentTemplateListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateDeleteResponse:
        """
        Delete a document template

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/fleetify/document_templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, document_template_delete_params.DocumentTemplateDeleteParams),
            ),
            cast_to=DocumentTemplateDeleteResponse,
        )


class AsyncDocumentTemplatesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentTemplatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentTemplatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentTemplatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncDocumentTemplatesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        content: Iterable[DocumentTemplateContentRequestParam],
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateCreateResponse:
        """
        Create Document template

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          content: A form field that drivers must complete when executing a route step. Defines the
              data structure and validation rules for collecting required information during
              route execution.

          name: Specify a name for the document template to be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/fleetify/document_templates",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "name": name,
                },
                document_template_create_params.DocumentTemplateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, document_template_create_params.DocumentTemplateCreateParams
                ),
            ),
            cast_to=DocumentTemplateCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateRetrieveResponse:
        """
        Retrieve template by ID

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/fleetify/document_templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, document_template_retrieve_params.DocumentTemplateRetrieveParams
                ),
            ),
            cast_to=DocumentTemplateRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        key: str,
        content: Iterable[DocumentTemplateContentRequestParam] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateUpdateResponse:
        """
        Update a document template

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          content: An object to collect the details of form fields to be updated - data structures,
              validation rules. Please note that the details provided here will overwrite any
              existing document fields in the given template.

          name: Specify the document template name to be updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/fleetify/document_templates/{id}",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "name": name,
                },
                document_template_update_params.DocumentTemplateUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, document_template_update_params.DocumentTemplateUpdateParams
                ),
            ),
            cast_to=DocumentTemplateUpdateResponse,
        )

    async def list(
        self,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateListResponse:
        """
        Get all document templates

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/fleetify/document_templates",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, document_template_list_params.DocumentTemplateListParams
                ),
            ),
            cast_to=DocumentTemplateListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTemplateDeleteResponse:
        """
        Delete a document template

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/fleetify/document_templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, document_template_delete_params.DocumentTemplateDeleteParams
                ),
            ),
            cast_to=DocumentTemplateDeleteResponse,
        )


class DocumentTemplatesResourceWithRawResponse:
    def __init__(self, document_templates: DocumentTemplatesResource) -> None:
        self._document_templates = document_templates

        self.create = to_raw_response_wrapper(
            document_templates.create,
        )
        self.retrieve = to_raw_response_wrapper(
            document_templates.retrieve,
        )
        self.update = to_raw_response_wrapper(
            document_templates.update,
        )
        self.list = to_raw_response_wrapper(
            document_templates.list,
        )
        self.delete = to_raw_response_wrapper(
            document_templates.delete,
        )


class AsyncDocumentTemplatesResourceWithRawResponse:
    def __init__(self, document_templates: AsyncDocumentTemplatesResource) -> None:
        self._document_templates = document_templates

        self.create = async_to_raw_response_wrapper(
            document_templates.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            document_templates.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            document_templates.update,
        )
        self.list = async_to_raw_response_wrapper(
            document_templates.list,
        )
        self.delete = async_to_raw_response_wrapper(
            document_templates.delete,
        )


class DocumentTemplatesResourceWithStreamingResponse:
    def __init__(self, document_templates: DocumentTemplatesResource) -> None:
        self._document_templates = document_templates

        self.create = to_streamed_response_wrapper(
            document_templates.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            document_templates.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            document_templates.update,
        )
        self.list = to_streamed_response_wrapper(
            document_templates.list,
        )
        self.delete = to_streamed_response_wrapper(
            document_templates.delete,
        )


class AsyncDocumentTemplatesResourceWithStreamingResponse:
    def __init__(self, document_templates: AsyncDocumentTemplatesResource) -> None:
        self._document_templates = document_templates

        self.create = async_to_streamed_response_wrapper(
            document_templates.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            document_templates.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            document_templates.update,
        )
        self.list = async_to_streamed_response_wrapper(
            document_templates.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            document_templates.delete,
        )
