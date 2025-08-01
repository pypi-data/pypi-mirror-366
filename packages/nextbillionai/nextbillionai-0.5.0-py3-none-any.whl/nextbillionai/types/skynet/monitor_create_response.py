# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["MonitorCreateResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Unique ID of the monitor created. Please note this ID cannot be updated."""


class MonitorCreateResponse(BaseModel):
    data: Optional[Data] = None
    """A data object containing the ID of the monitor created."""

    message: Optional[str] = None
    """Displays the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
