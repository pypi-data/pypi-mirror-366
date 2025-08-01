# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .v2 import (
    V2Resource,
    AsyncV2Resource,
    V2ResourceWithRawResponse,
    AsyncV2ResourceWithRawResponse,
    V2ResourceWithStreamingResponse,
    AsyncV2ResourceWithStreamingResponse,
)
from ...types import optimization_compute_params, optimization_re_optimize_params
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
from .driver_assignment import (
    DriverAssignmentResource,
    AsyncDriverAssignmentResource,
    DriverAssignmentResourceWithRawResponse,
    AsyncDriverAssignmentResourceWithRawResponse,
    DriverAssignmentResourceWithStreamingResponse,
    AsyncDriverAssignmentResourceWithStreamingResponse,
)
from ...types.post_response import PostResponse
from ...types.optimization_compute_response import OptimizationComputeResponse

__all__ = ["OptimizationResource", "AsyncOptimizationResource"]


class OptimizationResource(SyncAPIResource):
    @cached_property
    def driver_assignment(self) -> DriverAssignmentResource:
        return DriverAssignmentResource(self._client)

    @cached_property
    def v2(self) -> V2Resource:
        return V2Resource(self._client)

    @cached_property
    def with_raw_response(self) -> OptimizationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OptimizationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OptimizationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return OptimizationResourceWithStreamingResponse(self)

    def compute(
        self,
        *,
        coordinates: str,
        key: str,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        destination: Literal["any", "last"] | NotGiven = NOT_GIVEN,
        geometries: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        roundtrip: bool | NotGiven = NOT_GIVEN,
        source: Literal["any", "first"] | NotGiven = NOT_GIVEN,
        with_geometry: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OptimizationComputeResponse:
        """
        Nextbillion.ai Optimization API computes and returns an optimized route between
        an origin and destination which have multiple stop points in between. With
        NextBillion.ai's Route Optimization API you get.

        Optimized routing between way points

        Highly accurate ETAs with customized routes

        Roundtrip optimization with customized destinations

        A list of all parameters is specified in the next section.

        Args:
          coordinates: This is a pipe-separated list of coordinates.

              Minimum 3 pairs of coordinates and Maximum 12 pairs of coordinates are allowed.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          approaches: A semicolon-separated list indicating the side of the road from which to
              approach waypoints in a requested route. If provided, the number of approaches
              must be the same as the number of coordinates. However, you can skip a
              coordinate and show its position in the list with the ; separator.

          destination: Specify the destination coordinate of the returned route. If the input is last,
              the last coordinate will be the destination.

          geometries: Sets the output format of the route geometry in the response.

              On providing polyline and polyline6 as input, respective encoded geometry is
              returned. However, when geojson is provided as the input value, polyline encoded
              geometry is returned in the response along with a geojson details of the route.

          mode: Set which driving mode the service should use to determine a route. For example,
              if you use "car", the API will return a route that a car can take. Using "truck"
              will return a route a truck can use, taking into account appropriate truck
              routing restrictions.

              When "mode=truck", following are the default dimensions that are used:

              \\-- truck_height = 214 centimeters

              \\-- truck_width = 183 centimeters

              \\-- truck_length = 519 centimeters

              \\-- truck_weight = 5000 kg

              Please use the Directions Flexible version if you want to use custom truck
              dimensions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          roundtrip: Indicates whether the returned route is a roundtrip.

          source: The coordinate at which to start the returned route. If this is not configured,
              the return route’s destination will be the first coordinate.

          with_geometry: Indicates whether the return geometry should be computed or not.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/optimization/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "coordinates": coordinates,
                        "key": key,
                        "approaches": approaches,
                        "destination": destination,
                        "geometries": geometries,
                        "mode": mode,
                        "roundtrip": roundtrip,
                        "source": source,
                        "with_geometry": with_geometry,
                    },
                    optimization_compute_params.OptimizationComputeParams,
                ),
            ),
            cast_to=OptimizationComputeResponse,
        )

    def re_optimize(
        self,
        *,
        key: str,
        existing_request_id: str,
        job_changes: optimization_re_optimize_params.JobChanges | NotGiven = NOT_GIVEN,
        locations: List[str] | NotGiven = NOT_GIVEN,
        shipment_changes: optimization_re_optimize_params.ShipmentChanges | NotGiven = NOT_GIVEN,
        vehicle_changes: optimization_re_optimize_params.VehicleChanges | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PostResponse:
        """
        Re-optimization

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          existing_request_id: Specify the unique request ID that needs to be re-optimized.

          job_changes: This section gathers information on modifications to the number of jobs or their
              individual requirements for re-optimization. Any job from the original solution
              not specified here will be re-planned without alteration during the
              re-optimization process.

          locations: Provide the list of locations to be used during re-optimization process. Please
              note that

              - Providing the location input overwrites the list of locations used in the
                original request.
              - The location_indexes associated with all tasks and vehicles (both from the
                original and new re-optimization input requests) will follow the updated list
                of locations.

              As a best practice:

              1.  Don't provide the locations input when re-optimizing, if the original set
                  contains all the required location coordinates.
              2.  If any new location coordinates are required for re-optimization, copy the
                  full, original location list and update it in the following manner before
                  adding it to the re-optimization input:

                  1.  Ensure to not update the indexes of locations which just need to be
                      "modified".
                  2.  Add new location coordinates towards the end of the list.

          shipment_changes: This section gathers information on modifications to the number of shipments or
              their individual requirements for re-optimization. Any shipment from the
              original solution not specified here will be re-planned without alteration
              during the re-optimization process.

          vehicle_changes: This section gathers information on modifications to the number of vehicles or
              individual vehicle configurations for re-optimizing an existing solution. Any
              vehicle from the original solution not specified here will be reused without
              alteration during the re-optimization process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/optimization/re_optimization",
            body=maybe_transform(
                {
                    "existing_request_id": existing_request_id,
                    "job_changes": job_changes,
                    "locations": locations,
                    "shipment_changes": shipment_changes,
                    "vehicle_changes": vehicle_changes,
                },
                optimization_re_optimize_params.OptimizationReOptimizeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, optimization_re_optimize_params.OptimizationReOptimizeParams),
            ),
            cast_to=PostResponse,
        )


