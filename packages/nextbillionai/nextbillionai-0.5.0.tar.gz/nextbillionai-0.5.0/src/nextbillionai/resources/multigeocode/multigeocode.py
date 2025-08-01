# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .place import (
    PlaceResource,
    AsyncPlaceResource,
    PlaceResourceWithRawResponse,
    AsyncPlaceResourceWithRawResponse,
    PlaceResourceWithStreamingResponse,
    AsyncPlaceResourceWithStreamingResponse,
)
from ...types import multigeocode_search_params
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
from ...types.multigeocode_search_response import MultigeocodeSearchResponse

__all__ = ["MultigeocodeResource", "AsyncMultigeocodeResource"]


class MultigeocodeResource(SyncAPIResource):
    @cached_property
    def place(self) -> PlaceResource:
        return PlaceResource(self._client)

    @cached_property
    def with_raw_response(self) -> MultigeocodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return MultigeocodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MultigeocodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return MultigeocodeResourceWithStreamingResponse(self)

    def search(
        self,
        *,
        key: str,
        at: multigeocode_search_params.At,
        query: str,
        city: str | NotGiven = NOT_GIVEN,
        country: str | NotGiven = NOT_GIVEN,
        district: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        radius: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        street: str | NotGiven = NOT_GIVEN,
        sub_district: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MultigeocodeSearchResponse:
        """
        The method enables searching for known places from multiple data sources

        Use this method to find known places in default or your own custom (proprietary)
        dataset and get a combined search result. It accepts free-form, partially
        correct or even incomplete search texts. Results would be ranked based on the
        search score of a place.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          at: Specify the center of the search context expressed as coordinates.

          query: A free-form, complete or incomplete string to be searched. It allows searching
              for places using keywords or names.

          city: Specifies the primary city of the place.

          country: Country of the search context provided as comma-separated
              [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
              codes.
              Note: Country codes should be provided in uppercase.

          district: Specifies the district of the search place.

          limit: Sets the maximum number of results to be returned.

          radius: Filters the results to places within the specified radius from the 'at'
              location.

              Note: Supports 'meter' (m) and 'kilometer' (km) units. If no radius is given,
              the search method returns as many results as specified in limit.

          state: Specifies the state of the search place.

          street: Specifies the street name of the search place.

          sub_district: Specifies the subDistrict of the search place.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/multigeocode/search",
            body=maybe_transform(
                {
                    "at": at,
                    "query": query,
                    "city": city,
                    "country": country,
                    "district": district,
                    "limit": limit,
                    "radius": radius,
                    "state": state,
                    "street": street,
                    "sub_district": sub_district,
                },
                multigeocode_search_params.MultigeocodeSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, multigeocode_search_params.MultigeocodeSearchParams),
            ),
            cast_to=MultigeocodeSearchResponse,
        )


class AsyncMultigeocodeResource(AsyncAPIResource):
    @cached_property
    def place(self) -> AsyncPlaceResource:
        return AsyncPlaceResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMultigeocodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMultigeocodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMultigeocodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncMultigeocodeResourceWithStreamingResponse(self)

    async def search(
        self,
        *,
        key: str,
        at: multigeocode_search_params.At,
        query: str,
        city: str | NotGiven = NOT_GIVEN,
        country: str | NotGiven = NOT_GIVEN,
        district: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        radius: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        street: str | NotGiven = NOT_GIVEN,
        sub_district: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MultigeocodeSearchResponse:
        """
        The method enables searching for known places from multiple data sources

        Use this method to find known places in default or your own custom (proprietary)
        dataset and get a combined search result. It accepts free-form, partially
        correct or even incomplete search texts. Results would be ranked based on the
        search score of a place.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          at: Specify the center of the search context expressed as coordinates.

          query: A free-form, complete or incomplete string to be searched. It allows searching
              for places using keywords or names.

          city: Specifies the primary city of the place.

          country: Country of the search context provided as comma-separated
              [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
              codes.
              Note: Country codes should be provided in uppercase.

          district: Specifies the district of the search place.

          limit: Sets the maximum number of results to be returned.

          radius: Filters the results to places within the specified radius from the 'at'
              location.

              Note: Supports 'meter' (m) and 'kilometer' (km) units. If no radius is given,
              the search method returns as many results as specified in limit.

          state: Specifies the state of the search place.

          street: Specifies the street name of the search place.

          sub_district: Specifies the subDistrict of the search place.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/multigeocode/search",
            body=await async_maybe_transform(
                {
                    "at": at,
                    "query": query,
                    "city": city,
                    "country": country,
                    "district": district,
                    "limit": limit,
                    "radius": radius,
                    "state": state,
                    "street": street,
                    "sub_district": sub_district,
                },
                multigeocode_search_params.MultigeocodeSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, multigeocode_search_params.MultigeocodeSearchParams),
            ),
            cast_to=MultigeocodeSearchResponse,
        )


class MultigeocodeResourceWithRawResponse:
    def __init__(self, multigeocode: MultigeocodeResource) -> None:
        self._multigeocode = multigeocode

        self.search = to_raw_response_wrapper(
            multigeocode.search,
        )

    @cached_property
    def place(self) -> PlaceResourceWithRawResponse:
        return PlaceResourceWithRawResponse(self._multigeocode.place)


class AsyncMultigeocodeResourceWithRawResponse:
    def __init__(self, multigeocode: AsyncMultigeocodeResource) -> None:
        self._multigeocode = multigeocode

        self.search = async_to_raw_response_wrapper(
            multigeocode.search,
        )

    @cached_property
    def place(self) -> AsyncPlaceResourceWithRawResponse:
        return AsyncPlaceResourceWithRawResponse(self._multigeocode.place)


class MultigeocodeResourceWithStreamingResponse:
    def __init__(self, multigeocode: MultigeocodeResource) -> None:
        self._multigeocode = multigeocode

        self.search = to_streamed_response_wrapper(
            multigeocode.search,
        )

    @cached_property
    def place(self) -> PlaceResourceWithStreamingResponse:
        return PlaceResourceWithStreamingResponse(self._multigeocode.place)


class AsyncMultigeocodeResourceWithStreamingResponse:
    def __init__(self, multigeocode: AsyncMultigeocodeResource) -> None:
        self._multigeocode = multigeocode

        self.search = async_to_streamed_response_wrapper(
            multigeocode.search,
        )

    @cached_property
    def place(self) -> AsyncPlaceResourceWithStreamingResponse:
        return AsyncPlaceResourceWithStreamingResponse(self._multigeocode.place)
