# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .geofence.geofence import Geofence

__all__ = ["GeofenceContainsResponse", "Data", "DataResultList", "DataResultListResult"]


class DataResultListResult(BaseModel):
    contain: Optional[bool] = None
    """true when a coordinate point in locations is contained by this geofence."""

    location_index: Optional[int] = None
    """Index of the coordinate point in the input locations."""


class DataResultList(BaseModel):
    geofence_detail: Optional[Geofence] = None
    """An object with details of the geofence."""

    geofence_id: Optional[str] = None
    """ID of the geofence provided/generated at the time of creating the geofence."""

    result: Optional[List[DataResultListResult]] = None
    """
    An array of objects with results of the contains check for each of the
    coordinate points in locations against the geofence represented by geofence_id.
    """


class Data(BaseModel):
    result_list: Optional[List[DataResultList]] = None
    """
    An array of objects containing each of the geofences provided in the geofences
    input. If geofences in not provided then the array will return all the geofences
    associated with the key
    """


class GeofenceContainsResponse(BaseModel):
    data: Optional[Data] = None

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
