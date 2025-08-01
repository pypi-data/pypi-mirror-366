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
from ...types.optimization import driver_assignment_assign_params
from ...types.optimization.vehicle_param import VehicleParam
from ...types.optimization.driver_assignment_assign_response import DriverAssignmentAssignResponse

__all__ = ["DriverAssignmentResource", "AsyncDriverAssignmentResource"]


class DriverAssignmentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DriverAssignmentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return DriverAssignmentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DriverAssignmentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return DriverAssignmentResourceWithStreamingResponse(self)

    def assign(
        self,
        *,
        key: str,
        filter: driver_assignment_assign_params.Filter,
        orders: Iterable[driver_assignment_assign_params.Order],
        vehicles: Iterable[VehicleParam],
        options: driver_assignment_assign_params.Options | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DriverAssignmentAssignResponse:
        """
        Assigns available drivers (vehicles) to open orders based on specified criteria
        and constraints.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          filter: Specify the filtering criterion for the vehicles with respect to each order's
              location. filter is a mandatory input for all requests.

          orders: Collects the details of open orders to be fulfilled. Each object represents one
              order. All requests must include orders as a mandatory input. A maximum of 200
              orders is allowed per request.

          vehicles: Collects the details of vehicles available to fulfill the orders. Each object
              represents one vehicle. All requests must include vehicles as a mandatory input.
              A maximum of 100 vehicles is allowed per request.

          options: Configure the assignment constraints and response settings.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/optimization/driver-assignment/v1",
            body=maybe_transform(
                {
                    "filter": filter,
                    "orders": orders,
                    "vehicles": vehicles,
                    "options": options,
                },
                driver_assignment_assign_params.DriverAssignmentAssignParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, driver_assignment_assign_params.DriverAssignmentAssignParams),
            ),
            cast_to=DriverAssignmentAssignResponse,
        )


class AsyncDriverAssignmentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDriverAssignmentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDriverAssignmentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDriverAssignmentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncDriverAssignmentResourceWithStreamingResponse(self)

    async def assign(
        self,
        *,
        key: str,
        filter: driver_assignment_assign_params.Filter,
        orders: Iterable[driver_assignment_assign_params.Order],
        vehicles: Iterable[VehicleParam],
        options: driver_assignment_assign_params.Options | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DriverAssignmentAssignResponse:
        """
        Assigns available drivers (vehicles) to open orders based on specified criteria
        and constraints.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          filter: Specify the filtering criterion for the vehicles with respect to each order's
              location. filter is a mandatory input for all requests.

          orders: Collects the details of open orders to be fulfilled. Each object represents one
              order. All requests must include orders as a mandatory input. A maximum of 200
              orders is allowed per request.

          vehicles: Collects the details of vehicles available to fulfill the orders. Each object
              represents one vehicle. All requests must include vehicles as a mandatory input.
              A maximum of 100 vehicles is allowed per request.

          options: Configure the assignment constraints and response settings.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/optimization/driver-assignment/v1",
            body=await async_maybe_transform(
                {
                    "filter": filter,
                    "orders": orders,
                    "vehicles": vehicles,
                    "options": options,
                },
                driver_assignment_assign_params.DriverAssignmentAssignParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, driver_assignment_assign_params.DriverAssignmentAssignParams
                ),
            ),
            cast_to=DriverAssignmentAssignResponse,
        )


class DriverAssignmentResourceWithRawResponse:
    def __init__(self, driver_assignment: DriverAssignmentResource) -> None:
        self._driver_assignment = driver_assignment

        self.assign = to_raw_response_wrapper(
            driver_assignment.assign,
        )


class AsyncDriverAssignmentResourceWithRawResponse:
    def __init__(self, driver_assignment: AsyncDriverAssignmentResource) -> None:
        self._driver_assignment = driver_assignment

        self.assign = async_to_raw_response_wrapper(
            driver_assignment.assign,
        )


class DriverAssignmentResourceWithStreamingResponse:
    def __init__(self, driver_assignment: DriverAssignmentResource) -> None:
        self._driver_assignment = driver_assignment

        self.assign = to_streamed_response_wrapper(
            driver_assignment.assign,
        )


class AsyncDriverAssignmentResourceWithStreamingResponse:
    def __init__(self, driver_assignment: AsyncDriverAssignmentResource) -> None:
        self._driver_assignment = driver_assignment

        self.assign = async_to_streamed_response_wrapper(
            driver_assignment.assign,
        )