class AsyncOptimizationResource(AsyncAPIResource):
    @cached_property
    def driver_assignment(self) -> AsyncDriverAssignmentResource:
        return AsyncDriverAssignmentResource(self._client)

    @cached_property
    def v2(self) -> AsyncV2Resource:
        return AsyncV2Resource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOptimizationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOptimizationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOptimizationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncOptimizationResourceWithStreamingResponse(self)

    async def compute(
        self,
        *,
        coordinates: str,
        key: str,
        approaches: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        destination: Literal["any", "last"] | NotGiven = NOT_GIVEN,
        geometries: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        roundtrip: bool | NotGiven = NOT_GIVEN,
        source: Literal["any", "first"] | NotGiven = NOT_GIVEN,
        with_geometry: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OptimizationComputeResponse:
        """
        Nextbillion.ai Optimization API computes and returns an optimized route between
        an origin and destination which have multiple stop points in between. With
        NextBillion.ai's Route Optimization API you get.

        Optimized routing between way points

        Highly accurate ETAs with customized routes

        Roundtrip optimization with customized destinations

        A list of all parameters is specified in the next section.

        Args:
          coordinates: This is a pipe-separated list of coordinates.

              Minimum 3 pairs of coordinates and Maximum 12 pairs of coordinates are allowed.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          approaches: A semicolon-separated list indicating the side of the road from which to
              approach waypoints in a requested route. If provided, the number of approaches
              must be the same as the number of coordinates. However, you can skip a
              coordinate and show its position in the list with the ; separator.

          destination: Specify the destination coordinate of the returned route. If the input is last,
              the last coordinate will be the destination.

          geometries: Sets the output format of the route geometry in the response.

              On providing polyline and polyline6 as input, respective encoded geometry is
              returned. However, when geojson is provided as the input value, polyline encoded
              geometry is returned in the response along with a geojson details of the route.

          mode: Set which driving mode the service should use to determine a route. For example,
              if you use "car", the API will return a route that a car can take. Using "truck"
              will return a route a truck can use, taking into account appropriate truck
              routing restrictions.

              When "mode=truck", following are the default dimensions that are used:

              \\-- truck_height = 214 centimeters

              \\-- truck_width = 183 centimeters

              \\-- truck_length = 519 centimeters

              \\-- truck_weight = 5000 kg

              Please use the Directions Flexible version if you want to use custom truck
              dimensions.

              Note: Only the "car" profile is enabled by default. Please note that customized
              profiles (including "truck") might not be available for all regions. Please
              contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
              representative or reach out at
              [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
              additional profiles.

          roundtrip: Indicates whether the returned route is a roundtrip.

          source: The coordinate at which to start the returned route. If this is not configured,
              the return route’s destination will be the first coordinate.

          with_geometry: Indicates whether the return geometry should be computed or not.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/optimization/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "coordinates": coordinates,
                        "key": key,
                        "approaches": approaches,
                        "destination": destination,
                        "geometries": geometries,
                        "mode": mode,
                        "roundtrip": roundtrip,
                        "source": source,
                        "with_geometry": with_geometry,
                    },
                    optimization_compute_params.OptimizationComputeParams,
                ),
            ),
            cast_to=OptimizationComputeResponse,
        )

    async def re_optimize(
        self,
        *,
        key: str,
        existing_request_id: str,
        job_changes: optimization_re_optimize_params.JobChanges | NotGiven = NOT_GIVEN,
        locations: List[str] | NotGiven = NOT_GIVEN,
        shipment_changes: optimization_re_optimize_params.ShipmentChanges | NotGiven = NOT_GIVEN,
        vehicle_changes: optimization_re_optimize_params.VehicleChanges | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PostResponse:
        """
        Re-optimization

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          existing_request_id: Specify the unique request ID that needs to be re-optimized.

          job_changes: This section gathers information on modifications to the number of jobs or their
              individual requirements for re-optimization. Any job from the original solution
              not specified here will be re-planned without alteration during the
              re-optimization process.

          locations: Provide the list of locations to be used during re-optimization process. Please
              note that

              - Providing the location input overwrites the list of locations used in the
                original request.
              - The location_indexes associated with all tasks and vehicles (both from the
                original and new re-optimization input requests) will follow the updated list
                of locations.

              As a best practice:

              1.  Don't provide the locations input when re-optimizing, if the original set
                  contains all the required location coordinates.
              2.  If any new location coordinates are required for re-optimization, copy the
                  full, original location list and update it in the following manner before
                  adding it to the re-optimization input:

                  1.  Ensure to not update the indexes of locations which just need to be
                      "modified".
                  2.  Add new location coordinates towards the end of the list.

          shipment_changes: This section gathers information on modifications to the number of shipments or
              their individual requirements for re-optimization. Any shipment from the
              original solution not specified here will be re-planned without alteration
              during the re-optimization process.

          vehicle_changes: This section gathers information on modifications to the number of vehicles or
              individual vehicle configurations for re-optimizing an existing solution. Any
              vehicle from the original solution not specified here will be reused without
              alteration during the re-optimization process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/optimization/re_optimization",
            body=await async_maybe_transform(
                {
                    "existing_request_id": existing_request_id,
                    "job_changes": job_changes,
                    "locations": locations,
                    "shipment_changes": shipment_changes,
                    "vehicle_changes": vehicle_changes,
                },
                optimization_re_optimize_params.OptimizationReOptimizeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, optimization_re_optimize_params.OptimizationReOptimizeParams
                ),
            ),
            cast_to=PostResponse,
        )


