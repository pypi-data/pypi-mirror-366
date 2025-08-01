# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Access"]


class Access(BaseModel):
    lat: Optional[float] = None
    """The latitude of the access point of the search result."""

    lng: Optional[float] = None
    """The longitude of the access point of the search result."""
