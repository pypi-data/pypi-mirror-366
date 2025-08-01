# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PlaceCreateParams", "Place", "PlaceGeopoint", "PlacePoi", "DataSource"]


class PlaceCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    place: Required[Iterable[Place]]
    """
    This parameter represents the place details, including geographical information,
    address and other related information.
    """

    data_source: Annotated[DataSource, PropertyInfo(alias="dataSource")]
    """It contains information about the dataset that returns the specific result"""

    force: bool
    """
    When 2 places are located within 100 meters of each other and have more than 90%
    of matching attributes (at least 11 out of 12 attributes in the “place” object),
    they will be considered duplicates and any requests to add such a new place
    would be rejected. Set force=true to override this duplicate check. You can use
    this to create closely located POIs. For instance, places inside a mall,
    university or a government building etc.
    """

    score: int
    """Search score of the place.

    This is calculated based on how ‘richly’ the place is defined. For instance, a
    place with - street name, city, state and country attributes set might be ranked
    lower than a place which has values of - house, building, street name, city,
    state and country attributes set. The score determines the rank of the place
    among search results. You can also use this field to set a custom score as per
    its relevance to rank it among the search results from multiple data sources.
    """


class PlaceGeopoint(TypedDict, total=False):
    lat: float
    """This parameter represents the latitude value of the place."""

    lng: float
    """This parameter represents the longitude value of the place."""


class PlacePoi(TypedDict, total=False):
    title: str
    """A title that describes the point of interest."""


class Place(TypedDict, total=False):
    geopoint: Required[PlaceGeopoint]
    """This parameter represents the geographical coordinates of the place.

    It includes the latitude and longitude values.
    """

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
    """
    Country of the search context provided as comma-separated
    [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
    codes.

    Note: Country codes should be provided in uppercase.
    """

    district: str
    """This parameter represents the district of the place."""

    house: str
    """This parameter represents the house or building number of the place."""

    poi: PlacePoi
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


class DataSource(TypedDict, total=False):
    ref_id: Annotated[str, PropertyInfo(alias="refId")]
    """
    This parameter represents the unique reference ID associated with the data
    source.
    """

    source: str
    """This parameter represents the source of the data."""

    status: Literal["enable", "disable"]
    """This parameter indicates if a place is searchable."""
