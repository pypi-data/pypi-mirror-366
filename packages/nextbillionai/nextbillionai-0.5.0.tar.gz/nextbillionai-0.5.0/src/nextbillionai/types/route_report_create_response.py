# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = [
    "RouteReportCreateResponse",
    "Mileage",
    "MileageSegment",
    "MileageSegmentCountry",
    "MileageSegmentState",
    "MileageSummary",
    "RoadSummary",
    "RoadSummarySegment",
    "RoadSummarySegmentMaxSpeed",
    "RoadSummarySegmentRoadClass",
    "RoadSummarySummary",
]


class MileageSegmentCountry(BaseModel):
    distance: Optional[float] = None
    """Represents the total distance of this segment, in meters."""

    length: Optional[int] = None
    """
    Represents a sequence of ‘n’ consecutive vertices in the route geometry starting
    from the offset, forming a continuous section of route with a distance indicated
    in distancefield.
    """

    offset: Optional[int] = None
    """
    Represents the index value of the vertex of current segment's starting point in
    route geometry. First vertex in the route geometry has an offset of 0.
    """

    value: Optional[str] = None
    """Returns the name of the country in which the segment lies."""


class MileageSegmentState(BaseModel):
    distance: Optional[float] = None
    """Represents the real distance of this segment, in meters."""

    length: Optional[int] = None
    """
    Represents a sequence of ‘n’ consecutive vertices in the route geometry starting
    from the offset, forming a continuous section of route with a distance indicated
    in distancefield.
    """

    offset: Optional[int] = None
    """
    Represents the index value of the vertex of current segment's starting point in
    route geometry. First vertex in the route geometry has an offset of 0.
    """

    value: Optional[str] = None
    """Returns the name of the state in which the segment lies."""


class MileageSegment(BaseModel):
    country: Optional[List[MileageSegmentCountry]] = None
    """An array of objects containing country-wise break up of the route segments.

    Each object returns the segment details of a different country.
    """

    state: Optional[List[MileageSegmentState]] = None
    """An array of objects containing state-wise break up of the route segments.

    Each object returns the segment details of a different state.
    """


class MileageSummary(BaseModel):
    country: Optional[object] = None
    """
    A break up of country-wise distances that the route covers in key:value pair
    format.
    """

    state: Optional[object] = None
    """
    A break up of state-wise distances that the route covers specified in key:value
    pair format.
    """


class Mileage(BaseModel):
    segment: Optional[MileageSegment] = None
    """
    Returns the details of road segments that the route covers in different states
    and countries.
    """

    summary: Optional[MileageSummary] = None
    """
    Returns a summary of distances that the route covers in different states and
    countries.
    """


class RoadSummarySegmentMaxSpeed(BaseModel):
    distance: Optional[int] = None
    """Returns the total distance of this segment, in meters."""

    length: Optional[int] = None
    """
    Represents a sequence of ‘n’ consecutive vertices in the route geometry starting
    from the offset, forming a continuous section of route where the maximum speed
    is same and is indicated in value.
    """

    offset: Optional[int] = None
    """
    Represents the index value of the vertex of current segment's starting point in
    route geometry. First vertex in the route geometry has an offset of 0.
    """

    value: Optional[int] = None
    """Denotes the maximum speed of this segment, in kilometers per hour.

    - A value of “-1” indicates that the speed is unlimited for this road segment. -
      A value of “0” indicates that there is no information about the maximum speed
      for this road segment.
    """


class RoadSummarySegmentRoadClass(BaseModel):
    distance: Optional[int] = None
    """Returns the total distance of this segment, in meters."""

    length: Optional[int] = None
    """
    Represents a sequence of ‘n’ consecutive vertices in the route geometry starting
    from the offset, forming a continuous section of route with a distance indicated
    in distancefield.
    """

    offset: Optional[int] = None
    """
    Represents the index value of the vertex of current segment's starting point in
    route geometry. First vertex in the route geometry has an offset of 0.
    """

    value: Optional[str] = None
    """Returns the road class name to which the segment belongs."""


class RoadSummarySegment(BaseModel):
    max_speed: Optional[List[RoadSummarySegmentMaxSpeed]] = None
    """
    An array of objects returning the maximum speed of different segments that the
    route goes through.
    """

    road_class: Optional[List[RoadSummarySegmentRoadClass]] = None
    """
    An array of objects returning the details of road segments belonging to
    different road classes that the route goes through. Each object refers to a
    unique road class.
    """


class RoadSummarySummary(BaseModel):
    distance: Optional[float] = None
    """Returns the total distance of the route , in meters."""

    duration: Optional[float] = None
    """Returns the total duration of the route, in seconds."""

    has_bridge: Optional[bool] = None
    """A boolean value indicating if there are any bridges in the given route."""

    has_roundabout: Optional[bool] = None
    """A boolean value indicating if there are any roundabouts in the given route."""

    has_toll: Optional[bool] = None
    """A boolean value indicating if there are any tolls in the given route."""

    has_tunnel: Optional[bool] = None
    """A boolean value indicating if there are any tunnels in the given route."""

    road_class: Optional[object] = None
    """
    An object with details about the different types of road classes that the route
    goes through. Distance traversed on a given road class is also returned. The
    contents of this object follow the key:value pair format.
    """

    toll_distance: Optional[float] = None
    """Returns the total distance travelled on toll roads.

    This field is present in the response only when the has_toll property is true.
    """


class RoadSummary(BaseModel):
    segment: Optional[RoadSummarySegment] = None
    """Returns the segment-wise road class and max speed information of the route."""

    summary: Optional[RoadSummarySummary] = None
    """
    Returns an overview of the route with information about trip distance, duration
    and road class details among others.
    """


class RouteReportCreateResponse(BaseModel):
    geometry: Optional[List[str]] = None
    """An array of objects returning encoded geometry of the routes.

    Each object represents an individual route in the input.
    """

    mileage: Optional[List[Mileage]] = None
    """
    Returns the details of route segments in each state or country that the route
    passes through. Each object represents an individual route in the input request.
    """

    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    road_summary: Optional[List[RoadSummary]] = None
    """
    An array of objects returning a summary of the route with information about
    tolls, bridges, tunnels, segments, maximum speeds and more. Each array
    represents an individual route in the input request.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On normal responses, the value will be Ok. Indicative HTTP error codes are
    returned for different errors. See the
    [**API Errors Codes**](https://app.reapi.com/ws/hmx8aL45B5jjrJa8/p/vNNilNksLVz675pI/s/ealJmVGjTQv4x5Wi/edit/path/VYzo7gOlRsQQZo0U#api-error-codes)
    section below for more information.
    """
