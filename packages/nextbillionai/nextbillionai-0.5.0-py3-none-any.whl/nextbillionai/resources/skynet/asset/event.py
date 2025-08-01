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
from ....types.skynet.asset import event_list_params
from ....types.skynet.asset.event_list_response import EventListResponse

__all__ = ["EventResource", "AsyncEventResource"]


class EventResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EventResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return EventResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return EventResourceWithStreamingResponse(self)

    def list(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        end_time: int | NotGiven = NOT_GIVEN,
        monitor_id: str | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EventListResponse:
        """
        Event History of an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          end_time: Time before which the events triggered by the asset need to be retrieved.

          monitor_id: Filter the events by monitor_id. When provided, only the events triggered by the
              monitor will be returned in response.

              Please note that if the attributes of the asset identified by id and those of
              the monitor do not match, then no events might be returned for this monitor_id.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          start_time: Time after which the events triggered by the asset need to be retrieved.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/skynet/asset/{id}/event/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "end_time": end_time,
                        "monitor_id": monitor_id,
                        "pn": pn,
                        "ps": ps,
                        "start_time": start_time,
                    },
                    event_list_params.EventListParams,
                ),
            ),
            cast_to=EventListResponse,
        )


class AsyncEventResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEventResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEventResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncEventResourceWithStreamingResponse(self)

    async def list(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        end_time: int | NotGiven = NOT_GIVEN,
        monitor_id: str | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EventListResponse:
        """
        Event History of an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          end_time: Time before which the events triggered by the asset need to be retrieved.

          monitor_id: Filter the events by monitor_id. When provided, only the events triggered by the
              monitor will be returned in response.

              Please note that if the attributes of the asset identified by id and those of
              the monitor do not match, then no events might be returned for this monitor_id.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          start_time: Time after which the events triggered by the asset need to be retrieved.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/skynet/asset/{id}/event/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "end_time": end_time,
                        "monitor_id": monitor_id,
                        "pn": pn,
                        "ps": ps,
                        "start_time": start_time,
                    },
                    event_list_params.EventListParams,
                ),
            ),
            cast_to=EventListResponse,
        )


class EventResourceWithRawResponse:
    def __init__(self, event: EventResource) -> None:
        self._event = event

        self.list = to_raw_response_wrapper(
            event.list,
        )


class AsyncEventResourceWithRawResponse:
    def __init__(self, event: AsyncEventResource) -> None:
        self._event = event

        self.list = async_to_raw_response_wrapper(
            event.list,
        )


class EventResourceWithStreamingResponse:
    def __init__(self, event: EventResource) -> None:
        self._event = event

        self.list = to_streamed_response_wrapper(
            event.list,
        )


class AsyncEventResourceWithStreamingResponse:
    def __init__(self, event: AsyncEventResource) -> None:
        self._event = event

        self.list = async_to_streamed_response_wrapper(
            event.list,
        )
