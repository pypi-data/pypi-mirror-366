# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .geofence.geofence import Geofence

__all__ = ["GeofenceRetrieveResponse", "Data"]


class Data(BaseModel):
    geofence: Optional[Geofence] = None
    """An object with details of the geofence."""


class GeofenceRetrieveResponse(BaseModel):
    data: Optional[Data] = None

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
