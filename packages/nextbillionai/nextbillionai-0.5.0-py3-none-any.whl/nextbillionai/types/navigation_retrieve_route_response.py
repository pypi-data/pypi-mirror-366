# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "NavigationRetrieveRouteResponse",
    "Route",
    "RouteEndLocation",
    "RouteGeojson",
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
    "RouteLegStepIntersection",
    "RouteLegStepIntersectionLane",
    "RouteLegStepIntersectionLocation",
    "RouteLegStepManeuver",
    "RouteLegStepManeuverCoordinate",
    "RouteLegStepManeuverVoiceInstruction",
    "RouteLegStepRoadShieldType",
    "RouteLegStepStartLocation",
    "RouteStartLocation",
]


class RouteEndLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the end_location."""

    longitude: Optional[float] = None
    """Longitude of the end_location."""


class RouteGeojson(BaseModel):
    geometry: Optional[str] = None

    properties: Optional[str] = None

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


class RouteLegDistance(BaseModel):
    value: Optional[int] = None


class RouteLegDuration(BaseModel):
    value: Optional[int] = None


class RouteLegEndLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of end_location of the leg."""

    longitude: Optional[float] = None
    """Longitude of end_location of the leg."""


class RouteLegStartLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of start_location of the leg."""

    longitude: Optional[float] = None
    """Longitude of start_location of the leg."""


class RouteLegStepDistance(BaseModel):
    value: Optional[int] = None


class RouteLegStepDuration(BaseModel):
    value: Optional[int] = None


class RouteLegStepEndLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of the end_location of the step."""

    longitude: Optional[float] = None
    """Longitude of the end_location of the step."""


class RouteLegStepGeojson(BaseModel):
    geometry: Optional[str] = None

    type: Optional[str] = None


class RouteLegStepIntersectionLane(BaseModel):
    indications: Optional[List[str]] = None
    """It represents actions associated with the lane.

    These indications describe the permitted maneuvers or directions that can be
    taken from the lane. Common indications include "turn left," "turn right," "go
    straight," "merge," "exit," etc.
    """

    valid: Optional[bool] = None
    """This indicates the validity of the lane.

    It specifies whether the lane is considered valid for making the indicated
    maneuver or if there are any restrictions or limitations associated with it.
    """


class RouteLegStepIntersectionLocation(BaseModel):
    latitude: Optional[float] = None
    """The latitude coordinate of the intersection."""

    longitude: Optional[float] = None
    """The longitude coordinate of the intersection."""

    name: Optional[str] = None
    """The name or description of the intersection."""


class RouteLegStepIntersection(BaseModel):
    bearings: Optional[List[int]] = None
    """A list of bearing values (e.g.

    [0,90,180,270]) that are available at the intersection. The bearings describe
    all available roads at the intersection.
    """

    classes: Optional[List[str]] = None
    """
    An array of strings representing the classes or types of roads or paths at the
    intersection. The classes can indicate the road hierarchy, such as a motorway,
    primary road, secondary road, etc.
    """

    entry: Optional[List[bool]] = None
    """
    A value of true indicates that the respective road could be entered on a valid
    route. false indicates that the turn onto the respective road would violate a
    restriction. Each entry value corresponds to the bearing angle at the same
    index.
    """

    intersection_in: Optional[int] = None
    """The number of incoming roads or paths at the intersection."""

    intersection_out: Optional[int] = None
    """The number of outgoing roads or paths from the intersection."""

    lanes: Optional[List[RouteLegStepIntersectionLane]] = None
    """An array of lane objects representing the lanes available at the intersection.

    If no lane information is available for an intersection, the lanes property will
    not be present.
    """

    location: Optional[RouteLegStepIntersectionLocation] = None
    """A [longitude, latitude] pair describing the location of the intersection."""


class RouteLegStepManeuverCoordinate(BaseModel):
    latitude: Optional[float] = None
    """The latitude coordinate of the maneuver."""

    longitude: Optional[float] = None
    """The longitude coordinate of the maneuver."""

    name: Optional[str] = None
    """The name or description of the maneuver location."""


class RouteLegStepManeuverVoiceInstruction(BaseModel):
    distance_along_geometry: Optional[int] = None

    instruction: Optional[str] = None
    """The guidance instructions for the upcoming maneuver"""

    unit: Optional[str] = None
    """Unit of the distance_along_geometry metric"""


class RouteLegStepManeuver(BaseModel):
    bearing_after: Optional[float] = None
    """
    The clockwise angle from true north to the direction of travel immediately after
    the maneuver. Range of values is between 0-359.
    """

    bearing_before: Optional[float] = None
    """
    The clockwise angle from true north to the direction of travel immediately
    before the maneuver. Range of values is between 0-359.
    """

    coordinate: Optional[RouteLegStepManeuverCoordinate] = None
    """A coordinate pair describing the location of the maneuver."""

    instruction: Optional[str] = None
    """A text instruction describing the maneuver to be performed.

    It provides guidance on the action to take at the maneuver location, such as
    "Turn left," "Go straight," "Exit the roundabout," etc.
    """

    maneuver_type: Optional[str] = None
    """A string indicating the type of maneuver."""

    muted: Optional[bool] = None
    """
    A boolean value indicating whether the voice instruction for the maneuver should
    be muted or not.
    """

    roundabout_count: Optional[int] = None
    """The number of roundabouts encountered so far during the route.

    This parameter is specific to roundabout maneuvers and indicates the count of
    roundabouts before the current one.
    """

    voice_instruction: Optional[List[RouteLegStepManeuverVoiceInstruction]] = None
    """An array of voice instruction objects associated with the maneuver.

    Each object provides additional details about the voice instruction, including
    the distance along the geometry where the instruction applies, the instruction
    text, and the unit of measurement.
    """


