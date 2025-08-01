# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Pagination"]


class Pagination(BaseModel):
    hasmore: Optional[bool] = None
    """
    A boolean value indicating whether there are more items available beyond the
    current page.
    """

    page: Optional[int] = None
    """An integer value indicating the current page number (starting at 0)."""

    size: Optional[int] = None
    """An integer value indicating the maximum number of items retrieved per page."""

    total: Optional[int] = None
    """An integer value indicating the total number of items available in the data set.

    This parameter can be used to calculate the total number of pages available.
    """
