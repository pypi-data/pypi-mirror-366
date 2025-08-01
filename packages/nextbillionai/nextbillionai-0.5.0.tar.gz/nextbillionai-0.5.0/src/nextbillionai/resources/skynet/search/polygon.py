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
from ....types.skynet.search import polygon_get_params, polygon_create_params
from ....types.skynet.search_response import SearchResponse

__all__ = ["PolygonResource", "AsyncPolygonResource"]


class PolygonResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PolygonResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PolygonResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PolygonResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return PolygonResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        polygon: polygon_create_params.Polygon,
        filter: str | NotGiven = NOT_GIVEN,
        match_filter: polygon_create_params.MatchFilter | NotGiven = NOT_GIVEN,
        max_search_limit: bool | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort: polygon_create_params.Sort | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """
        Polygon Search

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          polygon:
              An object to collect geoJSON details of a custom polygon. Please ensure that:

              - the polygon provided is enclosed. This can be achieved by making the last
                location coordinate in the list equal to the first location coordinate of the
                list.

              - the 'polygon' provided does not contain multiple rings.

              The contents of this object follow the
              [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).

              Please note that the maximum area of the search polygon allowed is 3000
              km<sup>2</sup>.

          filter: **tags parameter will be deprecated soon! Please use the
              include_any_of_attributes or include_all_of_attributes parameters to match
              assets based on their labels or markers.**

              Use this parameter to filter the assets found inside the specified area by their
              tag. Multiple tag can be separated using comma (,).

              Please note the tags are case sensitive.

          match_filter: An object to define the attributes which will be used to filter the assets found
              within the polygon.

          max_search_limit: if ture, can get 16x bigger limitation in search.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results. Please note that ps has a
              default value of 20 and accepts integers only in the range of [1, 100].

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/search/polygon",
            body=maybe_transform(
                {
                    "polygon": polygon,
                    "filter": filter,
                    "match_filter": match_filter,
                    "max_search_limit": max_search_limit,
                    "pn": pn,
                    "ps": ps,
                    "sort": sort,
                },
                polygon_create_params.PolygonCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, polygon_create_params.PolygonCreateParams),
            ),
            cast_to=SearchResponse,
        )

    def get(
        self,
        *,
        key: str,
        polygon: str,
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
        Polygon Search

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          polygon: Define a custom polygon enclosing the area to be searched. It should be a pipe
              (|) delimited list of location coordinates.

              Please ensure that the polygon provided is enclosed. This can be achieved by
              making the last location coordinate in the list equal to the first location
              coordinate of the list.

              Please note that the maximum area of the search polygon allowed is 3000
              km<sup>2</sup>.

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
            "/skynet/search/polygon",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "polygon": polygon,
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
                    polygon_get_params.PolygonGetParams,
                ),
            ),
            cast_to=SearchResponse,
        )


class AsyncPolygonResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPolygonResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPolygonResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPolygonResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncPolygonResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        polygon: polygon_create_params.Polygon,
        filter: str | NotGiven = NOT_GIVEN,
        match_filter: polygon_create_params.MatchFilter | NotGiven = NOT_GIVEN,
        max_search_limit: bool | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort: polygon_create_params.Sort | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """
        Polygon Search

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          polygon:
              An object to collect geoJSON details of a custom polygon. Please ensure that:

              - the polygon provided is enclosed. This can be achieved by making the last
                location coordinate in the list equal to the first location coordinate of the
                list.

              - the 'polygon' provided does not contain multiple rings.

              The contents of this object follow the
              [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).

              Please note that the maximum area of the search polygon allowed is 3000
              km<sup>2</sup>.

          filter: **tags parameter will be deprecated soon! Please use the
              include_any_of_attributes or include_all_of_attributes parameters to match
              assets based on their labels or markers.**

              Use this parameter to filter the assets found inside the specified area by their
              tag. Multiple tag can be separated using comma (,).

              Please note the tags are case sensitive.

          match_filter: An object to define the attributes which will be used to filter the assets found
              within the polygon.

          max_search_limit: if ture, can get 16x bigger limitation in search.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results. Please note that ps has a
              default value of 20 and accepts integers only in the range of [1, 100].

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/search/polygon",
            body=await async_maybe_transform(
                {
                    "polygon": polygon,
                    "filter": filter,
                    "match_filter": match_filter,
                    "max_search_limit": max_search_limit,
                    "pn": pn,
                    "ps": ps,
                    "sort": sort,
                },
                polygon_create_params.PolygonCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, polygon_create_params.PolygonCreateParams),
            ),
            cast_to=SearchResponse,
        )

    async def get(
        self,
        *,
        key: str,
        polygon: str,
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
        Polygon Search

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          polygon: Define a custom polygon enclosing the area to be searched. It should be a pipe
              (|) delimited list of location coordinates.

              Please ensure that the polygon provided is enclosed. This can be achieved by
              making the last location coordinate in the list equal to the first location
              coordinate of the list.

              Please note that the maximum area of the search polygon allowed is 3000
              km<sup>2</sup>.

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
            "/skynet/search/polygon",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "polygon": polygon,
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
                    polygon_get_params.PolygonGetParams,
                ),
            ),
            cast_to=SearchResponse,
        )


class PolygonResourceWithRawResponse:
    def __init__(self, polygon: PolygonResource) -> None:
        self._polygon = polygon

        self.create = to_raw_response_wrapper(
            polygon.create,
        )
        self.get = to_raw_response_wrapper(
            polygon.get,
        )


class AsyncPolygonResourceWithRawResponse:
    def __init__(self, polygon: AsyncPolygonResource) -> None:
        self._polygon = polygon

        self.create = async_to_raw_response_wrapper(
            polygon.create,
        )
        self.get = async_to_raw_response_wrapper(
            polygon.get,
        )


class PolygonResourceWithStreamingResponse:
    def __init__(self, polygon: PolygonResource) -> None:
        self._polygon = polygon

        self.create = to_streamed_response_wrapper(
            polygon.create,
        )
        self.get = to_streamed_response_wrapper(
            polygon.get,
        )


class AsyncPolygonResourceWithStreamingResponse:
    def __init__(self, polygon: AsyncPolygonResource) -> None:
        self._polygon = polygon

        self.create = async_to_streamed_response_wrapper(
            polygon.create,
        )
        self.get = async_to_streamed_response_wrapper(
            polygon.get,
        )
