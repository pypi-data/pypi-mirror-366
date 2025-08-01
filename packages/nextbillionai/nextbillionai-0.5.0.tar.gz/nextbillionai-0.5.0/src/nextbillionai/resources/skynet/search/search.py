# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .polygon import (
    PolygonResource,
    AsyncPolygonResource,
    PolygonResourceWithRawResponse,
    AsyncPolygonResourceWithRawResponse,
    PolygonResourceWithStreamingResponse,
    AsyncPolygonResourceWithStreamingResponse,
)
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
from ....types.skynet import search_bound_params, search_around_params
from ....types.skynet.search_response import SearchResponse

__all__ = ["SearchResource", "AsyncSearchResource"]


class SearchResource(SyncAPIResource):
    @cached_property
    def polygon(self) -> PolygonResource:
        return PolygonResource(self._client)

    @cached_property
    def with_raw_response(self) -> SearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return SearchResourceWithStreamingResponse(self)

    def around(
        self,
        *,
        center: str,
        key: str,
        radius: float,
        filter: str | NotGiven = NOT_GIVEN,
        include_all_of_attributes: str | NotGiven = NOT_GIVEN,
        include_any_of_attributes: str | NotGiven = NOT_GIVEN,
        max_search_limit: bool | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["distance", "duration", "straight_distance"] | NotGiven = NOT_GIVEN,
        sort_destination: str | NotGiven = NOT_GIVEN,
        sort_driving_mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """
        Around Search

        Args:
          center: Location coordinates of the point which would act as the center of the circular
              area to be searched.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          radius: Radius, in meters, of the circular area to be searched.

          filter: **tags parameter will be deprecated soon! Please use the
              include_any_of_attributes or include_all_of_attributes parameters to match
              assets based on their labels or markers.**

              Use this parameter to filter the assets found inside the specified area by their
              tags. Multiple tags can be separated using commas (,).

              Please note the tags are case sensitive.

          include_all_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Only the assets having all the attributes that are added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_any_of_attributes parameter.

          include_any_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Assets having at least one of the attributes added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_all_of_attributes parameter.

          max_search_limit: When true, the maximum limit is 20Km for around search API and 48000 Km2 for
              other search methods.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          sort_by: Specify the metric to sort the assets returned in the search result. The valid
              values are:

              - **distance** : Sorts the assets by driving distance to the given
                sort_destination .
              - **duration** : Sorts the assets by travel time to the given sort_destination .
              - **straight_distance** : Sort the assets by straight-line distance to the given
                sort-destination .

          sort_destination: Specifies the location coordinates of the point which acts as destination for
              sorting the assets in the search results. The service will sort each asset based
              on the driving distance or travel time to this destination, from its current
              location. Use the sort_by parameter to configure the metric that should be used
              for sorting the assets. Please note that sort_destination is required when
              sort_by is provided.

          sort_driving_mode: Specifies the driving mode to be used for determining travel duration or driving
              distance for sorting the assets in search result.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/skynet/search/around",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "center": center,
                        "key": key,
                        "radius": radius,
                        "filter": filter,
                        "include_all_of_attributes": include_all_of_attributes,
                        "include_any_of_attributes": include_any_of_attributes,
                        "max_search_limit": max_search_limit,
                        "pn": pn,
                        "ps": ps,
                        "sort_by": sort_by,
                        "sort_destination": sort_destination,
                        "sort_driving_mode": sort_driving_mode,
                    },
                    search_around_params.SearchAroundParams,
                ),
            ),
            cast_to=SearchResponse,
        )

    def bound(
        self,
        *,
        bound: str,
        key: str,
        filter: str | NotGiven = NOT_GIVEN,
        include_all_of_attributes: str | NotGiven = NOT_GIVEN,
        include_any_of_attributes: str | NotGiven = NOT_GIVEN,
        max_search_limit: bool | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["distance", "duration", "straight_distance"] | NotGiven = NOT_GIVEN,
        sort_destination: str | NotGiven = NOT_GIVEN,
        sort_driving_mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """
        Bound Search

        Args:
          bound: Specify two, pipe (|) delimited location coordinates which would act as corners
              of the bounding box area to be searched. The first one should be the southwest
              coordinate of the bounds and the second one should be the northeast coordinate
              of the bounds.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          filter: **tags parameter will be deprecated soon! Please use the
              include_any_of_attributes or include_all_of_attributes parameters to match
              assets based on their labels or markers.**

              Use this parameter to filter the assets found inside the specified area by their
              tags. Multiple tags can be separated using commas (,).

              Please note the tags are case sensitive.

          include_all_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Only the assets having all the attributes that are added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_any_of_attributes parameter.

          include_any_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Assets having at least one of the attributes added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_all_of_attributes parameter.

          max_search_limit: When true, the maximum limit is 20Km for around search API and 48000 Km2 for
              other search methods.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          sort_by: Specify the metric to sort the assets returned in the search result. The valid
              values are:

              - **distance** : Sorts the assets by driving distance to the given
                sort_destination .
              - **duration** : Sorts the assets by travel time to the given sort_destination .
              - **straight_distance** : Sort the assets by straight-line distance to the given
                sort-destination .

          sort_destination: Specifies the location coordinates of the point which acts as destination for
              sorting the assets in the search results. The service will sort each asset based
              on the driving distance or travel time to this destination, from its current
              location. Use the sort_by parameter to configure the metric that should be used
              for sorting the assets. Please note that sort_destination is required when
              sort_by is provided.

          sort_driving_mode: Specifies the driving mode to be used for determining travel duration or driving
              distance for sorting the assets in search result.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/skynet/search/bound",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "bound": bound,
                        "key": key,
                        "filter": filter,
                        "include_all_of_attributes": include_all_of_attributes,
                        "include_any_of_attributes": include_any_of_attributes,
                        "max_search_limit": max_search_limit,
                        "pn": pn,
                        "ps": ps,
                        "sort_by": sort_by,
                        "sort_destination": sort_destination,
                        "sort_driving_mode": sort_driving_mode,
                    },
                    search_bound_params.SearchBoundParams,
                ),
            ),
            cast_to=SearchResponse,
        )


