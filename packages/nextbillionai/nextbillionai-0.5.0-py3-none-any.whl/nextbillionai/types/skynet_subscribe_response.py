# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SkynetSubscribeResponse"]


class SkynetSubscribeResponse(BaseModel):
    id: Optional[str] = None
    """Subscription ID as provided in the input action message."""

    error: Optional[str] = None
    """Returns the error message when status: error.

    Otherwise, response doesn't contain this field.
    """

    status: Optional[str] = None
    """Status of the action. It can have only two values - "success" or "error"."""

    timestamp: Optional[int] = None
    """
    Returns the UNIX timestamp, in milliseconds format, when the web-socket returns
    the action response.
    """
