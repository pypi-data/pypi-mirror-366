# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .json import (
    JsonResource,
    AsyncJsonResource,
    JsonResourceWithRawResponse,
    AsyncJsonResourceWithRawResponse,
    JsonResourceWithStreamingResponse,
    AsyncJsonResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["DistanceMatrixResource", "AsyncDistanceMatrixResource"]


class DistanceMatrixResource(SyncAPIResource):
    @cached_property
    def json(self) -> JsonResource:
        return JsonResource(self._client)

    @cached_property
    def with_raw_response(self) -> DistanceMatrixResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return DistanceMatrixResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DistanceMatrixResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return DistanceMatrixResourceWithStreamingResponse(self)


class AsyncDistanceMatrixResource(AsyncAPIResource):
    @cached_property
    def json(self) -> AsyncJsonResource:
        return AsyncJsonResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDistanceMatrixResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDistanceMatrixResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDistanceMatrixResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncDistanceMatrixResourceWithStreamingResponse(self)


class DistanceMatrixResourceWithRawResponse:
    def __init__(self, distance_matrix: DistanceMatrixResource) -> None:
        self._distance_matrix = distance_matrix

    @cached_property
    def json(self) -> JsonResourceWithRawResponse:
        return JsonResourceWithRawResponse(self._distance_matrix.json)


class AsyncDistanceMatrixResourceWithRawResponse:
    def __init__(self, distance_matrix: AsyncDistanceMatrixResource) -> None:
        self._distance_matrix = distance_matrix

    @cached_property
    def json(self) -> AsyncJsonResourceWithRawResponse:
        return AsyncJsonResourceWithRawResponse(self._distance_matrix.json)


class DistanceMatrixResourceWithStreamingResponse:
    def __init__(self, distance_matrix: DistanceMatrixResource) -> None:
        self._distance_matrix = distance_matrix

    @cached_property
    def json(self) -> JsonResourceWithStreamingResponse:
        return JsonResourceWithStreamingResponse(self._distance_matrix.json)


class AsyncDistanceMatrixResourceWithStreamingResponse:
    def __init__(self, distance_matrix: AsyncDistanceMatrixResource) -> None:
        self._distance_matrix = distance_matrix

    @cached_property
    def json(self) -> AsyncJsonResourceWithStreamingResponse:
        return AsyncJsonResourceWithStreamingResponse(self._distance_matrix.json)
