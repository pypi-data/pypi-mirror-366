# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

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
from ...types.skynet import (
    monitor_list_params,
    monitor_create_params,
    monitor_delete_params,
    monitor_update_params,
    monitor_retrieve_params,
)
from ...types.skynet.simple_resp import SimpleResp
from ...types.skynet.metadata_param import MetadataParam
from ...types.skynet.monitor_list_response import MonitorListResponse
from ...types.skynet.monitor_create_response import MonitorCreateResponse
from ...types.skynet.monitor_retrieve_response import MonitorRetrieveResponse

__all__ = ["MonitorResource", "AsyncMonitorResource"]


class MonitorResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MonitorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return MonitorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MonitorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return MonitorResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        tags: List[str],
        type: Literal["enter", "exit", "enter_and_exit", "speeding", "idle"],
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        geofence_config: monitor_create_params.GeofenceConfig | NotGiven = NOT_GIVEN,
        geofence_ids: List[str] | NotGiven = NOT_GIVEN,
        idle_config: monitor_create_params.IdleConfig | NotGiven = NOT_GIVEN,
        match_filter: monitor_create_params.MatchFilter | NotGiven = NOT_GIVEN,
        meta_data: MetadataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        speeding_config: monitor_create_params.SpeedingConfig | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MonitorCreateResponse:
        """
        Create a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          tags: Use this parameter to add tags to the monitor. tags can be used for filtering
              monitors in the _Get Monitor List_ operation. They can also be used for easy
              identification of monitors.

              Please note that valid tags are strings, consisting of alphanumeric characters
              (A-Z, a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          type: Specify the type of activity the monitor would detect.

              The monitor will be able to detect the specified type of activity and create
              events for eligible asset. A monitor can detect following types of asset
              activity:

              - enter: The monitor will create an event when a linked asset enters into the
                specified geofence.

              - exit: The monitor will create an event when a linked asset exits the specified
                geofence.

              - enter_and_exit: The monitor will create an event when a linked asset either
                enters or exits the specified geofence.

              - speeding: The monitor will create an event when a linked asset exceeds a given
                speed limit.

              - idle: The monitor will create an event when a linked asset exhibits idle
                activity.

              Please note that assets and geofences can be linked to a monitor using the
              match_filter and geofence_config attributes respectively.

          cluster: the cluster of the region you want to use

          custom_id: Set a unique ID for the new monitor. If not provided, an ID will be
              automatically generated in UUID format. A valid custom*id can contain letters,
              numbers, "-", & "*" only.

              Please note that the ID of an monitor can not be changed once it is created.

          description: Add a description for your monitor using this parameter.

          geofence_config: Geofences are geographic boundaries surrounding an area of interest.
              geofence_config is used to specify the geofences for creating enter or exit type
              of events based on the asset's location. When an asset associated with the
              monitor enters the given geofence, an enter type event is created, whereas when
              the asset moves out of the geofence an exit type event is created.

              Please note that this object is mandatory when the monitor type belongs to one
              of enter, exit or enter_and_exit.

          geofence_ids: **Deprecated. Please use the geofence_config to specify the geofence_ids for
              this monitor.**

              An array of strings to collect the geofence IDs that should be linked to the
              monitor. Geofences are geographic boundaries that can be used to trigger events
              based on an asset's location.

          idle_config: idle_config is used to set up constraints for creating idle events. When an
              asset associated with the monitor has not moved a given distance within a given
              time, the Live Tracking API can create events to denote such instances. Please
              note that this object is mandatory when the monitor type is idle.

              Let's look at the properties of this object.

          match_filter: This object is used to identify the asset(s) on which the monitor would be
              applied.

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Name of the monitor. Use this field to assign a meaningful, custom name to the
              monitor being created.

          speeding_config: speeding_config is used to set up constraints for creating over-speed events.
              When an asset associated with a monitor is traveling at a speed above the given
              limits, the Live Tracking API can create events to denote such instances. There
              is also an option to set up a tolerance before creating an event. Please note
              that this object is mandatory when type=speeding.

              Let's look at the properties of this object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/monitor",
            body=maybe_transform(
                {
                    "tags": tags,
                    "type": type,
                    "custom_id": custom_id,
                    "description": description,
                    "geofence_config": geofence_config,
                    "geofence_ids": geofence_ids,
                    "idle_config": idle_config,
                    "match_filter": match_filter,
                    "meta_data": meta_data,
                    "name": name,
                    "speeding_config": speeding_config,
                },
                monitor_create_params.MonitorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    monitor_create_params.MonitorCreateParams,
                ),
            ),
            cast_to=MonitorCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MonitorRetrieveResponse:
        """
        Get a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/skynet/monitor/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, monitor_retrieve_params.MonitorRetrieveParams),
            ),
            cast_to=MonitorRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        key: str,
        description: str | NotGiven = NOT_GIVEN,
        geofence_config: monitor_update_params.GeofenceConfig | NotGiven = NOT_GIVEN,
        geofence_ids: List[str] | NotGiven = NOT_GIVEN,
        idle_config: monitor_update_params.IdleConfig | NotGiven = NOT_GIVEN,
        match_filter: monitor_update_params.MatchFilter | NotGiven = NOT_GIVEN,
        meta_data: MetadataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        speeding_config: monitor_update_params.SpeedingConfig | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        type: Literal["enter", "exit", "enter_and_exit", "speeding", "idle"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Update a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          description: Use this parameter to update the description of the monitor.

          geofence_config: geofence_config is used to update the set of geofences linked to the monitor for
              creating enter or exit type of events based on the asset's location. Please note
              that this object is mandatory when the monitor type belongs to one of enter,
              exit or enter_and_exit.

          geofence_ids: Use this parameter to update the geofences linked to the monitor by providing
              the geofence id as , separated strings. Geofences are geographic boundaries that
              can be used to trigger events based on an asset's location.

          idle_config: idle_config is used to update the constraints for creating idle events. When an
              asset associated with the monitor has not moved a given distance within a given
              time, the Live Tracking API can create events to denote such instances.

              Please note that this object is mandatory when the monitor type is idle.

          match_filter: Use this object to update the attributes of the monitor. Please note that using
              this property will overwrite the existing attributes that the monitor might be
              using currently to match any asset(s).

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Use this parameter to update the name of the monitor. Users can add meaningful
              names to the monitors like "warehouse_exit", "depot_entry" etc.

          speeding_config: speeding_config is used to update the tolerance values for creating over-speed
              events. When an asset associated with a monitor is traveling at a speed above
              the given limits, Live Tracking API creates events to indicate such instances.

              Please note that this object is mandatory when the monitor type is speeding.

          tags: Use this parameter to update the tags of the monitor. tags can be used for
              filtering monitors in the _Get Monitor List_ operation. They can also be used
              for easy identification of monitors. Using this parameter overwrites the
              existing tags of the monitor.

              Please note that valid tags are strings, consisting of alphanumeric characters
              (A-Z, a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          type: Use this parameter to update the type of the monitor. The monitor will be able
              to detect the specified type of activity and create events for eligible asset. A
              monitor can detect following types of asset activity:

              - enter: The monitor will create an event when a linked asset enters into the
                specified geofence.

              - exit: The monitor will create an event when a linked asset exits the specified
                geofence.

              - enter_and_exit: The monitor will create an event when a linked asset either
                enters or exits the specified geofence.

              - speeding: The monitor will create an event when a linked asset exceeds a given
                speed limit.

              - idle: The monitor will create an event when a linked asset exhibits idle
                activity.

              Please note that assets and geofences can be linked to a monitor using the
              match_filter and geofence_config attributes respectively.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/skynet/monitor/{id}",
            body=maybe_transform(
                {
                    "description": description,
                    "geofence_config": geofence_config,
                    "geofence_ids": geofence_ids,
                    "idle_config": idle_config,
                    "match_filter": match_filter,
                    "meta_data": meta_data,
                    "name": name,
                    "speeding_config": speeding_config,
                    "tags": tags,
                    "type": type,
                },
                monitor_update_params.MonitorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, monitor_update_params.MonitorUpdateParams),
            ),
            cast_to=SimpleResp,
        )

    def list(
        self,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        tags: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MonitorListResponse:
        """
        Get Monitor List

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          sort: Provide a single field to sort the results by. Only updated_at or created_at
              fields can be selected for ordering the results.

              By default, the result is sorted by created_at field in the descending order.
              Allowed values for specifying the order are asc for ascending order and desc for
              descending order.

          tags: tags can be used to filter the monitors. Only those monitors which have all the
              tags provided here, will be included in the search result. In case multiple tags
              need to be specified, use , to separate them.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/skynet/monitor/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "pn": pn,
                        "ps": ps,
                        "sort": sort,
                        "tags": tags,
                    },
                    monitor_list_params.MonitorListParams,
                ),
            ),
            cast_to=MonitorListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Delete a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/skynet/monitor/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, monitor_delete_params.MonitorDeleteParams),
            ),
            cast_to=SimpleResp,
        )


class AsyncMonitorResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMonitorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMonitorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMonitorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncMonitorResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        tags: List[str],
        type: Literal["enter", "exit", "enter_and_exit", "speeding", "idle"],
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        geofence_config: monitor_create_params.GeofenceConfig | NotGiven = NOT_GIVEN,
        geofence_ids: List[str] | NotGiven = NOT_GIVEN,
        idle_config: monitor_create_params.IdleConfig | NotGiven = NOT_GIVEN,
        match_filter: monitor_create_params.MatchFilter | NotGiven = NOT_GIVEN,
        meta_data: MetadataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        speeding_config: monitor_create_params.SpeedingConfig | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MonitorCreateResponse:
        """
        Create a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          tags: Use this parameter to add tags to the monitor. tags can be used for filtering
              monitors in the _Get Monitor List_ operation. They can also be used for easy
              identification of monitors.

              Please note that valid tags are strings, consisting of alphanumeric characters
              (A-Z, a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          type: Specify the type of activity the monitor would detect.

              The monitor will be able to detect the specified type of activity and create
              events for eligible asset. A monitor can detect following types of asset
              activity:

              - enter: The monitor will create an event when a linked asset enters into the
                specified geofence.

              - exit: The monitor will create an event when a linked asset exits the specified
                geofence.

              - enter_and_exit: The monitor will create an event when a linked asset either
                enters or exits the specified geofence.

              - speeding: The monitor will create an event when a linked asset exceeds a given
                speed limit.

              - idle: The monitor will create an event when a linked asset exhibits idle
                activity.

              Please note that assets and geofences can be linked to a monitor using the
              match_filter and geofence_config attributes respectively.

          cluster: the cluster of the region you want to use

          custom_id: Set a unique ID for the new monitor. If not provided, an ID will be
              automatically generated in UUID format. A valid custom*id can contain letters,
              numbers, "-", & "*" only.

              Please note that the ID of an monitor can not be changed once it is created.

          description: Add a description for your monitor using this parameter.

          geofence_config: Geofences are geographic boundaries surrounding an area of interest.
              geofence_config is used to specify the geofences for creating enter or exit type
              of events based on the asset's location. When an asset associated with the
              monitor enters the given geofence, an enter type event is created, whereas when
              the asset moves out of the geofence an exit type event is created.

              Please note that this object is mandatory when the monitor type belongs to one
              of enter, exit or enter_and_exit.

          geofence_ids: **Deprecated. Please use the geofence_config to specify the geofence_ids for
              this monitor.**

              An array of strings to collect the geofence IDs that should be linked to the
              monitor. Geofences are geographic boundaries that can be used to trigger events
              based on an asset's location.

          idle_config: idle_config is used to set up constraints for creating idle events. When an
              asset associated with the monitor has not moved a given distance within a given
              time, the Live Tracking API can create events to denote such instances. Please
              note that this object is mandatory when the monitor type is idle.

              Let's look at the properties of this object.

          match_filter: This object is used to identify the asset(s) on which the monitor would be
              applied.

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Name of the monitor. Use this field to assign a meaningful, custom name to the
              monitor being created.

          speeding_config: speeding_config is used to set up constraints for creating over-speed events.
              When an asset associated with a monitor is traveling at a speed above the given
              limits, the Live Tracking API can create events to denote such instances. There
              is also an option to set up a tolerance before creating an event. Please note
              that this object is mandatory when type=speeding.

              Let's look at the properties of this object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/monitor",
            body=await async_maybe_transform(
                {
                    "tags": tags,
                    "type": type,
                    "custom_id": custom_id,
                    "description": description,
                    "geofence_config": geofence_config,
                    "geofence_ids": geofence_ids,
                    "idle_config": idle_config,
                    "match_filter": match_filter,
                    "meta_data": meta_data,
                    "name": name,
                    "speeding_config": speeding_config,
                },
                monitor_create_params.MonitorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                    },
                    monitor_create_params.MonitorCreateParams,
                ),
            ),
            cast_to=MonitorCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MonitorRetrieveResponse:
        """
        Get a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/skynet/monitor/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, monitor_retrieve_params.MonitorRetrieveParams),
            ),
            cast_to=MonitorRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        key: str,
        description: str | NotGiven = NOT_GIVEN,
        geofence_config: monitor_update_params.GeofenceConfig | NotGiven = NOT_GIVEN,
        geofence_ids: List[str] | NotGiven = NOT_GIVEN,
        idle_config: monitor_update_params.IdleConfig | NotGiven = NOT_GIVEN,
        match_filter: monitor_update_params.MatchFilter | NotGiven = NOT_GIVEN,
        meta_data: MetadataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        speeding_config: monitor_update_params.SpeedingConfig | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        type: Literal["enter", "exit", "enter_and_exit", "speeding", "idle"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Update a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          description: Use this parameter to update the description of the monitor.

          geofence_config: geofence_config is used to update the set of geofences linked to the monitor for
              creating enter or exit type of events based on the asset's location. Please note
              that this object is mandatory when the monitor type belongs to one of enter,
              exit or enter_and_exit.

          geofence_ids: Use this parameter to update the geofences linked to the monitor by providing
              the geofence id as , separated strings. Geofences are geographic boundaries that
              can be used to trigger events based on an asset's location.

          idle_config: idle_config is used to update the constraints for creating idle events. When an
              asset associated with the monitor has not moved a given distance within a given
              time, the Live Tracking API can create events to denote such instances.

              Please note that this object is mandatory when the monitor type is idle.

          match_filter: Use this object to update the attributes of the monitor. Please note that using
              this property will overwrite the existing attributes that the monitor might be
              using currently to match any asset(s).

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Use this parameter to update the name of the monitor. Users can add meaningful
              names to the monitors like "warehouse_exit", "depot_entry" etc.

          speeding_config: speeding_config is used to update the tolerance values for creating over-speed
              events. When an asset associated with a monitor is traveling at a speed above
              the given limits, Live Tracking API creates events to indicate such instances.

              Please note that this object is mandatory when the monitor type is speeding.

          tags: Use this parameter to update the tags of the monitor. tags can be used for
              filtering monitors in the _Get Monitor List_ operation. They can also be used
              for easy identification of monitors. Using this parameter overwrites the
              existing tags of the monitor.

              Please note that valid tags are strings, consisting of alphanumeric characters
              (A-Z, a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          type: Use this parameter to update the type of the monitor. The monitor will be able
              to detect the specified type of activity and create events for eligible asset. A
              monitor can detect following types of asset activity:

              - enter: The monitor will create an event when a linked asset enters into the
                specified geofence.

              - exit: The monitor will create an event when a linked asset exits the specified
                geofence.

              - enter_and_exit: The monitor will create an event when a linked asset either
                enters or exits the specified geofence.

              - speeding: The monitor will create an event when a linked asset exceeds a given
                speed limit.

              - idle: The monitor will create an event when a linked asset exhibits idle
                activity.

              Please note that assets and geofences can be linked to a monitor using the
              match_filter and geofence_config attributes respectively.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/skynet/monitor/{id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "geofence_config": geofence_config,
                    "geofence_ids": geofence_ids,
                    "idle_config": idle_config,
                    "match_filter": match_filter,
                    "meta_data": meta_data,
                    "name": name,
                    "speeding_config": speeding_config,
                    "tags": tags,
                    "type": type,
                },
                monitor_update_params.MonitorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, monitor_update_params.MonitorUpdateParams),
            ),
            cast_to=SimpleResp,
        )

    async def list(
        self,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        tags: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MonitorListResponse:
        """
        Get Monitor List

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          sort: Provide a single field to sort the results by. Only updated_at or created_at
              fields can be selected for ordering the results.

              By default, the result is sorted by created_at field in the descending order.
              Allowed values for specifying the order are asc for ascending order and desc for
              descending order.

          tags: tags can be used to filter the monitors. Only those monitors which have all the
              tags provided here, will be included in the search result. In case multiple tags
              need to be specified, use , to separate them.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/skynet/monitor/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "pn": pn,
                        "ps": ps,
                        "sort": sort,
                        "tags": tags,
                    },
                    monitor_list_params.MonitorListParams,
                ),
            ),
            cast_to=MonitorListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Delete a Monitor

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/skynet/monitor/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, monitor_delete_params.MonitorDeleteParams),
            ),
            cast_to=SimpleResp,
        )


