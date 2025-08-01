# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["BatchCreateResponse", "Data"]


class Data(BaseModel):
    ids: Optional[List[str]] = None


class BatchCreateResponse(BaseModel):
    data: Optional[Data] = None
    """A data object containing the IDs of the geofences created."""

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
