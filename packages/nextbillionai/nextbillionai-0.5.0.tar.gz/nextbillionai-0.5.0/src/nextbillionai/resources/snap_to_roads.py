# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import snap_to_road_snap_params
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
from ..types.snap_to_road_snap_response import SnapToRoadSnapResponse

__all__ = ["SnapToRoadsResource", "AsyncSnapToRoadsResource"]


class SnapToRoadsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SnapToRoadsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SnapToRoadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SnapToRoadsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return SnapToRoadsResourceWithStreamingResponse(self)

    def snap(
        self,
        *,
        key: str,
        path: str,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        avoid: Literal["toll", "ferry", "highway", "none"] | NotGiven = NOT_GIVEN,
        geometry: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        option: Literal["flexible"] | NotGiven = NOT_GIVEN,
        radiuses: str | NotGiven = NOT_GIVEN,
        road_info: Literal["max_speed"] | NotGiven = NOT_GIVEN,
        timestamps: str | NotGiven = NOT_GIVEN,
        tolerate_outlier: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SnapToRoadSnapResponse:
        """
        Nextbillion.ai Snap To Roads API takes a series of locations along a route, and
        returns the new locations on this route that are snapped to the best-matched
        roads where the trip took place. You can set various parameters, such as
        timestamps or radius, to optimize the result.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          path: Pipe-separated list of coordinate points along a path which would be snapped to
              a road.

          approaches: A semicolon-separated list indicating the side of the road from which to
              approach the locations on the snapped route. When set to "unrestricted" a route
              can arrive at the snapped location from either side of the road and when set to
              "curb" the route will arrive at the snapped location on the driving side of the
              region. Please note the number of values provided must be equal to the number of
              coordinate points provided in the "path" parameter. However, you can skip a
              coordinate and show its position in the list with the ";" separator.

          avoid: Setting this will ensure the route avoids ferries, tolls, highways or nothing.
              Multiple values should be separated by a pipe (|). If "none" is provided along
              with other values, an error is returned as a valid route is not feasible. Please
              note that when this parameter is not provided in the input, ferries are set to
              be avoided by default. When this parameter is provided, only the mentioned
              objects are avoided.

          geometry: Sets the output format of the route geometry in the response. Only the
              "polyline" or "polyline6" encoded "geometry" of the snapped path is returned in
              the response depending on the value provided in the input. When "geojson" is
              selected as the input value, "polyline6" encoded geometry of the snapped path is
              returned along with a "geojson" object.

          mode: Set which driving mode the service should use to determine a route. For example,
              if you use "car", the API will return a route that a car can take. Using "truck"
              will return a route a truck can use, taking into account appropriate truck
              routing restrictions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          option: Include this parameter in the request to return segment-wise speed information
              of the route returned in the response.

              Please note that returning speed information is a function of "road_info"
              parameter, which is effective only when "option=flexible". However, the
              resultant route might not contain all the locations provided in "path" input.

          radiuses: Pipe separated radiuses, in meters (m), up to which a coordinate point can be
              snapped. Please note, if no valid road is available within the specified radius,
              the API would snap the points to nearest, most viable road. When using this
              parameter, it is recommended to specify as many radius values as the number of
              points in "path" parameter. If the same number of "radiuses" are not provided,
              the API will use the default radius value of 25 meters for all locations.

          road_info: Use this parameter to receive segment-wise maximum speed information of the
              route in the response. "max_speed" is the only allowed value.

          timestamps: Pipe-separated UNIX epoch timestamp in seconds for each location. If used, the
              number of timestamps must be equal to the number of coordinate points in the
              "path" parameter. The "timestamps" must increase monotonically starting from the
              first timestamp. This means that each subsequent timestamp should either be more
              than or equal to the preceding one.

          tolerate_outlier: Enable it to ignore locations outside the service boundary. When "true", the
              service would ignore "path" coordinates points falling outside the accessible
              area, which otherwise would cause an error when this parameter is "false".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/snapToRoads/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "path": path,
                        "approaches": approaches,
                        "avoid": avoid,
                        "geometry": geometry,
                        "mode": mode,
                        "option": option,
                        "radiuses": radiuses,
                        "road_info": road_info,
                        "timestamps": timestamps,
                        "tolerate_outlier": tolerate_outlier,
                    },
                    snap_to_road_snap_params.SnapToRoadSnapParams,
                ),
            ),
            cast_to=SnapToRoadSnapResponse,
        )


class AsyncSnapToRoadsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSnapToRoadsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSnapToRoadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSnapToRoadsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncSnapToRoadsResourceWithStreamingResponse(self)

    async def snap(
        self,
        *,
        key: str,
        path: str,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        avoid: Literal["toll", "ferry", "highway", "none"] | NotGiven = NOT_GIVEN,
        geometry: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        option: Literal["flexible"] | NotGiven = NOT_GIVEN,
        radiuses: str | NotGiven = NOT_GIVEN,
        road_info: Literal["max_speed"] | NotGiven = NOT_GIVEN,
        timestamps: str | NotGiven = NOT_GIVEN,
        tolerate_outlier: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SnapToRoadSnapResponse:
        """
        Nextbillion.ai Snap To Roads API takes a series of locations along a route, and
        returns the new locations on this route that are snapped to the best-matched
        roads where the trip took place. You can set various parameters, such as
        timestamps or radius, to optimize the result.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          path: Pipe-separated list of coordinate points along a path which would be snapped to
              a road.

          approaches: A semicolon-separated list indicating the side of the road from which to
              approach the locations on the snapped route. When set to "unrestricted" a route
              can arrive at the snapped location from either side of the road and when set to
              "curb" the route will arrive at the snapped location on the driving side of the
              region. Please note the number of values provided must be equal to the number of
              coordinate points provided in the "path" parameter. However, you can skip a
              coordinate and show its position in the list with the ";" separator.

          avoid: Setting this will ensure the route avoids ferries, tolls, highways or nothing.
              Multiple values should be separated by a pipe (|). If "none" is provided along
              with other values, an error is returned as a valid route is not feasible. Please
              note that when this parameter is not provided in the input, ferries are set to
              be avoided by default. When this parameter is provided, only the mentioned
              objects are avoided.

          geometry: Sets the output format of the route geometry in the response. Only the
              "polyline" or "polyline6" encoded "geometry" of the snapped path is returned in
              the response depending on the value provided in the input. When "geojson" is
              selected as the input value, "polyline6" encoded geometry of the snapped path is
              returned along with a "geojson" object.

          mode: Set which driving mode the service should use to determine a route. For example,
              if you use "car", the API will return a route that a car can take. Using "truck"
              will return a route a truck can use, taking into account appropriate truck
              routing restrictions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          option: Include this parameter in the request to return segment-wise speed information
              of the route returned in the response.

              Please note that returning speed information is a function of "road_info"
              parameter, which is effective only when "option=flexible". However, the
              resultant route might not contain all the locations provided in "path" input.

          radiuses: Pipe separated radiuses, in meters (m), up to which a coordinate point can be
              snapped. Please note, if no valid road is available within the specified radius,
              the API would snap the points to nearest, most viable road. When using this
              parameter, it is recommended to specify as many radius values as the number of
              points in "path" parameter. If the same number of "radiuses" are not provided,
              the API will use the default radius value of 25 meters for all locations.

          road_info: Use this parameter to receive segment-wise maximum speed information of the
              route in the response. "max_speed" is the only allowed value.

          timestamps: Pipe-separated UNIX epoch timestamp in seconds for each location. If used, the
              number of timestamps must be equal to the number of coordinate points in the
              "path" parameter. The "timestamps" must increase monotonically starting from the
              first timestamp. This means that each subsequent timestamp should either be more
              than or equal to the preceding one.

          tolerate_outlier: Enable it to ignore locations outside the service boundary. When "true", the
              service would ignore "path" coordinates points falling outside the accessible
              area, which otherwise would cause an error when this parameter is "false".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/snapToRoads/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "path": path,
                        "approaches": approaches,
                        "avoid": avoid,
                        "geometry": geometry,
                        "mode": mode,
                        "option": option,
                        "radiuses": radiuses,
                        "road_info": road_info,
                        "timestamps": timestamps,
                        "tolerate_outlier": tolerate_outlier,
                    },
                    snap_to_road_snap_params.SnapToRoadSnapParams,
                ),
            ),
            cast_to=SnapToRoadSnapResponse,
        )


class SnapToRoadsResourceWithRawResponse:
    def __init__(self, snap_to_roads: SnapToRoadsResource) -> None:
        self._snap_to_roads = snap_to_roads

        self.snap = to_raw_response_wrapper(
            snap_to_roads.snap,
        )


class AsyncSnapToRoadsResourceWithRawResponse:
    def __init__(self, snap_to_roads: AsyncSnapToRoadsResource) -> None:
        self._snap_to_roads = snap_to_roads

        self.snap = async_to_raw_response_wrapper(
            snap_to_roads.snap,
        )


class SnapToRoadsResourceWithStreamingResponse:
    def __init__(self, snap_to_roads: SnapToRoadsResource) -> None:
        self._snap_to_roads = snap_to_roads

        self.snap = to_streamed_response_wrapper(
            snap_to_roads.snap,
        )


class AsyncSnapToRoadsResourceWithStreamingResponse:
    def __init__(self, snap_to_roads: AsyncSnapToRoadsResource) -> None:
        self._snap_to_roads = snap_to_roads

        self.snap = async_to_streamed_response_wrapper(
            snap_to_roads.snap,
        )
