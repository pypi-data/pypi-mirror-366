# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .batch import (
    BatchResource,
    AsyncBatchResource,
    BatchResourceWithRawResponse,
    AsyncBatchResourceWithRawResponse,
    BatchResourceWithStreamingResponse,
    AsyncBatchResourceWithStreamingResponse,
)
from ...types import (
    geofence_list_params,
    geofence_create_params,
    geofence_delete_params,
    geofence_update_params,
    geofence_contains_params,
    geofence_retrieve_params,
)
from .console import (
    ConsoleResource,
    AsyncConsoleResource,
    ConsoleResourceWithRawResponse,
    AsyncConsoleResourceWithRawResponse,
    ConsoleResourceWithStreamingResponse,
    AsyncConsoleResourceWithStreamingResponse,
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
from ..._base_client import make_request_options
from ...types.skynet.simple_resp import SimpleResp
from ...types.geofence_list_response import GeofenceListResponse
from ...types.geofence_create_response import GeofenceCreateResponse
from ...types.geofence_contains_response import GeofenceContainsResponse
from ...types.geofence_retrieve_response import GeofenceRetrieveResponse

__all__ = ["GeofenceResource", "AsyncGeofenceResource"]


class GeofenceResource(SyncAPIResource):
    @cached_property
    def console(self) -> ConsoleResource:
        return ConsoleResource(self._client)

    @cached_property
    def batch(self) -> BatchResource:
        return BatchResource(self._client)

    @cached_property
    def with_raw_response(self) -> GeofenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return GeofenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GeofenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return GeofenceResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        type: Literal["circle", "polygon", "isochrone"],
        circle: geofence_create_params.Circle | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        isochrone: geofence_create_params.Isochrone | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        polygon: geofence_create_params.Polygon | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeofenceCreateResponse:
        """
        Create a geofence

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          type: Specify the type of the geofence that is being created.

          circle: Provide the details to create a circular geofence. Please note that this object
              is mandatory when type is circle. When the type is not circle, the properties of
              this object will be ignored while creating the geofence.

          custom_id: Set an unique ID for the new geofence. If not provided, an ID will be
              automatically generated in UUID format. A valid custom*id can contain letters,
              numbers, "-", & "*" only.

              Please note that the ID of a geofence can not be changed once it is created.

          isochrone: Provide the details to create an isochrone based geofence. Use this object when
              type is isochrone. When the type is not isochrone, the properties of this object
              will be ignored while creating the geofence.

          meta_data: Metadata of the geofence. Use this field to define custom attributes that
              provide more context and information about the geofence being created like
              country, group ID etc.

              The data being added should be in valid JSON object format (i.e. key and value
              pairs). Max size allowed for the object is 65kb.

          name: Name of the geofence. Use this field to assign a meaningful, custom name to the
              geofence being created.

          polygon: Provide the details to create a custom polygon type of geofence. Please note
              that this object is mandatory when type is polygon. When the type is not
              polygon, the properties of this object will be ignored while creating the
              geofence.

              Self-intersecting polygons or polygons containing other polygons are invalid and
              will be removed while processing the request.

              Area of the polygon should be less than 2000 km<sup>2</sup>.

          tags: An array of strings to associate multiple tags to the geofence. tags can be used
              to search or filter geofences (using Get Geofence List method).

              Create valid tags using a string consisting of alphanumeric characters (A-Z,
              a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/geofence",
            body=maybe_transform(
                {
                    "type": type,
                    "circle": circle,
                    "custom_id": custom_id,
                    "isochrone": isochrone,
                    "meta_data": meta_data,
                    "name": name,
                    "polygon": polygon,
                    "tags": tags,
                },
                geofence_create_params.GeofenceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, geofence_create_params.GeofenceCreateParams),
            ),
            cast_to=GeofenceCreateResponse,
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
    ) -> GeofenceRetrieveResponse:
        """
        Get a Geofence

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
            f"/geofence/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, geofence_retrieve_params.GeofenceRetrieveParams),
            ),
            cast_to=GeofenceRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        key: str,
        circle: geofence_update_params.Circle | NotGiven = NOT_GIVEN,
        isochrone: geofence_update_params.Isochrone | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        polygon: geofence_update_params.Polygon | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        type: Literal["circle", "polygon", "isochrone"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Update a Geofence

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          circle: Use this object to update details of a circular geofence. Please note that this
              object is mandatory only when type is circle. When the type is not circle, the
              properties of this object will be ignored while creating the geofence.

          isochrone: Use this object to update details of an isochrone based geofence. Please note
              that this object is mandatory only when type is isochrone. When the type is not
              isochrone, the properties of this object will be ignored while creating the
              geofence.

          meta_data: Updated the meta_data associated with a geofence. Use this field to define
              custom attributes that provide more context and information about the geofence
              being updated like country, group ID etc.

              The data being added should be in valid JSON object format (i.e. key and value
              pairs). Max size allowed for the object is 65kb.

          name: Use this parameter to update the name of a geofence. Users can assign meaningful
              custom names to their geofences.

          polygon: Use this object to update details of a custom polygon geofence. Please note that
              this object is mandatory only when type is polygon. When the type is not
              polygon, the properties of this object will be ignored while creating the
              geofence.

              Self-intersecting polygons or polygons containing other polygons are invalid and
              will be removed while processing the request.

              Area of the polygon should be less than 2000 km<sup>2</sup>.

          tags: Use this parameter to add/modify one or multiple tags of a geofence. tags can be
              used to search or filter geofences (using Get Geofence List method).

              Valid values for updating tags consist of alphanumeric characters (A-Z, a-z,
              0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          type: Use this parameter to update the type of a geofence. Please note that you will
              need to provide required details for creating a geofence of the new type. Check
              other parameters of this method to know more.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/geofence/{id}",
            body=maybe_transform(
                {
                    "circle": circle,
                    "isochrone": isochrone,
                    "meta_data": meta_data,
                    "name": name,
                    "polygon": polygon,
                    "tags": tags,
                    "type": type,
                },
                geofence_update_params.GeofenceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, geofence_update_params.GeofenceUpdateParams),
            ),
            cast_to=SimpleResp,
        )

    def list(
        self,
        *,
        key: str,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        tags: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeofenceListResponse:
        """
        Get Geofence List

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          tags: Comma (,) separated list of tags which will be used to filter the geofences.

              Please note only the geofences which have all the tags added to this parameter
              will be included in the result. This parameter can accept a string with a
              maximum length of 256 characters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/geofence/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "pn": pn,
                        "ps": ps,
                        "tags": tags,
                    },
                    geofence_list_params.GeofenceListParams,
                ),
            ),
            cast_to=GeofenceListResponse,
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
        Delete a Geofence

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
            f"/geofence/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, geofence_delete_params.GeofenceDeleteParams),
            ),
            cast_to=SimpleResp,
        )

    def contains(
        self,
        *,
        key: str,
        locations: str,
        geofences: str | NotGiven = NOT_GIVEN,
        verbose: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeofenceContainsResponse:
        """
        Geofence Contains

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          locations: Pipe (|) separated coordinates, in [latitude,longitude] format, of the locations
              to be searched against the geofences.

          geofences: A , separated list geofence IDs against which the locations will be searched. If
              not provided, then the 'locations' will be searched against all your existing
              geofences.

              Maximum length of the string can be 256 characters.

          verbose: When true, an array with detailed information of geofences is returned. When
              false, an array containing only the IDs of the geofences is returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/geofence/contain",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "locations": locations,
                        "geofences": geofences,
                        "verbose": verbose,
                    },
                    geofence_contains_params.GeofenceContainsParams,
                ),
            ),
            cast_to=GeofenceContainsResponse,
        )


