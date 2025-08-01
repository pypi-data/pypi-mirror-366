# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .place_item import PlaceItem

__all__ = ["PlaceRetrieveResponse", "DataSorce"]


class DataSorce(BaseModel):
    ref_id: Optional[str] = FieldInfo(alias="refId", default=None)
    """
    This parameter represents the unique reference ID associated with the data
    source.
    """

    source: Optional[str] = None
    """
    This parameter represents the current dataset source of the information returned
    in the result.
    """

    status: Optional[Literal["enable", "disable"]] = None
    """
    This parameter indicates if a place is currently discoverable by search API or
    not.
    """


class PlaceRetrieveResponse(BaseModel):
    data_sorce: Optional[DataSorce] = FieldInfo(alias="dataSorce", default=None)
    """
    It displays the information about the current source and current status of the
    place. Use the “Update Place” method to change these values, as needed.
    """

    doc_id: Optional[str] = FieldInfo(alias="docId", default=None)
    """The unique NextBillion ID for the result item."""

    place: Optional[List[PlaceItem]] = None
    """
    This parameter represents the place details, including geographical information,
    address and other related information.
    """

    score: Optional[int] = None
    """It returns the system calculated weighted score of the place.

    It depends on how ‘richly’ the place was defined at the time of creation. In
    order to modify the score, use “Update Place” method and update information for
    parameters which are not set currently. As an alternative, you can directly
    update the score to a custom value.
    """