class RouteLegStepRoadShieldType(BaseModel):
    image_url: Optional[str] = None
    """The URL to fetch the road shield image."""

    label: Optional[str] = None
    """
    A label identifying the inscription on the road shield, such as containing the
    road number.
    """


class RouteLegStepStartLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of start_location of the step."""

    longitude: Optional[float] = None
    """Longitude of start_location of the step."""


class RouteLegStep(BaseModel):
    distance: Optional[RouteLegStepDistance] = None
    """An object containing step distance value, in meters."""

    driving_side: Optional[str] = None
    """
    Indicates the driving side of the road in case bidirectional traffic is allowed
    on the given segment. It can have two values: "left" & "right".
    """

    duration: Optional[RouteLegStepDuration] = None
    """An object containing step duration value, in seconds."""

    end_location: Optional[RouteLegStepEndLocation] = None
    """Location coordinates of the point where the step ends."""

    geojson: Optional[RouteLegStepGeojson] = None
    """The GeoJSON representation of the step."""

    geometry: Optional[str] = None
    """Encoded geometry of the step in the selected format."""

    intersections: Optional[List[RouteLegStepIntersection]] = None
    """
    An array of objects representing intersections (or cross-way) that the route
    passes by along the step. For every step, the very first intersection
    corresponds to the location of the maneuver. All intersections until the next
    maneuver are listed in this object.
    """

    maneuver: Optional[RouteLegStepManeuver] = None
    """An object with maneuver details for the step."""

    name: Optional[str] = None
    """The name of the step."""

    reference: Optional[str] = None
    """A reference for the step."""

    road_shield_type: Optional[RouteLegStepRoadShieldType] = None
    """An object containing road shield information."""

    start_location: Optional[RouteLegStepStartLocation] = None
    """Location coordinates of the point where the step starts."""


class RouteLeg(BaseModel):
    distance: Optional[RouteLegDistance] = None
    """An object containing leg distance value, in meters."""

    duration: Optional[RouteLegDuration] = None
    """An object containing leg duration value, in seconds."""

    end_location: Optional[RouteLegEndLocation] = None
    """Location coordinates of the point where the leg ends."""

    raw_duration: Optional[object] = None
    """The raw estimated duration of the leg in seconds."""

    start_location: Optional[RouteLegStartLocation] = None
    """Location coordinates of the point where the leg starts."""

    steps: Optional[List[RouteLegStep]] = None
    """An array of step objects containing turn-by-turn guidance for easy navigation."""


class RouteStartLocation(BaseModel):
    latitude: Optional[float] = None
    """Latitude of thestart_location."""

    longitude: Optional[float] = None
    """Longitude of the start_location."""


class Route(BaseModel):
    distance: Optional[float] = None
    """The distance, in meters, of the complete trip."""

    distance_full: Optional[float] = None
    """
    The total distance of the route, including additional details such as extra
    maneuvers or loops, in meters.
    """

    duration: Optional[int] = None
    """The duration, in seconds, of the complete trip."""

    end_location: Optional[RouteEndLocation] = None
    """Location coordinates of the point where the route ends."""

    geojson: Optional[RouteGeojson] = None
    """The GeoJSON representation of the route."""

    geometry: Optional[str] = None
    """
    Encoded geometry of the returned route as per the selected format in geometry
    and specified overview verbosity. Please note the overview will always be full
    when original_shape parameter is used in the input request.
    """

    legs: Optional[List[RouteLeg]] = None
    """An array of objects returning the details about each leg of the route.

    waypoints split the route into legs.
    """

    predicted_duration: Optional[float] = None
    """The predicted duration of the route based on real-time traffic conditions."""

    raw_duration: Optional[float] = None
    """The raw estimated duration of the route in seconds."""

    special_objects: Optional[object] = None
    """Special geospatial objects or landmarks crossed along the route."""

    start_location: Optional[RouteStartLocation] = None
    """Location coordinates of the point where the route starts."""

    weight: Optional[float] = None
    """A weight value associated with the route or leg."""


class NavigationRetrieveRouteResponse(BaseModel):
    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    routes: Optional[List[Route]] = None
    """
    An array of objects describing different possible routes from the starting
    location to the destination. Each object represents one route.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On normal responses, the value will be Ok. Indicative HTTP error codes are
    returned for different errors. See the [API Errors Codes](#api-error-codes)
    section below for more information.
    """

    warning: Optional[List[str]] = None
    """warning when facing unexpected behaviour"""
