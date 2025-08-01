# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["MapResource", "AsyncMapResource"]


class MapResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MapResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return MapResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MapResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return MapResourceWithStreamingResponse(self)

    def create_segment(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Road Segments"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/map/segments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncMapResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMapResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMapResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMapResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncMapResourceWithStreamingResponse(self)

    async def create_segment(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Road Segments"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/map/segments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class MapResourceWithRawResponse:
    def __init__(self, map: MapResource) -> None:
        self._map = map

        self.create_segment = to_raw_response_wrapper(
            map.create_segment,
        )


class AsyncMapResourceWithRawResponse:
    def __init__(self, map: AsyncMapResource) -> None:
        self._map = map

        self.create_segment = async_to_raw_response_wrapper(
            map.create_segment,
        )


class MapResourceWithStreamingResponse:
    def __init__(self, map: MapResource) -> None:
        self._map = map

        self.create_segment = to_streamed_response_wrapper(
            map.create_segment,
        )


class AsyncMapResourceWithStreamingResponse:
    def __init__(self, map: AsyncMapResource) -> None:
        self._map = map

        self.create_segment = async_to_streamed_response_wrapper(
            map.create_segment,
        )
