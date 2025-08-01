# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import geocode_retrieve_params, geocode_batch_create_params, geocode_structured_retrieve_params
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
from ..types.geocode_retrieve_response import GeocodeRetrieveResponse
from ..types.geocode_batch_create_response import GeocodeBatchCreateResponse
from ..types.geocode_structured_retrieve_response import GeocodeStructuredRetrieveResponse

__all__ = ["GeocodeResource", "AsyncGeocodeResource"]


class GeocodeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GeocodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return GeocodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GeocodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return GeocodeResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        key: str,
        q: str,
        at: str | NotGiven = NOT_GIVEN,
        in_: str | NotGiven = NOT_GIVEN,
        lang: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeRetrieveResponse:
        """
        Geocode

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          q: Specify the free-text search query.

              Please note that whitespace, urls, email addresses, or other out-of-scope
              queries will yield no results.

          at: Specify the center of the search context expressed as coordinates.

              Please note that one of "at", "in=circle" or "in=bbox" should be provided for
              relevant results.

          in_: Search within a geographic area. This is a hard filter. Results will be returned
              if they are located within the specified area.

              A geographic area can be

              - a country (or multiple countries), provided as comma-separated
                [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
                codes

                The country codes are to be provided in all uppercase.

                Format: countryCode:{countryCode}[,{countryCode}]

              - a circular area, provided as latitude, longitude, and radius (an integer with
                meters as unit)

                Format: circle:{latitude},{longitude};r={radius}

              - a bounding box, provided as _west longitude_, _south latitude_, _east
                longitude_, _north latitude_

                Format: bbox:{west longitude},{south latitude},{east longitude},{north
                latitude}

              Please provide one of 'at', 'in=circle' or 'in=bbox' input for a relevant
              result.

          lang: Select the language to be used for result rendering from a list of
              [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
              codes.

          limit: Sets the maximum number of results to be returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/geocode",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "q": q,
                        "at": at,
                        "in_": in_,
                        "lang": lang,
                        "limit": limit,
                    },
                    geocode_retrieve_params.GeocodeRetrieveParams,
                ),
            ),
            cast_to=GeocodeRetrieveResponse,
        )

    def batch_create(
        self,
        *,
        key: str,
        body: Iterable[geocode_batch_create_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeBatchCreateResponse:
        """
        Batch Geocode

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/geocode/batch",
            body=maybe_transform(body, Iterable[geocode_batch_create_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, geocode_batch_create_params.GeocodeBatchCreateParams),
            ),
            cast_to=GeocodeBatchCreateResponse,
        )

    def structured_retrieve(
        self,
        *,
        country_code: str,
        key: str,
        at: str | NotGiven = NOT_GIVEN,
        city: str | NotGiven = NOT_GIVEN,
        county: str | NotGiven = NOT_GIVEN,
        house_number: str | NotGiven = NOT_GIVEN,
        in_: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        postal_code: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        street: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeStructuredRetrieveResponse:
        """
        Structured Geocode

        Args:
          country_code: Specify a valid
              [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
              code in which the place being searched should be located. Please note that this
              is a case-sensitive field and the country code should be in all uppercase.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          at: Specify the center of the search context expressed as coordinates.

              Please note that one of "at", "in=circle" or "in=bbox" should be provided for
              relevant results.

          city: Specify the city in which the place being searched should be located.

          county: Specify the county division of the state in which the place being searched
              should be located.

          house_number: Specify the house number of the place being searched.

          in_: Search within a geographic area. This is a hard filter. Results will be returned
              if they are located within the specified area.

              A geographic area can be

              - a circular area, provided as latitude, longitude, and radius (an integer with
                meters as unit)

                Format: circle:{latitude},{longitude};r={radius}

              - a bounding box, provided as _west longitude_, _south latitude_, _east
                longitude_, _north latitude_

                Format: bbox:{west longitude},{south latitude},{east longitude},{north
                latitude}

              Please provide one of 'at', 'in=circle' or 'in=bbox' input for a relevant
              result.

          limit: Sets the maximum number of results to be returned.

          postal_code: Specify the postal code in which the place being searched should be located.

          state: Specify the state division of the country in which the place being searched
              should be located.

          street: Specify the name of the street in which the place being searched should be
              located.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/geocode/structured",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "country_code": country_code,
                        "key": key,
                        "at": at,
                        "city": city,
                        "county": county,
                        "house_number": house_number,
                        "in_": in_,
                        "limit": limit,
                        "postal_code": postal_code,
                        "state": state,
                        "street": street,
                    },
                    geocode_structured_retrieve_params.GeocodeStructuredRetrieveParams,
                ),
            ),
            cast_to=GeocodeStructuredRetrieveResponse,
        )


class AsyncGeocodeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGeocodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGeocodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGeocodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncGeocodeResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        key: str,
        q: str,
        at: str | NotGiven = NOT_GIVEN,
        in_: str | NotGiven = NOT_GIVEN,
        lang: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeRetrieveResponse:
        """
        Geocode

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          q: Specify the free-text search query.

              Please note that whitespace, urls, email addresses, or other out-of-scope
              queries will yield no results.

          at: Specify the center of the search context expressed as coordinates.

              Please note that one of "at", "in=circle" or "in=bbox" should be provided for
              relevant results.

          in_: Search within a geographic area. This is a hard filter. Results will be returned
              if they are located within the specified area.

              A geographic area can be

              - a country (or multiple countries), provided as comma-separated
                [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
                codes

                The country codes are to be provided in all uppercase.

                Format: countryCode:{countryCode}[,{countryCode}]

              - a circular area, provided as latitude, longitude, and radius (an integer with
                meters as unit)

                Format: circle:{latitude},{longitude};r={radius}

              - a bounding box, provided as _west longitude_, _south latitude_, _east
                longitude_, _north latitude_

                Format: bbox:{west longitude},{south latitude},{east longitude},{north
                latitude}

              Please provide one of 'at', 'in=circle' or 'in=bbox' input for a relevant
              result.

          lang: Select the language to be used for result rendering from a list of
              [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
              codes.

          limit: Sets the maximum number of results to be returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/geocode",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "q": q,
                        "at": at,
                        "in_": in_,
                        "lang": lang,
                        "limit": limit,
                    },
                    geocode_retrieve_params.GeocodeRetrieveParams,
                ),
            ),
            cast_to=GeocodeRetrieveResponse,
        )

    async def batch_create(
        self,
        *,
        key: str,
        body: Iterable[geocode_batch_create_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeBatchCreateResponse:
        """
        Batch Geocode

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/geocode/batch",
            body=await async_maybe_transform(body, Iterable[geocode_batch_create_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, geocode_batch_create_params.GeocodeBatchCreateParams),
            ),
            cast_to=GeocodeBatchCreateResponse,
        )

    async def structured_retrieve(
        self,
        *,
        country_code: str,
        key: str,
        at: str | NotGiven = NOT_GIVEN,
        city: str | NotGiven = NOT_GIVEN,
        county: str | NotGiven = NOT_GIVEN,
        house_number: str | NotGiven = NOT_GIVEN,
        in_: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        postal_code: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        street: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeStructuredRetrieveResponse:
        """
        Structured Geocode

        Args:
          country_code: Specify a valid
              [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
              code in which the place being searched should be located. Please note that this
              is a case-sensitive field and the country code should be in all uppercase.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          at: Specify the center of the search context expressed as coordinates.

              Please note that one of "at", "in=circle" or "in=bbox" should be provided for
              relevant results.

          city: Specify the city in which the place being searched should be located.

          county: Specify the county division of the state in which the place being searched
              should be located.

          house_number: Specify the house number of the place being searched.

          in_: Search within a geographic area. This is a hard filter. Results will be returned
              if they are located within the specified area.

              A geographic area can be

              - a circular area, provided as latitude, longitude, and radius (an integer with
                meters as unit)

                Format: circle:{latitude},{longitude};r={radius}

              - a bounding box, provided as _west longitude_, _south latitude_, _east
                longitude_, _north latitude_

                Format: bbox:{west longitude},{south latitude},{east longitude},{north
                latitude}

              Please provide one of 'at', 'in=circle' or 'in=bbox' input for a relevant
              result.

          limit: Sets the maximum number of results to be returned.

          postal_code: Specify the postal code in which the place being searched should be located.

          state: Specify the state division of the country in which the place being searched
              should be located.

          street: Specify the name of the street in which the place being searched should be
              located.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/geocode/structured",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "country_code": country_code,
                        "key": key,
                        "at": at,
                        "city": city,
                        "county": county,
                        "house_number": house_number,
                        "in_": in_,
                        "limit": limit,
                        "postal_code": postal_code,
                        "state": state,
                        "street": street,
                    },
                    geocode_structured_retrieve_params.GeocodeStructuredRetrieveParams,
                ),
            ),
            cast_to=GeocodeStructuredRetrieveResponse,
        )


