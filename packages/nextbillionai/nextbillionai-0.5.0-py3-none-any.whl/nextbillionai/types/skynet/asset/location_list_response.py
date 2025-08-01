# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..pagination import Pagination
from .track_location import TrackLocation

__all__ = [
    "LocationListResponse",
    "Data",
    "DataGeojson",
    "DataGeojsonGeometry",
    "DataSnappedPoint",
    "DataSnappedPointLocation",
]


class DataGeojsonGeometry(BaseModel):
    coordinates: Optional[List[float]] = None
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    route geometry.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry."""


class DataGeojson(BaseModel):
    geometry: Optional[DataGeojsonGeometry] = None
    """An object with details of the geoJSON geometry of the route."""

    type: Optional[str] = None
    """Type of the geoJSON object."""


class DataSnappedPointLocation(BaseModel):
    lat: Optional[float] = None
    """Latitude of the snapped point."""

    lon: Optional[float] = None
    """Longitude of the snapped point."""


class DataSnappedPoint(BaseModel):
    bearing: Optional[str] = None
    """
    The bearing angle of the snapped point from the original tracked location, in
    radians. It indicates the direction of the snapped point.
    """

    distance: Optional[float] = None
    """
    The distance of the snapped point from the original tracked location, in meters.
    """

    location: Optional[DataSnappedPointLocation] = None
    """The latitude and longitude coordinates of the snapped point."""

    name: Optional[str] = None
    """The name of the street or road of the snapped point."""

    original_index: Optional[str] = FieldInfo(alias="originalIndex", default=None)
    """The index of the tracked location to which this snapped point corresponds to."""


class Data(BaseModel):
    distance: Optional[float] = None
    """
    Distance of the path, in meters, formed by connecting all tracked locations
    returned.

    Please note that distance is returned only when the mapmatch property of
    correction parameter is set to 1.
    """

    geojson: Optional[DataGeojson] = None
    """An object with geoJSON details of the route.

    It is returned only when the mapmatch property of the correction parameter is
    set to 1 and geometry_type is geojson, otherwise it is not present in the
    response. The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    geometry: Optional[List[str]] = None
    """Geometry of tracked locations in the requested format.

    It is returned only if the mapmatch property of the ‘correction’ parameter is
    set to 1.
    """

    list: Optional[List[TrackLocation]] = None
    """An array of objects with details of the tracked locations of the asset.

    Each object represents one tracked location.
    """

    page: Optional[Pagination] = None
    """An object with pagination details of the search results.

    Use this object to implement pagination in your application.
    """

    snapped_points: Optional[List[DataSnappedPoint]] = None
    """
    An array of objects with details about the snapped points for each of the
    tracked locations returned for the asset.

    Please note that this property is returned only when the mapmatch property of
    correction parameter is set to 1.
    """


class LocationListResponse(BaseModel):
    data: Optional[Data] = None

    message: Optional[str] = None
    """Displays the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
