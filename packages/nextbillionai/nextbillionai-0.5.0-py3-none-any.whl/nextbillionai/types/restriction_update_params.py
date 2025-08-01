# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RestrictionUpdateParams", "Segment", "Turn"]


class RestrictionUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    area: Required[str]
    """Specify the area name.

    It represents a region where restrictions can be applied. This is a custom field
    and it is recommended for the users to check with
    [NextBillion.ai](www.nextbillion.ai) support for the right value. Alternatively,
    users can invoke the _[Areas](#supported-areas)_ method to get a list of
    available areas for them.
    """

    name: Required[str]
    """Specify a custom, descriptive name for the restriction."""

    latlon: bool
    """Use this parameter to decide the format for specifying the geofence coordinates.

    If true, then the coordinates of geofence can be specified as
    "latitude,longitude" format, otherwise they should be specified in
    "longitude,latitude" format.
    """

    comment: str
    """
    Use this parameter to add any custom information about the restriction being
    created.
    """

    direction: Literal["forward", "backward", "both"]
    """
    Represents the traffic direction on the segments to which the restriction will
    be applied.
    """

    end_time: float
    """
    Provide a UNIX epoch timestamp in seconds, representing the time when the
    restriction should cease to be in-effect.
    """

    geofence: Iterable[Iterable[float]]
    """
    An array of coordinates denoting the boundary of an area in which the
    restrictions are to be applied. The format in which coordinates should be listed
    is defined by the latlon field.

    Geofences can be used to create all restriction types, except for a turn type
    restriction. Please note that segments is not required when using geofence to
    create restrictions.
    """

    height: int
    """
    Specify the maximum truck height, in centimeter, that will be allowed under the
    restriction. A value of 0 indicates no limit.

    Please note this parameter is effective only when restriction_type is truck. At
    least one of truck parameters - weight, height, width and truck - needs to be
    provided when restriction type is truck.
    """

    length: int
    """
    Specify the maximum truck length, in centimeter, that will be allowed under the
    restriction. A value of 0 indicates no limit.

    Please note this parameter is effective only when restriction_type is truck. At
    least one of truck parameters - weight, height, width and truck - needs to be
    provided when restriction type is truck.
    """

    mode: List[Literal["0w", "2w", "3w", "4w", "6w"]]
    """Provide the driving modes for which the restriction should be effective.

    If the value is an empty array or if it is not provided then the restriction
    would be applied for all modes.
    """

    repeat_on: str
    """It represents the days and times when the restriction is in effect.

    Users can use this property to set recurring or one-time restrictions as per the
    [given format](https://wiki.openstreetmap.org/wiki/Key:opening_hours) for
    specifying the recurring schedule of the restriction.

    Please provided values as per the local time of the region where the restriction
    is being applied.
    """

    segments: Iterable[Segment]
    """
    An array of objects to collect the details of the segments of a road on which
    the restriction has to be applied. Each object corresponds to a new segment.

    Please note that segments is mandatory for all restrtiction_type except turn.
    """

    speed: float
    """
    Provide the the fixed speed of the segment where the restriction needs to be
    applied. Please note that this parameter is mandatory when the restrictionType
    is fixedspeed.
    """

    speed_limit: float
    """
    Provide the the maximum speed of the segment where the restriction needs to be
    applied. Please note that this parameter is mandatory when the restrictionType
    is maxspeed.
    """

    start_time: float
    """
    Provide a UNIX epoch timestamp in seconds, representing the start time for the
    restriction to be in-effect.
    """

    tracks: Iterable[Iterable[float]]
    """Specify a sequence of coordinates (track) where the restriction is to be
    applied.

    The coordinates will be snapped to nearest road. Please note when using tracks,
    segments and turns are not required.
    """

    turns: Iterable[Turn]
    """
    An array of objects to collect the details of the turns of a road on which the
    restriction has to be applied. Each object corresponds to a new turn.

    Please note that turns is mandatory for when restrtiction_type=turn.
    """

    weight: int
    """Specify the maximum truck weight, in kilograms, that the restriction will allow.

    A value of 0 indicates no limit.

    Please note this parameter is effective only when restriction_type is truck. At
    least one of truck parameters - weight, height, width and truck - needs to be
    provided for is truck restriction type.
    """

    width: int
    """
    Specify the maximum truck width, in centimeter, that will be allowed under the
    restriction. A value of 0 indicates no limit.

    Please note this parameter is effective only when restriction_type is truck. At
    least one of truck parameters - weight, height, width and truck - needs to be
    provided when restriction type is truck.
    """


_SegmentReservedKeywords = TypedDict(
    "_SegmentReservedKeywords",
    {
        "from": float,
    },
    total=False,
)


class Segment(_SegmentReservedKeywords, total=False):
    to: float
    """An integer value representing the ID of the ending node of the segment."""


_TurnReservedKeywords = TypedDict(
    "_TurnReservedKeywords",
    {
        "from": int,
    },
    total=False,
)


class Turn(_TurnReservedKeywords, total=False):
    to: int
    """An integer value that represents the ID of the ending node of the turn."""

    via: int
    """
    An integer value that represents the ID of a node connecting from and to nodes
    of the turn.
    """
