# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ...types.multigeocode import place_create_params, place_delete_params, place_update_params, place_retrieve_params
from ...types.multigeocode.place_item_param import PlaceItemParam
from ...types.multigeocode.place_create_response import PlaceCreateResponse
from ...types.multigeocode.place_delete_response import PlaceDeleteResponse
from ...types.multigeocode.place_update_response import PlaceUpdateResponse
from ...types.multigeocode.place_retrieve_response import PlaceRetrieveResponse

__all__ = ["PlaceResource", "AsyncPlaceResource"]


class PlaceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PlaceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PlaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PlaceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return PlaceResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        key: str,
        place: Iterable[place_create_params.Place],
        data_source: place_create_params.DataSource | NotGiven = NOT_GIVEN,
        force: bool | NotGiven = NOT_GIVEN,
        score: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceCreateResponse:
        """
        The "Add Place" method allows users to create custom places

        Add place method provides the flexibility to create custom places in a way that
        suits your business needs. The newly created place and its attributes can be
        added to custom (proprietary) dataset - to the effect of building your own
        places dataset (s) - or, to a default dataset. Overcome inaccurate ‘POI’ details
        from default search provider by creating custom, highly accurate ‘POIs’.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          place: This parameter represents the place details, including geographical information,
              address and other related information.

          data_source: It contains information about the dataset that returns the specific result

          force: When 2 places are located within 100 meters of each other and have more than 90%
              of matching attributes (at least 11 out of 12 attributes in the “place” object),
              they will be considered duplicates and any requests to add such a new place
              would be rejected. Set force=true to override this duplicate check. You can use
              this to create closely located POIs. For instance, places inside a mall,
              university or a government building etc.

          score: Search score of the place. This is calculated based on how ‘richly’ the place is
              defined. For instance, a place with - street name, city, state and country
              attributes set might be ranked lower than a place which has values of - house,
              building, street name, city, state and country attributes set. The score
              determines the rank of the place among search results. You can also use this
              field to set a custom score as per its relevance to rank it among the search
              results from multiple data sources.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/multigeocode/place",
            body=maybe_transform(
                {
                    "place": place,
                    "data_source": data_source,
                    "force": force,
                    "score": score,
                },
                place_create_params.PlaceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, place_create_params.PlaceCreateParams),
            ),
            cast_to=PlaceCreateResponse,
        )

    def retrieve(
        self,
        doc_id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceRetrieveResponse:
        """
        Use this method to get the details of previously created custom places using its
        NextBillion ID.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._get(
            f"/multigeocode/place/{doc_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, place_retrieve_params.PlaceRetrieveParams),
            ),
            cast_to=PlaceRetrieveResponse,
        )

    def update(
        self,
        doc_id: str,
        *,
        key: str,
        data_source: place_update_params.DataSource | NotGiven = NOT_GIVEN,
        place: Iterable[PlaceItemParam] | NotGiven = NOT_GIVEN,
        score: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceUpdateResponse:
        """
        The "Update Place" method allows businesses to update the attributes of an
        existing place.

        This method allows you to update the attributes of custom places. In effect,
        updating a place replaces the current information in search results with the
        updated information associated with the specific docID. Use this method to
        enhance the accuracy/usability of your search results with respect to the
        default dataset to suit your business needs.

        If you want to prioritize a particular result in your search results, update the
        ‘score’ of that specific place.
        Alternatively, you can block places which are no longer needed by setting their
        status: ‘disable’.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          data_source: dataSource values can be updated to enhance or prioritize the search results to
              better suit specific business use cases.

          place: This parameter represents the place details, including geographical information,
              address and other related information.

          score: Search score of the place. This is calculated based on how ‘richly’ the place is
              defined. For instance, a place with street name, city, state and country
              attributes set might be ranked lower than a place which has values of house,
              building, street name, city, state and country attributes set. The score
              determines the rank of the place among search results. You can also use this
              field to set a custom score as per its relevance to rank it among the search
              results from multiple data sources.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._put(
            f"/multigeocode/place/{doc_id}",
            body=maybe_transform(
                {
                    "data_source": data_source,
                    "place": place,
                    "score": score,
                },
                place_update_params.PlaceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, place_update_params.PlaceUpdateParams),
            ),
            cast_to=PlaceUpdateResponse,
        )

    def delete(
        self,
        doc_id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceDeleteResponse:
        """
        The "Delete Place" method enables businesses to delete a previously created
        place

        Use this method to delete a previously created place. Please note that the place
        associated with the specified docID only would be deleted. As a result, once a
        place is deleted, the search API can still return valid results from the default
        datasets or others, if present.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._delete(
            f"/multigeocode/place/{doc_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, place_delete_params.PlaceDeleteParams),
            ),
            cast_to=PlaceDeleteResponse,
        )


class AsyncPlaceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPlaceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPlaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPlaceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncPlaceResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        key: str,
        place: Iterable[place_create_params.Place],
        data_source: place_create_params.DataSource | NotGiven = NOT_GIVEN,
        force: bool | NotGiven = NOT_GIVEN,
        score: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceCreateResponse:
        """
        The "Add Place" method allows users to create custom places

        Add place method provides the flexibility to create custom places in a way that
        suits your business needs. The newly created place and its attributes can be
        added to custom (proprietary) dataset - to the effect of building your own
        places dataset (s) - or, to a default dataset. Overcome inaccurate ‘POI’ details
        from default search provider by creating custom, highly accurate ‘POIs’.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          place: This parameter represents the place details, including geographical information,
              address and other related information.

          data_source: It contains information about the dataset that returns the specific result

          force: When 2 places are located within 100 meters of each other and have more than 90%
              of matching attributes (at least 11 out of 12 attributes in the “place” object),
              they will be considered duplicates and any requests to add such a new place
              would be rejected. Set force=true to override this duplicate check. You can use
              this to create closely located POIs. For instance, places inside a mall,
              university or a government building etc.

          score: Search score of the place. This is calculated based on how ‘richly’ the place is
              defined. For instance, a place with - street name, city, state and country
              attributes set might be ranked lower than a place which has values of - house,
              building, street name, city, state and country attributes set. The score
              determines the rank of the place among search results. You can also use this
              field to set a custom score as per its relevance to rank it among the search
              results from multiple data sources.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/multigeocode/place",
            body=await async_maybe_transform(
                {
                    "place": place,
                    "data_source": data_source,
                    "force": force,
                    "score": score,
                },
                place_create_params.PlaceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, place_create_params.PlaceCreateParams),
            ),
            cast_to=PlaceCreateResponse,
        )

    async def retrieve(
        self,
        doc_id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceRetrieveResponse:
        """
        Use this method to get the details of previously created custom places using its
        NextBillion ID.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._get(
            f"/multigeocode/place/{doc_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, place_retrieve_params.PlaceRetrieveParams),
            ),
            cast_to=PlaceRetrieveResponse,
        )

    async def update(
        self,
        doc_id: str,
        *,
        key: str,
        data_source: place_update_params.DataSource | NotGiven = NOT_GIVEN,
        place: Iterable[PlaceItemParam] | NotGiven = NOT_GIVEN,
        score: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceUpdateResponse:
        """
        The "Update Place" method allows businesses to update the attributes of an
        existing place.

        This method allows you to update the attributes of custom places. In effect,
        updating a place replaces the current information in search results with the
        updated information associated with the specific docID. Use this method to
        enhance the accuracy/usability of your search results with respect to the
        default dataset to suit your business needs.

        If you want to prioritize a particular result in your search results, update the
        ‘score’ of that specific place.
        Alternatively, you can block places which are no longer needed by setting their
        status: ‘disable’.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          data_source: dataSource values can be updated to enhance or prioritize the search results to
              better suit specific business use cases.

          place: This parameter represents the place details, including geographical information,
              address and other related information.

          score: Search score of the place. This is calculated based on how ‘richly’ the place is
              defined. For instance, a place with street name, city, state and country
              attributes set might be ranked lower than a place which has values of house,
              building, street name, city, state and country attributes set. The score
              determines the rank of the place among search results. You can also use this
              field to set a custom score as per its relevance to rank it among the search
              results from multiple data sources.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._put(
            f"/multigeocode/place/{doc_id}",
            body=await async_maybe_transform(
                {
                    "data_source": data_source,
                    "place": place,
                    "score": score,
                },
                place_update_params.PlaceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, place_update_params.PlaceUpdateParams),
            ),
            cast_to=PlaceUpdateResponse,
        )

    async def delete(
        self,
        doc_id: str,
        *,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PlaceDeleteResponse:
        """
        The "Delete Place" method enables businesses to delete a previously created
        place

        Use this method to delete a previously created place. Please note that the place
        associated with the specified docID only would be deleted. As a result, once a
        place is deleted, the search API can still return valid results from the default
        datasets or others, if present.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._delete(
            f"/multigeocode/place/{doc_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, place_delete_params.PlaceDeleteParams),
            ),
            cast_to=PlaceDeleteResponse,
        )


class PlaceResourceWithRawResponse:
    def __init__(self, place: PlaceResource) -> None:
        self._place = place

        self.create = to_raw_response_wrapper(
            place.create,
        )
        self.retrieve = to_raw_response_wrapper(
            place.retrieve,
        )
        self.update = to_raw_response_wrapper(
            place.update,
        )
        self.delete = to_raw_response_wrapper(
            place.delete,
        )


class AsyncPlaceResourceWithRawResponse:
    def __init__(self, place: AsyncPlaceResource) -> None:
        self._place = place

        self.create = async_to_raw_response_wrapper(
            place.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            place.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            place.update,
        )
        self.delete = async_to_raw_response_wrapper(
            place.delete,
        )


class PlaceResourceWithStreamingResponse:
    def __init__(self, place: PlaceResource) -> None:
        self._place = place

        self.create = to_streamed_response_wrapper(
            place.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            place.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            place.update,
        )
        self.delete = to_streamed_response_wrapper(
            place.delete,
        )


class AsyncPlaceResourceWithStreamingResponse:
    def __init__(self, place: AsyncPlaceResource) -> None:
        self._place = place

        self.create = async_to_streamed_response_wrapper(
            place.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            place.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            place.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            place.delete,
        )
