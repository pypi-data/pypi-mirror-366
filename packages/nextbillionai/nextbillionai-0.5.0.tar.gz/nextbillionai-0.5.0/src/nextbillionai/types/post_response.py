# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["PostResponse"]


class PostResponse(BaseModel):
    id: Optional[str] = None
    """
    A unique ID which can be used in the Optimization GET method to retrieve the
    result of optimization.
    """

    message: Optional[str] = None
    """Displays an acknowledgement message once the job is submitted."""

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages/codes
    are returned in case of errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """

    warnings: Optional[List[str]] = None
    """Display the warnings for the given input parameters, values and constraints."""
