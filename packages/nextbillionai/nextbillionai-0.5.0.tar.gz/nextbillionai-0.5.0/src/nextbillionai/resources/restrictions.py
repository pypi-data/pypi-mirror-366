# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

from ..types import (
    restriction_list_params,
    restriction_create_params,
    restriction_delete_params,
    restriction_update_params,
    restriction_retrieve_params,
    restriction_set_state_params,
    restriction_list_by_bbox_params,
)
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
from ..types.rich_group_response import RichGroupResponse
from ..types.restriction_list_response import RestrictionListResponse
from ..types.restriction_delete_response import RestrictionDeleteResponse
from ..types.restriction_list_by_bbox_response import RestrictionListByBboxResponse

__all__ = ["RestrictionsResource", "AsyncRestrictionsResource"]


class RestrictionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RestrictionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RestrictionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RestrictionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return RestrictionsResourceWithStreamingResponse(self)

    def create(
        self,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"],
        *,
        key: str,
        area: str,
        name: str,
        latlon: bool | NotGiven = NOT_GIVEN,
        comment: str | NotGiven = NOT_GIVEN,
        direction: Literal["forward", "backward", "both"] | NotGiven = NOT_GIVEN,
        end_time: float | NotGiven = NOT_GIVEN,
        geofence: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        length: int | NotGiven = NOT_GIVEN,
        mode: List[Literal["0w", "2w", "3w", "4w", "6w"]] | NotGiven = NOT_GIVEN,
        repeat_on: str | NotGiven = NOT_GIVEN,
        segments: Iterable[restriction_create_params.Segment] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        speed_limit: float | NotGiven = NOT_GIVEN,
        start_time: float | NotGiven = NOT_GIVEN,
        tracks: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        turns: Iterable[restriction_create_params.Turn] | NotGiven = NOT_GIVEN,
        weight: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Create a new restriction

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          area: Specify the area name. It represents a region where restrictions can be applied.
              This is a custom field and it is recommended for the users to check with
              [NextBillion.ai](www.nextbillion.ai) support for the right value. Alternatively,
              users can invoke the _[Areas](#supported-areas)_ method to get a list of
              available areas for them.

          name: Specify a custom, descriptive name for the restriction.

          latlon: Use this parameter to decide the format for specifying the geofence coordinates.
              If true, then the coordinates of geofence can be specified as
              "latitude,longitude" format, otherwise they should be specified in
              "longitude,latitude" format.

          comment: Use this parameter to add any custom information about the restriction being
              created.

          direction: Represents the traffic direction on the segments to which the restriction will
              be applied.

          end_time: Provide a UNIX epoch timestamp in seconds, representing the time when the
              restriction should cease to be in-effect.

          geofence: An array of coordinates denoting the boundary of an area in which the
              restrictions are to be applied. The format in which coordinates should be listed
              is defined by the latlon field.

              Geofences can be used to create all restriction types, except for a turn type
              restriction. Please note that segments is not required when using geofence to
              create restrictions.

          height: Specify the maximum truck height, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          length: Specify the maximum truck length, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          mode: Provide the driving modes for which the restriction should be effective. If the
              value is an empty array or if it is not provided then the restriction would be
              applied for all modes.

          repeat_on: It represents the days and times when the restriction is in effect. Users can
              use this property to set recurring or one-time restrictions as per the
              [given format](https://wiki.openstreetmap.org/wiki/Key:opening_hours) for
              specifying the recurring schedule of the restriction.

              Please provided values as per the local time of the region where the restriction
              is being applied.

          segments: An array of objects to collect the details of the segments of a road on which
              the restriction has to be applied. Each object corresponds to a new segment.

              Please note that segments is mandatory for all restrtiction_type except turn.

          speed: Provide the the fixed speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is fixedspeed.

          speed_limit: Provide the the maximum speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is maxspeed.

          start_time: Provide a UNIX epoch timestamp in seconds, representing the start time for the
              restriction to be in-effect.

          tracks: Specify a sequence of coordinates (track) where the restriction is to be
              applied. The coordinates will be snapped to nearest road. Please note when using
              tracks, segments and turns are not required.

          turns: An array of objects to collect the details of the turns of a road on which the
              restriction has to be applied. Each object corresponds to a new turn.

              Please note that turns is mandatory for when restrtiction_type=turn.

          weight: Specify the maximum truck weight, in kilograms, that the restriction will allow.
              A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided for is truck restriction type.

          width: Specify the maximum truck width, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not restriction_type:
            raise ValueError(f"Expected a non-empty value for `restriction_type` but received {restriction_type!r}")
        return self._post(
            f"/restrictions/{restriction_type}",
            body=maybe_transform(
                {
                    "area": area,
                    "name": name,
                    "comment": comment,
                    "direction": direction,
                    "end_time": end_time,
                    "geofence": geofence,
                    "height": height,
                    "length": length,
                    "mode": mode,
                    "repeat_on": repeat_on,
                    "segments": segments,
                    "speed": speed,
                    "speed_limit": speed_limit,
                    "start_time": start_time,
                    "tracks": tracks,
                    "turns": turns,
                    "weight": weight,
                    "width": width,
                },
                restriction_create_params.RestrictionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "latlon": latlon,
                    },
                    restriction_create_params.RestrictionCreateParams,
                ),
            ),
            cast_to=RichGroupResponse,
        )

    def retrieve(
        self,
        id: int,
        *,
        key: str,
        transform: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Get a restriction by id

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          transform: a internal parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/restrictions/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "transform": transform,
                    },
                    restriction_retrieve_params.RestrictionRetrieveParams,
                ),
            ),
            cast_to=RichGroupResponse,
        )

    def update(
        self,
        id: int,
        *,
        key: str,
        area: str,
        name: str,
        latlon: bool | NotGiven = NOT_GIVEN,
        comment: str | NotGiven = NOT_GIVEN,
        direction: Literal["forward", "backward", "both"] | NotGiven = NOT_GIVEN,
        end_time: float | NotGiven = NOT_GIVEN,
        geofence: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        length: int | NotGiven = NOT_GIVEN,
        mode: List[Literal["0w", "2w", "3w", "4w", "6w"]] | NotGiven = NOT_GIVEN,
        repeat_on: str | NotGiven = NOT_GIVEN,
        segments: Iterable[restriction_update_params.Segment] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        speed_limit: float | NotGiven = NOT_GIVEN,
        start_time: float | NotGiven = NOT_GIVEN,
        tracks: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        turns: Iterable[restriction_update_params.Turn] | NotGiven = NOT_GIVEN,
        weight: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Update a restriction

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          area: Specify the area name. It represents a region where restrictions can be applied.
              This is a custom field and it is recommended for the users to check with
              [NextBillion.ai](www.nextbillion.ai) support for the right value. Alternatively,
              users can invoke the _[Areas](#supported-areas)_ method to get a list of
              available areas for them.

          name: Specify a custom, descriptive name for the restriction.

          latlon: Use this parameter to decide the format for specifying the geofence coordinates.
              If true, then the coordinates of geofence can be specified as
              "latitude,longitude" format, otherwise they should be specified in
              "longitude,latitude" format.

          comment: Use this parameter to add any custom information about the restriction being
              created.

          direction: Represents the traffic direction on the segments to which the restriction will
              be applied.

          end_time: Provide a UNIX epoch timestamp in seconds, representing the time when the
              restriction should cease to be in-effect.

          geofence: An array of coordinates denoting the boundary of an area in which the
              restrictions are to be applied. The format in which coordinates should be listed
              is defined by the latlon field.

              Geofences can be used to create all restriction types, except for a turn type
              restriction. Please note that segments is not required when using geofence to
              create restrictions.

          height: Specify the maximum truck height, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          length: Specify the maximum truck length, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          mode: Provide the driving modes for which the restriction should be effective. If the
              value is an empty array or if it is not provided then the restriction would be
              applied for all modes.

          repeat_on: It represents the days and times when the restriction is in effect. Users can
              use this property to set recurring or one-time restrictions as per the
              [given format](https://wiki.openstreetmap.org/wiki/Key:opening_hours) for
              specifying the recurring schedule of the restriction.

              Please provided values as per the local time of the region where the restriction
              is being applied.

          segments: An array of objects to collect the details of the segments of a road on which
              the restriction has to be applied. Each object corresponds to a new segment.

              Please note that segments is mandatory for all restrtiction_type except turn.

          speed: Provide the the fixed speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is fixedspeed.

          speed_limit: Provide the the maximum speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is maxspeed.

          start_time: Provide a UNIX epoch timestamp in seconds, representing the start time for the
              restriction to be in-effect.

          tracks: Specify a sequence of coordinates (track) where the restriction is to be
              applied. The coordinates will be snapped to nearest road. Please note when using
              tracks, segments and turns are not required.

          turns: An array of objects to collect the details of the turns of a road on which the
              restriction has to be applied. Each object corresponds to a new turn.

              Please note that turns is mandatory for when restrtiction_type=turn.

          weight: Specify the maximum truck weight, in kilograms, that the restriction will allow.
              A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided for is truck restriction type.

          width: Specify the maximum truck width, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/restrictions/{id}",
            body=maybe_transform(
                {
                    "area": area,
                    "name": name,
                    "comment": comment,
                    "direction": direction,
                    "end_time": end_time,
                    "geofence": geofence,
                    "height": height,
                    "length": length,
                    "mode": mode,
                    "repeat_on": repeat_on,
                    "segments": segments,
                    "speed": speed,
                    "speed_limit": speed_limit,
                    "start_time": start_time,
                    "tracks": tracks,
                    "turns": turns,
                    "weight": weight,
                    "width": width,
                },
                restriction_update_params.RestrictionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "latlon": latlon,
                    },
                    restriction_update_params.RestrictionUpdateParams,
                ),
            ),
            cast_to=RichGroupResponse,
        )

    def list(
        self,
        *,
        area: str,
        key: str,
        limit: int,
        offset: int,
        mode: Literal["0w", "2w", "3w", "4w", "6w"] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
        | NotGiven = NOT_GIVEN,
        source: Literal["rrt", "pbf"] | NotGiven = NOT_GIVEN,
        state: Literal["enabled", "disabled", "deleted"] | NotGiven = NOT_GIVEN,
        status: Literal["active", "inactive"] | NotGiven = NOT_GIVEN,
        transform: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionListResponse:
        """Get the paginated list of restrictions

        Args:
          area: Specify the area name.

        It represents a region where restrictions can be applied.

              _The area it belongs to. See Area API_

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          limit: The number of restrictions to be returned in the response. Please note that if
              the limit is set to a number more than the total number of available
              restrictions, then all restrictions would be returned together.

          offset: An integer value indicating the number of items in the collection that need to
              be skipped in the response. Please note that the offset starts from 0, so the
              first item returned in the result would be the item at (offset + 1) position in
              collection.

              Users can use offset along with limit to implement paginated result.

          mode: Specify the modes of travel that the restriction pertains to.

          name: The name of the restriction. This should be same as that provided while creating
              or updating the restriction.

          restriction_type: Specify the type of restrictions to fetch.

          source: It represents where it comes from, currently the possible values include "rrt",
              "xsm"

          state: This parameter is used to filter restrictions based on their state i.e. whether
              the restriction is currently enabled, disabled, or deleted. For example, users
              can retrieve a list of all the deleted restrictions by setting state=deleted.

          status: Restrictions can be active or inactive at a given time by virtue of their
              nature. For example, maximum speed limits can be active on the roads leading to
              schools during school hours and be inactive afterwards or certain road closure
              restrictions be active during holidays/concerts and be inactive otherwise.

              Use this parameter to filter the restrictions based on their status at the time
              of making the request i.e. whether they are in force or not.

          transform: a internal parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/restrictions/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "area": area,
                        "key": key,
                        "limit": limit,
                        "offset": offset,
                        "mode": mode,
                        "name": name,
                        "restriction_type": restriction_type,
                        "source": source,
                        "state": state,
                        "status": status,
                        "transform": transform,
                    },
                    restriction_list_params.RestrictionListParams,
                ),
            ),
            cast_to=RestrictionListResponse,
        )

    def delete(
        self,
        id: int,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionDeleteResponse:
        """
        Delete a restriction by ID

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            f"/restrictions/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, restriction_delete_params.RestrictionDeleteParams),
            ),
            cast_to=RestrictionDeleteResponse,
        )

    def list_by_bbox(
        self,
        *,
        key: str,
        max_lat: float,
        max_lon: float,
        min_lat: float,
        min_lon: float,
        mode: List[Literal["0w", "2w", "3w", "4w", "6w"]] | NotGiven = NOT_GIVEN,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
        | NotGiven = NOT_GIVEN,
        source: Literal["rrt", "pbf"] | NotGiven = NOT_GIVEN,
        state: Literal["enabled", "disabled", "deleted"] | NotGiven = NOT_GIVEN,
        status: Literal["active", "inactive"] | NotGiven = NOT_GIVEN,
        transform: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionListByBboxResponse:
        """
        Get restrictions by bbox

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          max_lat: Specifies the maximum latitude value for the bounding box.

          max_lon: Specifies the maximum longitude value for the bounding box.

          min_lat: Specifies the minimum latitude value for the bounding box.

          min_lon: Specifies the minimum longitude value for the bounding box.

          mode: Specify the modes of travel that the restriction pertains to.

          restriction_type: Specify the type of restrictions to fetch.

          source: This parameter represents where the restriction comes from and cannot be
              modified by clients sending requests to the API endpoint.

              For example, an API endpoint that returns a list of restrictions could include
              the source parameter to indicate where each item comes from. This parameter can
              be useful for filtering, sorting, or grouping the results based on their source.

          state: This parameter is used to filter restrictions based on their state i.e. whether
              the restriction is currently enabled, disabled, or deleted. For example, users
              can retrieve a list of all the deleted restrictions by setting state=deleted.

          status: Restrictions can be active or inactive at a given time by virtue of their
              nature. For example, maximum speed limits can be active on the roads leading to
              schools during school hours and be inactive afterwards or certain road closure
              restrictions be active during holidays/concerts and be inactive otherwise.

              Use this parameter to filter the restrictions based on their status at the time
              of making the request i.e. whether they are in force or not.

          transform: This is internal parameter with a default value as false.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/restrictions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "max_lat": max_lat,
                        "max_lon": max_lon,
                        "min_lat": min_lat,
                        "min_lon": min_lon,
                        "mode": mode,
                        "restriction_type": restriction_type,
                        "source": source,
                        "state": state,
                        "status": status,
                        "transform": transform,
                    },
                    restriction_list_by_bbox_params.RestrictionListByBboxParams,
                ),
            ),
            cast_to=RestrictionListByBboxResponse,
        )

    def set_state(
        self,
        id: int,
        *,
        key: str,
        state: Literal["enabled", "disabled", "deleted"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Set the state of a restriction by ID

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          state: Use this field to specify the new state of the restriction. Please note that
              this method cannot update the state of restrictions that are currently in
              'deleted' state.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            f"/restrictions/{id}/state",
            body=maybe_transform({"state": state}, restriction_set_state_params.RestrictionSetStateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, restriction_set_state_params.RestrictionSetStateParams),
            ),
            cast_to=RichGroupResponse,
        )


class AsyncRestrictionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRestrictionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRestrictionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRestrictionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncRestrictionsResourceWithStreamingResponse(self)

    async def create(
        self,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"],
        *,
        key: str,
        area: str,
        name: str,
        latlon: bool | NotGiven = NOT_GIVEN,
        comment: str | NotGiven = NOT_GIVEN,
        direction: Literal["forward", "backward", "both"] | NotGiven = NOT_GIVEN,
        end_time: float | NotGiven = NOT_GIVEN,
        geofence: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        length: int | NotGiven = NOT_GIVEN,
        mode: List[Literal["0w", "2w", "3w", "4w", "6w"]] | NotGiven = NOT_GIVEN,
        repeat_on: str | NotGiven = NOT_GIVEN,
        segments: Iterable[restriction_create_params.Segment] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        speed_limit: float | NotGiven = NOT_GIVEN,
        start_time: float | NotGiven = NOT_GIVEN,
        tracks: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        turns: Iterable[restriction_create_params.Turn] | NotGiven = NOT_GIVEN,
        weight: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Create a new restriction

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          area: Specify the area name. It represents a region where restrictions can be applied.
              This is a custom field and it is recommended for the users to check with
              [NextBillion.ai](www.nextbillion.ai) support for the right value. Alternatively,
              users can invoke the _[Areas](#supported-areas)_ method to get a list of
              available areas for them.

          name: Specify a custom, descriptive name for the restriction.

          latlon: Use this parameter to decide the format for specifying the geofence coordinates.
              If true, then the coordinates of geofence can be specified as
              "latitude,longitude" format, otherwise they should be specified in
              "longitude,latitude" format.

          comment: Use this parameter to add any custom information about the restriction being
              created.

          direction: Represents the traffic direction on the segments to which the restriction will
              be applied.

          end_time: Provide a UNIX epoch timestamp in seconds, representing the time when the
              restriction should cease to be in-effect.

          geofence: An array of coordinates denoting the boundary of an area in which the
              restrictions are to be applied. The format in which coordinates should be listed
              is defined by the latlon field.

              Geofences can be used to create all restriction types, except for a turn type
              restriction. Please note that segments is not required when using geofence to
              create restrictions.

          height: Specify the maximum truck height, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          length: Specify the maximum truck length, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          mode: Provide the driving modes for which the restriction should be effective. If the
              value is an empty array or if it is not provided then the restriction would be
              applied for all modes.

          repeat_on: It represents the days and times when the restriction is in effect. Users can
              use this property to set recurring or one-time restrictions as per the
              [given format](https://wiki.openstreetmap.org/wiki/Key:opening_hours) for
              specifying the recurring schedule of the restriction.

              Please provided values as per the local time of the region where the restriction
              is being applied.

          segments: An array of objects to collect the details of the segments of a road on which
              the restriction has to be applied. Each object corresponds to a new segment.

              Please note that segments is mandatory for all restrtiction_type except turn.

          speed: Provide the the fixed speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is fixedspeed.

          speed_limit: Provide the the maximum speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is maxspeed.

          start_time: Provide a UNIX epoch timestamp in seconds, representing the start time for the
              restriction to be in-effect.

          tracks: Specify a sequence of coordinates (track) where the restriction is to be
              applied. The coordinates will be snapped to nearest road. Please note when using
              tracks, segments and turns are not required.

          turns: An array of objects to collect the details of the turns of a road on which the
              restriction has to be applied. Each object corresponds to a new turn.

              Please note that turns is mandatory for when restrtiction_type=turn.

          weight: Specify the maximum truck weight, in kilograms, that the restriction will allow.
              A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided for is truck restriction type.

          width: Specify the maximum truck width, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not restriction_type:
            raise ValueError(f"Expected a non-empty value for `restriction_type` but received {restriction_type!r}")
        return await self._post(
            f"/restrictions/{restriction_type}",
            body=await async_maybe_transform(
                {
                    "area": area,
                    "name": name,
                    "comment": comment,
                    "direction": direction,
                    "end_time": end_time,
                    "geofence": geofence,
                    "height": height,
                    "length": length,
                    "mode": mode,
                    "repeat_on": repeat_on,
                    "segments": segments,
                    "speed": speed,
                    "speed_limit": speed_limit,
                    "start_time": start_time,
                    "tracks": tracks,
                    "turns": turns,
                    "weight": weight,
                    "width": width,
                },
                restriction_create_params.RestrictionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "latlon": latlon,
                    },
                    restriction_create_params.RestrictionCreateParams,
                ),
            ),
            cast_to=RichGroupResponse,
        )

    async def retrieve(
        self,
        id: int,
        *,
        key: str,
        transform: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Get a restriction by id

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          transform: a internal parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/restrictions/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "transform": transform,
                    },
                    restriction_retrieve_params.RestrictionRetrieveParams,
                ),
            ),
            cast_to=RichGroupResponse,
        )

    async def update(
        self,
        id: int,
        *,
        key: str,
        area: str,
        name: str,
        latlon: bool | NotGiven = NOT_GIVEN,
        comment: str | NotGiven = NOT_GIVEN,
        direction: Literal["forward", "backward", "both"] | NotGiven = NOT_GIVEN,
        end_time: float | NotGiven = NOT_GIVEN,
        geofence: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        length: int | NotGiven = NOT_GIVEN,
        mode: List[Literal["0w", "2w", "3w", "4w", "6w"]] | NotGiven = NOT_GIVEN,
        repeat_on: str | NotGiven = NOT_GIVEN,
        segments: Iterable[restriction_update_params.Segment] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        speed_limit: float | NotGiven = NOT_GIVEN,
        start_time: float | NotGiven = NOT_GIVEN,
        tracks: Iterable[Iterable[float]] | NotGiven = NOT_GIVEN,
        turns: Iterable[restriction_update_params.Turn] | NotGiven = NOT_GIVEN,
        weight: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Update a restriction

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          area: Specify the area name. It represents a region where restrictions can be applied.
              This is a custom field and it is recommended for the users to check with
              [NextBillion.ai](www.nextbillion.ai) support for the right value. Alternatively,
              users can invoke the _[Areas](#supported-areas)_ method to get a list of
              available areas for them.

          name: Specify a custom, descriptive name for the restriction.

          latlon: Use this parameter to decide the format for specifying the geofence coordinates.
              If true, then the coordinates of geofence can be specified as
              "latitude,longitude" format, otherwise they should be specified in
              "longitude,latitude" format.

          comment: Use this parameter to add any custom information about the restriction being
              created.

          direction: Represents the traffic direction on the segments to which the restriction will
              be applied.

          end_time: Provide a UNIX epoch timestamp in seconds, representing the time when the
              restriction should cease to be in-effect.

          geofence: An array of coordinates denoting the boundary of an area in which the
              restrictions are to be applied. The format in which coordinates should be listed
              is defined by the latlon field.

              Geofences can be used to create all restriction types, except for a turn type
              restriction. Please note that segments is not required when using geofence to
              create restrictions.

          height: Specify the maximum truck height, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          length: Specify the maximum truck length, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          mode: Provide the driving modes for which the restriction should be effective. If the
              value is an empty array or if it is not provided then the restriction would be
              applied for all modes.

          repeat_on: It represents the days and times when the restriction is in effect. Users can
              use this property to set recurring or one-time restrictions as per the
              [given format](https://wiki.openstreetmap.org/wiki/Key:opening_hours) for
              specifying the recurring schedule of the restriction.

              Please provided values as per the local time of the region where the restriction
              is being applied.

          segments: An array of objects to collect the details of the segments of a road on which
              the restriction has to be applied. Each object corresponds to a new segment.

              Please note that segments is mandatory for all restrtiction_type except turn.

          speed: Provide the the fixed speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is fixedspeed.

          speed_limit: Provide the the maximum speed of the segment where the restriction needs to be
              applied. Please note that this parameter is mandatory when the restrictionType
              is maxspeed.

          start_time: Provide a UNIX epoch timestamp in seconds, representing the start time for the
              restriction to be in-effect.

          tracks: Specify a sequence of coordinates (track) where the restriction is to be
              applied. The coordinates will be snapped to nearest road. Please note when using
              tracks, segments and turns are not required.

          turns: An array of objects to collect the details of the turns of a road on which the
              restriction has to be applied. Each object corresponds to a new turn.

              Please note that turns is mandatory for when restrtiction_type=turn.

          weight: Specify the maximum truck weight, in kilograms, that the restriction will allow.
              A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided for is truck restriction type.

          width: Specify the maximum truck width, in centimeter, that will be allowed under the
              restriction. A value of 0 indicates no limit.

              Please note this parameter is effective only when restriction_type is truck. At
              least one of truck parameters - weight, height, width and truck - needs to be
              provided when restriction type is truck.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/restrictions/{id}",
            body=await async_maybe_transform(
                {
                    "area": area,
                    "name": name,
                    "comment": comment,
                    "direction": direction,
                    "end_time": end_time,
                    "geofence": geofence,
                    "height": height,
                    "length": length,
                    "mode": mode,
                    "repeat_on": repeat_on,
                    "segments": segments,
                    "speed": speed,
                    "speed_limit": speed_limit,
                    "start_time": start_time,
                    "tracks": tracks,
                    "turns": turns,
                    "weight": weight,
                    "width": width,
                },
                restriction_update_params.RestrictionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "latlon": latlon,
                    },
                    restriction_update_params.RestrictionUpdateParams,
                ),
            ),
            cast_to=RichGroupResponse,
        )

    async def list(
        self,
        *,
        area: str,
        key: str,
        limit: int,
        offset: int,
        mode: Literal["0w", "2w", "3w", "4w", "6w"] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
        | NotGiven = NOT_GIVEN,
        source: Literal["rrt", "pbf"] | NotGiven = NOT_GIVEN,
        state: Literal["enabled", "disabled", "deleted"] | NotGiven = NOT_GIVEN,
        status: Literal["active", "inactive"] | NotGiven = NOT_GIVEN,
        transform: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionListResponse:
        """Get the paginated list of restrictions

        Args:
          area: Specify the area name.

        It represents a region where restrictions can be applied.

              _The area it belongs to. See Area API_

          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          limit: The number of restrictions to be returned in the response. Please note that if
              the limit is set to a number more than the total number of available
              restrictions, then all restrictions would be returned together.

          offset: An integer value indicating the number of items in the collection that need to
              be skipped in the response. Please note that the offset starts from 0, so the
              first item returned in the result would be the item at (offset + 1) position in
              collection.

              Users can use offset along with limit to implement paginated result.

          mode: Specify the modes of travel that the restriction pertains to.

          name: The name of the restriction. This should be same as that provided while creating
              or updating the restriction.

          restriction_type: Specify the type of restrictions to fetch.

          source: It represents where it comes from, currently the possible values include "rrt",
              "xsm"

          state: This parameter is used to filter restrictions based on their state i.e. whether
              the restriction is currently enabled, disabled, or deleted. For example, users
              can retrieve a list of all the deleted restrictions by setting state=deleted.

          status: Restrictions can be active or inactive at a given time by virtue of their
              nature. For example, maximum speed limits can be active on the roads leading to
              schools during school hours and be inactive afterwards or certain road closure
              restrictions be active during holidays/concerts and be inactive otherwise.

              Use this parameter to filter the restrictions based on their status at the time
              of making the request i.e. whether they are in force or not.

          transform: a internal parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/restrictions/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "area": area,
                        "key": key,
                        "limit": limit,
                        "offset": offset,
                        "mode": mode,
                        "name": name,
                        "restriction_type": restriction_type,
                        "source": source,
                        "state": state,
                        "status": status,
                        "transform": transform,
                    },
                    restriction_list_params.RestrictionListParams,
                ),
            ),
            cast_to=RestrictionListResponse,
        )

    async def delete(
        self,
        id: int,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionDeleteResponse:
        """
        Delete a restriction by ID

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            f"/restrictions/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, restriction_delete_params.RestrictionDeleteParams),
            ),
            cast_to=RestrictionDeleteResponse,
        )

    async def list_by_bbox(
        self,
        *,
        key: str,
        max_lat: float,
        max_lon: float,
        min_lat: float,
        min_lon: float,
        mode: List[Literal["0w", "2w", "3w", "4w", "6w"]] | NotGiven = NOT_GIVEN,
        restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
        | NotGiven = NOT_GIVEN,
        source: Literal["rrt", "pbf"] | NotGiven = NOT_GIVEN,
        state: Literal["enabled", "disabled", "deleted"] | NotGiven = NOT_GIVEN,
        status: Literal["active", "inactive"] | NotGiven = NOT_GIVEN,
        transform: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RestrictionListByBboxResponse:
        """
        Get restrictions by bbox

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          max_lat: Specifies the maximum latitude value for the bounding box.

          max_lon: Specifies the maximum longitude value for the bounding box.

          min_lat: Specifies the minimum latitude value for the bounding box.

          min_lon: Specifies the minimum longitude value for the bounding box.

          mode: Specify the modes of travel that the restriction pertains to.

          restriction_type: Specify the type of restrictions to fetch.

          source: This parameter represents where the restriction comes from and cannot be
              modified by clients sending requests to the API endpoint.

              For example, an API endpoint that returns a list of restrictions could include
              the source parameter to indicate where each item comes from. This parameter can
              be useful for filtering, sorting, or grouping the results based on their source.

          state: This parameter is used to filter restrictions based on their state i.e. whether
              the restriction is currently enabled, disabled, or deleted. For example, users
              can retrieve a list of all the deleted restrictions by setting state=deleted.

          status: Restrictions can be active or inactive at a given time by virtue of their
              nature. For example, maximum speed limits can be active on the roads leading to
              schools during school hours and be inactive afterwards or certain road closure
              restrictions be active during holidays/concerts and be inactive otherwise.

              Use this parameter to filter the restrictions based on their status at the time
              of making the request i.e. whether they are in force or not.

          transform: This is internal parameter with a default value as false.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/restrictions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "max_lat": max_lat,
                        "max_lon": max_lon,
                        "min_lat": min_lat,
                        "min_lon": min_lon,
                        "mode": mode,
                        "restriction_type": restriction_type,
                        "source": source,
                        "state": state,
                        "status": status,
                        "transform": transform,
                    },
                    restriction_list_by_bbox_params.RestrictionListByBboxParams,
                ),
            ),
            cast_to=RestrictionListByBboxResponse,
        )

    async def set_state(
        self,
        id: int,
        *,
        key: str,
        state: Literal["enabled", "disabled", "deleted"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RichGroupResponse:
        """
        Set the state of a restriction by ID

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          state: Use this field to specify the new state of the restriction. Please note that
              this method cannot update the state of restrictions that are currently in
              'deleted' state.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            f"/restrictions/{id}/state",
            body=await async_maybe_transform({"state": state}, restriction_set_state_params.RestrictionSetStateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, restriction_set_state_params.RestrictionSetStateParams),
            ),
            cast_to=RichGroupResponse,
        )


class RestrictionsResourceWithRawResponse:
    def __init__(self, restrictions: RestrictionsResource) -> None:
        self._restrictions = restrictions

        self.create = to_raw_response_wrapper(
            restrictions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            restrictions.retrieve,
        )
        self.update = to_raw_response_wrapper(
            restrictions.update,
        )
        self.list = to_raw_response_wrapper(
            restrictions.list,
        )
        self.delete = to_raw_response_wrapper(
            restrictions.delete,
        )
        self.list_by_bbox = to_raw_response_wrapper(
            restrictions.list_by_bbox,
        )
        self.set_state = to_raw_response_wrapper(
            restrictions.set_state,
        )


class AsyncRestrictionsResourceWithRawResponse:
    def __init__(self, restrictions: AsyncRestrictionsResource) -> None:
        self._restrictions = restrictions

        self.create = async_to_raw_response_wrapper(
            restrictions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            restrictions.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            restrictions.update,
        )
        self.list = async_to_raw_response_wrapper(
            restrictions.list,
        )
        self.delete = async_to_raw_response_wrapper(
            restrictions.delete,
        )
        self.list_by_bbox = async_to_raw_response_wrapper(
            restrictions.list_by_bbox,
        )
        self.set_state = async_to_raw_response_wrapper(
            restrictions.set_state,
        )


class RestrictionsResourceWithStreamingResponse:
    def __init__(self, restrictions: RestrictionsResource) -> None:
        self._restrictions = restrictions

        self.create = to_streamed_response_wrapper(
            restrictions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            restrictions.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            restrictions.update,
        )
        self.list = to_streamed_response_wrapper(
            restrictions.list,
        )
        self.delete = to_streamed_response_wrapper(
            restrictions.delete,
        )
        self.list_by_bbox = to_streamed_response_wrapper(
            restrictions.list_by_bbox,
        )
        self.set_state = to_streamed_response_wrapper(
            restrictions.set_state,
        )


class AsyncRestrictionsResourceWithStreamingResponse:
    def __init__(self, restrictions: AsyncRestrictionsResource) -> None:
        self._restrictions = restrictions

        self.create = async_to_streamed_response_wrapper(
            restrictions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            restrictions.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            restrictions.update,
        )
        self.list = async_to_streamed_response_wrapper(
            restrictions.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            restrictions.delete,
        )
        self.list_by_bbox = async_to_streamed_response_wrapper(
            restrictions.list_by_bbox,
        )
        self.set_state = async_to_streamed_response_wrapper(
            restrictions.set_state,
        )
