# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

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
from ...types.geofence import console_search_params, console_preview_params
from ...types.geofence.console_search_response import ConsoleSearchResponse
from ...types.geofence.console_preview_response import ConsolePreviewResponse

__all__ = ["ConsoleResource", "AsyncConsoleResource"]


class ConsoleResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConsoleResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ConsoleResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConsoleResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return ConsoleResourceWithStreamingResponse(self)

    def preview(
        self,
        *,
        type: Literal["circle", "polygon", "isochrone"],
        circle: console_preview_params.Circle | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        isochrone: console_preview_params.Isochrone | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        polygon: console_preview_params.Polygon | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConsolePreviewResponse:
        """
        preview geofence geojson

        Args:
          type: Specify the type of the geofence that is being created.

          circle: Provide the details to create a circular geofence. Please note that this object
              is mandatory when type is circle. When the type is not circle, the properties of
              this object will be ignored while creating the geofence.

          custom_id: Set an unique ID for the new geofence. If not provided, an ID will be
              automatically generated in UUID format. A valid custom*id can contain letters,
              numbers, "-", & "*" only.

              Please note that the ID of a geofence can not be changed once it is created.

          isochrone: Provide the details to create an isochrone based geofence. Use this object when
              type is isochrone. When the type is not isochrone, the properties of this object
              will be ignored while creating the geofence.

          meta_data: Metadata of the geofence. Use this field to define custom attributes that
              provide more context and information about the geofence being created like
              country, group ID etc.

              The data being added should be in valid JSON object format (i.e. key and value
              pairs). Max size allowed for the object is 65kb.

          name: Name of the geofence. Use this field to assign a meaningful, custom name to the
              geofence being created.

          polygon: Provide the details to create a custom polygon type of geofence. Please note
              that this object is mandatory when type is polygon. When the type is not
              polygon, the properties of this object will be ignored while creating the
              geofence.

              Self-intersecting polygons or polygons containing other polygons are invalid and
              will be removed while processing the request.

              Area of the polygon should be less than 2000 km<sup>2</sup>.

          tags: An array of strings to associate multiple tags to the geofence. tags can be used
              to search or filter geofences (using Get Geofence List method).

              Create valid tags using a string consisting of alphanumeric characters (A-Z,
              a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/geofence/console/preview",
            body=maybe_transform(
                {
                    "type": type,
                    "circle": circle,
                    "custom_id": custom_id,
                    "isochrone": isochrone,
                    "meta_data": meta_data,
                    "name": name,
                    "polygon": polygon,
                    "tags": tags,
                },
                console_preview_params.ConsolePreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConsolePreviewResponse,
        )

    def search(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConsoleSearchResponse:
        """
        Console Geofence Search API

        Args:
          query: string to be searched, will used to match name or id of geofence.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/geofence/console/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"query": query}, console_search_params.ConsoleSearchParams),
            ),
            cast_to=ConsoleSearchResponse,
        )


class AsyncConsoleResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConsoleResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConsoleResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConsoleResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncConsoleResourceWithStreamingResponse(self)

    async def preview(
        self,
        *,
        type: Literal["circle", "polygon", "isochrone"],
        circle: console_preview_params.Circle | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        isochrone: console_preview_params.Isochrone | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        polygon: console_preview_params.Polygon | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConsolePreviewResponse:
        """
        preview geofence geojson

        Args:
          type: Specify the type of the geofence that is being created.

          circle: Provide the details to create a circular geofence. Please note that this object
              is mandatory when type is circle. When the type is not circle, the properties of
              this object will be ignored while creating the geofence.

          custom_id: Set an unique ID for the new geofence. If not provided, an ID will be
              automatically generated in UUID format. A valid custom*id can contain letters,
              numbers, "-", & "*" only.

              Please note that the ID of a geofence can not be changed once it is created.

          isochrone: Provide the details to create an isochrone based geofence. Use this object when
              type is isochrone. When the type is not isochrone, the properties of this object
              will be ignored while creating the geofence.

          meta_data: Metadata of the geofence. Use this field to define custom attributes that
              provide more context and information about the geofence being created like
              country, group ID etc.

              The data being added should be in valid JSON object format (i.e. key and value
              pairs). Max size allowed for the object is 65kb.

          name: Name of the geofence. Use this field to assign a meaningful, custom name to the
              geofence being created.

          polygon: Provide the details to create a custom polygon type of geofence. Please note
              that this object is mandatory when type is polygon. When the type is not
              polygon, the properties of this object will be ignored while creating the
              geofence.

              Self-intersecting polygons or polygons containing other polygons are invalid and
              will be removed while processing the request.

              Area of the polygon should be less than 2000 km<sup>2</sup>.

          tags: An array of strings to associate multiple tags to the geofence. tags can be used
              to search or filter geofences (using Get Geofence List method).

              Create valid tags using a string consisting of alphanumeric characters (A-Z,
              a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/geofence/console/preview",
            body=await async_maybe_transform(
                {
                    "type": type,
                    "circle": circle,
                    "custom_id": custom_id,
                    "isochrone": isochrone,
                    "meta_data": meta_data,
                    "name": name,
                    "polygon": polygon,
                    "tags": tags,
                },
                console_preview_params.ConsolePreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConsolePreviewResponse,
        )

    async def search(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConsoleSearchResponse:
        """
        Console Geofence Search API

        Args:
          query: string to be searched, will used to match name or id of geofence.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/geofence/console/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"query": query}, console_search_params.ConsoleSearchParams),
            ),
            cast_to=ConsoleSearchResponse,
        )


class ConsoleResourceWithRawResponse:
    def __init__(self, console: ConsoleResource) -> None:
        self._console = console

        self.preview = to_raw_response_wrapper(
            console.preview,
        )
        self.search = to_raw_response_wrapper(
            console.search,
        )


class AsyncConsoleResourceWithRawResponse:
    def __init__(self, console: AsyncConsoleResource) -> None:
        self._console = console

        self.preview = async_to_raw_response_wrapper(
            console.preview,
        )
        self.search = async_to_raw_response_wrapper(
            console.search,
        )


class ConsoleResourceWithStreamingResponse:
    def __init__(self, console: ConsoleResource) -> None:
        self._console = console

        self.preview = to_streamed_response_wrapper(
            console.preview,
        )
        self.search = to_streamed_response_wrapper(
            console.search,
        )


class AsyncConsoleResourceWithStreamingResponse:
    def __init__(self, console: AsyncConsoleResource) -> None:
        self._console = console

        self.preview = async_to_streamed_response_wrapper(
            console.preview,
        )
        self.search = async_to_streamed_response_wrapper(
            console.search,
        )