class AsyncGeofenceResource(AsyncAPIResource):
    @cached_property
    def console(self) -> AsyncConsoleResource:
        return AsyncConsoleResource(self._client)

    @cached_property
    def batch(self) -> AsyncBatchResource:
        return AsyncBatchResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncGeofenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGeofenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGeofenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncGeofenceResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        type: Literal["circle", "polygon", "isochrone"],
        circle: geofence_create_params.Circle | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        isochrone: geofence_create_params.Isochrone | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        polygon: geofence_create_params.Polygon | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeofenceCreateResponse:
        """
        Create a geofence

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          type: Specify the type of the geofence that is being created.

          circle: Provide the details to create a circular geofence. Please note that this object
              is mandatory when type is circle. When the type is not circle, the properties of
              this object will be ignored while creating the geofence.

          custom_id: Set an unique ID for the new geofence. If not provided, an ID will be
              automatically generated in UUID format. A valid custom*id can contain letters,
              numbers, "-", & "*" only.

              Please note that the ID of a geofence can not be changed once it is created.

          isochrone: Provide the details to create an isochrone based geofence. Use this object when
              type is isochrone. When the type is not isochrone, the properties of this object
              will be ignored while creating the geofence.

          meta_data: Metadata of the geofence. Use this field to define custom attributes that
              provide more context and information about the geofence being created like
              country, group ID etc.

              The data being added should be in valid JSON object format (i.e. key and value
              pairs). Max size allowed for the object is 65kb.

          name: Name of the geofence. Use this field to assign a meaningful, custom name to the
              geofence being created.

          polygon: Provide the details to create a custom polygon type of geofence. Please note
              that this object is mandatory when type is polygon. When the type is not
              polygon, the properties of this object will be ignored while creating the
              geofence.

              Self-intersecting polygons or polygons containing other polygons are invalid and
              will be removed while processing the request.

              Area of the polygon should be less than 2000 km<sup>2</sup>.

          tags: An array of strings to associate multiple tags to the geofence. tags can be used
              to search or filter geofences (using Get Geofence List method).

              Create valid tags using a string consisting of alphanumeric characters (A-Z,
              a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/geofence",
            body=await async_maybe_transform(
                {
                    "type": type,
                    "circle": circle,
                    "custom_id": custom_id,
                    "isochrone": isochrone,
                    "meta_data": meta_data,
                    "name": name,
                    "polygon": polygon,
                    "tags": tags,
                },
                geofence_create_params.GeofenceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, geofence_create_params.GeofenceCreateParams),
            ),
            cast_to=GeofenceCreateResponse,
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
    ) -> GeofenceRetrieveResponse:
        """
        Get a Geofence

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
            f"/geofence/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, geofence_retrieve_params.GeofenceRetrieveParams),
            ),
            cast_to=GeofenceRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        key: str,
        circle: geofence_update_params.Circle | NotGiven = NOT_GIVEN,
        isochrone: geofence_update_params.Isochrone | NotGiven = NOT_GIVEN,
        meta_data: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        polygon: geofence_update_params.Polygon | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        type: Literal["circle", "polygon", "isochrone"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Update a Geofence

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          circle: Use this object to update details of a circular geofence. Please note that this
              object is mandatory only when type is circle. When the type is not circle, the
              properties of this object will be ignored while creating the geofence.

          isochrone: Use this object to update details of an isochrone based geofence. Please note
              that this object is mandatory only when type is isochrone. When the type is not
              isochrone, the properties of this object will be ignored while creating the
              geofence.

          meta_data: Updated the meta_data associated with a geofence. Use this field to define
              custom attributes that provide more context and information about the geofence
              being updated like country, group ID etc.

              The data being added should be in valid JSON object format (i.e. key and value
              pairs). Max size allowed for the object is 65kb.

          name: Use this parameter to update the name of a geofence. Users can assign meaningful
              custom names to their geofences.

          polygon: Use this object to update details of a custom polygon geofence. Please note that
              this object is mandatory only when type is polygon. When the type is not
              polygon, the properties of this object will be ignored while creating the
              geofence.

              Self-intersecting polygons or polygons containing other polygons are invalid and
              will be removed while processing the request.

              Area of the polygon should be less than 2000 km<sup>2</sup>.

          tags: Use this parameter to add/modify one or multiple tags of a geofence. tags can be
              used to search or filter geofences (using Get Geofence List method).

              Valid values for updating tags consist of alphanumeric characters (A-Z, a-z,
              0-9) along with the underscore ('\\__') and hyphen ('-') symbols.

          type: Use this parameter to update the type of a geofence. Please note that you will
              need to provide required details for creating a geofence of the new type. Check
              other parameters of this method to know more.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/geofence/{id}",
            body=await async_maybe_transform(
                {
                    "circle": circle,
                    "isochrone": isochrone,
                    "meta_data": meta_data,
                    "name": name,
                    "polygon": polygon,
                    "tags": tags,
                    "type": type,
                },
                geofence_update_params.GeofenceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, geofence_update_params.GeofenceUpdateParams),
            ),
            cast_to=SimpleResp,
        )

    async def list(
        self,
        *,
        key: str,
        pn: int | NotGiven = NOT_GIVEN,
        ps: int | NotGiven = NOT_GIVEN,
        tags: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeofenceListResponse:
        """
        Get Geofence List

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          pn: Denotes page number. Use this along with the ps parameter to implement
              pagination for your searched results. This parameter does not have a maximum
              limit but would return an empty response in case a higher value is provided when
              the result-set itself is smaller.

          ps: Denotes number of search results per page. Use this along with the pn parameter
              to implement pagination for your searched results.

          tags: Comma (,) separated list of tags which will be used to filter the geofences.

              Please note only the geofences which have all the tags added to this parameter
              will be included in the result. This parameter can accept a string with a
              maximum length of 256 characters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/geofence/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "pn": pn,
                        "ps": ps,
                        "tags": tags,
                    },
                    geofence_list_params.GeofenceListParams,
                ),
            ),
            cast_to=GeofenceListResponse,
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
        Delete a Geofence

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
            f"/geofence/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, geofence_delete_params.GeofenceDeleteParams),
            ),
            cast_to=SimpleResp,
        )

    async def contains(
        self,
        *,
        key: str,
        locations: str,
        geofences: str | NotGiven = NOT_GIVEN,
        verbose: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeofenceContainsResponse:
        """
        Geofence Contains

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          locations: Pipe (|) separated coordinates, in [latitude,longitude] format, of the locations
              to be searched against the geofences.

          geofences: A , separated list geofence IDs against which the locations will be searched. If
              not provided, then the 'locations' will be searched against all your existing
              geofences.

              Maximum length of the string can be 256 characters.

          verbose: When true, an array with detailed information of geofences is returned. When
              false, an array containing only the IDs of the geofences is returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/geofence/contain",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "locations": locations,
                        "geofences": geofences,
                        "verbose": verbose,
                    },
                    geofence_contains_params.GeofenceContainsParams,
                ),
            ),
            cast_to=GeofenceContainsResponse,
        )


