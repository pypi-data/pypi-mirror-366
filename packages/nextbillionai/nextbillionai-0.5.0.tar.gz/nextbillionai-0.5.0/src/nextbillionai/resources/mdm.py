# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import mdm_create_distance_matrix_params, mdm_get_distance_matrix_status_params
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
from ..types.mdm_create_distance_matrix_response import MdmCreateDistanceMatrixResponse
from ..types.mdm_get_distance_matrix_status_response import MdmGetDistanceMatrixStatusResponse

__all__ = ["MdmResource", "AsyncMdmResource"]


class MdmResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MdmResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return MdmResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MdmResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return MdmResourceWithStreamingResponse(self)

    def create_distance_matrix(
        self,
        *,
        key: str,
        option: Literal["flexible"],
        origins: str,
        spliter: Literal["od_number_spliter", "straight_distance_spliter", "location_spliter"] | NotGiven = NOT_GIVEN,
        area: Literal["singapore", "usa", "india"] | NotGiven = NOT_GIVEN,
        avoid: Literal[
            "toll", "ferry", "highway", "sharp_turn", "service_road", "bbox", "left_turn", "right_turn", "none"
        ]
        | NotGiven = NOT_GIVEN,
        cross_border: bool | NotGiven = NOT_GIVEN,
        departure_time: int | NotGiven = NOT_GIVEN,
        destinations: str | NotGiven = NOT_GIVEN,
        destinations_approach: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        hazmat_type: Literal["general", "circumstantial", "explosive", "harmful_to_water"] | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        origins_approach: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        route_type: Literal["fastest", "shortest"] | NotGiven = NOT_GIVEN,
        truck_axle_load: float | NotGiven = NOT_GIVEN,
        truck_size: str | NotGiven = NOT_GIVEN,
        truck_weight: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MdmCreateDistanceMatrixResponse:
        """
        Create a massive distance matrix task

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          option: Use this option to switch to truck-specific routing or time based routing or if
              you want to choose between the fastest and shortest route types.

          origins: origins are the starting point of your route. Ensure that origins are routable
              land locations. Multiple origins should be separated by a pipe symbol (|).

              **Format:** latitude_1,longitude_1|latitude_2,longitude_2|…

          spliter:
              Specify a spliter to split the matrix by. It accepts 2 values:

              - od_number_spliter:

              - straight_distance_spliter:

              Please note it is an internal, debug field only.

              _debug field. choose specific spliter to split matrix._

          area: Provide the country that the coordinates belong to.

              _the input coordinates area._

          avoid: Setting this will ensure the route avoids the object(s) specified as input.
              Multiple values should be separated by a pipe (|). If none is provided along
              with other values, an error is returned as a valid route is not feasible.

              - **Note:**

                - This parameter is effective only when route_type=fastest.
                - When this parameter is not provided in the input, ferries are set to be
                  avoided by default. When avoid input is provided, only the mentioned objects
                  are avoided.
                - When using avoid=bbox users also need to specify the boundaries of the
                  bounding box to be avoid. Multiple bounding boxes can be specified
                  simultaneously. Please note that bounding box is a hard filter and if it
                  blocks all possible routes between given locations, a 4xx error is returned.

                  - **Format:** bbox: min_latitude,min_longtitude,max_latitude,max_longitude.
                  - **Example:** avoid=bbox: 34.0635,-118.2547, 34.0679,-118.2478 | bbox:
                    34.0521,-118.2342, 34.0478,-118.2437

                - When using avoid=sharp_turn, default range of permissible turn angles is
                  \\[[120,240\\]].

          cross_border: Specify if crossing an international border is expected for operations near
              border areas. When set to false, the API will prohibit routes going back & forth
              between countries. Consequently, routes within the same country will be
              preferred if they are feasible for the given set of destination or waypoints .
              When set to true, the routes will be allowed to go back & forth between
              countries as needed.

              This feature is available in North America region only. Please get in touch with
              [support@nextbillion.ai](mailto:support@nextbillion.ai) to enquire/enable other
              areas.

          departure_time: This is a number in UNIX epoch timestamp in seconds format that can be used to
              provide the departure time. The response will return the distance and duration
              of the route based on typical traffic for at the given start time.If no input is
              provided for this parameter then the traffic conditions at the time of making
              the request are considered.

              Please note that when route_type is set to shortest then the departure_time will
              be ineffective as the service will return the result for the shortest path
              possible irrespective of the traffic conditions.

          destinations: destinations are the ending coordinates of your route. Ensure that destinations
              are routable land locations. Multiple destinations should be separated by a pipe
              symbol (|).

              In case destinations are not provided or if it is left empty, then the input
              value of origins will be copied to destinations to create the OD matrix pairs.

              **Format:** latitude_1,longitude_1|latitude_2,longitude_2|…

          destinations_approach: Specify the side of the road from which to approach destinations points. Please
              note that the given approach will be applied to all the destinations.

          hazmat_type: Specify the type of hazardous material being carried and the service will avoid
              roads which are not suitable for the type of goods specified. Multiple values
              can be separated using a pipe operator | .

              Please note that this parameter is effective only when mode=truck.

          mode: Set which driving mode the service should use to determine a route.

              For example, if you use car, the API will return a route that a car can take.
              Using truck will return a route a truck can use, taking into account appropriate
              truck routing restrictions.

          origins_approach: Specify the side of the road from which to approach origins points. Please note
              that the given approach will be applied to all the points provided as origins.

          route_type: Set the route type that needs to be returned. Please note that route_type is
              effective only when option=flexible.

          truck_axle_load: Specify the total load per axle (including the weight of trailers and shipped
              goods) of the truck, in tonnes. When used, the service will return routes which
              are legally allowed to carry the load specified per axle.

              Please note this parameter is effective only when mode=truck.

          truck_size: This defines the dimensions of a truck in centimeters (cm) in the format of
              "height,width,length". This parameter is effective only when mode=truck and
              option=flexible. Maximum dimensions are as follows:

              Height = 1000 cm Width = 5000 cm Length = 5000 cm

          truck_weight: This parameter defines the weight of the truck including trailers and shipped
              goods in kilograms (kg). This parameter is effective only when mode=truck and
              option=flexible.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/mdm/create",
            body=maybe_transform(
                {
                    "origins": origins,
                    "area": area,
                    "avoid": avoid,
                    "cross_border": cross_border,
                    "departure_time": departure_time,
                    "destinations": destinations,
                    "destinations_approach": destinations_approach,
                    "hazmat_type": hazmat_type,
                    "mode": mode,
                    "origins_approach": origins_approach,
                    "route_type": route_type,
                    "truck_axle_load": truck_axle_load,
                    "truck_size": truck_size,
                    "truck_weight": truck_weight,
                },
                mdm_create_distance_matrix_params.MdmCreateDistanceMatrixParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "option": option,
                        "spliter": spliter,
                    },
                    mdm_create_distance_matrix_params.MdmCreateDistanceMatrixParams,
                ),
            ),
            cast_to=MdmCreateDistanceMatrixResponse,
        )

    def get_distance_matrix_status(
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
    ) -> MdmGetDistanceMatrixStatusResponse:
        """
        Get massive distance matrix task status

        Args:
          id: Provide the unique ID that was returned on successful submission of the
              Asynchronous Distance Matrix POST request.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/mdm/status",
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
                    mdm_get_distance_matrix_status_params.MdmGetDistanceMatrixStatusParams,
                ),
            ),
            cast_to=MdmGetDistanceMatrixStatusResponse,
        )


class AsyncMdmResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMdmResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMdmResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMdmResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncMdmResourceWithStreamingResponse(self)

    async def create_distance_matrix(
        self,
        *,
        key: str,
        option: Literal["flexible"],
        origins: str,
        spliter: Literal["od_number_spliter", "straight_distance_spliter", "location_spliter"] | NotGiven = NOT_GIVEN,
        area: Literal["singapore", "usa", "india"] | NotGiven = NOT_GIVEN,
        avoid: Literal[
            "toll", "ferry", "highway", "sharp_turn", "service_road", "bbox", "left_turn", "right_turn", "none"
        ]
        | NotGiven = NOT_GIVEN,
        cross_border: bool | NotGiven = NOT_GIVEN,
        departure_time: int | NotGiven = NOT_GIVEN,
        destinations: str | NotGiven = NOT_GIVEN,
        destinations_approach: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        hazmat_type: Literal["general", "circumstantial", "explosive", "harmful_to_water"] | NotGiven = NOT_GIVEN,
        mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        origins_approach: Literal["unrestricted", "curb"] | NotGiven = NOT_GIVEN,
        route_type: Literal["fastest", "shortest"] | NotGiven = NOT_GIVEN,
        truck_axle_load: float | NotGiven = NOT_GIVEN,
        truck_size: str | NotGiven = NOT_GIVEN,
        truck_weight: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MdmCreateDistanceMatrixResponse:
        """
        Create a massive distance matrix task

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          option: Use this option to switch to truck-specific routing or time based routing or if
              you want to choose between the fastest and shortest route types.

          origins: origins are the starting point of your route. Ensure that origins are routable
              land locations. Multiple origins should be separated by a pipe symbol (|).

              **Format:** latitude_1,longitude_1|latitude_2,longitude_2|…

          spliter:
              Specify a spliter to split the matrix by. It accepts 2 values:

              - od_number_spliter:

              - straight_distance_spliter:

              Please note it is an internal, debug field only.

              _debug field. choose specific spliter to split matrix._

          area: Provide the country that the coordinates belong to.

              _the input coordinates area._

          avoid: Setting this will ensure the route avoids the object(s) specified as input.
              Multiple values should be separated by a pipe (|). If none is provided along
              with other values, an error is returned as a valid route is not feasible.

              - **Note:**

                - This parameter is effective only when route_type=fastest.
                - When this parameter is not provided in the input, ferries are set to be
                  avoided by default. When avoid input is provided, only the mentioned objects
                  are avoided.
                - When using avoid=bbox users also need to specify the boundaries of the
                  bounding box to be avoid. Multiple bounding boxes can be specified
                  simultaneously. Please note that bounding box is a hard filter and if it
                  blocks all possible routes between given locations, a 4xx error is returned.

                  - **Format:** bbox: min_latitude,min_longtitude,max_latitude,max_longitude.
                  - **Example:** avoid=bbox: 34.0635,-118.2547, 34.0679,-118.2478 | bbox:
                    34.0521,-118.2342, 34.0478,-118.2437

                - When using avoid=sharp_turn, default range of permissible turn angles is
                  \\[[120,240\\]].

          cross_border: Specify if crossing an international border is expected for operations near
              border areas. When set to false, the API will prohibit routes going back & forth
              between countries. Consequently, routes within the same country will be
              preferred if they are feasible for the given set of destination or waypoints .
              When set to true, the routes will be allowed to go back & forth between
              countries as needed.

              This feature is available in North America region only. Please get in touch with
              [support@nextbillion.ai](mailto:support@nextbillion.ai) to enquire/enable other
              areas.

          departure_time: This is a number in UNIX epoch timestamp in seconds format that can be used to
              provide the departure time. The response will return the distance and duration
              of the route based on typical traffic for at the given start time.If no input is
              provided for this parameter then the traffic conditions at the time of making
              the request are considered.

              Please note that when route_type is set to shortest then the departure_time will
              be ineffective as the service will return the result for the shortest path
              possible irrespective of the traffic conditions.

          destinations: destinations are the ending coordinates of your route. Ensure that destinations
              are routable land locations. Multiple destinations should be separated by a pipe
              symbol (|).

              In case destinations are not provided or if it is left empty, then the input
              value of origins will be copied to destinations to create the OD matrix pairs.

              **Format:** latitude_1,longitude_1|latitude_2,longitude_2|…

          destinations_approach: Specify the side of the road from which to approach destinations points. Please
              note that the given approach will be applied to all the destinations.

          hazmat_type: Specify the type of hazardous material being carried and the service will avoid
              roads which are not suitable for the type of goods specified. Multiple values
              can be separated using a pipe operator | .

              Please note that this parameter is effective only when mode=truck.

          mode: Set which driving mode the service should use to determine a route.

              For example, if you use car, the API will return a route that a car can take.
              Using truck will return a route a truck can use, taking into account appropriate
              truck routing restrictions.

          origins_approach: Specify the side of the road from which to approach origins points. Please note
              that the given approach will be applied to all the points provided as origins.

          route_type: Set the route type that needs to be returned. Please note that route_type is
              effective only when option=flexible.

          truck_axle_load: Specify the total load per axle (including the weight of trailers and shipped
              goods) of the truck, in tonnes. When used, the service will return routes which
              are legally allowed to carry the load specified per axle.

              Please note this parameter is effective only when mode=truck.

          truck_size: This defines the dimensions of a truck in centimeters (cm) in the format of
              "height,width,length". This parameter is effective only when mode=truck and
              option=flexible. Maximum dimensions are as follows:

              Height = 1000 cm Width = 5000 cm Length = 5000 cm

          truck_weight: This parameter defines the weight of the truck including trailers and shipped
              goods in kilograms (kg). This parameter is effective only when mode=truck and
              option=flexible.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/mdm/create",
            body=await async_maybe_transform(
                {
                    "origins": origins,
                    "area": area,
                    "avoid": avoid,
                    "cross_border": cross_border,
                    "departure_time": departure_time,
                    "destinations": destinations,
                    "destinations_approach": destinations_approach,
                    "hazmat_type": hazmat_type,
                    "mode": mode,
                    "origins_approach": origins_approach,
                    "route_type": route_type,
                    "truck_axle_load": truck_axle_load,
                    "truck_size": truck_size,
                    "truck_weight": truck_weight,
                },
                mdm_create_distance_matrix_params.MdmCreateDistanceMatrixParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "option": option,
                        "spliter": spliter,
                    },
                    mdm_create_distance_matrix_params.MdmCreateDistanceMatrixParams,
                ),
            ),
            cast_to=MdmCreateDistanceMatrixResponse,
        )

    async def get_distance_matrix_status(
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
    ) -> MdmGetDistanceMatrixStatusResponse:
        """
        Get massive distance matrix task status

        Args:
          id: Provide the unique ID that was returned on successful submission of the
              Asynchronous Distance Matrix POST request.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/mdm/status",
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
                    mdm_get_distance_matrix_status_params.MdmGetDistanceMatrixStatusParams,
                ),
            ),
            cast_to=MdmGetDistanceMatrixStatusResponse,
        )


