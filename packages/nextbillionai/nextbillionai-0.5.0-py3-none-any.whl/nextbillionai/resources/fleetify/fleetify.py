# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .routes.routes import (
    RoutesResource,
    AsyncRoutesResource,
    RoutesResourceWithRawResponse,
    AsyncRoutesResourceWithRawResponse,
    RoutesResourceWithStreamingResponse,
    AsyncRoutesResourceWithStreamingResponse,
)
from .document_templates import (
    DocumentTemplatesResource,
    AsyncDocumentTemplatesResource,
    DocumentTemplatesResourceWithRawResponse,
    AsyncDocumentTemplatesResourceWithRawResponse,
    DocumentTemplatesResourceWithStreamingResponse,
    AsyncDocumentTemplatesResourceWithStreamingResponse,
)

__all__ = ["FleetifyResource", "AsyncFleetifyResource"]


class FleetifyResource(SyncAPIResource):
    @cached_property
    def routes(self) -> RoutesResource:
        return RoutesResource(self._client)

    @cached_property
    def document_templates(self) -> DocumentTemplatesResource:
        return DocumentTemplatesResource(self._client)

    @cached_property
    def with_raw_response(self) -> FleetifyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FleetifyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FleetifyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return FleetifyResourceWithStreamingResponse(self)


class AsyncFleetifyResource(AsyncAPIResource):
    @cached_property
    def routes(self) -> AsyncRoutesResource:
        return AsyncRoutesResource(self._client)

    @cached_property
    def document_templates(self) -> AsyncDocumentTemplatesResource:
        return AsyncDocumentTemplatesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFleetifyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFleetifyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFleetifyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncFleetifyResourceWithStreamingResponse(self)


class FleetifyResourceWithRawResponse:
    def __init__(self, fleetify: FleetifyResource) -> None:
        self._fleetify = fleetify

    @cached_property
    def routes(self) -> RoutesResourceWithRawResponse:
        return RoutesResourceWithRawResponse(self._fleetify.routes)

    @cached_property
    def document_templates(self) -> DocumentTemplatesResourceWithRawResponse:
        return DocumentTemplatesResourceWithRawResponse(self._fleetify.document_templates)


class AsyncFleetifyResourceWithRawResponse:
    def __init__(self, fleetify: AsyncFleetifyResource) -> None:
        self._fleetify = fleetify

    @cached_property
    def routes(self) -> AsyncRoutesResourceWithRawResponse:
        return AsyncRoutesResourceWithRawResponse(self._fleetify.routes)

    @cached_property
    def document_templates(self) -> AsyncDocumentTemplatesResourceWithRawResponse:
        return AsyncDocumentTemplatesResourceWithRawResponse(self._fleetify.document_templates)


class FleetifyResourceWithStreamingResponse:
    def __init__(self, fleetify: FleetifyResource) -> None:
        self._fleetify = fleetify

    @cached_property
    def routes(self) -> RoutesResourceWithStreamingResponse:
        return RoutesResourceWithStreamingResponse(self._fleetify.routes)

    @cached_property
    def document_templates(self) -> DocumentTemplatesResourceWithStreamingResponse:
        return DocumentTemplatesResourceWithStreamingResponse(self._fleetify.document_templates)


class AsyncFleetifyResourceWithStreamingResponse:
    def __init__(self, fleetify: AsyncFleetifyResource) -> None:
        self._fleetify = fleetify

    @cached_property
    def routes(self) -> AsyncRoutesResourceWithStreamingResponse:
        return AsyncRoutesResourceWithStreamingResponse(self._fleetify.routes)

    @cached_property
    def document_templates(self) -> AsyncDocumentTemplatesResourceWithStreamingResponse:
        return AsyncDocumentTemplatesResourceWithStreamingResponse(self._fleetify.document_templates)