class AsyncSearchResource(AsyncAPIResource):
    @cached_property
    def polygon(self) -> AsyncPolygonResource:
        return AsyncPolygonResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncSearchResourceWithStreamingResponse(self)

    async def around(
        self,
        *,
        center: str,
        key: str,
        radius: float,
        filter: str | NotGiven = NOT_GIVEN,
        include_all_of_attributes: str | NotGiven = NOT_GIVEN,
        include_any_of_attributes: str | NotGiven = NOT_GIVEN,
        max_search_limit: bool | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["distance", "duration", "straight_distance"] | NotGiven = NOT_GIVEN,
        sort_destination: str | NotGiven = NOT_GIVEN,
        sort_driving_mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """
        Around Search

        Args:
          center: Location coordinates of the point which would act as the center of the circular
              area to be searched.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          radius: Radius, in meters, of the circular area to be searched.

          filter: **tags parameter will be deprecated soon! Please use the
              include_any_of_attributes or include_all_of_attributes parameters to match
              assets based on their labels or markers.**

              Use this parameter to filter the assets found inside the specified area by their
              tags. Multiple tags can be separated using commas (,).

              Please note the tags are case sensitive.

          include_all_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Only the assets having all the attributes that are added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_any_of_attributes parameter.

          include_any_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Assets having at least one of the attributes added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_all_of_attributes parameter.

          max_search_limit: When true, the maximum limit is 20Km for around search API and 48000 Km2 for
              other search methods.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          sort_by: Specify the metric to sort the assets returned in the search result. The valid
              values are:

              - **distance** : Sorts the assets by driving distance to the given
                sort_destination .
              - **duration** : Sorts the assets by travel time to the given sort_destination .
              - **straight_distance** : Sort the assets by straight-line distance to the given
                sort-destination .

          sort_destination: Specifies the location coordinates of the point which acts as destination for
              sorting the assets in the search results. The service will sort each asset based
              on the driving distance or travel time to this destination, from its current
              location. Use the sort_by parameter to configure the metric that should be used
              for sorting the assets. Please note that sort_destination is required when
              sort_by is provided.

          sort_driving_mode: Specifies the driving mode to be used for determining travel duration or driving
              distance for sorting the assets in search result.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/skynet/search/around",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "center": center,
                        "key": key,
                        "radius": radius,
                        "filter": filter,
                        "include_all_of_attributes": include_all_of_attributes,
                        "include_any_of_attributes": include_any_of_attributes,
                        "max_search_limit": max_search_limit,
                        "pn": pn,
                        "ps": ps,
                        "sort_by": sort_by,
                        "sort_destination": sort_destination,
                        "sort_driving_mode": sort_driving_mode,
                    },
                    search_around_params.SearchAroundParams,
                ),
            ),
            cast_to=SearchResponse,
        )

    async def bound(
        self,
        *,
        bound: str,
        key: str,
        filter: str | NotGiven = NOT_GIVEN,
        include_all_of_attributes: str | NotGiven = NOT_GIVEN,
        include_any_of_attributes: str | NotGiven = NOT_GIVEN,
        max_search_limit: bool | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["distance", "duration", "straight_distance"] | NotGiven = NOT_GIVEN,
        sort_destination: str | NotGiven = NOT_GIVEN,
        sort_driving_mode: Literal["car", "truck"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """
        Bound Search

        Args:
          bound: Specify two, pipe (|) delimited location coordinates which would act as corners
              of the bounding box area to be searched. The first one should be the southwest
              coordinate of the bounds and the second one should be the northeast coordinate
              of the bounds.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          filter: **tags parameter will be deprecated soon! Please use the
              include_any_of_attributes or include_all_of_attributes parameters to match
              assets based on their labels or markers.**

              Use this parameter to filter the assets found inside the specified area by their
              tags. Multiple tags can be separated using commas (,).

              Please note the tags are case sensitive.

          include_all_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Only the assets having all the attributes that are added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_any_of_attributes parameter.

          include_any_of_attributes: Use this parameter to filter the assets found inside the specified area by their
              attributes. Assets having at least one of the attributes added to this
              parameter, will be returned in the search results. Multiple attributes can be
              separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_all_of_attributes parameter.

          max_search_limit: When true, the maximum limit is 20Km for around search API and 48000 Km2 for
              other search methods.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          sort_by: Specify the metric to sort the assets returned in the search result. The valid
              values are:

              - **distance** : Sorts the assets by driving distance to the given
                sort_destination .
              - **duration** : Sorts the assets by travel time to the given sort_destination .
              - **straight_distance** : Sort the assets by straight-line distance to the given
                sort-destination .

          sort_destination: Specifies the location coordinates of the point which acts as destination for
              sorting the assets in the search results. The service will sort each asset based
              on the driving distance or travel time to this destination, from its current
              location. Use the sort_by parameter to configure the metric that should be used
              for sorting the assets. Please note that sort_destination is required when
              sort_by is provided.

          sort_driving_mode: Specifies the driving mode to be used for determining travel duration or driving
              distance for sorting the assets in search result.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/skynet/search/bound",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "bound": bound,
                        "key": key,
                        "filter": filter,
                        "include_all_of_attributes": include_all_of_attributes,
                        "include_any_of_attributes": include_any_of_attributes,
                        "max_search_limit": max_search_limit,
                        "pn": pn,
                        "ps": ps,
                        "sort_by": sort_by,
                        "sort_destination": sort_destination,
                        "sort_driving_mode": sort_driving_mode,
                    },
                    search_bound_params.SearchBoundParams,
                ),
            ),
            cast_to=SearchResponse,
        )


class SearchResourceWithRawResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.around = to_raw_response_wrapper(
            search.around,
        )
        self.bound = to_raw_response_wrapper(
            search.bound,
        )

    @cached_property
    def polygon(self) -> PolygonResourceWithRawResponse:
        return PolygonResourceWithRawResponse(self._search.polygon)


class AsyncSearchResourceWithRawResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.around = async_to_raw_response_wrapper(
            search.around,
        )
        self.bound = async_to_raw_response_wrapper(
            search.bound,
        )

    @cached_property
    def polygon(self) -> AsyncPolygonResourceWithRawResponse:
        return AsyncPolygonResourceWithRawResponse(self._search.polygon)


class SearchResourceWithStreamingResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.around = to_streamed_response_wrapper(
            search.around,
        )
        self.bound = to_streamed_response_wrapper(
            search.bound,
        )

    @cached_property
    def polygon(self) -> PolygonResourceWithStreamingResponse:
        return PolygonResourceWithStreamingResponse(self._search.polygon)


class AsyncSearchResourceWithStreamingResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.around = async_to_streamed_response_wrapper(
            search.around,
        )
        self.bound = async_to_streamed_response_wrapper(
            search.bound,
        )

    @cached_property
    def polygon(self) -> AsyncPolygonResourceWithStreamingResponse:
        return AsyncPolygonResourceWithStreamingResponse(self._search.polygon)
