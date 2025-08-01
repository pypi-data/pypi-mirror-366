# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .event import (
    EventResource,
    AsyncEventResource,
    EventResourceWithRawResponse,
    AsyncEventResourceWithRawResponse,
    EventResourceWithStreamingResponse,
    AsyncEventResourceWithStreamingResponse,
)
from .location import (
    LocationResource,
    AsyncLocationResource,
    LocationResourceWithRawResponse,
    AsyncLocationResourceWithRawResponse,
    LocationResourceWithStreamingResponse,
    AsyncLocationResourceWithStreamingResponse,
)
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
from ....types.skynet import (
    asset_bind_params,
    asset_list_params,
    asset_track_params,
    asset_create_params,
    asset_delete_params,
    asset_update_params,
    asset_retrieve_params,
    asset_update_attributes_params,
)
from ....types.skynet.simple_resp import SimpleResp
from ....types.skynet.meta_data_param import MetaDataParam
from ....types.skynet.asset_list_response import AssetListResponse
from ....types.skynet.asset_create_response import AssetCreateResponse
from ....types.skynet.asset_retrieve_response import AssetRetrieveResponse

__all__ = ["AssetResource", "AsyncAssetResource"]


class AssetResource(SyncAPIResource):
    @cached_property
    def event(self) -> EventResource:
        return EventResource(self._client)

    @cached_property
    def location(self) -> LocationResource:
        return LocationResource(self._client)

    @cached_property
    def with_raw_response(self) -> AssetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AssetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AssetResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: MetaDataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetCreateResponse:
        """
        Create an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          attributes: attributes can be used to store custom information about an asset in key:value
              format. Use attributes to add any useful information or context to your assets
              like the vehicle type, shift timing etc. Moreover, these attributes can be used
              to filter assets in **Search**, **Monitor**, and _Get Asset List_ queries.

              Please note that the maximum number of key:value pairs that can be added to an
              attributes object is 100. Also, the overall size of attributes object should not
              exceed 65kb.

          custom_id: Set a unique ID for the new asset. If not provided, an ID will be automatically
              generated in UUID format. A valid custom*id can contain letters, numbers, "-", &
              "*" only.

              Please note that the ID of an asset can not be changed once it is created.

          description: Description for the asset.

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Name of the asset. Use this field to assign a meaningful, custom name to the
              asset being created.

          tags: **This parameter will be deprecated soon! Please use the attributes parameter to
              add labels or markers for the asset.**

              Tags of the asset. tags can be used for filtering assets in operations like _Get
              Asset List_ and asset **Search** methods. They can also be used for monitoring
              of assets using the **Monitor** methods after linking tags and asset.

              Valid tags are strings consisting of alphanumeric characters (A-Z, a-z, 0-9)
              along with the underscore ('\\__') and hyphen ('-') symbols.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/asset",
            body=maybe_transform(
                {
                    "attributes": attributes,
                    "custom_id": custom_id,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "tags": tags,
                },
                asset_create_params.AssetCreateParams,
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
                    asset_create_params.AssetCreateParams,
                ),
            ),
            cast_to=AssetCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetRetrieveResponse:
        """
        Get an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/skynet/asset/{id}",
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
                    asset_retrieve_params.AssetRetrieveParams,
                ),
            ),
            cast_to=AssetRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: MetaDataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Update an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          attributes: Use this param to update the attributes of an asset in key:value format. Users
              can maintain any useful information or context about the assets by utilising
              this parameter.

              Please be careful when using this parameter while updating an asset as the new
              attributes object provided will completely overwrite the old attributes object.
              Use the _Update Asset Attributes_ method to add new or modify existing
              attributes.

              Another point to note is that the overall size of the attributes object cannot
              exceed 65kb and the maximum number of key:value pairs that can be added to this
              object is 100.

          description: Use this param to update the description of an asset.

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Use this param to update the name of an asset. Users can assign meaningful
              custom names to their assets.

          tags: **This parameter will be deprecated soon! Please use the attributes parameter to
              add labels or markers for the asset.**

              Use this param to update the tags of an asset. tags can be used to filter asset
              in _Get Asset List_, **Search** and **Monitor** queries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/skynet/asset/{id}",
            body=maybe_transform(
                {
                    "attributes": attributes,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "tags": tags,
                },
                asset_update_params.AssetUpdateParams,
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
                    asset_update_params.AssetUpdateParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    def list(
        self,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        include_all_of_attributes: str | NotGiven = NOT_GIVEN,
        include_any_of_attributes: str | NotGiven = NOT_GIVEN,
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
    ) -> AssetListResponse:
        """
        Get Asset List

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          include_all_of_attributes: Use this parameter to filter the assets by their attributes. Only the assets
              having all the attributes added to this parameter, will be returned in the
              response. Multiple attributes can be separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_any_of_attributes parameter.

          include_any_of_attributes: Use this parameter to filter the assets by their attributes. Assets having at
              least one of the attributes added to this parameter, will be returned in the
              response. Multiple attributes can be separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_all_of_attributes parameter.

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

          tags: **This parameter will be deprecated soon! Please use the
              include_all_of_attributes or include_any_of_attributes parameters to provide
              labels or markers for the assets to be retrieved.**

              tags can be used to filter the assets. Only those assets which have all the tags
              provided, will be included in the result. In case multiple tags need to be
              specified, use , to separate them.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/skynet/asset/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "include_all_of_attributes": include_all_of_attributes,
                        "include_any_of_attributes": include_any_of_attributes,
                        "pn": pn,
                        "ps": ps,
                        "sort": sort,
                        "tags": tags,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            cast_to=AssetListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Delete an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/skynet/asset/{id}",
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
                    asset_delete_params.AssetDeleteParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    def bind(
        self,
        id: str,
        *,
        key: str,
        device_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Bind asset to device

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          device_id: Device ID to be linked to the asset identified by id.

              Please note that the device needs to be linked to an asset before using it in
              the _Upload locations of an Asset_ method for sending GPS information about the
              asset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/skynet/asset/{id}/bind",
            body=maybe_transform({"device_id": device_id}, asset_bind_params.AssetBindParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, asset_bind_params.AssetBindParams),
            ),
            cast_to=SimpleResp,
        )

    def track(
        self,
        id: str,
        *,
        key: str,
        device_id: str,
        locations: asset_track_params.Locations,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Upload track info

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          device_id: ID of the device used to upload the tracking information of the asset.

              Please note that the device_id used here must already be linked to the asset.
              Use the _Bind Device to Asset_ method to link a device with your asset.

          locations: An array of objects to collect the location tracking information for an asset.
              Each object must correspond to details of only one location.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/skynet/asset/{id}/track",
            body=maybe_transform(
                {
                    "device_id": device_id,
                    "locations": locations,
                },
                asset_track_params.AssetTrackParams,
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
                    asset_track_params.AssetTrackParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    def update_attributes(
        self,
        id: str,
        *,
        key: str,
        attributes: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """Update asset attributes.

        (add)

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          attributes: attributes can be used to add any useful information or context to your assets
              like the vehicle type, shift timing etc. These attributes can also be used to
              filter assets in **Search**, **Monitor**, and _Get Asset List_ queries.

              Provide the attributes to be added or updated, in key:value format. If an
              existing key is provided in the input, then the value will be modified as per
              the input value. If a new key is provided in the input, then the key would be
              added to the existing set. The contents of any value field are neither altered
              nor removed unless specifically referred to by its key in the input request.

              Please note that the maximum number of key:value pairs that can be added to an
              attributes object is 100. Also, the overall size of attributes object should not
              exceed 65kb.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/skynet/asset/{id}/attributes",
            body=maybe_transform(
                {"attributes": attributes}, asset_update_attributes_params.AssetUpdateAttributesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, asset_update_attributes_params.AssetUpdateAttributesParams),
            ),
            cast_to=SimpleResp,
        )


