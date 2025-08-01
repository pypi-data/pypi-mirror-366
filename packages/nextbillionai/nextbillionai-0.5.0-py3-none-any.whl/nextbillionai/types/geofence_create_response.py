# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["GeofenceCreateResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Unique ID of the geofence created.

    It will be the same as custom_id, if provided. Else it will be an auto generated
    UUID. Please note this ID cannot be updated.
    """


class GeofenceCreateResponse(BaseModel):
    data: Optional[Data] = None
    """A data object containing the ID of the geofence created."""

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
