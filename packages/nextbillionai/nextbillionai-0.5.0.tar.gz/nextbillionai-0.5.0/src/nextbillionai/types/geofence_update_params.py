# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["GeofenceUpdateParams", "Circle", "CircleCenter", "Isochrone", "Polygon", "PolygonGeojson"]


class GeofenceUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    circle: Circle
    """Use this object to update details of a circular geofence.

    Please note that this object is mandatory only when type is circle. When the
    type is not circle, the properties of this object will be ignored while creating
    the geofence.
    """

    isochrone: Isochrone
    """Use this object to update details of an isochrone based geofence.

    Please note that this object is mandatory only when type is isochrone. When the
    type is not isochrone, the properties of this object will be ignored while
    creating the geofence.
    """

    meta_data: object
    """Updated the meta_data associated with a geofence.

    Use this field to define custom attributes that provide more context and
    information about the geofence being updated like country, group ID etc.

    The data being added should be in valid JSON object format (i.e. key and value
    pairs). Max size allowed for the object is 65kb.
    """

    name: str
    """Use this parameter to update the name of a geofence.

    Users can assign meaningful custom names to their geofences.
    """

    polygon: Polygon
    """Use this object to update details of a custom polygon geofence.

    Please note that this object is mandatory only when type is polygon. When the
    type is not polygon, the properties of this object will be ignored while
    creating the geofence.

    Self-intersecting polygons or polygons containing other polygons are invalid and
    will be removed while processing the request.

    Area of the polygon should be less than 2000 km<sup>2</sup>.
    """

    tags: List[str]
    """Use this parameter to add/modify one or multiple tags of a geofence.

    tags can be used to search or filter geofences (using Get Geofence List method).

    Valid values for updating tags consist of alphanumeric characters (A-Z, a-z,
    0-9) along with the underscore ('\\__') and hyphen ('-') symbols.
    """

    type: Literal["circle", "polygon", "isochrone"]
    """Use this parameter to update the type of a geofence.

    Please note that you will need to provide required details for creating a
    geofence of the new type. Check other parameters of this method to know more.
    """


class CircleCenter(TypedDict, total=False):
    lat: float
    """Latitude of the center location."""

    lon: float
    """Longitude of the center location."""


class Circle(TypedDict, total=False):
    center: Required[CircleCenter]
    """
    Use this parameter to update the coordinate of the location which will act as
    the center of a circular geofence.
    """

    radius: float
    """Use this parameter to update the radius of the circular geofence, in meters.

    Maximum value allowed is 50000 meters.
    """


class Isochrone(TypedDict, total=False):
    contours_meter: int
    """
    Use this parameter to update the distance, in meters, for which an isochrone
    polygon needs to be determined. When provided, the API would create a geofence
    representing the area that can be reached after driving the given number of
    meters starting from the point specified in coordinates.

    The maximum distance that can be specified is 60000 meters (60km).

    At least one of contours_meter or contours_minute is mandatory when type is
    isochrone.
    """

    contours_minute: int
    """
    Use this parameter to update the duration, in minutes, for which an isochrone
    polygon needs to be determined. When provided, the API would create a geofence
    representing the area that can be reached after driving for the given number of
    minutes starting from the point specified in coordinates.

    The maximum duration that can be specified is 40 minutes.

    At least one of contours_meter or contours_minute is mandatory when type is
    isochrone.
    """

    coordinates: str
    """
    Use this parameter to update the coordinates of the location, in
    [latitude,longitude] format, which would act as the starting point for
    identifying the isochrone polygon or the boundary of reachable area.
    """

    denoise: float
    """
    A floating point value from 0.0 to 1.0 that can be used to remove smaller
    contours. A value of 1.0 will only return the largest contour for a given value.
    A value of 0.5 drops any contours that are less than half the area of the
    largest contour in the set of contours for that same value.

    Use this parameter to update the denoise value of the isochrone geofence.
    """

    departure_time: int
    """
    Use this parameter to update the departure_time, expressed as UNIX epoch
    timestamp in seconds. The isochrone boundary will be determined based on the
    typical traffic conditions at the given time.

    If no input is provided for this parameter then, the traffic conditions at the
    time of making the request are considered by default. Please note that because
    of this behavior the geofence boundaries may change even if the departure_time
    was not specifically provided at the time of updating the geofence.
    """

    mode: str
    """
    Use this parameter to update the driving mode that the service should use to
    determine the isochrone line. For example, if you use car, the API will return
    an isochrone polygon that a car can cover within the specified time or after
    driving the specified distance. Using truck will return an isochrone that a
    truck can reach after taking into account appropriate truck routing
    restrictions.
    """


class PolygonGeojson(TypedDict, total=False):
    geometry: Iterable[Iterable[float]]
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    geofence boundary.
    """

    type: str
    """Type of the geoJSON geometry. Should always be Polygon."""


class Polygon(TypedDict, total=False):
    geojson: PolygonGeojson
    """An object to collect geoJSON details of the polygon geofence.

    The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """
