# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .trip import (
    TripResource,
    AsyncTripResource,
    TripResourceWithRawResponse,
    AsyncTripResourceWithRawResponse,
    TripResourceWithStreamingResponse,
    AsyncTripResourceWithStreamingResponse,
)
from .config import (
    ConfigResource,
    AsyncConfigResource,
    ConfigResourceWithRawResponse,
    AsyncConfigResourceWithRawResponse,
    ConfigResourceWithStreamingResponse,
    AsyncConfigResourceWithStreamingResponse,
)
from ...types import skynet_subscribe_params
from .monitor import (
    MonitorResource,
    AsyncMonitorResource,
    MonitorResourceWithRawResponse,
    AsyncMonitorResourceWithRawResponse,
    MonitorResourceWithStreamingResponse,
    AsyncMonitorResourceWithStreamingResponse,
)
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
from .asset.asset import (
    AssetResource,
    AsyncAssetResource,
    AssetResourceWithRawResponse,
    AsyncAssetResourceWithRawResponse,
    AssetResourceWithStreamingResponse,
    AsyncAssetResourceWithStreamingResponse,
)
from .search.search import (
    SearchResource,
    AsyncSearchResource,
    SearchResourceWithRawResponse,
    AsyncSearchResourceWithRawResponse,
    SearchResourceWithStreamingResponse,
    AsyncSearchResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .namespaced_apikeys import (
    NamespacedApikeysResource,
    AsyncNamespacedApikeysResource,
    NamespacedApikeysResourceWithRawResponse,
    AsyncNamespacedApikeysResourceWithRawResponse,
    NamespacedApikeysResourceWithStreamingResponse,
    AsyncNamespacedApikeysResourceWithStreamingResponse,
)
from ...types.skynet_subscribe_response import SkynetSubscribeResponse

__all__ = ["SkynetResource", "AsyncSkynetResource"]


class SkynetResource(SyncAPIResource):
    @cached_property
    def asset(self) -> AssetResource:
        return AssetResource(self._client)

    @cached_property
    def monitor(self) -> MonitorResource:
        return MonitorResource(self._client)

    @cached_property
    def trip(self) -> TripResource:
        return TripResource(self._client)

    @cached_property
    def namespaced_apikeys(self) -> NamespacedApikeysResource:
        return NamespacedApikeysResource(self._client)

    @cached_property
    def config(self) -> ConfigResource:
        return ConfigResource(self._client)

    @cached_property
    def search(self) -> SearchResource:
        return SearchResource(self._client)

    @cached_property
    def with_raw_response(self) -> SkynetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SkynetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SkynetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return SkynetResourceWithStreamingResponse(self)

    def subscribe(
        self,
        *,
        action: Literal["TRIP_SUBSCRIBE", "TRIP_UNSUBSCRIBE", "HEARTBEAT"],
        id: str | NotGiven = NOT_GIVEN,
        params: skynet_subscribe_params.Params | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SkynetSubscribeResponse:
        """
        POST Action

        Args:
          action: Specify the behavior that needs to be achieved for the subscription. Following
              values are accepted:

              - TRIP_SUBSCRIBE: Enable a trip subscription.
              - TRIP_UNSUBSCRIBE: Unsubscribe from a trip
              - HEARTBEAT: Enable heartbeat mechanism for a web-socket connection. The action
                message need to be sent at a frequency higher than every 5 mins to keep the
                connection alive. Alternatively, users can chose to respond to the ping frame
                sent by web socket server to keep the connection alive. Refer to
                [connection details](https://188--nbai-docs-stg.netlify.app/docs/tracking/api/live-tracking-api#connect-to-web-socket-server)
                for more details.

          id: Specify a custom ID for the subscription. It can be used to reference a given
              subscription in the downstream applications / systems.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/subscribe",
            body=maybe_transform(
                {
                    "action": action,
                    "id": id,
                    "params": params,
                },
                skynet_subscribe_params.SkynetSubscribeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SkynetSubscribeResponse,
        )


class AsyncSkynetResource(AsyncAPIResource):
    @cached_property
    def asset(self) -> AsyncAssetResource:
        return AsyncAssetResource(self._client)

    @cached_property
    def monitor(self) -> AsyncMonitorResource:
        return AsyncMonitorResource(self._client)

    @cached_property
    def trip(self) -> AsyncTripResource:
        return AsyncTripResource(self._client)

    @cached_property
    def namespaced_apikeys(self) -> AsyncNamespacedApikeysResource:
        return AsyncNamespacedApikeysResource(self._client)

    @cached_property
    def config(self) -> AsyncConfigResource:
        return AsyncConfigResource(self._client)

    @cached_property
    def search(self) -> AsyncSearchResource:
        return AsyncSearchResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSkynetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSkynetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSkynetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncSkynetResourceWithStreamingResponse(self)

    async def subscribe(
        self,
        *,
        action: Literal["TRIP_SUBSCRIBE", "TRIP_UNSUBSCRIBE", "HEARTBEAT"],
        id: str | NotGiven = NOT_GIVEN,
        params: skynet_subscribe_params.Params | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SkynetSubscribeResponse:
        """
        POST Action

        Args:
          action: Specify the behavior that needs to be achieved for the subscription. Following
              values are accepted:

              - TRIP_SUBSCRIBE: Enable a trip subscription.
              - TRIP_UNSUBSCRIBE: Unsubscribe from a trip
              - HEARTBEAT: Enable heartbeat mechanism for a web-socket connection. The action
                message need to be sent at a frequency higher than every 5 mins to keep the
                connection alive. Alternatively, users can chose to respond to the ping frame
                sent by web socket server to keep the connection alive. Refer to
                [connection details](https://188--nbai-docs-stg.netlify.app/docs/tracking/api/live-tracking-api#connect-to-web-socket-server)
                for more details.

          id: Specify a custom ID for the subscription. It can be used to reference a given
              subscription in the downstream applications / systems.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/subscribe",
            body=await async_maybe_transform(
                {
                    "action": action,
                    "id": id,
                    "params": params,
                },
                skynet_subscribe_params.SkynetSubscribeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SkynetSubscribeResponse,
        )


class SkynetResourceWithRawResponse:
    def __init__(self, skynet: SkynetResource) -> None:
        self._skynet = skynet

        self.subscribe = to_raw_response_wrapper(
            skynet.subscribe,
        )

    @cached_property
    def asset(self) -> AssetResourceWithRawResponse:
        return AssetResourceWithRawResponse(self._skynet.asset)

    @cached_property
    def monitor(self) -> MonitorResourceWithRawResponse:
        return MonitorResourceWithRawResponse(self._skynet.monitor)

    @cached_property
    def trip(self) -> TripResourceWithRawResponse:
        return TripResourceWithRawResponse(self._skynet.trip)

    @cached_property
    def namespaced_apikeys(self) -> NamespacedApikeysResourceWithRawResponse:
        return NamespacedApikeysResourceWithRawResponse(self._skynet.namespaced_apikeys)

    @cached_property
    def config(self) -> ConfigResourceWithRawResponse:
        return ConfigResourceWithRawResponse(self._skynet.config)

    @cached_property
    def search(self) -> SearchResourceWithRawResponse:
        return SearchResourceWithRawResponse(self._skynet.search)


class AsyncSkynetResourceWithRawResponse:
    def __init__(self, skynet: AsyncSkynetResource) -> None:
        self._skynet = skynet

        self.subscribe = async_to_raw_response_wrapper(
            skynet.subscribe,
        )

    @cached_property
    def asset(self) -> AsyncAssetResourceWithRawResponse:
        return AsyncAssetResourceWithRawResponse(self._skynet.asset)

    @cached_property
    def monitor(self) -> AsyncMonitorResourceWithRawResponse:
        return AsyncMonitorResourceWithRawResponse(self._skynet.monitor)

    @cached_property
    def trip(self) -> AsyncTripResourceWithRawResponse:
        return AsyncTripResourceWithRawResponse(self._skynet.trip)

    @cached_property
    def namespaced_apikeys(self) -> AsyncNamespacedApikeysResourceWithRawResponse:
        return AsyncNamespacedApikeysResourceWithRawResponse(self._skynet.namespaced_apikeys)

    @cached_property
    def config(self) -> AsyncConfigResourceWithRawResponse:
        return AsyncConfigResourceWithRawResponse(self._skynet.config)

    @cached_property
    def search(self) -> AsyncSearchResourceWithRawResponse:
        return AsyncSearchResourceWithRawResponse(self._skynet.search)


class SkynetResourceWithStreamingResponse:
    def __init__(self, skynet: SkynetResource) -> None:
        self._skynet = skynet

        self.subscribe = to_streamed_response_wrapper(
            skynet.subscribe,
        )

    @cached_property
    def asset(self) -> AssetResourceWithStreamingResponse:
        return AssetResourceWithStreamingResponse(self._skynet.asset)

    @cached_property
    def monitor(self) -> MonitorResourceWithStreamingResponse:
        return MonitorResourceWithStreamingResponse(self._skynet.monitor)

    @cached_property
    def trip(self) -> TripResourceWithStreamingResponse:
        return TripResourceWithStreamingResponse(self._skynet.trip)

    @cached_property
    def namespaced_apikeys(self) -> NamespacedApikeysResourceWithStreamingResponse:
        return NamespacedApikeysResourceWithStreamingResponse(self._skynet.namespaced_apikeys)

    @cached_property
    def config(self) -> ConfigResourceWithStreamingResponse:
        return ConfigResourceWithStreamingResponse(self._skynet.config)

    @cached_property
    def search(self) -> SearchResourceWithStreamingResponse:
        return SearchResourceWithStreamingResponse(self._skynet.search)


class AsyncSkynetResourceWithStreamingResponse:
    def __init__(self, skynet: AsyncSkynetResource) -> None:
        self._skynet = skynet

        self.subscribe = async_to_streamed_response_wrapper(
            skynet.subscribe,
        )

    @cached_property
    def asset(self) -> AsyncAssetResourceWithStreamingResponse:
        return AsyncAssetResourceWithStreamingResponse(self._skynet.asset)

    @cached_property
    def monitor(self) -> AsyncMonitorResourceWithStreamingResponse:
        return AsyncMonitorResourceWithStreamingResponse(self._skynet.monitor)

    @cached_property
    def trip(self) -> AsyncTripResourceWithStreamingResponse:
        return AsyncTripResourceWithStreamingResponse(self._skynet.trip)

    @cached_property
    def namespaced_apikeys(self) -> AsyncNamespacedApikeysResourceWithStreamingResponse:
        return AsyncNamespacedApikeysResourceWithStreamingResponse(self._skynet.namespaced_apikeys)

    @cached_property
    def config(self) -> AsyncConfigResourceWithStreamingResponse:
        return AsyncConfigResourceWithStreamingResponse(self._skynet.config)

    @cached_property
    def search(self) -> AsyncSearchResourceWithStreamingResponse:
        return AsyncSearchResourceWithStreamingResponse(self._skynet.search)
