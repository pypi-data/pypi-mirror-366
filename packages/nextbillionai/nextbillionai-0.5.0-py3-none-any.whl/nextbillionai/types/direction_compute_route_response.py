# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = [
    "DirectionComputeRouteResponse",
    "Route",
    "RouteEndLocation",
    "RouteGeojson",
    "RouteGeojsonGeometry",
    "RouteLeg",
    "RouteLegDistance",
    "RouteLegDuration",
    "RouteLegEndLocation",
    "RouteLegStartLocation",
    "RouteLegStep",
    "RouteLegStepDistance",
    "RouteLegStepDuration",
    "RouteLegStepEndLocation",
    "RouteLegStepGeojson",
    "RouteLegStepGeojsonGeometry",
    "RouteLegStepManeuver",
    "RouteLegStepManeuverCoordinate",
    "RouteLegStepStartLocation",
    "RouteStartLocation",
]


class RouteEndLocation(BaseModel):
    latitude: Optional[float] = None
    """latitude of the start_location."""

    longitude: Optional[float] = None
    """longitude of the start_location."""


class RouteGeojsonGeometry(BaseModel):
    coordinates: Optional[List[float]] = None
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    route geometry.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry."""


class RouteGeojson(BaseModel):
    geometry: Optional[RouteGeojsonGeometry] = None
    """An object with details of the geoJSON geometry of the route."""

    properties: Optional[str] = None
    """Property associated with the geoJSON shape."""

    type: Optional[str] = None
    """Type of the geoJSON object."""


class RouteLegDistance(BaseModel):
    value: Optional[float] = None


class RouteLegDuration(BaseModel):
    value: Optional[float] = None


class RouteLegEndLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the end_location of the leg."""

    longitude: Optional[float] = None
    """Longitude of the end_location of the leg."""


class RouteLegStartLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the start_location of the leg."""

    longitude: Optional[float] = None
    """Longitude of the start_location of the leg."""


class RouteLegStepDistance(BaseModel):
    value: Optional[float] = None


class RouteLegStepDuration(BaseModel):
    value: Optional[float] = None


class RouteLegStepEndLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the end_location of the step."""

    longitude: Optional[float] = None
    """Longitude of the end_location of the step."""


class RouteLegStepGeojsonGeometry(BaseModel):
    coordinates: Optional[List[float]] = None
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    step geometry.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry."""


class RouteLegStepGeojson(BaseModel):
    geometry: Optional[RouteLegStepGeojsonGeometry] = None
    """An object with details of the geoJSON geometry of the step."""

    properties: Optional[str] = None
    """Property associated with the geoJSON shape."""

    type: Optional[str] = None
    """Type of the geoJSON object."""


class RouteLegStepManeuverCoordinate(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the maneuver location."""

    longitude: Optional[float] = None
    """Longitude of the maneuver location."""


class RouteLegStepManeuver(BaseModel):
    bearing_after: Optional[int] = None
    """
    The clockwise angle from true north to the direction of travel immediately after
    the maneuver. Range of values is between 0-359.
    """

    bearing_before: Optional[int] = None
    """
    The clockwise angle from true north to the direction of travel immediately
    before the maneuver. Range of values is between 0-359.
    """

    coordinate: Optional[RouteLegStepManeuverCoordinate] = None
    """A coordinate pair describing the location of the maneuver."""

    maneuver_type: Optional[str] = None
    """A string indicating the type of maneuver."""

    modifier: Optional[str] = None
    """Modifier associated with maneuver_type."""


class RouteLegStepStartLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the start_location of the step."""

    longitude: Optional[float] = None
    """Longitude of the start_location of the step."""


class RouteLegStep(BaseModel):
    distance: Optional[RouteLegStepDistance] = None
    """An object containing step distance value, in meters."""

    duration: Optional[RouteLegStepDuration] = None
    """An object containing step duration value, in seconds."""

    end_location: Optional[RouteLegStepEndLocation] = None
    """Location coordinates of the point where the step ends."""

    geojson: Optional[RouteLegStepGeojson] = None
    """
    An object with geoJSON details of the step.This object is returned when the
    geometry field is set to geojson in the input request, otherwise it is not
    present in the response. The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    geometry: Optional[str] = None
    """Encoded geometry of the step in the selected format."""

    maneuver: Optional[RouteLegStepManeuver] = None
    """An object with maneuver details for the step."""

    start_location: Optional[RouteLegStepStartLocation] = None
    """Location coordinates of the point where the step starts."""


class RouteLeg(BaseModel):
    distance: Optional[RouteLegDistance] = None
    """An object containing leg distance value, in meters."""

    duration: Optional[RouteLegDuration] = None
    """An object containing leg duration value, in seconds."""

    end_location: Optional[RouteLegEndLocation] = None
    """Location coordinates of the point where the leg ends.

    Returned only when steps is true in the input request.
    """

    start_location: Optional[RouteLegStartLocation] = None
    """Location coordinates of the point where the leg starts.

    Returned only when steps is true in the input request.
    """

    steps: Optional[List[RouteLegStep]] = None
    """An array of objects with details of each step of the legs.

    Returned only when steps is true in the input request. An empty array is
    returned when steps is false in the input request.
    """


class RouteStartLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the start_location."""

    longitude: Optional[float] = None
    """Longitude of the start_location."""


class Route(BaseModel):
    distance: Optional[float] = None
    """The distance, in meters, for the complete trip."""

    duration: Optional[float] = None
    """The duration, in seconds, of the complete trip."""

    end_location: Optional[RouteEndLocation] = None
    """Location coordinates of the point where the route ends.

    It is the same as the destination in the input request. Returned only when steps
    is true in the input request.
    """

    geojson: Optional[RouteGeojson] = None
    """An object with geoJSON details of the route.

    This object is returned when the geometry field is set to geojson in the input
    request, otherwise it is not present in the response. The contents of this
    object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    geometry: Optional[str] = None
    """
    Encoded geometry of the returned route in the selected format and specified
    overview verbosity. This parameter is configured in the input request.
    """

    legs: Optional[List[RouteLeg]] = None
    """An array of objects returning the details about each leg of the route.

    waypoints split the route into legs.
    """

    start_location: Optional[RouteStartLocation] = None
    """Location coordinates of the point where the route starts.

    It is the same as the origin in the input request. Returned only when steps is
    true in the input request.
    """


class DirectionComputeRouteResponse(BaseModel):
    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    route: Optional[Route] = None
    """An object containing details about the returned route.

    Will contain multiple objects if more than one routes are present in the
    response.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On normal responses, the value will be Ok. Indicative HTTP error codes are
    returned for different errors. See the [API Errors Codes](#api-error-codes)
    section below for more information.
    """