class MonitorResourceWithRawResponse:
    def __init__(self, monitor: MonitorResource) -> None:
        self._monitor = monitor

        self.create = to_raw_response_wrapper(
            monitor.create,
        )
        self.retrieve = to_raw_response_wrapper(
            monitor.retrieve,
        )
        self.update = to_raw_response_wrapper(
            monitor.update,
        )
        self.list = to_raw_response_wrapper(
            monitor.list,
        )
        self.delete = to_raw_response_wrapper(
            monitor.delete,
        )


class AsyncMonitorResourceWithRawResponse:
    def __init__(self, monitor: AsyncMonitorResource) -> None:
        self._monitor = monitor

        self.create = async_to_raw_response_wrapper(
            monitor.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            monitor.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            monitor.update,
        )
        self.list = async_to_raw_response_wrapper(
            monitor.list,
        )
        self.delete = async_to_raw_response_wrapper(
            monitor.delete,
        )


class MonitorResourceWithStreamingResponse:
    def __init__(self, monitor: MonitorResource) -> None:
        self._monitor = monitor

        self.create = to_streamed_response_wrapper(
            monitor.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            monitor.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            monitor.update,
        )
        self.list = to_streamed_response_wrapper(
            monitor.list,
        )
        self.delete = to_streamed_response_wrapper(
            monitor.delete,
        )


class AsyncMonitorResourceWithStreamingResponse:
    def __init__(self, monitor: AsyncMonitorResource) -> None:
        self._monitor = monitor

        self.create = async_to_streamed_response_wrapper(
            monitor.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            monitor.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            monitor.update,
        )
        self.list = async_to_streamed_response_wrapper(
            monitor.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            monitor.delete,
        )