class AsyncAssetResource(AsyncAPIResource):
    @cached_property
    def event(self) -> AsyncEventResource:
        return AsyncEventResource(self._client)

    @cached_property
    def location(self) -> AsyncLocationResource:
        return AsyncLocationResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAssetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncAssetResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: MetaDataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetCreateResponse:
        """
        Create an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          attributes: attributes can be used to store custom information about an asset in key:value
              format. Use attributes to add any useful information or context to your assets
              like the vehicle type, shift timing etc. Moreover, these attributes can be used
              to filter assets in **Search**, **Monitor**, and _Get Asset List_ queries.

              Please note that the maximum number of key:value pairs that can be added to an
              attributes object is 100. Also, the overall size of attributes object should not
              exceed 65kb.

          custom_id: Set a unique ID for the new asset. If not provided, an ID will be automatically
              generated in UUID format. A valid custom*id can contain letters, numbers, "-", &
              "*" only.

              Please note that the ID of an asset can not be changed once it is created.

          description: Description for the asset.

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Name of the asset. Use this field to assign a meaningful, custom name to the
              asset being created.

          tags: **This parameter will be deprecated soon! Please use the attributes parameter to
              add labels or markers for the asset.**

              Tags of the asset. tags can be used for filtering assets in operations like _Get
              Asset List_ and asset **Search** methods. They can also be used for monitoring
              of assets using the **Monitor** methods after linking tags and asset.

              Valid tags are strings consisting of alphanumeric characters (A-Z, a-z, 0-9)
              along with the underscore ('\\__') and hyphen ('-') symbols.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/asset",
            body=await async_maybe_transform(
                {
                    "attributes": attributes,
                    "custom_id": custom_id,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "tags": tags,
                },
                asset_create_params.AssetCreateParams,
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
                    asset_create_params.AssetCreateParams,
                ),
            ),
            cast_to=AssetCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetRetrieveResponse:
        """
        Get an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/skynet/asset/{id}",
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
                    asset_retrieve_params.AssetRetrieveParams,
                ),
            ),
            cast_to=AssetRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        attributes: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        meta_data: MetaDataParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Update an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          attributes: Use this param to update the attributes of an asset in key:value format. Users
              can maintain any useful information or context about the assets by utilising
              this parameter.

              Please be careful when using this parameter while updating an asset as the new
              attributes object provided will completely overwrite the old attributes object.
              Use the _Update Asset Attributes_ method to add new or modify existing
              attributes.

              Another point to note is that the overall size of the attributes object cannot
              exceed 65kb and the maximum number of key:value pairs that can be added to this
              object is 100.

          description: Use this param to update the description of an asset.

          meta_data: Any valid json object data. Can be used to save customized data. Max size is
              65kb.

          name: Use this param to update the name of an asset. Users can assign meaningful
              custom names to their assets.

          tags: **This parameter will be deprecated soon! Please use the attributes parameter to
              add labels or markers for the asset.**

              Use this param to update the tags of an asset. tags can be used to filter asset
              in _Get Asset List_, **Search** and **Monitor** queries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/skynet/asset/{id}",
            body=await async_maybe_transform(
                {
                    "attributes": attributes,
                    "description": description,
                    "meta_data": meta_data,
                    "name": name,
                    "tags": tags,
                },
                asset_update_params.AssetUpdateParams,
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
                    asset_update_params.AssetUpdateParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    async def list(
        self,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        include_all_of_attributes: str | NotGiven = NOT_GIVEN,
        include_any_of_attributes: str | NotGiven = NOT_GIVEN,
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
    ) -> AssetListResponse:
        """
        Get Asset List

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          include_all_of_attributes: Use this parameter to filter the assets by their attributes. Only the assets
              having all the attributes added to this parameter, will be returned in the
              response. Multiple attributes can be separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_any_of_attributes parameter.

          include_any_of_attributes: Use this parameter to filter the assets by their attributes. Assets having at
              least one of the attributes added to this parameter, will be returned in the
              response. Multiple attributes can be separated using pipes (|).

              Please note the attributes are case sensitive. Also, this parameter can not be
              used in conjunction with include_all_of_attributes parameter.

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

          tags: **This parameter will be deprecated soon! Please use the
              include_all_of_attributes or include_any_of_attributes parameters to provide
              labels or markers for the assets to be retrieved.**

              tags can be used to filter the assets. Only those assets which have all the tags
              provided, will be included in the result. In case multiple tags need to be
              specified, use , to separate them.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/skynet/asset/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "cluster": cluster,
                        "include_all_of_attributes": include_all_of_attributes,
                        "include_any_of_attributes": include_any_of_attributes,
                        "pn": pn,
                        "ps": ps,
                        "sort": sort,
                        "tags": tags,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            cast_to=AssetListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        key: str,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Delete an Asset

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/skynet/asset/{id}",
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
                    asset_delete_params.AssetDeleteParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    async def bind(
        self,
        id: str,
        *,
        key: str,
        device_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Bind asset to device

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          device_id: Device ID to be linked to the asset identified by id.

              Please note that the device needs to be linked to an asset before using it in
              the _Upload locations of an Asset_ method for sending GPS information about the
              asset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/skynet/asset/{id}/bind",
            body=await async_maybe_transform({"device_id": device_id}, asset_bind_params.AssetBindParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, asset_bind_params.AssetBindParams),
            ),
            cast_to=SimpleResp,
        )

    async def track(
        self,
        id: str,
        *,
        key: str,
        device_id: str,
        locations: asset_track_params.Locations,
        cluster: Literal["america"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Upload track info

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          device_id: ID of the device used to upload the tracking information of the asset.

              Please note that the device_id used here must already be linked to the asset.
              Use the _Bind Device to Asset_ method to link a device with your asset.

          locations: An array of objects to collect the location tracking information for an asset.
              Each object must correspond to details of only one location.

          cluster: the cluster of the region you want to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/skynet/asset/{id}/track",
            body=await async_maybe_transform(
                {
                    "device_id": device_id,
                    "locations": locations,
                },
                asset_track_params.AssetTrackParams,
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
                    asset_track_params.AssetTrackParams,
                ),
            ),
            cast_to=SimpleResp,
        )

    async def update_attributes(
        self,
        id: str,
        *,
        key: str,
        attributes: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """Update asset attributes.

        (add)

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          attributes: attributes can be used to add any useful information or context to your assets
              like the vehicle type, shift timing etc. These attributes can also be used to
              filter assets in **Search**, **Monitor**, and _Get Asset List_ queries.

              Provide the attributes to be added or updated, in key:value format. If an
              existing key is provided in the input, then the value will be modified as per
              the input value. If a new key is provided in the input, then the key would be
              added to the existing set. The contents of any value field are neither altered
              nor removed unless specifically referred to by its key in the input request.

              Please note that the maximum number of key:value pairs that can be added to an
              attributes object is 100. Also, the overall size of attributes object should not
              exceed 65kb.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/skynet/asset/{id}/attributes",
            body=await async_maybe_transform(
                {"attributes": attributes}, asset_update_attributes_params.AssetUpdateAttributesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"key": key}, asset_update_attributes_params.AssetUpdateAttributesParams
                ),
            ),
            cast_to=SimpleResp,
        )


