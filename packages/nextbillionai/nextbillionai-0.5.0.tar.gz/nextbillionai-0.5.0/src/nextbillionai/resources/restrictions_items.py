# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import restrictions_item_list_params
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
from ..types.restrictions_item_list_response import RestrictionsItemListResponse

__all__ = ["RestrictionsItemsResource", "AsyncRestrictionsItemsResource"]


class RestrictionsItemsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RestrictionsItemsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RestrictionsItemsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RestrictionsItemsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return RestrictionsItemsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        max_lat: float,
        max_lon: float,
        min_lat: float,
        min_lon: float,
        group_id: float | NotGiven = NOT_GIVEN,
        mode: Literal["0w", "1w", "2w", "3w", "4w", "6w"] | NotGiven = NOT_GIVEN,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
        | NotGiven = NOT_GIVEN,
        source: str | NotGiven = NOT_GIVEN,
        state: Literal["enabled", "disabled", "deleted"] | NotGiven = NOT_GIVEN,
        status: Literal["active", "inactive"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionsItemListResponse:
        """
        Get restriction items by bbox

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/restrictions_items",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "max_lat": max_lat,
                        "max_lon": max_lon,
                        "min_lat": min_lat,
                        "min_lon": min_lon,
                        "group_id": group_id,
                        "mode": mode,
                        "restriction_type": restriction_type,
                        "source": source,
                        "state": state,
                        "status": status,
                    },
                    restrictions_item_list_params.RestrictionsItemListParams,
                ),
            ),
            cast_to=RestrictionsItemListResponse,
        )


class AsyncRestrictionsItemsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRestrictionsItemsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRestrictionsItemsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRestrictionsItemsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncRestrictionsItemsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        max_lat: float,
        max_lon: float,
        min_lat: float,
        min_lon: float,
        group_id: float | NotGiven = NOT_GIVEN,
        mode: Literal["0w", "1w", "2w", "3w", "4w", "6w"] | NotGiven = NOT_GIVEN,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
        | NotGiven = NOT_GIVEN,
        source: str | NotGiven = NOT_GIVEN,
        state: Literal["enabled", "disabled", "deleted"] | NotGiven = NOT_GIVEN,
        status: Literal["active", "inactive"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionsItemListResponse:
        """
        Get restriction items by bbox

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/restrictions_items",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "max_lat": max_lat,
                        "max_lon": max_lon,
                        "min_lat": min_lat,
                        "min_lon": min_lon,
                        "group_id": group_id,
                        "mode": mode,
                        "restriction_type": restriction_type,
                        "source": source,
                        "state": state,
                        "status": status,
                    },
                    restrictions_item_list_params.RestrictionsItemListParams,
                ),
            ),
            cast_to=RestrictionsItemListResponse,
        )


class RestrictionsItemsResourceWithRawResponse:
    def __init__(self, restrictions_items: RestrictionsItemsResource) -> None:
        self._restrictions_items = restrictions_items

        self.list = to_raw_response_wrapper(
            restrictions_items.list,
        )


class AsyncRestrictionsItemsResourceWithRawResponse:
    def __init__(self, restrictions_items: AsyncRestrictionsItemsResource) -> None:
        self._restrictions_items = restrictions_items

        self.list = async_to_raw_response_wrapper(
            restrictions_items.list,
        )


class RestrictionsItemsResourceWithStreamingResponse:
    def __init__(self, restrictions_items: RestrictionsItemsResource) -> None:
        self._restrictions_items = restrictions_items

        self.list = to_streamed_response_wrapper(
            restrictions_items.list,
        )


class AsyncRestrictionsItemsResourceWithStreamingResponse:
    def __init__(self, restrictions_items: AsyncRestrictionsItemsResource) -> None:
        self._restrictions_items = restrictions_items

        self.list = async_to_streamed_response_wrapper(
            restrictions_items.list,
        )
