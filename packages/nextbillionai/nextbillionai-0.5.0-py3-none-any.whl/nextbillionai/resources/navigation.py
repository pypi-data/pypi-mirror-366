# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import navigation_retrieve_route_params
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
from ..types.navigation_retrieve_route_response import NavigationRetrieveRouteResponse

__all__ = ["NavigationResource", "AsyncNavigationResource"]


class NavigationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NavigationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return NavigationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NavigationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return NavigationResourceWithStreamingResponse(self)

    def retrieve_route(
        self,
        *,
        key: str,
        altcount: int | NotGiven = NOT_GIVEN,
        alternatives: bool | NotGiven = NOT_GIVEN,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        avoid: Literal["toll", "ferry", "highway", "none"] | NotGiven = NOT_GIVEN,
        bearings: str | NotGiven = NOT_GIVEN,
        destination: str | NotGiven = NOT_GIVEN,
        geometry: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        lang: str | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        origin: str | NotGiven = NOT_GIVEN,
        original_shape: str | NotGiven = NOT_GIVEN,
        original_shape_type: Literal["polyline", "polyline6"] | NotGiven = NOT_GIVEN,
        overview: Literal["full", "simplified", "false"] | NotGiven = NOT_GIVEN,
        waypoints: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NavigationRetrieveRouteResponse:
        """
        Nextbillion.ai’s Navigation API is a service that computes a route between 2
        places, and also returns detailed turn by turn instructions for the route.

        The Navigation API can be used as an input into your Navigation app.
        Alternatively, you can directly use Nextbillion.ai’s Navigation SDK for a
        complete turn by turn navigation experience.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          altcount: Sets the number of alternative routes to return. It is effective only when
              "alternatives" is "true". Please note that adding alternative route count does
              not guarantee matching number of routes to be returned if potential alternative
              routes do not exist.

          alternatives: When "true" the API will return alternate routes. The "alternatives" is
              effective only when there are no "waypoints" included in the request. You can
              set the number of alternate routes to be returned in the "altcount" property.

          approaches: A semicolon-separated list indicating the side of the road from which to
              approach "waypoints" in a requested route. When set to "unrestricted" a route
              can arrive at the waypoint from either side of the road and when set to "curb"
              the route will arrive at the waypoint on the driving side of the region. Please
              note the number of values provided must be one more than the number of
              "waypoints". The last value of "approaches" will determine the approach for the
              "destination". However, you can skip a coordinate and show its position in the
              list with the ";" separator.

          avoid: Setting this will ensure the route avoids ferries, tolls, highways or nothing.
              Multiple values should be separated by a pipe (|). If "none" is provided along
              with other values, an error is returned as a valid route is not feasible. Please
              note that when this parameter is not provided in the input, ferries are set to
              be avoided by default. When this parameter is provided, only the mentioned
              objects are avoided.

          bearings: Limits the search to road segments with given bearing, in degrees, towards true
              north in clockwise direction. Each "bearings" should be in the format of
              "degree,range", where the "degree" should be a value between \\[[0, 360\\]] and
              "range" should be a value between \\[[0, 180\\]]. Please note that the number of
              "bearings" should be two more than the number of "waypoints". This is to account
              for the bearing of "origin" and "destination". If a route can approach a
              "waypoint" or the "destination" from any direction, the bearing for that point
              can be specified as "0,180".

          destination: "destination" is the ending point of your route. Ensure that the "destination"
              is a routable land location. Please note that this parameter is mandatory if the
              "original_shape" parameter is not given.

          geometry: Sets the output format of the route geometry in the response. On providing
              “polyline“ and “polyline6“ as input, respective encoded geometry is returned.
              However, when “geojson“ is provided as the input value, “polyline“ encoded
              geometry is returned in the response along with the geojson details of the
              route.

          lang: Select the language to be used for result rendering from a list of
              [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
              codes.

          mode: Set which driving mode the service should use to determine a route. For example,
              if you use "car", the API will return a route that a car can take. Using "truck"
              will return a route a truck can use, taking into account appropriate truck
              routing restrictions.

              When "mode=truck", following are the default dimensions that are used:

              \\-- truck_height = 214 centimeters

              \\-- truck_width = 183 centimeters

              \\-- truck_length = 519 centimeters

              \\-- truck_weight = 5000 kg

              Please use the Navigation Flexible version if you want to use custom truck
              dimensions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          origin: "origin" is the starting point of your route. Ensure that "origin" is a routable
              land location. Please note that this parameter is mandatory if the geometry
              parameter is not given.

          original_shape: Takes a route geometry as input and returns the navigation information for that
              route. Accepts "polyline" and "polyline6" encoded geometry as input.
              "original_shape_type" becomes mandatory when "original_shape" is used. If this
              parameter is provided, the only other parameters which will be considered are
              "original_shape_type", "lang", "geometry". The rest of the parameters in the
              input request will be ignored. Please note overview verbosity will always be
              "full" when using this parameter.

          original_shape_type: Specify the encoding format of route geometry provided in the request using
              "original_shape" parameter. Please note that an error is returned when this
              parameter is not specified while an input is added to "original_shape"
              parameter.

          overview: Specify the verbosity of route geometry. When set to "full", the most detailed
              geometry available is returned. When set to "simplified", a simplified version
              of the full geometry is returned. No overview geometry is returned when set to
              "false".

          waypoints: "waypoints" are coordinates along the route between the "origin" and
              "destination". It is a pipe-separated list of coordinate pairs. Please note that
              the route returned will arrive at the "waypoints" in the sequence they are
              provided in the input request. Please note that the maximum number of waypoints
              that can be provided in a single request is 50 when using GET method and 200
              with POST method.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/navigation/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "altcount": altcount,
                        "alternatives": alternatives,
                        "approaches": approaches,
                        "avoid": avoid,
                        "bearings": bearings,
                        "destination": destination,
                        "geometry": geometry,
                        "lang": lang,
                        "mode": mode,
                        "origin": origin,
                        "original_shape": original_shape,
                        "original_shape_type": original_shape_type,
                        "overview": overview,
                        "waypoints": waypoints,
                    },
                    navigation_retrieve_route_params.NavigationRetrieveRouteParams,
                ),
            ),
            cast_to=NavigationRetrieveRouteResponse,
        )


class AsyncNavigationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNavigationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNavigationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNavigationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncNavigationResourceWithStreamingResponse(self)

    async def retrieve_route(
        self,
        *,
        key: str,
        altcount: int | NotGiven = NOT_GIVEN,
        alternatives: bool | NotGiven = NOT_GIVEN,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        avoid: Literal["toll", "ferry", "highway", "none"] | NotGiven = NOT_GIVEN,
        bearings: str | NotGiven = NOT_GIVEN,
        destination: str | NotGiven = NOT_GIVEN,
        geometry: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        lang: str | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        origin: str | NotGiven = NOT_GIVEN,
        original_shape: str | NotGiven = NOT_GIVEN,
        original_shape_type: Literal["polyline", "polyline6"] | NotGiven = NOT_GIVEN,
        overview: Literal["full", "simplified", "false"] | NotGiven = NOT_GIVEN,
        waypoints: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NavigationRetrieveRouteResponse:
        """
        Nextbillion.ai’s Navigation API is a service that computes a route between 2
        places, and also returns detailed turn by turn instructions for the route.

        The Navigation API can be used as an input into your Navigation app.
        Alternatively, you can directly use Nextbillion.ai’s Navigation SDK for a
        complete turn by turn navigation experience.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          altcount: Sets the number of alternative routes to return. It is effective only when
              "alternatives" is "true". Please note that adding alternative route count does
              not guarantee matching number of routes to be returned if potential alternative
              routes do not exist.

          alternatives: When "true" the API will return alternate routes. The "alternatives" is
              effective only when there are no "waypoints" included in the request. You can
              set the number of alternate routes to be returned in the "altcount" property.

          approaches: A semicolon-separated list indicating the side of the road from which to
              approach "waypoints" in a requested route. When set to "unrestricted" a route
              can arrive at the waypoint from either side of the road and when set to "curb"
              the route will arrive at the waypoint on the driving side of the region. Please
              note the number of values provided must be one more than the number of
              "waypoints". The last value of "approaches" will determine the approach for the
              "destination". However, you can skip a coordinate and show its position in the
              list with the ";" separator.

          avoid: Setting this will ensure the route avoids ferries, tolls, highways or nothing.
              Multiple values should be separated by a pipe (|). If "none" is provided along
              with other values, an error is returned as a valid route is not feasible. Please
              note that when this parameter is not provided in the input, ferries are set to
              be avoided by default. When this parameter is provided, only the mentioned
              objects are avoided.

          bearings: Limits the search to road segments with given bearing, in degrees, towards true
              north in clockwise direction. Each "bearings" should be in the format of
              "degree,range", where the "degree" should be a value between \\[[0, 360\\]] and
              "range" should be a value between \\[[0, 180\\]]. Please note that the number of
              "bearings" should be two more than the number of "waypoints". This is to account
              for the bearing of "origin" and "destination". If a route can approach a
              "waypoint" or the "destination" from any direction, the bearing for that point
              can be specified as "0,180".

          destination: "destination" is the ending point of your route. Ensure that the "destination"
              is a routable land location. Please note that this parameter is mandatory if the
              "original_shape" parameter is not given.

          geometry: Sets the output format of the route geometry in the response. On providing
              “polyline“ and “polyline6“ as input, respective encoded geometry is returned.
              However, when “geojson“ is provided as the input value, “polyline“ encoded
              geometry is returned in the response along with the geojson details of the
              route.

          lang: Select the language to be used for result rendering from a list of
              [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
              codes.

          mode: Set which driving mode the service should use to determine a route. For example,
              if you use "car", the API will return a route that a car can take. Using "truck"
              will return a route a truck can use, taking into account appropriate truck
              routing restrictions.

              When "mode=truck", following are the default dimensions that are used:

              \\-- truck_height = 214 centimeters

              \\-- truck_width = 183 centimeters

              \\-- truck_length = 519 centimeters

              \\-- truck_weight = 5000 kg

              Please use the Navigation Flexible version if you want to use custom truck
              dimensions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          origin: "origin" is the starting point of your route. Ensure that "origin" is a routable
              land location. Please note that this parameter is mandatory if the geometry
              parameter is not given.

          original_shape: Takes a route geometry as input and returns the navigation information for that
              route. Accepts "polyline" and "polyline6" encoded geometry as input.
              "original_shape_type" becomes mandatory when "original_shape" is used. If this
              parameter is provided, the only other parameters which will be considered are
              "original_shape_type", "lang", "geometry". The rest of the parameters in the
              input request will be ignored. Please note overview verbosity will always be
              "full" when using this parameter.

          original_shape_type: Specify the encoding format of route geometry provided in the request using
              "original_shape" parameter. Please note that an error is returned when this
              parameter is not specified while an input is added to "original_shape"
              parameter.

          overview: Specify the verbosity of route geometry. When set to "full", the most detailed
              geometry available is returned. When set to "simplified", a simplified version
              of the full geometry is returned. No overview geometry is returned when set to
              "false".

          waypoints: "waypoints" are coordinates along the route between the "origin" and
              "destination". It is a pipe-separated list of coordinate pairs. Please note that
              the route returned will arrive at the "waypoints" in the sequence they are
              provided in the input request. Please note that the maximum number of waypoints
              that can be provided in a single request is 50 when using GET method and 200
              with POST method.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/navigation/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "altcount": altcount,
                        "alternatives": alternatives,
                        "approaches": approaches,
                        "avoid": avoid,
                        "bearings": bearings,
                        "destination": destination,
                        "geometry": geometry,
                        "lang": lang,
                        "mode": mode,
                        "origin": origin,
                        "original_shape": original_shape,
                        "original_shape_type": original_shape_type,
                        "overview": overview,
                        "waypoints": waypoints,
                    },
                    navigation_retrieve_route_params.NavigationRetrieveRouteParams,
                ),
            ),
            cast_to=NavigationRetrieveRouteResponse,
        )


class NavigationResourceWithRawResponse:
    def __init__(self, navigation: NavigationResource) -> None:
        self._navigation = navigation

        self.retrieve_route = to_raw_response_wrapper(
            navigation.retrieve_route,
        )


class AsyncNavigationResourceWithRawResponse:
    def __init__(self, navigation: AsyncNavigationResource) -> None:
        self._navigation = navigation

        self.retrieve_route = async_to_raw_response_wrapper(
            navigation.retrieve_route,
        )


class NavigationResourceWithStreamingResponse:
    def __init__(self, navigation: NavigationResource) -> None:
        self._navigation = navigation

        self.retrieve_route = to_streamed_response_wrapper(
            navigation.retrieve_route,
        )


class AsyncNavigationResourceWithStreamingResponse:
    def __init__(self, navigation: AsyncNavigationResource) -> None:
        self._navigation = navigation

        self.retrieve_route = async_to_streamed_response_wrapper(
            navigation.retrieve_route,
        )
