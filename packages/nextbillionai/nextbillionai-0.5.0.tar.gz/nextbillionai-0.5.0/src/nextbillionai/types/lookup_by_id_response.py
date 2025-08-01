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

__all__ = ["LookupByIDResponse", "Item"]


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

    map_view: Optional[MapView] = FieldInfo(alias="mapView", default=None)
    """
    The bounding box enclosing the geometric shape (area or line) that an individual
    result covers. place typed results have no mapView.
    """

    position: Optional[Position] = None
    """Returns the location coordinates of the result."""

    title: Optional[str] = None
    """The localized display name of this result item."""


class LookupByIDResponse(BaseModel):
    items: Optional[List[Item]] = None
    """
    The results are presented as a JSON list of candidates in ranked order
    (most-likely to least-likely) based on the matched location criteria.
    """
