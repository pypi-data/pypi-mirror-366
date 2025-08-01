# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PlaceItemParam", "Geopoint", "Poi"]


class Geopoint(TypedDict, total=False):
    lat: float
    """This parameter represents the latitude value of the place."""

    lng: float
    """This parameter represents the longitude value of the place."""


class Poi(TypedDict, total=False):
    title: str
    """A title that describes the point of interest."""


class PlaceItemParam(TypedDict, total=False):
    address: str
    """
    This parameter represents the complete address of the place, including the
    street, city, state, postal code and country.
    """

    building: str
    """This parameter represents additional building information if applicable."""

    city: str
    """This parameter represents the city or town of the place."""

    country: str
    """This parameter represents the country of the place."""

    district: str
    """This parameter represents the district of the place."""

    geopoint: Geopoint
    """This parameter represents the geographical coordinates of the place.

    It includes the latitude and longitude values.
    """

    house: str
    """This parameter represents the house or building number of the place."""

    poi: Poi
    """This parameter represents a point of interest within the place.

    A Point of Interest (POI) refers to a specific location or area that is of
    interest to individuals for various reasons. It could be a landmark, tourist
    attraction, business, or any other location that people might find important or
    intriguing.
    """

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]
    """This parameter represents the postal code or ZIP code of the place."""

    state: str
    """This parameter represents the state or region of the place."""

    street: str
    """This parameter represents the street name of the place."""

    sub_district: Annotated[str, PropertyInfo(alias="subDistrict")]
    """This parameter represents the sub-district or locality of the place."""
