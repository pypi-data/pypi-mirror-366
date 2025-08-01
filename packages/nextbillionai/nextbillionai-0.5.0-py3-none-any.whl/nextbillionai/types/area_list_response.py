# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["AreaListResponse", "AreaListResponseItem"]


class AreaListResponseItem(BaseModel):
    code: Optional[str] = None
    """Returns the code for the available area."""

    modes: Optional[List[str]] = None
    """Returns available traveling modes for the given area."""

    name: Optional[str] = None
    """Returns the name of the available area."""

    timezone: Optional[float] = None
    """Returns the offset from UTC time."""


AreaListResponse: TypeAlias = List[AreaListResponseItem]
