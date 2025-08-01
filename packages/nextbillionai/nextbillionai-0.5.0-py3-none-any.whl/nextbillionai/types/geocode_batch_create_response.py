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

__all__ = ["GeocodeBatchCreateResponse", "Item", "ItemScoring"]


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

    position: Optional[Position] = None
    """Returns the location coordinates of the result."""

    scoring: Optional[ItemScoring] = None
    """Score of the result. A higher score indicates a closer match."""

    title: Optional[str] = None
    """The localized display name of this result item."""


class GeocodeBatchCreateResponse(BaseModel):
    items: Optional[List[Item]] = None
    """
    The results are presented as a JSON list of candidates in ranked order
    (most-likely to least-likely) based on the matched location criteria.
    """