class AssetResourceWithRawResponse:
    def __init__(self, asset: AssetResource) -> None:
        self._asset = asset

        self.create = to_raw_response_wrapper(
            asset.create,
        )
        self.retrieve = to_raw_response_wrapper(
            asset.retrieve,
        )
        self.update = to_raw_response_wrapper(
            asset.update,
        )
        self.list = to_raw_response_wrapper(
            asset.list,
        )
        self.delete = to_raw_response_wrapper(
            asset.delete,
        )
        self.bind = to_raw_response_wrapper(
            asset.bind,
        )
        self.track = to_raw_response_wrapper(
            asset.track,
        )
        self.update_attributes = to_raw_response_wrapper(
            asset.update_attributes,
        )

    @cached_property
    def event(self) -> EventResourceWithRawResponse:
        return EventResourceWithRawResponse(self._asset.event)

    @cached_property
    def location(self) -> LocationResourceWithRawResponse:
        return LocationResourceWithRawResponse(self._asset.location)


class AsyncAssetResourceWithRawResponse:
    def __init__(self, asset: AsyncAssetResource) -> None:
        self._asset = asset

        self.create = async_to_raw_response_wrapper(
            asset.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            asset.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            asset.update,
        )
        self.list = async_to_raw_response_wrapper(
            asset.list,
        )
        self.delete = async_to_raw_response_wrapper(
            asset.delete,
        )
        self.bind = async_to_raw_response_wrapper(
            asset.bind,
        )
        self.track = async_to_raw_response_wrapper(
            asset.track,
        )
        self.update_attributes = async_to_raw_response_wrapper(
            asset.update_attributes,
        )

    @cached_property
    def event(self) -> AsyncEventResourceWithRawResponse:
        return AsyncEventResourceWithRawResponse(self._asset.event)

    @cached_property
    def location(self) -> AsyncLocationResourceWithRawResponse:
        return AsyncLocationResourceWithRawResponse(self._asset.location)


