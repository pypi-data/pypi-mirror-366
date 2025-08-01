# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .rich_group_response import RichGroupResponse

__all__ = ["RestrictionListResponse", "Meta"]


class Meta(BaseModel):
    limit: Optional[int] = None
    """An integer value indicating the maximum number of items retrieved per "page".

    This is the same number as provided for the limit parameter in input.
    """

    offset: Optional[int] = None
    """
    An integer value indicating the number of items in the collection that were
    skipped to display the current response. Please note that the offset starts from
    zero.
    """

    total: Optional[int] = None
    """
    An integer value indicating the total number of items available in the data set.
    """


class RestrictionListResponse(BaseModel):
    data: Optional[List[RichGroupResponse]] = None
    """An array of objects containing the details of the restrictions returned.

    Each object represents one restriction.
    """

    meta: Optional[Meta] = None