class OptimizationResourceWithRawResponse:
    def __init__(self, optimization: OptimizationResource) -> None:
        self._optimization = optimization

        self.compute = to_raw_response_wrapper(
            optimization.compute,
        )
        self.re_optimize = to_raw_response_wrapper(
            optimization.re_optimize,
        )

    @cached_property
    def driver_assignment(self) -> DriverAssignmentResourceWithRawResponse:
        return DriverAssignmentResourceWithRawResponse(self._optimization.driver_assignment)

    @cached_property
    def v2(self) -> V2ResourceWithRawResponse:
        return V2ResourceWithRawResponse(self._optimization.v2)


class AsyncOptimizationResourceWithRawResponse:
    def __init__(self, optimization: AsyncOptimizationResource) -> None:
        self._optimization = optimization

        self.compute = async_to_raw_response_wrapper(
            optimization.compute,
        )
        self.re_optimize = async_to_raw_response_wrapper(
            optimization.re_optimize,
        )

    @cached_property
    def driver_assignment(self) -> AsyncDriverAssignmentResourceWithRawResponse:
        return AsyncDriverAssignmentResourceWithRawResponse(self._optimization.driver_assignment)

    @cached_property
    def v2(self) -> AsyncV2ResourceWithRawResponse:
        return AsyncV2ResourceWithRawResponse(self._optimization.v2)


class OptimizationResourceWithStreamingResponse:
    def __init__(self, optimization: OptimizationResource) -> None:
        self._optimization = optimization

        self.compute = to_streamed_response_wrapper(
            optimization.compute,
        )
        self.re_optimize = to_streamed_response_wrapper(
            optimization.re_optimize,
        )

    @cached_property
    def driver_assignment(self) -> DriverAssignmentResourceWithStreamingResponse:
        return DriverAssignmentResourceWithStreamingResponse(self._optimization.driver_assignment)

    @cached_property
    def v2(self) -> V2ResourceWithStreamingResponse:
        return V2ResourceWithStreamingResponse(self._optimization.v2)


class AsyncOptimizationResourceWithStreamingResponse:
    def __init__(self, optimization: AsyncOptimizationResource) -> None:
        self._optimization = optimization

        self.compute = async_to_streamed_response_wrapper(
            optimization.compute,
        )
        self.re_optimize = async_to_streamed_response_wrapper(
            optimization.re_optimize,
        )

    @cached_property
    def driver_assignment(self) -> AsyncDriverAssignmentResourceWithStreamingResponse:
        return AsyncDriverAssignmentResourceWithStreamingResponse(self._optimization.driver_assignment)

    @cached_property
    def v2(self) -> AsyncV2ResourceWithStreamingResponse:
        return AsyncV2ResourceWithStreamingResponse(self._optimization.v2)
