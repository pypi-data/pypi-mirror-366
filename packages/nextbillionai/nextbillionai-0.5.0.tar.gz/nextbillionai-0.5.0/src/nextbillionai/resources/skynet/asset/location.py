# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.skynet.asset import location_list_params, location_get_last_params
from ....types.skynet.asset.location_list_response import LocationListResponse
from ....types.skynet.asset.location_get_last_response import LocationGetLastResponse

__all__ = ["LocationResource", "AsyncLocationResource"]


class LocationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LocationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return LocationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LocationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return LocationResourceWithStreamingResponse(self)

    def list(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        correction: str | NotGiven = NOT_GIVEN,
        end_time: int | NotGiven = NOT_GIVEN,
        geometry_type: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LocationListResponse:
        """
        Track locations of an asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          correction: Describe the geometry characteristics through a , separated list of properties.

              Setting mapmatch to 1 returns the geometry of the tracked points, snapped to the
              nearest road.

              Setting interpolate to 1 smoothens the snapped geometry by adding more points,
              as needed. Please note, mapmatch should be set to 1 for interpolate to be
              effective.

              mode is used to set the transport mode for which the snapped route will be
              determined. Allowed values for mode are car and truck.

          end_time: Time until which the tracked locations of the asset need to be retrieved.

          geometry_type: Set the geometry format to encode the path linking the tracked locations of the
              asset.

              Please note that geometry_type is effective only when mapmatch property of
              correction parameter is set to 1.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          start_time: Time after which the tracked locations of the asset need to be retrieved.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/skynet/asset/{id}/location/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "correction": correction,
                        "end_time": end_time,
                        "geometry_type": geometry_type,
                        "pn": pn,
                        "ps": ps,
                        "start_time": start_time,
                    },
                    location_list_params.LocationListParams,
                ),
            ),
            cast_to=LocationListResponse,
        )

    def get_last(
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
    ) -> LocationGetLastResponse:
        """
        Track the last location of an asset

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
            f"/skynet/asset/{id}/location/last",
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
                    location_get_last_params.LocationGetLastParams,
                ),
            ),
            cast_to=LocationGetLastResponse,
        )


class AsyncLocationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLocationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLocationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLocationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncLocationResourceWithStreamingResponse(self)

    async def list(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        correction: str | NotGiven = NOT_GIVEN,
        end_time: int | NotGiven = NOT_GIVEN,
        geometry_type: Literal["polyline", "polyline6", "geojson"] | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LocationListResponse:
        """
        Track locations of an asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          correction: Describe the geometry characteristics through a , separated list of properties.

              Setting mapmatch to 1 returns the geometry of the tracked points, snapped to the
              nearest road.

              Setting interpolate to 1 smoothens the snapped geometry by adding more points,
              as needed. Please note, mapmatch should be set to 1 for interpolate to be
              effective.

              mode is used to set the transport mode for which the snapped route will be
              determined. Allowed values for mode are car and truck.

          end_time: Time until which the tracked locations of the asset need to be retrieved.

          geometry_type: Set the geometry format to encode the path linking the tracked locations of the
              asset.

              Please note that geometry_type is effective only when mapmatch property of
              correction parameter is set to 1.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          start_time: Time after which the tracked locations of the asset need to be retrieved.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/skynet/asset/{id}/location/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "correction": correction,
                        "end_time": end_time,
                        "geometry_type": geometry_type,
                        "pn": pn,
                        "ps": ps,
                        "start_time": start_time,
                    },
                    location_list_params.LocationListParams,
                ),
            ),
            cast_to=LocationListResponse,
        )

    async def get_last(
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
    ) -> LocationGetLastResponse:
        """
        Track the last location of an asset

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
            f"/skynet/asset/{id}/location/last",
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
                    location_get_last_params.LocationGetLastParams,
                ),
            ),
            cast_to=LocationGetLastResponse,
        )


class LocationResourceWithRawResponse:
    def __init__(self, location: LocationResource) -> None:
        self._location = location

        self.list = to_raw_response_wrapper(
            location.list,
        )
        self.get_last = to_raw_response_wrapper(
            location.get_last,
        )


class AsyncLocationResourceWithRawResponse:
    def __init__(self, location: AsyncLocationResource) -> None:
        self._location = location

        self.list = async_to_raw_response_wrapper(
            location.list,
        )
        self.get_last = async_to_raw_response_wrapper(
            location.get_last,
        )


class LocationResourceWithStreamingResponse:
    def __init__(self, location: LocationResource) -> None:
        self._location = location

        self.list = to_streamed_response_wrapper(
            location.list,
        )
        self.get_last = to_streamed_response_wrapper(
            location.get_last,
        )


class AsyncLocationResourceWithStreamingResponse:
    def __init__(self, location: AsyncLocationResource) -> None:
        self._location = location

        self.list = async_to_streamed_response_wrapper(
            location.list,
        )
        self.get_last = async_to_streamed_response_wrapper(
            location.get_last,
        )
