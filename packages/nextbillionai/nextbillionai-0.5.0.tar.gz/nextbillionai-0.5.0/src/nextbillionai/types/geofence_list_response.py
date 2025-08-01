# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .geofence.geofence import Geofence
from .skynet.pagination import Pagination

__all__ = ["GeofenceListResponse", "Data"]


class Data(BaseModel):
    list: Optional[List[Geofence]] = None

    page: Optional[Pagination] = None
    """An object with pagination details of the search results.

    Use this object to implement pagination in your application.
    """


class GeofenceListResponse(BaseModel):
    data: Optional[Data] = None

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
