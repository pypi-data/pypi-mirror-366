# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ConsolePreviewParams", "Circle", "CircleCenter", "Isochrone", "Polygon", "PolygonGeojson"]


class ConsolePreviewParams(TypedDict, total=False):
    type: Required[Literal["circle", "polygon", "isochrone"]]
    """Specify the type of the geofence that is being created."""

    circle: Circle
    """Provide the details to create a circular geofence.

    Please note that this object is mandatory when type is circle. When the type is
    not circle, the properties of this object will be ignored while creating the
    geofence.
    """

    custom_id: str
    """Set an unique ID for the new geofence.

    If not provided, an ID will be automatically generated in UUID format. A valid
    custom*id can contain letters, numbers, "-", & "*" only.

    Please note that the ID of a geofence can not be changed once it is created.
    """

    isochrone: Isochrone
    """Provide the details to create an isochrone based geofence.

    Use this object when type is isochrone. When the type is not isochrone, the
    properties of this object will be ignored while creating the geofence.
    """

    meta_data: object
    """Metadata of the geofence.

    Use this field to define custom attributes that provide more context and
    information about the geofence being created like country, group ID etc.

    The data being added should be in valid JSON object format (i.e. key and value
    pairs). Max size allowed for the object is 65kb.
    """

    name: str
    """Name of the geofence.

    Use this field to assign a meaningful, custom name to the geofence being
    created.
    """

    polygon: Polygon
    """Provide the details to create a custom polygon type of geofence.

    Please note that this object is mandatory when type is polygon. When the type is
    not polygon, the properties of this object will be ignored while creating the
    geofence.

    Self-intersecting polygons or polygons containing other polygons are invalid and
    will be removed while processing the request.

    Area of the polygon should be less than 2000 km<sup>2</sup>.
    """

    tags: List[str]
    """An array of strings to associate multiple tags to the geofence.

    tags can be used to search or filter geofences (using Get Geofence List method).

    Create valid tags using a string consisting of alphanumeric characters (A-Z,
    a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.
    """


class CircleCenter(TypedDict, total=False):
    lat: Required[float]
    """Latitude of the center location."""

    lon: Required[float]
    """Longitude of the center location."""


class Circle(TypedDict, total=False):
    center: Required[CircleCenter]
    """Coordinate of the location which will act as the center of a circular geofence."""

    radius: Required[float]
    """Radius of the circular geofence, in meters.

    Maximum value allowed is 50000 meters.
    """


class Isochrone(TypedDict, total=False):
    coordinates: Required[str]
    """
    Coordinates of the location, in [latitude,longitude] format, which would act as
    the starting point for identifying the isochrone polygon or the boundary of
    reachable area. This parameter is mandatory when type is isochrone.
    """

    contours_meter: int
    """The distance, in meters, for which an isochrone polygon needs to be determined.

    When provided, the API would create a geofence representing the area that can be
    reached after driving the given number of meters starting from the point
    specified in coordinates.

    The maximum distance that can be specified is 60000 meters (60km).

    At least one of contours_meter or contours_minute is mandatory when type is
    isochrone.
    """

    contours_minute: int
    """The duration, in minutes, for which an isochrone polygon needs to be determined.

    When provided, the API would create a geofence representing the area that can be
    reached after driving for the given number of minutes starting from the point
    specified in coordinates.

    The maximum duration that can be specified is 40 minutes.

    At least one of contours_meter or contours_minute is mandatory when type is
    isochrone.
    """

    denoise: float
    """
    A floating point value from 0.0 to 1.0 that can be used to remove smaller
    contours. A value of 1.0 will only return the largest contour for a given value.
    A value of 0.5 drops any contours that are less than half the area of the
    largest contour in the set of contours for that same value.
    """

    departure_time: int
    """
    A UNIX epoch timestamp in seconds format that can be used to set the departure
    time. The isochrone boundary will be determined based on the typical traffic
    conditions at the given time. If no input is provided for this parameter then
    the traffic conditions at the time of making the request are considered
    """

    mode: Literal["car", "truck"]
    """Set which driving mode the service should use to determine the isochrone line.

    For example, if you use car, the API will return an isochrone polygon that a car
    can cover within the specified time or after driving the specified distance.
    Using truck will return an isochrone that a truck can reach after taking into
    account appropriate truck routing restrictions.
    """


class PolygonGeojson(TypedDict, total=False):
    coordinates: Required[Iterable[Iterable[float]]]
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    geofence boundary.
    """

    type: Required[str]
    """Type of the geoJSON geometry. Should always be Polygon."""


class Polygon(TypedDict, total=False):
    geojson: Required[PolygonGeojson]
    """An object to collect geoJSON details of the geofence.

    The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """
