# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from ..pagination import Pagination

__all__ = [
    "EventListResponse",
    "Data",
    "DataList",
    "DataListPrevLocation",
    "DataListPrevLocationLocation",
    "DataListTriggeredLocation",
    "DataListTriggeredLocationLocation",
]


class DataListPrevLocationLocation(BaseModel):
    lat: Optional[float] = None
    """Latitude of the prev_location tracked for the asset."""

    lon: Optional[float] = None
    """Longitude of the prev_location tracked for the asset."""


class DataListPrevLocation(BaseModel):
    bearing: Optional[float] = None
    """
    If available, this property returns the heading of the asset from true north in
    clockwise direction, at the prev_location tracked for the asset.
    """

    location: Optional[DataListPrevLocationLocation] = None
    """prev_location information of the asset."""

    meta_data: Optional[object] = None
    """Returns the custom data added during the location information upload."""

    speed: Optional[float] = None
    """
    If available, this property returns the speed of the asset, in meters per
    second, at the prev_location of the asset.
    """

    timestamp: Optional[int] = None
    """
    A UNIX epoch timestamp in milliseconds representing the time at which the asset
    was at the prev_location.
    """


class DataListTriggeredLocationLocation(BaseModel):
    lat: Optional[float] = None
    """Latitude of the triggered_location of the event."""

    lon: Optional[float] = None
    """Longitude of the triggered_location of the event."""


class DataListTriggeredLocation(BaseModel):
    bearing: Optional[float] = None
    """
    If available, this property returns the heading of the asset from true north in
    clockwise direction, when the event was triggered.
    """

    location: Optional[DataListTriggeredLocationLocation] = None
    """An object with information about the location at which the event was triggered."""

    meta_data: Optional[object] = None
    """Returns the custom data added during the location information upload."""

    speed: Optional[float] = None
    """
    If available, this property returns the speed of the asset, in meters per
    second, when the event was triggered.
    """

    timestamp: Optional[int] = None
    """
    A UNIX epoch timestamp in milliseconds representing the time at which the asset
    was at the triggered_location.
    """


class DataList(BaseModel):
    asset_id: Optional[str] = None
    """ID of the asset.

    This is the same ID that was generated/provided at the time of creating the
    asset.
    """

    event_type: Optional[Literal["enter", "exit", "speeding", "idle"]] = None
    """Nature of the event triggered by the asset. It can have following values:

    - enter: When the asset enters a specific geofence

    - exit: When the asset moves out of a specific geofence.

    - speeding: When the asset exceeds the certain speed limit.

    - idle: When the asset exhibits idle or no activity.
    """

    extra: Optional[object] = None
    """Additional information about the event.

    Currently, this object returns the speed limit that was used to generate the
    over-speeding events, for a speeding type event.

    It is worth highlighting that, when the use_admin_speed_limit is true, the speed
    limit value will be obtained from the underlying road information. Whereas, if
    the use_admin_speed_limit is false, the speed limit will be equal to the
    customer_speed_limit value provided by the user when creating or updating the
    monitor.
    """

    geofence_id: Optional[str] = None
    """ID of the geofence associated with the event."""

    monitor_id: Optional[str] = None
    """ID of the monitor associated with the event."""

    monitor_tags: Optional[List[str]] = None
    """Tags associated with the monitor."""

    prev_location: Optional[DataListPrevLocation] = None
    """
    An object with details of the asset at the last tracked location before the
    event was triggered.
    """

    timestamp: Optional[int] = None
    """
    A UNIX epoch timestamp in milliseconds representing the time at which the event
    was added/created.
    """

    triggered_location: Optional[DataListTriggeredLocation] = None
    """
    An object with details of the asset at the location where the event was
    triggered.
    """

    triggered_timestamp: Optional[int] = None
    """
    A UNIX epoch timestamp in milliseconds representing the time at which the event
    was triggered.
    """


class Data(BaseModel):
    list: Optional[List[DataList]] = None
    """An array of objects with each object on the list representing one event."""

    page: Optional[Pagination] = None
    """An object with pagination details of the search results.

    Use this object to implement pagination in your application.
    """


class EventListResponse(BaseModel):
    data: Optional[Data] = None
    """
    An object containing the information about the event history for the requested
    asset.
    """

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
