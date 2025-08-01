# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import revgeocode_retrieve_params
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
from ..types.revgeocode_retrieve_response import RevgeocodeRetrieveResponse

__all__ = ["RevgeocodeResource", "AsyncRevgeocodeResource"]


class RevgeocodeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RevgeocodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RevgeocodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RevgeocodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return RevgeocodeResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        at: str,
        key: str,
        in_: str | NotGiven = NOT_GIVEN,
        lang: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RevgeocodeRetrieveResponse:
        """
        Reverse Geocode

        Args:
          at: Specify the center of the search context expressed as coordinates.

              Please note that one of "at", "in=circle" or "in=bbox" should be provided for
              relevant results.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

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

          lang: Select the language to be used for result rendering from a list of
              [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
              codes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/revgeocode",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "at": at,
                        "key": key,
                        "in_": in_,
                        "lang": lang,
                    },
                    revgeocode_retrieve_params.RevgeocodeRetrieveParams,
                ),
            ),
            cast_to=RevgeocodeRetrieveResponse,
        )


class AsyncRevgeocodeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRevgeocodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRevgeocodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRevgeocodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncRevgeocodeResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        at: str,
        key: str,
        in_: str | NotGiven = NOT_GIVEN,
        lang: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RevgeocodeRetrieveResponse:
        """
        Reverse Geocode

        Args:
          at: Specify the center of the search context expressed as coordinates.

              Please note that one of "at", "in=circle" or "in=bbox" should be provided for
              relevant results.

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

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

          lang: Select the language to be used for result rendering from a list of
              [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
              codes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/revgeocode",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "at": at,
                        "key": key,
                        "in_": in_,
                        "lang": lang,
                    },
                    revgeocode_retrieve_params.RevgeocodeRetrieveParams,
                ),
            ),
            cast_to=RevgeocodeRetrieveResponse,
        )


class RevgeocodeResourceWithRawResponse:
    def __init__(self, revgeocode: RevgeocodeResource) -> None:
        self._revgeocode = revgeocode

        self.retrieve = to_raw_response_wrapper(
            revgeocode.retrieve,
        )


class AsyncRevgeocodeResourceWithRawResponse:
    def __init__(self, revgeocode: AsyncRevgeocodeResource) -> None:
        self._revgeocode = revgeocode

        self.retrieve = async_to_raw_response_wrapper(
            revgeocode.retrieve,
        )


class RevgeocodeResourceWithStreamingResponse:
    def __init__(self, revgeocode: RevgeocodeResource) -> None:
        self._revgeocode = revgeocode

        self.retrieve = to_streamed_response_wrapper(
            revgeocode.retrieve,
        )


class AsyncRevgeocodeResourceWithStreamingResponse:
    def __init__(self, revgeocode: AsyncRevgeocodeResource) -> None:
        self._revgeocode = revgeocode

        self.retrieve = async_to_streamed_response_wrapper(
            revgeocode.retrieve,
        )
