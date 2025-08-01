# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import autocomplete_suggest_params
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
from ..types.autocomplete_suggest_response import AutocompleteSuggestResponse

__all__ = ["AutocompleteResource", "AsyncAutocompleteResource"]


class AutocompleteResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AutocompleteResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AutocompleteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AutocompleteResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AutocompleteResourceWithStreamingResponse(self)

    def suggest(
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
    ) -> AutocompleteSuggestResponse:
        """
        Autocomplete

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
            "/autocomplete",
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
                    autocomplete_suggest_params.AutocompleteSuggestParams,
                ),
            ),
            cast_to=AutocompleteSuggestResponse,
        )


class AsyncAutocompleteResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAutocompleteResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAutocompleteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAutocompleteResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncAutocompleteResourceWithStreamingResponse(self)

    async def suggest(
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
    ) -> AutocompleteSuggestResponse:
        """
        Autocomplete

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
            "/autocomplete",
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
                    autocomplete_suggest_params.AutocompleteSuggestParams,
                ),
            ),
            cast_to=AutocompleteSuggestResponse,
        )


class AutocompleteResourceWithRawResponse:
    def __init__(self, autocomplete: AutocompleteResource) -> None:
        self._autocomplete = autocomplete

        self.suggest = to_raw_response_wrapper(
            autocomplete.suggest,
        )


class AsyncAutocompleteResourceWithRawResponse:
    def __init__(self, autocomplete: AsyncAutocompleteResource) -> None:
        self._autocomplete = autocomplete

        self.suggest = async_to_raw_response_wrapper(
            autocomplete.suggest,
        )


class AutocompleteResourceWithStreamingResponse:
    def __init__(self, autocomplete: AutocompleteResource) -> None:
        self._autocomplete = autocomplete

        self.suggest = to_streamed_response_wrapper(
            autocomplete.suggest,
        )


class AsyncAutocompleteResourceWithStreamingResponse:
    def __init__(self, autocomplete: AsyncAutocompleteResource) -> None:
        self._autocomplete = autocomplete

        self.suggest = async_to_streamed_response_wrapper(
            autocomplete.suggest,
        )
