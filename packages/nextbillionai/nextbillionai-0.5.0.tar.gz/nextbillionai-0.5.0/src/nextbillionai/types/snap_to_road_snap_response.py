# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "SnapToRoadSnapResponse",
    "Geojson",
    "GeojsonGeometry",
    "RoadInfo",
    "RoadInfoMaxSpeed",
    "SnappedPoint",
    "SnappedPointLocation",
]


class GeojsonGeometry(BaseModel):
    coordinates: Optional[List[float]] = None
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    snapped path geometry.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry"""


class Geojson(BaseModel):
    geometry: Optional[GeojsonGeometry] = None
    """An object with details of the geoJSON geometry of the snapped path."""

    properties: Optional[str] = None
    """Properties associated with the geoJSON shape of the snapped path."""

    type: Optional[str] = None
    """Type of the GeoJSON object."""


class RoadInfoMaxSpeed(BaseModel):
    length: Optional[int] = None
    """
    length refers to a sequence of 'n' consecutive vertices in the route geometry
    starting from the offset, forming a continuous section of route where the
    maximum speed is the same and is indicated in value.
    """

    offset: Optional[int] = None
    """
    offset is the index value of the vertex of route geometry, which is the starting
    point of the segment.
    """

    value: Optional[float] = None
    """value denotes the maximum speed of this segment, in kilometers per hour.

    - A value of "-1" indicates that the speed is unlimited for this road segment.
    - A value of "0" indicates that there is no information about the maximum speed
      for this road segment.
    """


class RoadInfo(BaseModel):
    max_speed: Optional[List[RoadInfoMaxSpeed]] = None
    """
    An array of objects containing maximum speed, in kilometers per hour, for each
    segment of the route. Each object represents one road segment.
    """


class SnappedPointLocation(BaseModel):
    latitude: float
    """Latitude of the snapped point."""

    longitude: float
    """Longitude of the snapped point."""


class SnappedPoint(BaseModel):
    bearing: float
    """
    The bearing, calculated as the angle from true north in clockwise direction, of
    the route leading to the next snapped point from the current snapped_point, in
    radians. In case of the last snapped_point of the route, the bearing indicates
    the direction of the route to the previous snapped_location.
    """

    distance: float
    """The distance of the snapped point from the original input coordinate in meters."""

    location: SnappedPointLocation
    """The latitude and longitude coordinates of the snapped point."""

    name: str
    """The name of the street or road that the input coordinate snapped to."""

    original_index: int = FieldInfo(alias="originalIndex")
    """
    The index of the input path coordinate point to which this snapped point
    corresponds to.
    """


class SnapToRoadSnapResponse(BaseModel):
    distance: Optional[int] = None
    """The total distance of the snapped path in meters."""

    geojson: Optional[Geojson] = None
    """A GeoJSON object with details of the snapped path.

    This object is returned when the geometry field is set to geojson in the input
    request, otherwise it is not present in the response. The contents of this
    object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    geometry: Optional[List[str]] = None
    """
    An array of strings containing the encoded geometries of snapped paths in
    polyline or polyline6 format.
    """

    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    road_info: Optional[RoadInfo] = None
    """
    An object containing the maximum speed information for each road segment present
    in the route.
    """

    snapped_points: Optional[List[SnappedPoint]] = FieldInfo(alias="snappedPoints", default=None)
    """An array of objects.

    Each object provides the details of a path coordinate point snapped to the
    nearest road.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On normal responses, the value will be Ok. Indicative HTTP error codes are
    returned for different errors. See the [API Errors Codes](#api-error-codes)
    section below for more information.
    """
