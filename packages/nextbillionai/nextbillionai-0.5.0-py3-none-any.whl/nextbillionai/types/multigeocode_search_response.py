# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .multigeocode.place_item import PlaceItem

__all__ = ["MultigeocodeSearchResponse", "Entity", "EntityDataSource"]


class EntityDataSource(BaseModel):
    ref_id: Optional[str] = FieldInfo(alias="refId", default=None)
    """
    This parameter represents the unique reference ID associated with the data
    source.
    """

    source: Optional[str] = None
    """This parameter represents the source of the data."""

    status: Optional[Literal["enable", "disable"]] = None
    """This parameter indicates if a place is searchable."""


class Entity(BaseModel):
    data_source: Optional[EntityDataSource] = FieldInfo(alias="dataSource", default=None)
    """It contains information about the dataset that returns the specific result"""

    doc_id: Optional[str] = FieldInfo(alias="docId", default=None)
    """The unique NextBillion ID for the result item.

    This ID can be used as input in “Get Place”, “Update Place”, “Delete Place”
    methods.
    """

    place: Optional[List[PlaceItem]] = None
    """
    This parameter represents the place details, including geographical information,
    address and other related information.
    """

    score: Optional[int] = None
    """Integer value representing how good the result is.

    Higher score indicates a better match between the search query and the result.
    This can be used to accept or reject the results depending on how “relevant” a
    result is, for a given use case
    """


class MultigeocodeSearchResponse(BaseModel):
    entities: Optional[List[Entity]] = None
    """An array of objects containing the search result response.

    Each object represents one place returned in the search response. An empty array
    would be returned if no matching place is found.
    """