class MdmResourceWithRawResponse:
    def __init__(self, mdm: MdmResource) -> None:
        self._mdm = mdm

        self.create_distance_matrix = to_raw_response_wrapper(
            mdm.create_distance_matrix,
        )
        self.get_distance_matrix_status = to_raw_response_wrapper(
            mdm.get_distance_matrix_status,
        )


class AsyncMdmResourceWithRawResponse:
    def __init__(self, mdm: AsyncMdmResource) -> None:
        self._mdm = mdm

        self.create_distance_matrix = async_to_raw_response_wrapper(
            mdm.create_distance_matrix,
        )
        self.get_distance_matrix_status = async_to_raw_response_wrapper(
            mdm.get_distance_matrix_status,
        )


class MdmResourceWithStreamingResponse:
    def __init__(self, mdm: MdmResource) -> None:
        self._mdm = mdm

        self.create_distance_matrix = to_streamed_response_wrapper(
            mdm.create_distance_matrix,
        )
        self.get_distance_matrix_status = to_streamed_response_wrapper(
            mdm.get_distance_matrix_status,
        )


class AsyncMdmResourceWithStreamingResponse:
    def __init__(self, mdm: AsyncMdmResource) -> None:
        self._mdm = mdm

        self.create_distance_matrix = async_to_streamed_response_wrapper(
            mdm.create_distance_matrix,
        )
        self.get_distance_matrix_status = async_to_streamed_response_wrapper(
            mdm.get_distance_matrix_status,
        )
