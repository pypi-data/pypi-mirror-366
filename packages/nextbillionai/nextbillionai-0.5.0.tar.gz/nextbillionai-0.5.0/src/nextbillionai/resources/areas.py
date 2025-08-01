# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import area_list_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.area_list_response import AreaListResponse

__all__ = ["AreasResource", "AsyncAreasResource"]


class AreasResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AreasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AreasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AreasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AreasResourceWithStreamingResponse(self)

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
    ) -> AreaListResponse:
        """
        Get available areas

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/areas",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, area_list_params.AreaListParams),
            ),
            cast_to=AreaListResponse,
        )


class AsyncAreasResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAreasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAreasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAreasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncAreasResourceWithStreamingResponse(self)

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
    ) -> AreaListResponse:
        """
        Get available areas

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/areas",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, area_list_params.AreaListParams),
            ),
            cast_to=AreaListResponse,
        )


class AreasResourceWithRawResponse:
    def __init__(self, areas: AreasResource) -> None:
        self._areas = areas

        self.list = to_raw_response_wrapper(
            areas.list,
        )


class AsyncAreasResourceWithRawResponse:
    def __init__(self, areas: AsyncAreasResource) -> None:
        self._areas = areas

        self.list = async_to_raw_response_wrapper(
            areas.list,
        )


class AreasResourceWithStreamingResponse:
    def __init__(self, areas: AreasResource) -> None:
        self._areas = areas

        self.list = to_streamed_response_wrapper(
            areas.list,
        )


class AsyncAreasResourceWithStreamingResponse:
    def __init__(self, areas: AsyncAreasResource) -> None:
        self._areas = areas

        self.list = async_to_streamed_response_wrapper(
            areas.list,
        )
