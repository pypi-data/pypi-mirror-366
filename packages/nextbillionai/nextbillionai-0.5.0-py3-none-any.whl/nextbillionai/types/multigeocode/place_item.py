# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["PlaceItem", "Geopoint", "Poi"]


class Geopoint(BaseModel):
    lat: Optional[float] = None
    """This parameter represents the latitude value of the place."""

    lng: Optional[float] = None
    """This parameter represents the longitude value of the place."""


class Poi(BaseModel):
    title: Optional[str] = None
    """A title that describes the point of interest."""


class PlaceItem(BaseModel):
    address: Optional[str] = None
    """
    This parameter represents the complete address of the place, including the
    street, city, state, postal code and country.
    """

    building: Optional[str] = None
    """This parameter represents additional building information if applicable."""

    city: Optional[str] = None
    """This parameter represents the city or town of the place."""

    country: Optional[str] = None
    """This parameter represents the country of the place."""

    district: Optional[str] = None
    """This parameter represents the district of the place."""

    geopoint: Optional[Geopoint] = None
    """This parameter represents the geographical coordinates of the place.

    It includes the latitude and longitude values.
    """

    house: Optional[str] = None
    """This parameter represents the house or building number of the place."""

    poi: Optional[Poi] = None
    """This parameter represents a point of interest within the place.

    A Point of Interest (POI) refers to a specific location or area that is of
    interest to individuals for various reasons. It could be a landmark, tourist
    attraction, business, or any other location that people might find important or
    intriguing.
    """

    postal_code: Optional[str] = FieldInfo(alias="postalCode", default=None)
    """This parameter represents the postal code or ZIP code of the place."""

    state: Optional[str] = None
    """This parameter represents the state or region of the place."""

    street: Optional[str] = None
    """This parameter represents the street name of the place."""

    sub_district: Optional[str] = FieldInfo(alias="subDistrict", default=None)
    """This parameter represents the sub-district or locality of the place."""
