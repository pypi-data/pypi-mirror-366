# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "OptimizationComputeResponse",
    "Location",
    "Trip",
    "TripGeojson",
    "TripLeg",
    "TripLegStep",
    "TripLegStepGeojson",
    "Waypoint",
    "WaypointLocation",
]


class Location(BaseModel):
    latitude: Optional[float] = None
    """Latitude coordinate of the location."""

    longitude: Optional[float] = None
    """Longitude coordinate of the location."""


class TripGeojson(BaseModel):
    geometry: Optional[str] = None
    """The encoded geometry of the geojson in the trip."""

    properties: Optional[str] = None
    """Additional properties associated with the trip."""

    type: Optional[
        Literal[
            "Point",
            "MultiPoint",
            "LineString",
            "MultiLineString",
            "Polygon",
            "MultiPolygon",
            "GeometryCollection",
            "Feature",
            "FeatureCollection",
            "Link",
        ]
    ] = None
    """The type of the GeoJSON object."""


class TripLegStepGeojson(BaseModel):
    geometry: Optional[str] = None
    """The encoded geometry of the geojson in the step."""

    properties: Optional[str] = None
    """Additional properties associated with the step."""

    type: Optional[
        Literal[
            "Point",
            "MultiPoint",
            "LineString",
            "MultiLineString",
            "Polygon",
            "MultiPolygon",
            "GeometryCollection",
            "Feature",
            "FeatureCollection",
            "Link",
        ]
    ] = None
    """The type of the GeoJSON object."""


class TripLegStep(BaseModel):
    distance: Optional[float] = None
    """Distance of the step object in meters."""

    duration: Optional[float] = None
    """Duration of the step object in seconds."""

    geojson: Optional[TripLegStepGeojson] = None
    """The GeoJSON representation of the step."""

    geometry: Optional[str] = None
    """Encoded geometry of the step in the selected format."""


class TripLeg(BaseModel):
    distance: Optional[float] = None
    """Distance of leg in metres."""

    duration: Optional[float] = None
    """Duration of leg in seconds."""

    steps: Optional[List[TripLegStep]] = None
    """An array of step objects."""

    summary: Optional[str] = None
    """Summary of the leg object."""


class Trip(BaseModel):
    distance: Optional[float] = None
    """Distance of the trip in meters."""

    duration: Optional[float] = None
    """Duration of the trip in seconds"""

    geojson: Optional[TripGeojson] = None
    """The GeoJSON representation of the route."""

    geometry: Optional[str] = None
    """polyline or polyline6 format of route geometry."""

    legs: Optional[List[TripLeg]] = None


class WaypointLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude coordinate of the waypoint."""

    longitude: Optional[float] = None
    """Longitude coordinate of the waypoint."""


class Waypoint(BaseModel):
    location: Optional[WaypointLocation] = None
    """Describes the location of the waypoint."""

    name: Optional[str] = None
    """Name of the waypoint."""

    trips_index: Optional[int] = None
    """Denotes the ID of a trip. Starts with 0."""

    waypoint_index: Optional[int] = None
    """Denotes the id of a waypoint.

    The first waypoint is denoted with 0. And onwards with 1, 2 etc.
    """


class OptimizationComputeResponse(BaseModel):
    code: Optional[str] = None
    """A string indicating the state of the response.

    This is a separate code than the HTTP status code. On normal valid responses,
    the value will be Ok.
    """

    location: Optional[Location] = None
    """Contains the latitude and longitude of a location"""

    trips: Optional[List[Trip]] = None
    """An array of 0 or 1 trip objects. Each object has the following schema."""

    waypoints: Optional[List[Waypoint]] = None
    """Each waypoint is an input coordinate snapped to the road and path network."""
