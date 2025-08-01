# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import route_report_create_params
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
from ..types.route_report_create_response import RouteReportCreateResponse

__all__ = ["RouteReportResource", "AsyncRouteReportResource"]


class RouteReportResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RouteReportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RouteReportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RouteReportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return RouteReportResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        original_shape: str,
        original_shape_type: Literal["polyline", "polyline6"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RouteReportCreateResponse:
        """
        Route Report

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          original_shape: Takes a route geometry as input and returns the route details. Accepts polyline
              and polyline6 encoded geometry as input.

              **Note**: Route geometries generated from sources other than
              [NextBillion.ai](http://NextBillion.ai) services, are not supported in this
              version.

          original_shape_type: Specify the encoding type of route geometry provided in original_shape input.
              Please note that an error is returned when this parameter is not specified while
              an input is added to original_shape parameter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/route_report",
            body=maybe_transform(
                {
                    "original_shape": original_shape,
                    "original_shape_type": original_shape_type,
                },
                route_report_create_params.RouteReportCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, route_report_create_params.RouteReportCreateParams),
            ),
            cast_to=RouteReportCreateResponse,
        )


class AsyncRouteReportResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRouteReportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRouteReportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRouteReportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncRouteReportResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        original_shape: str,
        original_shape_type: Literal["polyline", "polyline6"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RouteReportCreateResponse:
        """
        Route Report

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          original_shape: Takes a route geometry as input and returns the route details. Accepts polyline
              and polyline6 encoded geometry as input.

              **Note**: Route geometries generated from sources other than
              [NextBillion.ai](http://NextBillion.ai) services, are not supported in this
              version.

          original_shape_type: Specify the encoding type of route geometry provided in original_shape input.
              Please note that an error is returned when this parameter is not specified while
              an input is added to original_shape parameter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/route_report",
            body=await async_maybe_transform(
                {
                    "original_shape": original_shape,
                    "original_shape_type": original_shape_type,
                },
                route_report_create_params.RouteReportCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, route_report_create_params.RouteReportCreateParams),
            ),
            cast_to=RouteReportCreateResponse,
        )


class RouteReportResourceWithRawResponse:
    def __init__(self, route_report: RouteReportResource) -> None:
        self._route_report = route_report

        self.create = to_raw_response_wrapper(
            route_report.create,
        )


class AsyncRouteReportResourceWithRawResponse:
    def __init__(self, route_report: AsyncRouteReportResource) -> None:
        self._route_report = route_report

        self.create = async_to_raw_response_wrapper(
            route_report.create,
        )


class RouteReportResourceWithStreamingResponse:
    def __init__(self, route_report: RouteReportResource) -> None:
        self._route_report = route_report

        self.create = to_streamed_response_wrapper(
            route_report.create,
        )


class AsyncRouteReportResourceWithStreamingResponse:
    def __init__(self, route_report: AsyncRouteReportResource) -> None:
        self._route_report = route_report

        self.create = async_to_streamed_response_wrapper(
            route_report.create,
        )
