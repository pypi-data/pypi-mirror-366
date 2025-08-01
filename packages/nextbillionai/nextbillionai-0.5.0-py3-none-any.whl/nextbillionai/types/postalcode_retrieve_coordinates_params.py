# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["PostalcodeRetrieveCoordinatesParams", "At"]


class PostalcodeRetrieveCoordinatesParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    at: At
    """Location coordinates that you want to get the postal code of.

    If not providing postalcode in the request, at becomes mandatory. Please note
    that only 1 point can be requested. [See this example](#note).
    """

    country: str
    """Country containing the postal code or the location.

    It is mandatory if postalcode is provided in the request.
    [See this example](#note).

    Please check the [API Query Limits](#api-query-limits) section below for a list
    of the countries covered by the Geocode Postcode API. Users can provide either
    the name or the alpha-2/3 code as per the
    [ISO 3166-1 standard](https://en.wikipedia.org/wiki/ISO_3166-1) of a country
    covered by the API as input for this parameter.
    """

    format: Literal["geojson"]
    """
    Specify the format in which the boundary details of the post code will be
    returned. When specified, the boundary details will be returned in the geojson
    format. When not specified, the boundary details are returned in general format.
    """

    postalcode: str
    """Provide the postal code for which the information is needed.

    At least one of (postalcode + country) or at needs to be provided. Please note
    that only 1 postal code can be requested. [See this example](#note).
    """


class At(TypedDict, total=False):
    lat: float
    """Latitude of the location."""

    lng: float
    """Longitude of the location."""