class GeofenceResourceWithRawResponse:
    def __init__(self, geofence: GeofenceResource) -> None:
        self._geofence = geofence

        self.create = to_raw_response_wrapper(
            geofence.create,
        )
        self.retrieve = to_raw_response_wrapper(
            geofence.retrieve,
        )
        self.update = to_raw_response_wrapper(
            geofence.update,
        )
        self.list = to_raw_response_wrapper(
            geofence.list,
        )
        self.delete = to_raw_response_wrapper(
            geofence.delete,
        )
        self.contains = to_raw_response_wrapper(
            geofence.contains,
        )

    @cached_property
    def console(self) -> ConsoleResourceWithRawResponse:
        return ConsoleResourceWithRawResponse(self._geofence.console)

    @cached_property
    def batch(self) -> BatchResourceWithRawResponse:
        return BatchResourceWithRawResponse(self._geofence.batch)


class AsyncGeofenceResourceWithRawResponse:
    def __init__(self, geofence: AsyncGeofenceResource) -> None:
        self._geofence = geofence

        self.create = async_to_raw_response_wrapper(
            geofence.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            geofence.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            geofence.update,
        )
        self.list = async_to_raw_response_wrapper(
            geofence.list,
        )
        self.delete = async_to_raw_response_wrapper(
            geofence.delete,
        )
        self.contains = async_to_raw_response_wrapper(
            geofence.contains,
        )

    @cached_property
    def console(self) -> AsyncConsoleResourceWithRawResponse:
        return AsyncConsoleResourceWithRawResponse(self._geofence.console)

    @cached_property
    def batch(self) -> AsyncBatchResourceWithRawResponse:
        return AsyncBatchResourceWithRawResponse(self._geofence.batch)


