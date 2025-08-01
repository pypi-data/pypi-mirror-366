# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .geofence import Geofence
from ..._models import BaseModel

__all__ = ["BatchListResponse", "Data"]


class Data(BaseModel):
    list: List[Geofence]
    """
    An array of objects containing the details of the geofences returned matching
    the IDs provided. Each object represents one geofence.
    """


class BatchListResponse(BaseModel):
    data: Data

    status: str
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