class AssetResourceWithStreamingResponse:
    def __init__(self, asset: AssetResource) -> None:
        self._asset = asset

        self.create = to_streamed_response_wrapper(
            asset.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            asset.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            asset.update,
        )
        self.list = to_streamed_response_wrapper(
            asset.list,
        )
        self.delete = to_streamed_response_wrapper(
            asset.delete,
        )
        self.bind = to_streamed_response_wrapper(
            asset.bind,
        )
        self.track = to_streamed_response_wrapper(
            asset.track,
        )
        self.update_attributes = to_streamed_response_wrapper(
            asset.update_attributes,
        )

    @cached_property
    def event(self) -> EventResourceWithStreamingResponse:
        return EventResourceWithStreamingResponse(self._asset.event)

    @cached_property
    def location(self) -> LocationResourceWithStreamingResponse:
        return LocationResourceWithStreamingResponse(self._asset.location)


class AsyncAssetResourceWithStreamingResponse:
    def __init__(self, asset: AsyncAssetResource) -> None:
        self._asset = asset

        self.create = async_to_streamed_response_wrapper(
            asset.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            asset.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            asset.update,
        )
        self.list = async_to_streamed_response_wrapper(
            asset.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            asset.delete,
        )
        self.bind = async_to_streamed_response_wrapper(
            asset.bind,
        )
        self.track = async_to_streamed_response_wrapper(
            asset.track,
        )
        self.update_attributes = async_to_streamed_response_wrapper(
            asset.update_attributes,
        )

    @cached_property
    def event(self) -> AsyncEventResourceWithStreamingResponse:
        return AsyncEventResourceWithStreamingResponse(self._asset.event)

    @cached_property
    def location(self) -> AsyncLocationResourceWithStreamingResponse:
        return AsyncLocationResourceWithStreamingResponse(self._asset.location)
