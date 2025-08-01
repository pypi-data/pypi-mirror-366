# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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
from ...types.distance_matrix import json_retrieve_params
from ...types.distance_matrix.json_retrieve_response import JsonRetrieveResponse

__all__ = ["JsonResource", "AsyncJsonResource"]


class JsonResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> JsonResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return JsonResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> JsonResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return JsonResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """asfd"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/distancematrix/json",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        *,
        destinations: str,
        key: str,
        origins: str,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        avoid: Literal["toll", "ferry", "highway", "none"] | NotGiven = NOT_GIVEN,
        bearings: str | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        route_failed_prompt: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JsonRetrieveResponse:
        """
        Nextbillion.ai Distance Matrix API computes distances and ETAs between a set of
        origins and destinations — could be for one-to-many or many-to-many scenarios.
        The API call returns a matrix of ETAs and distances for each origin and
        destination pair. For example, If the set is Origins {A,B} and Destinations
        {C,D,E} we can get the following set of results with distance (meters) and time
        (seconds) for each. The GET method can only handle up to 100 locations (1
        location is either 1 origin or 1 destination).

        Args:
          destinations: "destinations" are the ending coordinates of your route. Ensure that
              "destinations" are routable land locations. Multiple "destinations" should be
              separated by a pipe symbol "|".

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          origins: "origins" are the starting point of your route. Ensure that "origins" are
              routable land locations. Multiple "origins" should be separated by a pipe symbol
              "|".

          approaches: A semicolon-separated list indicating the side of the road from which the route
              will approach "destinations". When set to "unrestricted" a route can arrive at a
              destination from either side of the road. When set to "curb" the route will
              arrive at a destination on the driving side of the region. Please note the
              number of values provided must be equal to the number of "destinations".
              However, you can skip a coordinate and show its position in the list with the
              ";" separator. The values provided for the "approaches" parameter are effective
              for the "destinations" value at the same index. Example: "curb;;curb" will apply
              curbside restriction on the "destinations" points provided at the first and
              third index.

          avoid: Setting this will ensure the route avoids ferries, tolls, highways or nothing.
              Multiple values should be separated by a pipe (|). If "none" is provided along
              with other values, an error is returned as a valid route is not feasible. Please
              note that when this parameter is not provided in the input, ferries are set to
              be avoided by default. When this parameter is provided, only the mentioned
              objects are avoided.

          bearings: Limits the search to segments with given bearing in degrees towards true north
              in clockwise direction. Each "bearing" should be in the format of
              "degree,range", where the "degree" should be a value between \\[[0, 360\\]] and
              "range" should be a value between \\[[0, 180\\]]. Please note that the number of
              "bearings" should be equal to the sum of the number of points in "origins" and
              "destinations". If a route can approach a destination from any direction, the
              bearing for that point can be specified as "0,180".

          mode: Set which driving mode the service should use to determine the "distance" and
              "duration" values. For example, if you use "car", the API will return the
              duration and distance of a route that a car can take. Using "truck" will return
              the same for a route a truck can use, taking into account appropriate truck
              routing restrictions.

              When "mode=truck", following are the default dimensions that are used:

              \\-- truck_height = 214 centimeters

              \\-- truck_width = 183 centimeters

              \\-- truck_length = 519 centimeters

              \\-- truck_weight = 5000 kg

              Please use the Distance Matrix Flexible version if you want to use custom truck
              dimensions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          route_failed_prompt: A prompt to modify the response in case no feasible route is available for a
              given pair of origin and destination. When set to "true", a value of "-1" is
              returned for those pairs in which:

              \\-- Either origin or the destination can not be snapped to a nearest road. Please
              note that if all the origins and destinations in a request can't be snapped to
              their nearest roads, a 4xx error is returned instead, as the entire request
              failed.

              \\-- Both origin and destination can be snapped to the nearest road, but the
              service can't find a valid route between them. However, a value of "0" is
              returned if both the origin and destination are snapped to the same location.

              "false" is the default value. In this case, a "0" value is returned for all the
              above cases. A 4xx error is returned, in this case as well, when all origins and
              destinations in the request can't be snapped to their nearest road.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/distancematrix/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "destinations": destinations,
                        "key": key,
                        "origins": origins,
                        "approaches": approaches,
                        "avoid": avoid,
                        "bearings": bearings,
                        "mode": mode,
                        "route_failed_prompt": route_failed_prompt,
                    },
                    json_retrieve_params.JsonRetrieveParams,
                ),
            ),
            cast_to=JsonRetrieveResponse,
        )


class AsyncJsonResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncJsonResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncJsonResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncJsonResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncJsonResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """asfd"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/distancematrix/json",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        *,
        destinations: str,
        key: str,
        origins: str,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        avoid: Literal["toll", "ferry", "highway", "none"] | NotGiven = NOT_GIVEN,
        bearings: str | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        route_failed_prompt: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JsonRetrieveResponse:
        """
        Nextbillion.ai Distance Matrix API computes distances and ETAs between a set of
        origins and destinations — could be for one-to-many or many-to-many scenarios.
        The API call returns a matrix of ETAs and distances for each origin and
        destination pair. For example, If the set is Origins {A,B} and Destinations
        {C,D,E} we can get the following set of results with distance (meters) and time
        (seconds) for each. The GET method can only handle up to 100 locations (1
        location is either 1 origin or 1 destination).

        Args:
          destinations: "destinations" are the ending coordinates of your route. Ensure that
              "destinations" are routable land locations. Multiple "destinations" should be
              separated by a pipe symbol "|".

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          origins: "origins" are the starting point of your route. Ensure that "origins" are
              routable land locations. Multiple "origins" should be separated by a pipe symbol
              "|".

          approaches: A semicolon-separated list indicating the side of the road from which the route
              will approach "destinations". When set to "unrestricted" a route can arrive at a
              destination from either side of the road. When set to "curb" the route will
              arrive at a destination on the driving side of the region. Please note the
              number of values provided must be equal to the number of "destinations".
              However, you can skip a coordinate and show its position in the list with the
              ";" separator. The values provided for the "approaches" parameter are effective
              for the "destinations" value at the same index. Example: "curb;;curb" will apply
              curbside restriction on the "destinations" points provided at the first and
              third index.

          avoid: Setting this will ensure the route avoids ferries, tolls, highways or nothing.
              Multiple values should be separated by a pipe (|). If "none" is provided along
              with other values, an error is returned as a valid route is not feasible. Please
              note that when this parameter is not provided in the input, ferries are set to
              be avoided by default. When this parameter is provided, only the mentioned
              objects are avoided.

          bearings: Limits the search to segments with given bearing in degrees towards true north
              in clockwise direction. Each "bearing" should be in the format of
              "degree,range", where the "degree" should be a value between \\[[0, 360\\]] and
              "range" should be a value between \\[[0, 180\\]]. Please note that the number of
              "bearings" should be equal to the sum of the number of points in "origins" and
              "destinations". If a route can approach a destination from any direction, the
              bearing for that point can be specified as "0,180".

          mode: Set which driving mode the service should use to determine the "distance" and
              "duration" values. For example, if you use "car", the API will return the
              duration and distance of a route that a car can take. Using "truck" will return
              the same for a route a truck can use, taking into account appropriate truck
              routing restrictions.

              When "mode=truck", following are the default dimensions that are used:

              \\-- truck_height = 214 centimeters

              \\-- truck_width = 183 centimeters

              \\-- truck_length = 519 centimeters

              \\-- truck_weight = 5000 kg

              Please use the Distance Matrix Flexible version if you want to use custom truck
              dimensions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          route_failed_prompt: A prompt to modify the response in case no feasible route is available for a
              given pair of origin and destination. When set to "true", a value of "-1" is
              returned for those pairs in which:

              \\-- Either origin or the destination can not be snapped to a nearest road. Please
              note that if all the origins and destinations in a request can't be snapped to
              their nearest roads, a 4xx error is returned instead, as the entire request
              failed.

              \\-- Both origin and destination can be snapped to the nearest road, but the
              service can't find a valid route between them. However, a value of "0" is
              returned if both the origin and destination are snapped to the same location.

              "false" is the default value. In this case, a "0" value is returned for all the
              above cases. A 4xx error is returned, in this case as well, when all origins and
              destinations in the request can't be snapped to their nearest road.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/distancematrix/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "destinations": destinations,
                        "key": key,
                        "origins": origins,
                        "approaches": approaches,
                        "avoid": avoid,
                        "bearings": bearings,
                        "mode": mode,
                        "route_failed_prompt": route_failed_prompt,
                    },
                    json_retrieve_params.JsonRetrieveParams,
                ),
            ),
            cast_to=JsonRetrieveResponse,
        )


class JsonResourceWithRawResponse:
    def __init__(self, json: JsonResource) -> None:
        self._json = json

        self.create = to_raw_response_wrapper(
            json.create,
        )
        self.retrieve = to_raw_response_wrapper(
            json.retrieve,
        )


class AsyncJsonResourceWithRawResponse:
    def __init__(self, json: AsyncJsonResource) -> None:
        self._json = json

        self.create = async_to_raw_response_wrapper(
            json.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            json.retrieve,
        )


class JsonResourceWithStreamingResponse:
    def __init__(self, json: JsonResource) -> None:
        self._json = json

        self.create = to_streamed_response_wrapper(
            json.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            json.retrieve,
        )


class AsyncJsonResourceWithStreamingResponse:
    def __init__(self, json: AsyncJsonResource) -> None:
        self._json = json

        self.create = async_to_streamed_response_wrapper(
            json.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            json.retrieve,
        )