class GeocodeResourceWithRawResponse:
    def __init__(self, geocode: GeocodeResource) -> None:
        self._geocode = geocode

        self.retrieve = to_raw_response_wrapper(
            geocode.retrieve,
        )
        self.batch_create = to_raw_response_wrapper(
            geocode.batch_create,
        )
        self.structured_retrieve = to_raw_response_wrapper(
            geocode.structured_retrieve,
        )


class AsyncGeocodeResourceWithRawResponse:
    def __init__(self, geocode: AsyncGeocodeResource) -> None:
        self._geocode = geocode

        self.retrieve = async_to_raw_response_wrapper(
            geocode.retrieve,
        )
        self.batch_create = async_to_raw_response_wrapper(
            geocode.batch_create,
        )
        self.structured_retrieve = async_to_raw_response_wrapper(
            geocode.structured_retrieve,
        )


class GeocodeResourceWithStreamingResponse:
    def __init__(self, geocode: GeocodeResource) -> None:
        self._geocode = geocode

        self.retrieve = to_streamed_response_wrapper(
            geocode.retrieve,
        )
        self.batch_create = to_streamed_response_wrapper(
            geocode.batch_create,
        )
        self.structured_retrieve = to_streamed_response_wrapper(
            geocode.structured_retrieve,
        )


class AsyncGeocodeResourceWithStreamingResponse:
    def __init__(self, geocode: AsyncGeocodeResource) -> None:
        self._geocode = geocode

        self.retrieve = async_to_streamed_response_wrapper(
            geocode.retrieve,
        )
        self.batch_create = async_to_streamed_response_wrapper(
            geocode.batch_create,
        )
        self.structured_retrieve = async_to_streamed_response_wrapper(
            geocode.structured_retrieve,
        )
