# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import postalcode_retrieve_coordinates_params
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
from ..types.postalcode_retrieve_coordinates_response import PostalcodeRetrieveCoordinatesResponse

__all__ = ["PostalcodeResource", "AsyncPostalcodeResource"]


class PostalcodeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PostalcodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PostalcodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PostalcodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return PostalcodeResourceWithStreamingResponse(self)

    def retrieve_coordinates(
        self,
        *,
        key: str,
        at: postalcode_retrieve_coordinates_params.At | NotGiven = NOT_GIVEN,
        country: str | NotGiven = NOT_GIVEN,
        format: Literal["geojson"] | NotGiven = NOT_GIVEN,
        postalcode: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PostalcodeRetrieveCoordinatesResponse:
        """
        Retrieve coordinates by postal code

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          at: Location coordinates that you want to get the postal code of. If not providing
              postalcode in the request, at becomes mandatory. Please note that only 1 point
              can be requested. [See this example](#note).

          country: Country containing the postal code or the location. It is mandatory if
              postalcode is provided in the request. [See this example](#note).

              Please check the [API Query Limits](#api-query-limits) section below for a list
              of the countries covered by the Geocode Postcode API. Users can provide either
              the name or the alpha-2/3 code as per the
              [ISO 3166-1 standard](https://en.wikipedia.org/wiki/ISO_3166-1) of a country
              covered by the API as input for this parameter.

          format: Specify the format in which the boundary details of the post code will be
              returned. When specified, the boundary details will be returned in the geojson
              format. When not specified, the boundary details are returned in general format.

          postalcode: Provide the postal code for which the information is needed. At least one of
              (postalcode + country) or at needs to be provided. Please note that only 1
              postal code can be requested. [See this example](#note).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/postalcode",
            body=maybe_transform(
                {
                    "at": at,
                    "country": country,
                    "format": format,
                    "postalcode": postalcode,
                },
                postalcode_retrieve_coordinates_params.PostalcodeRetrieveCoordinatesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"key": key}, postalcode_retrieve_coordinates_params.PostalcodeRetrieveCoordinatesParams
                ),
            ),
            cast_to=PostalcodeRetrieveCoordinatesResponse,
        )


class AsyncPostalcodeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPostalcodeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPostalcodeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPostalcodeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncPostalcodeResourceWithStreamingResponse(self)

    async def retrieve_coordinates(
        self,
        *,
        key: str,
        at: postalcode_retrieve_coordinates_params.At | NotGiven = NOT_GIVEN,
        country: str | NotGiven = NOT_GIVEN,
        format: Literal["geojson"] | NotGiven = NOT_GIVEN,
        postalcode: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PostalcodeRetrieveCoordinatesResponse:
        """
        Retrieve coordinates by postal code

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          at: Location coordinates that you want to get the postal code of. If not providing
              postalcode in the request, at becomes mandatory. Please note that only 1 point
              can be requested. [See this example](#note).

          country: Country containing the postal code or the location. It is mandatory if
              postalcode is provided in the request. [See this example](#note).

              Please check the [API Query Limits](#api-query-limits) section below for a list
              of the countries covered by the Geocode Postcode API. Users can provide either
              the name or the alpha-2/3 code as per the
              [ISO 3166-1 standard](https://en.wikipedia.org/wiki/ISO_3166-1) of a country
              covered by the API as input for this parameter.

          format: Specify the format in which the boundary details of the post code will be
              returned. When specified, the boundary details will be returned in the geojson
              format. When not specified, the boundary details are returned in general format.

          postalcode: Provide the postal code for which the information is needed. At least one of
              (postalcode + country) or at needs to be provided. Please note that only 1
              postal code can be requested. [See this example](#note).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/postalcode",
            body=await async_maybe_transform(
                {
                    "at": at,
                    "country": country,
                    "format": format,
                    "postalcode": postalcode,
                },
                postalcode_retrieve_coordinates_params.PostalcodeRetrieveCoordinatesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, postalcode_retrieve_coordinates_params.PostalcodeRetrieveCoordinatesParams
                ),
            ),
            cast_to=PostalcodeRetrieveCoordinatesResponse,
        )


class PostalcodeResourceWithRawResponse:
    def __init__(self, postalcode: PostalcodeResource) -> None:
        self._postalcode = postalcode

        self.retrieve_coordinates = to_raw_response_wrapper(
            postalcode.retrieve_coordinates,
        )


class AsyncPostalcodeResourceWithRawResponse:
    def __init__(self, postalcode: AsyncPostalcodeResource) -> None:
        self._postalcode = postalcode

        self.retrieve_coordinates = async_to_raw_response_wrapper(
            postalcode.retrieve_coordinates,
        )


class PostalcodeResourceWithStreamingResponse:
    def __init__(self, postalcode: PostalcodeResource) -> None:
        self._postalcode = postalcode

        self.retrieve_coordinates = to_streamed_response_wrapper(
            postalcode.retrieve_coordinates,
        )


class AsyncPostalcodeResourceWithStreamingResponse:
    def __init__(self, postalcode: AsyncPostalcodeResource) -> None:
        self._postalcode = postalcode

        self.retrieve_coordinates = async_to_streamed_response_wrapper(
            postalcode.retrieve_coordinates,
        )
