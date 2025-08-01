# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["MultigeocodeSearchParams", "At"]


class MultigeocodeSearchParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    at: Required[At]
    """Specify the center of the search context expressed as coordinates."""

    query: Required[str]
    """A free-form, complete or incomplete string to be searched.

    It allows searching for places using keywords or names.
    """

    city: str
    """Specifies the primary city of the place."""

    country: str
    """
    Country of the search context provided as comma-separated
    [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
    codes.
    Note: Country codes should be provided in uppercase.
    """

    district: str
    """Specifies the district of the search place."""

    limit: int
    """Sets the maximum number of results to be returned."""

    radius: str
    """
    Filters the results to places within the specified radius from the 'at'
    location.

    Note: Supports 'meter' (m) and 'kilometer' (km) units. If no radius is given,
    the search method returns as many results as specified in limit.
    """

    state: str
    """Specifies the state of the search place."""

    street: str
    """Specifies the street name of the search place."""

    sub_district: Annotated[str, PropertyInfo(alias="subDistrict")]
    """Specifies the subDistrict of the search place."""


class At(TypedDict, total=False):
    lat: Required[float]
    """Latitude coordinate of the location"""

    lng: Required[float]
    """Longitude coordinate of the location."""
