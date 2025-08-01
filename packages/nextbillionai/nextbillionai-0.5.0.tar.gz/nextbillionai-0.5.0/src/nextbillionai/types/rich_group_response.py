# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["RichGroupResponse"]


class RichGroupResponse(BaseModel):
    id: Optional[int] = None
    """Returns the unique ID of the restriction.

    This ID can be used for update, delete, get operations on the restriction using
    the available API methods.
    """

    area: Optional[str] = None
    """Returns the area to which the restriction belongs to."""

    bbox: Optional[object] = None
    """Returns the details of the bounding box containing the restriction."""

    comment: Optional[str] = None
    """
    Returns the comments that were provided for the restriction at the time of
    creating or updating the request.
    """

    create_at: Optional[datetime] = None
    """The timestamp at which the restriction was created."""

    direction: Optional[Literal["forward", "backward", "both"]] = None
    """
    Returns the direction of travel on the segments to which the restriction
    applies.
    """

    end_time: Optional[float] = None
    """The time when the restriction ceases to be in-effect. It is a UNIX timestamp."""

    geofence: Optional[object] = None
    """
    Returns the list of coordinates representing the area that was used to apply the
    given restriction. The geofence returned is same as that provided while creating
    or updating the restriction.
    """

    highway: Optional[str] = None
    """Returns the highway information on which the restriction applies to.

    If no highway is impacted by the restriction, then this field is not present in
    the response.
    """

    mode: Optional[List[str]] = None
    """Returns an array denoting all the traveling modes the restriction applies on."""

    name: Optional[str] = None
    """Returns the name of the restriction.

    This value is same as that provided at the time of creating or updating the
    restriction.
    """

    repeat_on: Optional[str] = None
    """Returns the time periods during which this restriction active or repeats on.

    The time values follow a
    [given format](https://wiki.openstreetmap.org/wiki/Key:opening_hours).
    """

    restriction_type: Optional[Literal["closure", "maxspeed", "fixedspeed", "parking", "turn", "truck"]] = None
    """Returns the type of restriction.

    This is the same value as provided when creating or updating the restriction.
    """

    speed: Optional[float] = None
    """Returns the fixed speed of segments.

    This field is not present in the response if the restriction type is not
    fixedspeed
    """

    speed_limit: Optional[float] = None
    """Returns the maximum speed of segments.

    This field is not present in the response if the restriction type is not
    maxspeed
    """

    start_time: Optional[float] = None
    """The time when the restriction starts to be in-effect. It is a UNIX timestamp."""

    state: Optional[Literal["enabled", "disabled", "deleted"]] = None
    """Returns the state of the "restriction" itself - enabled, disabled or deleted.

    It does not denote if the restriction is actually in effect or not.
    """

    status: Optional[Literal["active", "inactive"]] = None
    """Returns the status of the restriction at the time of making the request i.e.

    whether the restriction is in force or not. It will have one of the following
    values: active or inactive.

    Please note that this field can not be directly influenced by the users. It will
    always be calculated using the start_time, end_time and repeat_on parameters.
    """

    update_at: Optional[datetime] = None
    """The timestamp at which the restriction was updated."""
