# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["PlaceDeleteResponse"]


class PlaceDeleteResponse(BaseModel):
    msg: Optional[str] = None
    """
    This could be “Ok” representing success or “not found” representing error in
    processing the request.
    """

    status: Optional[str] = None
    """Represents the status of the response."""
