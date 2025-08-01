# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Position"]


class Position(BaseModel):
    lat: Optional[str] = None
    """The latitude of the searched place."""

    lng: Optional[str] = None
    """The longitude of the searched place."""
