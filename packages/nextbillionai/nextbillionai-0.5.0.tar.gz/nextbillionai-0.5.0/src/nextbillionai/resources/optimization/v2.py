# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ...types.optimization import v2_submit_params, v2_retrieve_result_params
from ...types.post_response import PostResponse
from ...types.optimization.job_param import JobParam
from ...types.optimization.vehicle_param import VehicleParam
from ...types.optimization.shipment_param import ShipmentParam
from ...types.optimization.v2_retrieve_result_response import V2RetrieveResultResponse

__all__ = ["V2Resource", "AsyncV2Resource"]


class V2Resource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> V2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return V2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return V2ResourceWithStreamingResponse(self)

    def retrieve_result(
        self,
        *,
        id: str,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V2RetrieveResultResponse:
        """
        Flexible GET

        Args:
          id: The unique ID that was returned on successful submission of the Optimization
              POST request.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/optimization/v2/result",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "key": key,
                    },
                    v2_retrieve_result_params.V2RetrieveResultParams,
                ),
            ),
            cast_to=V2RetrieveResultResponse,
        )

    def submit(
        self,
        *,
        key: str,
        locations: v2_submit_params.Locations,
        vehicles: Iterable[VehicleParam],
        cost_matrix: Iterable[Iterable[int]] | NotGiven = NOT_GIVEN,
        depots: Iterable[v2_submit_params.Depot] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        distance_matrix: Iterable[Iterable[int]] | NotGiven = NOT_GIVEN,
        duration_matrix: Iterable[Iterable[int]] | NotGiven = NOT_GIVEN,
        existing_solution_id: str | NotGiven = NOT_GIVEN,
        jobs: Iterable[JobParam] | NotGiven = NOT_GIVEN,
        options: v2_submit_params.Options | NotGiven = NOT_GIVEN,
        relations: Iterable[v2_submit_params.Relation] | NotGiven = NOT_GIVEN,
        shipments: Iterable[ShipmentParam] | NotGiven = NOT_GIVEN,
        solution: Iterable[v2_submit_params.Solution] | NotGiven = NOT_GIVEN,
        unassigned: v2_submit_params.Unassigned | NotGiven = NOT_GIVEN,
        zones: Iterable[v2_submit_params.Zone] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PostResponse:
        """
        Flexible POST

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          locations: The locations object is used to define all the locations that will be used
              during the optimization process. Read more about this attribute in the
              [Location Object](#location-object) section.

          vehicles: The vehicles attribute describes the characteristics and constraints of the
              vehicles that will be used for fulfilling the tasks. Read more about this
              attribute in the [Vehicle Object](#vehicle-object) section.

          cost_matrix: An array of arrays to denote the user-defined costs of traveling between each
              pair of geographic coordinates mentioned in the location array. The number of
              arrays should be equal to the number of coordinate points mentioned in the
              location array and each array should contain the same number of elements as
              well. Please note that cost_matrix is effective only when
              travel_cost=customized. Read more about this attribute in the
              [Custom Cost Matrix](#custom-cost-matrix) section.

          depots: depots object is used to collect the details of a depot. Depots can be used as a
              starting point and/or ending point for the routes and vehicles. They also can be
              used to fulfil pickup and delivery typejobs . The loads which are to be
              delivered at task locations will be picked from depots and loads picked-up from
              task locations will be delivered back to the depots. A depot can be configured
              using the following fields:

          description: Define the optimization job using any custom message. This description is
              returned as is in the response.

          distance_matrix: An array of arrays to denote the user-defined distances, in meters, for
              travelling between each pair of geographic coordinates mentioned in the location
              array. When this input is provided, actual distances between the locations will
              be ignored in favor of the values provided in this input for any distance
              calculations during the optimization process. The values provided here will also
              be used for cost calculations when travel_cost is “distance”.

              The number of arrays in the input should be equal to the number of coordinate
              points mentioned in the location array and each array, in turn, should contain
              the same number of elements as well.

              **Note:**

              - duration_matrix is mandatory when usingdistance_matrix.
              - When using distance_matrix route geometry will not be available in the
                optimized solution.

          duration_matrix: An array of arrays to denote the user-defined durations, in seconds, for
              travelling between each pair of geographic coordinates mentioned in the location
              array. When this input is provided, actual durations between the locations will
              be ignored in favor of the values provided in the matrix for any ETA
              calculations during the optimization process. The values provided in the matrix
              will also be used for cost calculations when travel_cost is “duration”.

              The number of arrays in the input should be equal to the number of coordinate
              points mentioned in the location array and each array, in turn, should contain
              the same number of elements as well.

              Please note that, unlike distance_matrix, duration_matrix can be used
              independently in following cases:

              - when travel_cost is “duration”
              - when travel_cost is “customized” and a cost_matrix is provided

              Also, the route geometry will not be available in the optimized solution when
              using duration_matrix.

          existing_solution_id: The previous optimization request id used to retrieve solution for
              reoptimization

          jobs: jobs object is used to collect the details of a particular job or task that
              needs to be completed as part of the optimization process. Each job can have
              either a pickup or delivery step, but not both. Read more about this attribute
              in the [Job Object](#job-object) section.

              Please note that either the jobs or the shipments attribute should be specified
              to build a valid request.

          options: It represents the set of options that can be used to configure optimization
              algorithms so that the solver provides a solution that meets the desired
              business objectives.

          relations: relations attribute is an array of individual relation objects. type parameter
              and steps object are mandatory when using this attribute.

              Please note:

              - The soft constraints are **not** effective when using the relations attribute.
              - In case a given relation can't be satisfied, the optimizer will flag all the
                tasks involved in that "relation" as unassigned.

              Read more about this attribute in the [Relations Object](#relations-object)
              section.

          shipments: The shipments object is used to collect the details of shipments that need to be
              completed as part of the optimization process.

              Each shipment should have a pickup and the corresponding delivery step.

              Please note that either the jobs or the shipments attribute should be specified
              to build a valid request.

          solution: This attribute is related to the re-optimization feature. It allows for the
              previous optimization result to be provided in case new orders are received and
              the solution needs to be re-planned. The solution attribute should contain the
              same routes as the previous optimization result. solution attribute is an array
              of objects with each object corresponding to one route.

          unassigned: unassigned attribute is related to the re-optimization feature. This attribute
              should contain the tasks that were not assigned during an earlier optimization
              process. Please note that the unassigned part in request should be consistent
              with the unassigned part in the previous optimization result.

              Users can reduce the number of unassigned tasks in the re-optimized solution, by
              following strategies such as:

              - Extending the time windows for vehicles or tasks to give more flexibility
              - Adding more vehicles to the optimization problem
              - Adjusting the priority of different tasks to balance the workload more evenly
              - Modifying other constraints or parameters to make the problem more solvable

              Ultimately, the goal is to minimize the number of unassigned tasks while still
              meeting all the necessary constraints and objectives.

          zones: An array of objects to specify geometry of all the zones involved. Each object
              corresponds to a single zone. A valid zone can be a
              [geoJSON](https://datatracker.ietf.org/doc/html/rfc7946#page-9) polygon,
              multi-polygon or a geofence created using
              [NextBillion.ai](http://NextBillion.ai)’s
              [Geofence API](https://docs.nextbillion.ai/docs/tracking/api/geofence).

              Please note that

              - Each zone should have a geometry specified either throughgeometry or through
                the geofence_id parameter.
              - When zone IDs are not provided for individual tasks (jobs or shipments) then
                the API will automatically allocate zones based on the task’s geolocation and
                the geometries of the zones provided here. Otherwise, if the zone IDs are
                provided while configuring individual tasks, the zone IDs will override the
                geometries provided here.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/optimization/v2",
            body=maybe_transform(
                {
                    "locations": locations,
                    "vehicles": vehicles,
                    "cost_matrix": cost_matrix,
                    "depots": depots,
                    "description": description,
                    "distance_matrix": distance_matrix,
                    "duration_matrix": duration_matrix,
                    "existing_solution_id": existing_solution_id,
                    "jobs": jobs,
                    "options": options,
                    "relations": relations,
                    "shipments": shipments,
                    "solution": solution,
                    "unassigned": unassigned,
                    "zones": zones,
                },
                v2_submit_params.V2SubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, v2_submit_params.V2SubmitParams),
            ),
            cast_to=PostResponse,
        )


class AsyncV2Resource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncV2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncV2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncV2ResourceWithStreamingResponse(self)

    async def retrieve_result(
        self,
        *,
        id: str,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V2RetrieveResultResponse:
        """
        Flexible GET

        Args:
          id: The unique ID that was returned on successful submission of the Optimization
              POST request.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/optimization/v2/result",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "key": key,
                    },
                    v2_retrieve_result_params.V2RetrieveResultParams,
                ),
            ),
            cast_to=V2RetrieveResultResponse,
        )

    async def submit(
        self,
        *,
        key: str,
        locations: v2_submit_params.Locations,
        vehicles: Iterable[VehicleParam],
        cost_matrix: Iterable[Iterable[int]] | NotGiven = NOT_GIVEN,
        depots: Iterable[v2_submit_params.Depot] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        distance_matrix: Iterable[Iterable[int]] | NotGiven = NOT_GIVEN,
        duration_matrix: Iterable[Iterable[int]] | NotGiven = NOT_GIVEN,
        existing_solution_id: str | NotGiven = NOT_GIVEN,
        jobs: Iterable[JobParam] | NotGiven = NOT_GIVEN,
        options: v2_submit_params.Options | NotGiven = NOT_GIVEN,
        relations: Iterable[v2_submit_params.Relation] | NotGiven = NOT_GIVEN,
        shipments: Iterable[ShipmentParam] | NotGiven = NOT_GIVEN,
        solution: Iterable[v2_submit_params.Solution] | NotGiven = NOT_GIVEN,
        unassigned: v2_submit_params.Unassigned | NotGiven = NOT_GIVEN,
        zones: Iterable[v2_submit_params.Zone] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PostResponse:
        """
        Flexible POST

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          locations: The locations object is used to define all the locations that will be used
              during the optimization process. Read more about this attribute in the
              [Location Object](#location-object) section.

          vehicles: The vehicles attribute describes the characteristics and constraints of the
              vehicles that will be used for fulfilling the tasks. Read more about this
              attribute in the [Vehicle Object](#vehicle-object) section.

          cost_matrix: An array of arrays to denote the user-defined costs of traveling between each
              pair of geographic coordinates mentioned in the location array. The number of
              arrays should be equal to the number of coordinate points mentioned in the
              location array and each array should contain the same number of elements as
              well. Please note that cost_matrix is effective only when
              travel_cost=customized. Read more about this attribute in the
              [Custom Cost Matrix](#custom-cost-matrix) section.

          depots: depots object is used to collect the details of a depot. Depots can be used as a
              starting point and/or ending point for the routes and vehicles. They also can be
              used to fulfil pickup and delivery typejobs . The loads which are to be
              delivered at task locations will be picked from depots and loads picked-up from
              task locations will be delivered back to the depots. A depot can be configured
              using the following fields:

          description: Define the optimization job using any custom message. This description is
              returned as is in the response.

          distance_matrix: An array of arrays to denote the user-defined distances, in meters, for
              travelling between each pair of geographic coordinates mentioned in the location
              array. When this input is provided, actual distances between the locations will
              be ignored in favor of the values provided in this input for any distance
              calculations during the optimization process. The values provided here will also
              be used for cost calculations when travel_cost is “distance”.

              The number of arrays in the input should be equal to the number of coordinate
              points mentioned in the location array and each array, in turn, should contain
              the same number of elements as well.

              **Note:**

              - duration_matrix is mandatory when usingdistance_matrix.
              - When using distance_matrix route geometry will not be available in the
                optimized solution.

          duration_matrix: An array of arrays to denote the user-defined durations, in seconds, for
              travelling between each pair of geographic coordinates mentioned in the location
              array. When this input is provided, actual durations between the locations will
              be ignored in favor of the values provided in the matrix for any ETA
              calculations during the optimization process. The values provided in the matrix
              will also be used for cost calculations when travel_cost is “duration”.

              The number of arrays in the input should be equal to the number of coordinate
              points mentioned in the location array and each array, in turn, should contain
              the same number of elements as well.

              Please note that, unlike distance_matrix, duration_matrix can be used
              independently in following cases:

              - when travel_cost is “duration”
              - when travel_cost is “customized” and a cost_matrix is provided

              Also, the route geometry will not be available in the optimized solution when
              using duration_matrix.

          existing_solution_id: The previous optimization request id used to retrieve solution for
              reoptimization

          jobs: jobs object is used to collect the details of a particular job or task that
              needs to be completed as part of the optimization process. Each job can have
              either a pickup or delivery step, but not both. Read more about this attribute
              in the [Job Object](#job-object) section.

              Please note that either the jobs or the shipments attribute should be specified
              to build a valid request.

          options: It represents the set of options that can be used to configure optimization
              algorithms so that the solver provides a solution that meets the desired
              business objectives.

          relations: relations attribute is an array of individual relation objects. type parameter
              and steps object are mandatory when using this attribute.

              Please note:

              - The soft constraints are **not** effective when using the relations attribute.
              - In case a given relation can't be satisfied, the optimizer will flag all the
                tasks involved in that "relation" as unassigned.

              Read more about this attribute in the [Relations Object](#relations-object)
              section.

          shipments: The shipments object is used to collect the details of shipments that need to be
              completed as part of the optimization process.

              Each shipment should have a pickup and the corresponding delivery step.

              Please note that either the jobs or the shipments attribute should be specified
              to build a valid request.

          solution: This attribute is related to the re-optimization feature. It allows for the
              previous optimization result to be provided in case new orders are received and
              the solution needs to be re-planned. The solution attribute should contain the
              same routes as the previous optimization result. solution attribute is an array
              of objects with each object corresponding to one route.

          unassigned: unassigned attribute is related to the re-optimization feature. This attribute
              should contain the tasks that were not assigned during an earlier optimization
              process. Please note that the unassigned part in request should be consistent
              with the unassigned part in the previous optimization result.

              Users can reduce the number of unassigned tasks in the re-optimized solution, by
              following strategies such as:

              - Extending the time windows for vehicles or tasks to give more flexibility
              - Adding more vehicles to the optimization problem
              - Adjusting the priority of different tasks to balance the workload more evenly
              - Modifying other constraints or parameters to make the problem more solvable

              Ultimately, the goal is to minimize the number of unassigned tasks while still
              meeting all the necessary constraints and objectives.

          zones: An array of objects to specify geometry of all the zones involved. Each object
              corresponds to a single zone. A valid zone can be a
              [geoJSON](https://datatracker.ietf.org/doc/html/rfc7946#page-9) polygon,
              multi-polygon or a geofence created using
              [NextBillion.ai](http://NextBillion.ai)’s
              [Geofence API](https://docs.nextbillion.ai/docs/tracking/api/geofence).

              Please note that

              - Each zone should have a geometry specified either throughgeometry or through
                the geofence_id parameter.
              - When zone IDs are not provided for individual tasks (jobs or shipments) then
                the API will automatically allocate zones based on the task’s geolocation and
                the geometries of the zones provided here. Otherwise, if the zone IDs are
                provided while configuring individual tasks, the zone IDs will override the
                geometries provided here.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/optimization/v2",
            body=await async_maybe_transform(
                {
                    "locations": locations,
                    "vehicles": vehicles,
                    "cost_matrix": cost_matrix,
                    "depots": depots,
                    "description": description,
                    "distance_matrix": distance_matrix,
                    "duration_matrix": duration_matrix,
                    "existing_solution_id": existing_solution_id,
                    "jobs": jobs,
                    "options": options,
                    "relations": relations,
                    "shipments": shipments,
                    "solution": solution,
                    "unassigned": unassigned,
                    "zones": zones,
                },
                v2_submit_params.V2SubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, v2_submit_params.V2SubmitParams),
            ),
            cast_to=PostResponse,
        )


class V2ResourceWithRawResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

        self.retrieve_result = to_raw_response_wrapper(
            v2.retrieve_result,
        )
        self.submit = to_raw_response_wrapper(
            v2.submit,
        )


class AsyncV2ResourceWithRawResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

        self.retrieve_result = async_to_raw_response_wrapper(
            v2.retrieve_result,
        )
        self.submit = async_to_raw_response_wrapper(
            v2.submit,
        )


class V2ResourceWithStreamingResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

        self.retrieve_result = to_streamed_response_wrapper(
            v2.retrieve_result,
        )
        self.submit = to_streamed_response_wrapper(
            v2.submit,
        )


class AsyncV2ResourceWithStreamingResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

        self.retrieve_result = async_to_streamed_response_wrapper(
            v2.retrieve_result,
        )
        self.submit = async_to_streamed_response_wrapper(
            v2.submit,
        )
