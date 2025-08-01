# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "PostalcodeRetrieveCoordinatesResponse",
    "Places",
    "PlacesBoundary",
    "PlacesBoundaryGeometry",
    "PlacesBoundaryMultipolygon",
    "PlacesBoundaryMultipolygonPolygon",
    "PlacesBoundaryMultipolygonPolygonPoint",
    "PlacesGeopoint",
]


class PlacesBoundaryGeometry(BaseModel):
    coordinates: Optional[List[List[List[float]]]] = None
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    coordinates points which lie on the boundary of the postal code area.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry."""


class PlacesBoundaryMultipolygonPolygonPoint(BaseModel):
    lat: Optional[float] = None
    """Latitude of the coordinate."""

    lng: Optional[float] = None
    """Longitude of the coordinate."""


class PlacesBoundaryMultipolygonPolygon(BaseModel):
    points: Optional[List[PlacesBoundaryMultipolygonPolygonPoint]] = None
    """Represents an array of geographic coordinates that define a polygon boundary."""


class PlacesBoundaryMultipolygon(BaseModel):
    polygon: Optional[List[PlacesBoundaryMultipolygonPolygon]] = None
    """
    An object containing the details of a single polygon that is a part of the
    postal code area. In case the postal code area contains other polygon(s), the
    details of such polygon(s) would be returned through an array of points object.
    """


class PlacesBoundary(BaseModel):
    geometry: Optional[PlacesBoundaryGeometry] = None
    """An object with geoJSON details of the boundary.

    This object is returned when the format field is set to geojson in the input
    request, otherwise it is not present in the response. The contents of this
    object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    multipolygon: Optional[List[PlacesBoundaryMultipolygon]] = None
    """
    An array of objects containing information about all the polygons forming the
    postal code area. In case, the postal code area is formed by multiple polygons
    not containing each other, a matching count of polygon objects will be returned.

    Please note that this object is returned only when format field is not specified
    in the input, otherwise it is not present in the response.
    """

    properties: Optional[str] = None
    """Property associated with the geoJSON shape."""

    type: Optional[str] = None
    """Type of the geoJSON object.

    This parameter is returned when the format field is set to geojson in the input
    request, otherwise it is not present in the response. The contents of this
    object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """


class PlacesGeopoint(BaseModel):
    lat: Optional[float] = None
    """Latitude of the location."""

    lng: Optional[float] = None
    """Longitude of the location."""


class Places(BaseModel):
    address: Optional[str] = None
    """Returns the address of the postalcode returned."""

    boundary: Optional[PlacesBoundary] = None
    """An object containing the boundary details of the postal code area.

    This object will not be returned in case the boundary information of the postal
    code provided is not available (only for selected countries).

    Please note the contents of this object will change based on the format field in
    the input. When the format field is not present in the input this object would
    contain multipolygon - polygon - points objects depending on the boundary of the
    given postal code. When the format field is present in the input, then the
    contents of this object would match the
    [geojson format and standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    country: Optional[str] = None
    """
    Name of the country containing the geographic coordinate point / postal code
    provided in the input request.
    """

    country_code: Optional[str] = FieldInfo(alias="countryCode", default=None)
    """
    Returns the [alpha-3 ISO code](https://www.iban.com/country-codes) of the
    country containing the postalcode returned.
    """

    distance: Optional[float] = None
    """
    This property is returned only when the API is requested to fetch the postal
    code containing the location coordinate provided in the at input parameter.
    distance denotes the straight line distance, in meters, from the requested
    location coordinate to the postal code centroid.
    """

    district: Optional[str] = None
    """
    Name of the district or region containing the geographic coordinate point /
    postal code provided in the input request.
    """

    geopoint: Optional[PlacesGeopoint] = None
    """
    Refers to the geographic coordinate denoting the center of the postal code in
    latitude, longitude format.
    """

    postalcode: Optional[str] = None
    """
    Returns the postal code associated with the requested geographic coordinate
    point or the postal code itself as provided in the input API request.
    """

    state: Optional[str] = None
    """
    Name of the state or province containing the geographic coordinate point /
    postal code provided in the input request.
    """

    subdistrict: Optional[str] = None
    """
    Name of the sub-district or sub-region containing the postal code or geographic
    coordinate point / postal code provided in the input request
    """


class PostalcodeRetrieveCoordinatesResponse(BaseModel):
    places: Optional[Places] = None
    """An object that contains details about the place that was provided in the input."""

    warning: Optional[List[str]] = None
    """Returns a message, in case the input provided triggers any warnings."""
