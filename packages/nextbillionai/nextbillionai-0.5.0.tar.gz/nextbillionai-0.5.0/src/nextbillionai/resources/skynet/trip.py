# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

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
from ...types.skynet import (
    trip_end_params,
    trip_start_params,
    trip_delete_params,
    trip_update_params,
    trip_retrieve_params,
    trip_get_summary_params,
)
from ...types.skynet.simple_resp import SimpleResp
from ...types.skynet.trip_start_response import TripStartResponse
from ...types.skynet.trip_retrieve_response import TripRetrieveResponse
from ...types.skynet.trip_get_summary_response import TripGetSummaryResponse

__all__ = ["TripResource", "AsyncTripResource"]


class TripResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TripResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return TripResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TripResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return TripResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TripRetrieveResponse:
        """
        Retrieves detailed information about a specific trip.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/skynet/trip/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_retrieve_params.TripRetrieveParams,
                ),
            ),
            cast_to=TripRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        key: str,
        asset_id: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        stops: Iterable[trip_update_params.Stop] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Updates the data of a specified trip with the provided data.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          asset_id: Use this param to update the ID of the asset which made this trip. Please be
              cautious when using this field as providing an ID other than what was provided
              at the time of starting the trip, will link a new asset to the trip and un-link
              the original asset, even if the trip is still active.

          cluster: the cluster of the region you want to use

          attributes: Use this field to update the attributes of the trip. Please note that when
              updating the attributes field, previously added information will be overwritten.

          description: Use this parameter to update the custom description of the trip.

          meta_data: Use this JSON object to update additional details about the trip. This property
              is used to add any custom information / context about the trip.

              Please note that updating the meta_data field will overwrite the previously
              added information.

          name: Use this property to update the name of the trip.

          stops: Use this object to update the details of the stops made during the trip. Each
              object represents a single stop.

              Please note that when updating this field, the new stops will overwrite any
              existing stops configured for the trip.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/skynet/trip/{id}",
            body=maybe_transform(
                {
                    "asset_id": asset_id,
                    "attributes": attributes,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "stops": stops,
                },
                trip_update_params.TripUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_update_params.TripUpdateParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    def delete(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Deletes a specified trip from the system.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/skynet/trip/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_delete_params.TripDeleteParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    def end(
        self,
        *,
        key: str,
        id: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        End a trip

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          id: Specify the ID of the trip to be ended.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/trip/end",
            body=maybe_transform({"id": id}, trip_end_params.TripEndParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_end_params.TripEndParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    def get_summary(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TripGetSummaryResponse:
        """
        Get summary of an ended trip

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/skynet/trip/{id}/summary",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_get_summary_params.TripGetSummaryParams,
                ),
            ),
            cast_to=TripGetSummaryResponse,
        )

    def start(
        self,
        *,
        key: str,
        asset_id: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        stops: Iterable[trip_start_params.Stop] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TripStartResponse:
        """
        Add a new trip to the system with the provided data.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          asset_id: Specify the ID of the asset which is making this trip. The asset will be linked
              to this trip.

          cluster: the cluster of the region you want to use

          attributes: attributes can be used to store custom information about a trip in key:value
              format. Use attributes to add any useful information or context to your trips
              like the driver name, destination etc.

              Please note that the maximum number of key:value pairs that can be added to an
              attributes object is 100. Also, the overall size of attributes object should not
              exceed 65kb.

          custom_id: Set a unique ID for the new trip. If not provided, an ID will be automatically
              generated in UUID format. A valid custom_id can contain letters, numbers, “-”, &
              “\\__” only.

              Please note that the ID of a trip can not be changed once it is created.

          description: Add a custom description for the trip.

          meta_data: An JSON object to collect additional details about the trip. Use this property
              to add any custom information / context about the trip. The input will be passed
              on to the response as-is and can be used to display useful information on, for
              example, a UI app.

          name: Specify a name for the trip.

          stops: An array of objects to collect the details about all the stops that need to be
              made before the trip ends. Each object represents one stop.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/trip/start",
            body=maybe_transform(
                {
                    "asset_id": asset_id,
                    "attributes": attributes,
                    "custom_id": custom_id,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "stops": stops,
                },
                trip_start_params.TripStartParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_start_params.TripStartParams,
                ),
            ),
            cast_to=TripStartResponse,
        )


class AsyncTripResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTripResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTripResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTripResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncTripResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TripRetrieveResponse:
        """
        Retrieves detailed information about a specific trip.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/skynet/trip/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_retrieve_params.TripRetrieveParams,
                ),
            ),
            cast_to=TripRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        key: str,
        asset_id: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        stops: Iterable[trip_update_params.Stop] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Updates the data of a specified trip with the provided data.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          asset_id: Use this param to update the ID of the asset which made this trip. Please be
              cautious when using this field as providing an ID other than what was provided
              at the time of starting the trip, will link a new asset to the trip and un-link
              the original asset, even if the trip is still active.

          cluster: the cluster of the region you want to use

          attributes: Use this field to update the attributes of the trip. Please note that when
              updating the attributes field, previously added information will be overwritten.

          description: Use this parameter to update the custom description of the trip.

          meta_data: Use this JSON object to update additional details about the trip. This property
              is used to add any custom information / context about the trip.

              Please note that updating the meta_data field will overwrite the previously
              added information.

          name: Use this property to update the name of the trip.

          stops: Use this object to update the details of the stops made during the trip. Each
              object represents a single stop.

              Please note that when updating this field, the new stops will overwrite any
              existing stops configured for the trip.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/skynet/trip/{id}",
            body=await async_maybe_transform(
                {
                    "asset_id": asset_id,
                    "attributes": attributes,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "stops": stops,
                },
                trip_update_params.TripUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_update_params.TripUpdateParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    async def delete(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Deletes a specified trip from the system.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/skynet/trip/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_delete_params.TripDeleteParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    async def end(
        self,
        *,
        key: str,
        id: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        End a trip

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          id: Specify the ID of the trip to be ended.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/trip/end",
            body=await async_maybe_transform({"id": id}, trip_end_params.TripEndParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_end_params.TripEndParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    async def get_summary(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TripGetSummaryResponse:
        """
        Get summary of an ended trip

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/skynet/trip/{id}/summary",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_get_summary_params.TripGetSummaryParams,
                ),
            ),
            cast_to=TripGetSummaryResponse,
        )

    async def start(
        self,
        *,
        key: str,
        asset_id: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        stops: Iterable[trip_start_params.Stop] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TripStartResponse:
        """
        Add a new trip to the system with the provided data.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          asset_id: Specify the ID of the asset which is making this trip. The asset will be linked
              to this trip.

          cluster: the cluster of the region you want to use

          attributes: attributes can be used to store custom information about a trip in key:value
              format. Use attributes to add any useful information or context to your trips
              like the driver name, destination etc.

              Please note that the maximum number of key:value pairs that can be added to an
              attributes object is 100. Also, the overall size of attributes object should not
              exceed 65kb.

          custom_id: Set a unique ID for the new trip. If not provided, an ID will be automatically
              generated in UUID format. A valid custom_id can contain letters, numbers, “-”, &
              “\\__” only.

              Please note that the ID of a trip can not be changed once it is created.

          description: Add a custom description for the trip.

          meta_data: An JSON object to collect additional details about the trip. Use this property
              to add any custom information / context about the trip. The input will be passed
              on to the response as-is and can be used to display useful information on, for
              example, a UI app.

          name: Specify a name for the trip.

          stops: An array of objects to collect the details about all the stops that need to be
              made before the trip ends. Each object represents one stop.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/trip/start",
            body=await async_maybe_transform(
                {
                    "asset_id": asset_id,
                    "attributes": attributes,
                    "custom_id": custom_id,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "stops": stops,
                },
                trip_start_params.TripStartParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    trip_start_params.TripStartParams,
                ),
            ),
            cast_to=TripStartResponse,
        )


class TripResourceWithRawResponse:
    def __init__(self, trip: TripResource) -> None:
        self._trip = trip

        self.retrieve = to_raw_response_wrapper(
            trip.retrieve,
        )
        self.update = to_raw_response_wrapper(
            trip.update,
        )
        self.delete = to_raw_response_wrapper(
            trip.delete,
        )
        self.end = to_raw_response_wrapper(
            trip.end,
        )
        self.get_summary = to_raw_response_wrapper(
            trip.get_summary,
        )
        self.start = to_raw_response_wrapper(
            trip.start,
        )


class AsyncTripResourceWithRawResponse:
    def __init__(self, trip: AsyncTripResource) -> None:
        self._trip = trip

        self.retrieve = async_to_raw_response_wrapper(
            trip.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            trip.update,
        )
        self.delete = async_to_raw_response_wrapper(
            trip.delete,
        )
        self.end = async_to_raw_response_wrapper(
            trip.end,
        )
        self.get_summary = async_to_raw_response_wrapper(
            trip.get_summary,
        )
        self.start = async_to_raw_response_wrapper(
            trip.start,
        )


class TripResourceWithStreamingResponse:
    def __init__(self, trip: TripResource) -> None:
        self._trip = trip

        self.retrieve = to_streamed_response_wrapper(
            trip.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            trip.update,
        )
        self.delete = to_streamed_response_wrapper(
            trip.delete,
        )
        self.end = to_streamed_response_wrapper(
            trip.end,
        )
        self.get_summary = to_streamed_response_wrapper(
            trip.get_summary,
        )
        self.start = to_streamed_response_wrapper(
            trip.start,
        )


class AsyncTripResourceWithStreamingResponse:
    def __init__(self, trip: AsyncTripResource) -> None:
        self._trip = trip

        self.retrieve = async_to_streamed_response_wrapper(
            trip.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            trip.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            trip.delete,
        )
        self.end = async_to_streamed_response_wrapper(
            trip.end,
        )
        self.get_summary = async_to_streamed_response_wrapper(
            trip.get_summary,
        )
        self.start = async_to_streamed_response_wrapper(
            trip.start,
        )