class GeofenceResourceWithStreamingResponse:
    def __init__(self, geofence: GeofenceResource) -> None:
        self._geofence = geofence

        self.create = to_streamed_response_wrapper(
            geofence.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            geofence.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            geofence.update,
        )
        self.list = to_streamed_response_wrapper(
            geofence.list,
        )
        self.delete = to_streamed_response_wrapper(
            geofence.delete,
        )
        self.contains = to_streamed_response_wrapper(
            geofence.contains,
        )

    @cached_property
    def console(self) -> ConsoleResourceWithStreamingResponse:
        return ConsoleResourceWithStreamingResponse(self._geofence.console)

    @cached_property
    def batch(self) -> BatchResourceWithStreamingResponse:
        return BatchResourceWithStreamingResponse(self._geofence.batch)


class AsyncGeofenceResourceWithStreamingResponse:
    def __init__(self, geofence: AsyncGeofenceResource) -> None:
        self._geofence = geofence

        self.create = async_to_streamed_response_wrapper(
            geofence.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            geofence.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            geofence.update,
        )
        self.list = async_to_streamed_response_wrapper(
            geofence.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            geofence.delete,
        )
        self.contains = async_to_streamed_response_wrapper(
            geofence.contains,
        )

    @cached_property
    def console(self) -> AsyncConsoleResourceWithStreamingResponse:
        return AsyncConsoleResourceWithStreamingResponse(self._geofence.console)

    @cached_property
    def batch(self) -> AsyncBatchResourceWithStreamingResponse:
        return AsyncBatchResourceWithStreamingResponse(self._geofence.batch)
