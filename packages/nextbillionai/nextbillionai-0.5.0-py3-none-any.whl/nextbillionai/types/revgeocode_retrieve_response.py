# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .access import Access
from .address import Address
from .._models import BaseModel
from .contacts import Contacts
from .map_view import MapView
from .position import Position
from .categories import Categories

__all__ = [
    "RevgeocodeRetrieveResponse",
    "Item",
    "ItemOpeningHours",
    "ItemOpeningHoursTimeRange",
    "ItemOpeningHoursTimeRangeEndTime",
    "ItemOpeningHoursTimeRangeStartTime",
    "ItemScoring",
]


class ItemOpeningHoursTimeRangeEndTime(BaseModel):
    date: Optional[str] = None
    """The date to which the subsequent closing time details belong to."""

    hour: Optional[int] = None
    """The hour of the day when the place closes."""

    minute: Optional[int] = None
    """The minute of the hour when the place closes."""


class ItemOpeningHoursTimeRangeStartTime(BaseModel):
    date: Optional[str] = None
    """The date to which the subsequent open time details belong to."""

    hour: Optional[int] = None
    """The hour of the day when the place opens."""

    minute: Optional[int] = None
    """The minute of the hour when the place opens."""


class ItemOpeningHoursTimeRange(BaseModel):
    end_time: Optional[ItemOpeningHoursTimeRangeEndTime] = FieldInfo(alias="endTime", default=None)
    """Returns the closing time details."""

    start_time: Optional[ItemOpeningHoursTimeRangeStartTime] = FieldInfo(alias="startTime", default=None)
    """Returns the open time details."""


class ItemOpeningHours(BaseModel):
    time_ranges: Optional[List[ItemOpeningHoursTimeRange]] = FieldInfo(alias="timeRanges", default=None)
    """
    A collection of attributes with details about the opening and closing hours for
    each day of the week.
    """


class ItemScoring(BaseModel):
    field_score: Optional[object] = FieldInfo(alias="fieldScore", default=None)
    """
    A breakdown of how closely individual field of the result matched with the
    provided query q.
    """

    query_score: Optional[float] = FieldInfo(alias="queryScore", default=None)
    """
    A score, out of 1, indicating how closely the result matches with the provided
    query q .
    """


class Item(BaseModel):
    id: Optional[str] = None
    """The unique identifier for the result item."""

    access: Optional[Access] = None
    """
    An array returning the location coordinates of all the access points of the
    search result.
    """

    address: Optional[Address] = None
    """Postal address of the result item."""

    categories: Optional[List[Categories]] = None
    """The list of categories assigned to this place."""

    contacts: Optional[List[Contacts]] = None
    """Contact information like phone, email or website."""

    distance: Optional[int] = None
    """
    The distance "as the crow flies" from the search center to this result item in
    meters.
    """

    map_view: Optional[MapView] = FieldInfo(alias="mapView", default=None)
    """
    The bounding box enclosing the geometric shape (area or line) that an individual
    result covers. place typed results have no mapView.
    """

    opening_hours: Optional[ItemOpeningHours] = FieldInfo(alias="openingHours", default=None)
    """Returns the operating hours of the place, if available."""

    position: Optional[Position] = None
    """Returns the location coordinates of the result."""

    scoring: Optional[ItemScoring] = None
    """Score of the result. A higher score indicates a closer match."""

    title: Optional[str] = None
    """The localized display name of this result item."""


class RevgeocodeRetrieveResponse(BaseModel):
    items: Optional[List[Item]] = None
    """
    The results are presented as a JSON list of candidates in ranked order
    (most-likely to least-likely) based on the matched location criteria.
    """
