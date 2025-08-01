# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["JsonRetrieveResponse", "Row", "RowElement"]


class RowElement(BaseModel):
    distance: Optional[float] = None
    """Distance of the route from an origin to a destination, in meters."""

    duration: Optional[float] = None
    """Duration of the trip from an origin to a destination, in seconds."""


class Row(BaseModel):
    elements: Optional[List[RowElement]] = None
    """An array of objects.

    Each elements array corresponds to a single origins coordinate and contains
    objects with distance and duration values for each of the destinations. The
    details in the first elements array correspond to the first origins point and
    the first object corresponds to the first destinations point and so on.
    """


class JsonRetrieveResponse(BaseModel):
    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    rows: Optional[List[Row]] = None
    """Container object for a response with an array of arrays structure."""

    status: Optional[str] = None
    """A string indicating the state of the response.

    On normal responses, the value will be Ok. Indicative HTTP error codes are
    returned for different errors. See the [API Errors Codes](#api-error-codes)
    section below for more information.
    """
