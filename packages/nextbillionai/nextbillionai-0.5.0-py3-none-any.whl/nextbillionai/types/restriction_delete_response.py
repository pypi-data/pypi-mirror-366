# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["RestrictionDeleteResponse"]


class RestrictionDeleteResponse(BaseModel):
    id: Optional[float] = None
    """It is the unique ID of the restriction."""

    state: Optional[str] = None
    """Returns the state of the restriction. It would always be deleted."""
