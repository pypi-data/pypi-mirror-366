# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import isochrone_compute_params
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
from ..types.isochrone_compute_response import IsochroneComputeResponse

__all__ = ["IsochroneResource", "AsyncIsochroneResource"]


class IsochroneResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IsochroneResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return IsochroneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IsochroneResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return IsochroneResourceWithStreamingResponse(self)

    def compute(
        self,
        *,
        contours_meters: int,
        contours_minutes: int,
        coordinates: str,
        key: str,
        contours_colors: str | NotGiven = NOT_GIVEN,
        denoise: float | NotGiven = NOT_GIVEN,
        departure_time: int | NotGiven = NOT_GIVEN,
        generalize: float | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        polygons: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IsochroneComputeResponse:
        """
        The NextBillion.ai Isochrone API computes areas that are reachable within a
        specified amount of time from a location, and returns the reachable regions as
        contours of polygons or lines that you can display on a map.

        Args:
          contours_meters: The distances, in meters, to use for each isochrone contour. You can specify up
              to four contours. Distances must be in increasing order. The maximum distance
              that can be specified is 60000 meters (60 km).

          contours_minutes: The times, in minutes, to use for each isochrone contour. You can specify up to
              four contours. Times must be in increasing order. The maximum time that can be
              specified is 40 minutes.

          coordinates: The coordinates of the location which acts as the starting point for which the
              isochrone lines need to be determined.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          contours_colors: The hex code of the color to fill isochrone contour. When requesting multiple
              contours, it is recommended to provide color codes for each of the requested
              contours, separated by a ",". If no colors are specified, the Isochrone API will
              assign a random color scheme to the output.

          denoise: A floating point value from 0.0 to 1.0 can be used to remove smaller contours.
              The default is 1.0. A value of 1.0 will only return the largest contour for a
              given value. A value of 0.5 drops any contours that are less than half the area
              of the largest contour in the set of contours for that same value.

          departure_time: Use this parameter to set a departure time, expressed as UNIX epoch timestamp in
              seconds, for calculating the isochrone contour. The response will consider the
              typical traffic conditions at the given time and return a contour which can be
              reached under those traffic conditions. Please note that if no input is provided
              for this parameter then the traffic conditions at the time of making the request
              are considered.

          generalize: A positive floating point value, in meters, used as the tolerance for
              Douglas-Peucker generalization. There is no upper bound. If no value is
              specified in the request, the Isochrone API will choose the most optimized
              generalization to use for the request. Note that the generalization of contours
              can lead to self-intersections, as well as intersections of adjacent contours.

          mode: Set which driving mode the service should use to determine the contour. For
              example, if you use "car", the API will return an isochrone contour that a car
              can reach within the specified time or after driving the specified distance.
              Using "truck" will return a contour that a truck can reach after taking into
              account appropriate truck routing restrictions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          polygons: Specify whether to return the contours as GeoJSON polygons (true) or linestrings
              (false, default). When polygons=true, any contour that forms a ring is returned
              as a polygon.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/isochrone/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "contours_meters": contours_meters,
                        "contours_minutes": contours_minutes,
                        "coordinates": coordinates,
                        "key": key,
                        "contours_colors": contours_colors,
                        "denoise": denoise,
                        "departure_time": departure_time,
                        "generalize": generalize,
                        "mode": mode,
                        "polygons": polygons,
                    },
                    isochrone_compute_params.IsochroneComputeParams,
                ),
            ),
            cast_to=IsochroneComputeResponse,
        )


class AsyncIsochroneResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIsochroneResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIsochroneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIsochroneResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncIsochroneResourceWithStreamingResponse(self)

    async def compute(
        self,
        *,
        contours_meters: int,
        contours_minutes: int,
        coordinates: str,
        key: str,
        contours_colors: str | NotGiven = NOT_GIVEN,
        denoise: float | NotGiven = NOT_GIVEN,
        departure_time: int | NotGiven = NOT_GIVEN,
        generalize: float | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        polygons: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IsochroneComputeResponse:
        """
        The NextBillion.ai Isochrone API computes areas that are reachable within a
        specified amount of time from a location, and returns the reachable regions as
        contours of polygons or lines that you can display on a map.

        Args:
          contours_meters: The distances, in meters, to use for each isochrone contour. You can specify up
              to four contours. Distances must be in increasing order. The maximum distance
              that can be specified is 60000 meters (60 km).

          contours_minutes: The times, in minutes, to use for each isochrone contour. You can specify up to
              four contours. Times must be in increasing order. The maximum time that can be
              specified is 40 minutes.

          coordinates: The coordinates of the location which acts as the starting point for which the
              isochrone lines need to be determined.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          contours_colors: The hex code of the color to fill isochrone contour. When requesting multiple
              contours, it is recommended to provide color codes for each of the requested
              contours, separated by a ",". If no colors are specified, the Isochrone API will
              assign a random color scheme to the output.

          denoise: A floating point value from 0.0 to 1.0 can be used to remove smaller contours.
              The default is 1.0. A value of 1.0 will only return the largest contour for a
              given value. A value of 0.5 drops any contours that are less than half the area
              of the largest contour in the set of contours for that same value.

          departure_time: Use this parameter to set a departure time, expressed as UNIX epoch timestamp in
              seconds, for calculating the isochrone contour. The response will consider the
              typical traffic conditions at the given time and return a contour which can be
              reached under those traffic conditions. Please note that if no input is provided
              for this parameter then the traffic conditions at the time of making the request
              are considered.

          generalize: A positive floating point value, in meters, used as the tolerance for
              Douglas-Peucker generalization. There is no upper bound. If no value is
              specified in the request, the Isochrone API will choose the most optimized
              generalization to use for the request. Note that the generalization of contours
              can lead to self-intersections, as well as intersections of adjacent contours.

          mode: Set which driving mode the service should use to determine the contour. For
              example, if you use "car", the API will return an isochrone contour that a car
              can reach within the specified time or after driving the specified distance.
              Using "truck" will return a contour that a truck can reach after taking into
              account appropriate truck routing restrictions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          polygons: Specify whether to return the contours as GeoJSON polygons (true) or linestrings
              (false, default). When polygons=true, any contour that forms a ring is returned
              as a polygon.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/isochrone/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "contours_meters": contours_meters,
                        "contours_minutes": contours_minutes,
                        "coordinates": coordinates,
                        "key": key,
                        "contours_colors": contours_colors,
                        "denoise": denoise,
                        "departure_time": departure_time,
                        "generalize": generalize,
                        "mode": mode,
                        "polygons": polygons,
                    },
                    isochrone_compute_params.IsochroneComputeParams,
                ),
            ),
            cast_to=IsochroneComputeResponse,
        )


class IsochroneResourceWithRawResponse:
    def __init__(self, isochrone: IsochroneResource) -> None:
        self._isochrone = isochrone

        self.compute = to_raw_response_wrapper(
            isochrone.compute,
        )


class AsyncIsochroneResourceWithRawResponse:
    def __init__(self, isochrone: AsyncIsochroneResource) -> None:
        self._isochrone = isochrone

        self.compute = async_to_raw_response_wrapper(
            isochrone.compute,
        )


class IsochroneResourceWithStreamingResponse:
    def __init__(self, isochrone: IsochroneResource) -> None:
        self._isochrone = isochrone

        self.compute = to_streamed_response_wrapper(
            isochrone.compute,
        )


class AsyncIsochroneResourceWithStreamingResponse:
    def __init__(self, isochrone: AsyncIsochroneResource) -> None:
        self._isochrone = isochrone

        self.compute = async_to_streamed_response_wrapper(
            isochrone.compute,
        )
