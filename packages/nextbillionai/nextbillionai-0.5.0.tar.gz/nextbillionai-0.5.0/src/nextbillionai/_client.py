# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import (
    map,
    mdm,
    areas,
    batch,
    browse,
    lookup,
    geocode,
    discover,
    isochrone,
    directions,
    navigation,
    postalcode,
    revgeocode,
    autosuggest,
    autocomplete,
    restrictions,
    route_report,
    snap_to_roads,
    restrictions_items,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, NextbillionSDKError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.skynet import skynet
from .resources.fleetify import fleetify
from .resources.geofence import geofence
from .resources.multigeocode import multigeocode
from .resources.optimization import optimization
from .resources.distance_matrix import distance_matrix

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "NextbillionSDK",
    "AsyncNextbillionSDK",
    "Client",
    "AsyncClient",
]


class NextbillionSDK(SyncAPIClient):
    fleetify: fleetify.FleetifyResource
    skynet: skynet.SkynetResource
    geocode: geocode.GeocodeResource
    optimization: optimization.OptimizationResource
    geofence: geofence.GeofenceResource
    discover: discover.DiscoverResource
    browse: browse.BrowseResource
    mdm: mdm.MdmResource
    isochrone: isochrone.IsochroneResource
    restrictions: restrictions.RestrictionsResource
    restrictions_items: restrictions_items.RestrictionsItemsResource
    distance_matrix: distance_matrix.DistanceMatrixResource
    autocomplete: autocomplete.AutocompleteResource
    navigation: navigation.NavigationResource
    map: map.MapResource
    autosuggest: autosuggest.AutosuggestResource
    directions: directions.DirectionsResource
    batch: batch.BatchResource
    multigeocode: multigeocode.MultigeocodeResource
    revgeocode: revgeocode.RevgeocodeResource
    route_report: route_report.RouteReportResource
    snap_to_roads: snap_to_roads.SnapToRoadsResource
    postalcode: postalcode.PostalcodeResource
    lookup: lookup.LookupResource
    areas: areas.AreasResource
    with_raw_response: NextbillionSDKWithRawResponse
    with_streaming_response: NextbillionSDKWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous NextbillionSDK client instance.

        This automatically infers the `api_key` argument from the `NEXTBILLION_SDK_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("NEXTBILLION_SDK_API_KEY")
        if api_key is None:
            raise NextbillionSDKError(
                "The api_key client option must be set either by passing api_key to the client or by setting the NEXTBILLION_SDK_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("NEXTBILLION_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://api.nextbillion.io"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.fleetify = fleetify.FleetifyResource(self)
        self.skynet = skynet.SkynetResource(self)
        self.geocode = geocode.GeocodeResource(self)
        self.optimization = optimization.OptimizationResource(self)
        self.geofence = geofence.GeofenceResource(self)
        self.discover = discover.DiscoverResource(self)
        self.browse = browse.BrowseResource(self)
        self.mdm = mdm.MdmResource(self)
        self.isochrone = isochrone.IsochroneResource(self)
        self.restrictions = restrictions.RestrictionsResource(self)
        self.restrictions_items = restrictions_items.RestrictionsItemsResource(self)
        self.distance_matrix = distance_matrix.DistanceMatrixResource(self)
        self.autocomplete = autocomplete.AutocompleteResource(self)
        self.navigation = navigation.NavigationResource(self)
        self.map = map.MapResource(self)
        self.autosuggest = autosuggest.AutosuggestResource(self)
        self.directions = directions.DirectionsResource(self)
        self.batch = batch.BatchResource(self)
        self.multigeocode = multigeocode.MultigeocodeResource(self)
        self.revgeocode = revgeocode.RevgeocodeResource(self)
        self.route_report = route_report.RouteReportResource(self)
        self.snap_to_roads = snap_to_roads.SnapToRoadsResource(self)
        self.postalcode = postalcode.PostalcodeResource(self)
        self.lookup = lookup.LookupResource(self)
        self.areas = areas.AreasResource(self)
        self.with_raw_response = NextbillionSDKWithRawResponse(self)
        self.with_streaming_response = NextbillionSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    @property
    @override
    def default_query(self) -> dict[str, object]:
        return {
            **super().default_query,
            "key": self.api_key,
            **self._custom_query,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncNextbillionSDK(AsyncAPIClient):
    fleetify: fleetify.AsyncFleetifyResource
    skynet: skynet.AsyncSkynetResource
    geocode: geocode.AsyncGeocodeResource
    optimization: optimization.AsyncOptimizationResource
    geofence: geofence.AsyncGeofenceResource
    discover: discover.AsyncDiscoverResource
    browse: browse.AsyncBrowseResource
    mdm: mdm.AsyncMdmResource
    isochrone: isochrone.AsyncIsochroneResource
    restrictions: restrictions.AsyncRestrictionsResource
    restrictions_items: restrictions_items.AsyncRestrictionsItemsResource
    distance_matrix: distance_matrix.AsyncDistanceMatrixResource
    autocomplete: autocomplete.AsyncAutocompleteResource
    navigation: navigation.AsyncNavigationResource
    map: map.AsyncMapResource
    autosuggest: autosuggest.AsyncAutosuggestResource
    directions: directions.AsyncDirectionsResource
    batch: batch.AsyncBatchResource
    multigeocode: multigeocode.AsyncMultigeocodeResource
    revgeocode: revgeocode.AsyncRevgeocodeResource
    route_report: route_report.AsyncRouteReportResource
    snap_to_roads: snap_to_roads.AsyncSnapToRoadsResource
    postalcode: postalcode.AsyncPostalcodeResource
    lookup: lookup.AsyncLookupResource
    areas: areas.AsyncAreasResource
    with_raw_response: AsyncNextbillionSDKWithRawResponse
    with_streaming_response: AsyncNextbillionSDKWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncNextbillionSDK client instance.

        This automatically infers the `api_key` argument from the `NEXTBILLION_SDK_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("NEXTBILLION_SDK_API_KEY")
        if api_key is None:
            raise NextbillionSDKError(
                "The api_key client option must be set either by passing api_key to the client or by setting the NEXTBILLION_SDK_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("NEXTBILLION_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://api.nextbillion.io"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.fleetify = fleetify.AsyncFleetifyResource(self)
        self.skynet = skynet.AsyncSkynetResource(self)
        self.geocode = geocode.AsyncGeocodeResource(self)
        self.optimization = optimization.AsyncOptimizationResource(self)
        self.geofence = geofence.AsyncGeofenceResource(self)
        self.discover = discover.AsyncDiscoverResource(self)
        self.browse = browse.AsyncBrowseResource(self)
        self.mdm = mdm.AsyncMdmResource(self)
        self.isochrone = isochrone.AsyncIsochroneResource(self)
        self.restrictions = restrictions.AsyncRestrictionsResource(self)
        self.restrictions_items = restrictions_items.AsyncRestrictionsItemsResource(self)
        self.distance_matrix = distance_matrix.AsyncDistanceMatrixResource(self)
        self.autocomplete = autocomplete.AsyncAutocompleteResource(self)
        self.navigation = navigation.AsyncNavigationResource(self)
        self.map = map.AsyncMapResource(self)
        self.autosuggest = autosuggest.AsyncAutosuggestResource(self)
        self.directions = directions.AsyncDirectionsResource(self)
        self.batch = batch.AsyncBatchResource(self)
        self.multigeocode = multigeocode.AsyncMultigeocodeResource(self)
        self.revgeocode = revgeocode.AsyncRevgeocodeResource(self)
        self.route_report = route_report.AsyncRouteReportResource(self)
        self.snap_to_roads = snap_to_roads.AsyncSnapToRoadsResource(self)
        self.postalcode = postalcode.AsyncPostalcodeResource(self)
        self.lookup = lookup.AsyncLookupResource(self)
        self.areas = areas.AsyncAreasResource(self)
        self.with_raw_response = AsyncNextbillionSDKWithRawResponse(self)
        self.with_streaming_response = AsyncNextbillionSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    @property
    @override
    def default_query(self) -> dict[str, object]:
        return {
            **super().default_query,
            "key": self.api_key,
            **self._custom_query,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class NextbillionSDKWithRawResponse:
    def __init__(self, client: NextbillionSDK) -> None:
        self.fleetify = fleetify.FleetifyResourceWithRawResponse(client.fleetify)
        self.skynet = skynet.SkynetResourceWithRawResponse(client.skynet)
        self.geocode = geocode.GeocodeResourceWithRawResponse(client.geocode)
        self.optimization = optimization.OptimizationResourceWithRawResponse(client.optimization)
        self.geofence = geofence.GeofenceResourceWithRawResponse(client.geofence)
        self.discover = discover.DiscoverResourceWithRawResponse(client.discover)
        self.browse = browse.BrowseResourceWithRawResponse(client.browse)
        self.mdm = mdm.MdmResourceWithRawResponse(client.mdm)
        self.isochrone = isochrone.IsochroneResourceWithRawResponse(client.isochrone)
        self.restrictions = restrictions.RestrictionsResourceWithRawResponse(client.restrictions)
        self.restrictions_items = restrictions_items.RestrictionsItemsResourceWithRawResponse(client.restrictions_items)
        self.distance_matrix = distance_matrix.DistanceMatrixResourceWithRawResponse(client.distance_matrix)
        self.autocomplete = autocomplete.AutocompleteResourceWithRawResponse(client.autocomplete)
        self.navigation = navigation.NavigationResourceWithRawResponse(client.navigation)
        self.map = map.MapResourceWithRawResponse(client.map)
        self.autosuggest = autosuggest.AutosuggestResourceWithRawResponse(client.autosuggest)
        self.directions = directions.DirectionsResourceWithRawResponse(client.directions)
        self.batch = batch.BatchResourceWithRawResponse(client.batch)
        self.multigeocode = multigeocode.MultigeocodeResourceWithRawResponse(client.multigeocode)
        self.revgeocode = revgeocode.RevgeocodeResourceWithRawResponse(client.revgeocode)
        self.route_report = route_report.RouteReportResourceWithRawResponse(client.route_report)
        self.snap_to_roads = snap_to_roads.SnapToRoadsResourceWithRawResponse(client.snap_to_roads)
        self.postalcode = postalcode.PostalcodeResourceWithRawResponse(client.postalcode)
        self.lookup = lookup.LookupResourceWithRawResponse(client.lookup)
        self.areas = areas.AreasResourceWithRawResponse(client.areas)


class AsyncNextbillionSDKWithRawResponse:
    def __init__(self, client: AsyncNextbillionSDK) -> None:
        self.fleetify = fleetify.AsyncFleetifyResourceWithRawResponse(client.fleetify)
        self.skynet = skynet.AsyncSkynetResourceWithRawResponse(client.skynet)
        self.geocode = geocode.AsyncGeocodeResourceWithRawResponse(client.geocode)
        self.optimization = optimization.AsyncOptimizationResourceWithRawResponse(client.optimization)
        self.geofence = geofence.AsyncGeofenceResourceWithRawResponse(client.geofence)
        self.discover = discover.AsyncDiscoverResourceWithRawResponse(client.discover)
        self.browse = browse.AsyncBrowseResourceWithRawResponse(client.browse)
        self.mdm = mdm.AsyncMdmResourceWithRawResponse(client.mdm)
        self.isochrone = isochrone.AsyncIsochroneResourceWithRawResponse(client.isochrone)
        self.restrictions = restrictions.AsyncRestrictionsResourceWithRawResponse(client.restrictions)
        self.restrictions_items = restrictions_items.AsyncRestrictionsItemsResourceWithRawResponse(
            client.restrictions_items
        )
        self.distance_matrix = distance_matrix.AsyncDistanceMatrixResourceWithRawResponse(client.distance_matrix)
        self.autocomplete = autocomplete.AsyncAutocompleteResourceWithRawResponse(client.autocomplete)
        self.navigation = navigation.AsyncNavigationResourceWithRawResponse(client.navigation)
        self.map = map.AsyncMapResourceWithRawResponse(client.map)
        self.autosuggest = autosuggest.AsyncAutosuggestResourceWithRawResponse(client.autosuggest)
        self.directions = directions.AsyncDirectionsResourceWithRawResponse(client.directions)
        self.batch = batch.AsyncBatchResourceWithRawResponse(client.batch)
        self.multigeocode = multigeocode.AsyncMultigeocodeResourceWithRawResponse(client.multigeocode)
        self.revgeocode = revgeocode.AsyncRevgeocodeResourceWithRawResponse(client.revgeocode)
        self.route_report = route_report.AsyncRouteReportResourceWithRawResponse(client.route_report)
        self.snap_to_roads = snap_to_roads.AsyncSnapToRoadsResourceWithRawResponse(client.snap_to_roads)
        self.postalcode = postalcode.AsyncPostalcodeResourceWithRawResponse(client.postalcode)
        self.lookup = lookup.AsyncLookupResourceWithRawResponse(client.lookup)
        self.areas = areas.AsyncAreasResourceWithRawResponse(client.areas)


class NextbillionSDKWithStreamedResponse:
    def __init__(self, client: NextbillionSDK) -> None:
        self.fleetify = fleetify.FleetifyResourceWithStreamingResponse(client.fleetify)
        self.skynet = skynet.SkynetResourceWithStreamingResponse(client.skynet)
        self.geocode = geocode.GeocodeResourceWithStreamingResponse(client.geocode)
        self.optimization = optimization.OptimizationResourceWithStreamingResponse(client.optimization)
        self.geofence = geofence.GeofenceResourceWithStreamingResponse(client.geofence)
        self.discover = discover.DiscoverResourceWithStreamingResponse(client.discover)
        self.browse = browse.BrowseResourceWithStreamingResponse(client.browse)
        self.mdm = mdm.MdmResourceWithStreamingResponse(client.mdm)
        self.isochrone = isochrone.IsochroneResourceWithStreamingResponse(client.isochrone)
        self.restrictions = restrictions.RestrictionsResourceWithStreamingResponse(client.restrictions)
        self.restrictions_items = restrictions_items.RestrictionsItemsResourceWithStreamingResponse(
            client.restrictions_items
        )
        self.distance_matrix = distance_matrix.DistanceMatrixResourceWithStreamingResponse(client.distance_matrix)
        self.autocomplete = autocomplete.AutocompleteResourceWithStreamingResponse(client.autocomplete)
        self.navigation = navigation.NavigationResourceWithStreamingResponse(client.navigation)
        self.map = map.MapResourceWithStreamingResponse(client.map)
        self.autosuggest = autosuggest.AutosuggestResourceWithStreamingResponse(client.autosuggest)
        self.directions = directions.DirectionsResourceWithStreamingResponse(client.directions)
        self.batch = batch.BatchResourceWithStreamingResponse(client.batch)
        self.multigeocode = multigeocode.MultigeocodeResourceWithStreamingResponse(client.multigeocode)
        self.revgeocode = revgeocode.RevgeocodeResourceWithStreamingResponse(client.revgeocode)
        self.route_report = route_report.RouteReportResourceWithStreamingResponse(client.route_report)
        self.snap_to_roads = snap_to_roads.SnapToRoadsResourceWithStreamingResponse(client.snap_to_roads)
        self.postalcode = postalcode.PostalcodeResourceWithStreamingResponse(client.postalcode)
        self.lookup = lookup.LookupResourceWithStreamingResponse(client.lookup)
        self.areas = areas.AreasResourceWithStreamingResponse(client.areas)


class AsyncNextbillionSDKWithStreamedResponse:
    def __init__(self, client: AsyncNextbillionSDK) -> None:
        self.fleetify = fleetify.AsyncFleetifyResourceWithStreamingResponse(client.fleetify)
        self.skynet = skynet.AsyncSkynetResourceWithStreamingResponse(client.skynet)
        self.geocode = geocode.AsyncGeocodeResourceWithStreamingResponse(client.geocode)
        self.optimization = optimization.AsyncOptimizationResourceWithStreamingResponse(client.optimization)
        self.geofence = geofence.AsyncGeofenceResourceWithStreamingResponse(client.geofence)
        self.discover = discover.AsyncDiscoverResourceWithStreamingResponse(client.discover)
        self.browse = browse.AsyncBrowseResourceWithStreamingResponse(client.browse)
        self.mdm = mdm.AsyncMdmResourceWithStreamingResponse(client.mdm)
        self.isochrone = isochrone.AsyncIsochroneResourceWithStreamingResponse(client.isochrone)
        self.restrictions = restrictions.AsyncRestrictionsResourceWithStreamingResponse(client.restrictions)
        self.restrictions_items = restrictions_items.AsyncRestrictionsItemsResourceWithStreamingResponse(
            client.restrictions_items
        )
        self.distance_matrix = distance_matrix.AsyncDistanceMatrixResourceWithStreamingResponse(client.distance_matrix)
        self.autocomplete = autocomplete.AsyncAutocompleteResourceWithStreamingResponse(client.autocomplete)
        self.navigation = navigation.AsyncNavigationResourceWithStreamingResponse(client.navigation)
        self.map = map.AsyncMapResourceWithStreamingResponse(client.map)
        self.autosuggest = autosuggest.AsyncAutosuggestResourceWithStreamingResponse(client.autosuggest)
        self.directions = directions.AsyncDirectionsResourceWithStreamingResponse(client.directions)
        self.batch = batch.AsyncBatchResourceWithStreamingResponse(client.batch)
        self.multigeocode = multigeocode.AsyncMultigeocodeResourceWithStreamingResponse(client.multigeocode)
        self.revgeocode = revgeocode.AsyncRevgeocodeResourceWithStreamingResponse(client.revgeocode)
        self.route_report = route_report.AsyncRouteReportResourceWithStreamingResponse(client.route_report)
        self.snap_to_roads = snap_to_roads.AsyncSnapToRoadsResourceWithStreamingResponse(client.snap_to_roads)
        self.postalcode = postalcode.AsyncPostalcodeResourceWithStreamingResponse(client.postalcode)
        self.lookup = lookup.AsyncLookupResourceWithStreamingResponse(client.lookup)
        self.areas = areas.AsyncAreasResourceWithStreamingResponse(client.areas)


Client = NextbillionSDK

AsyncClient = AsyncNextbillionSDK
