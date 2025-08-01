# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["TripStop"]


class TripStop(BaseModel):
    geofence_id: Optional[str] = None
    """
    Returns the ID of the geofence that was used to indicate the area to make a
    stop.
    """

    meta_data: Optional[object] = None
    """
    Returns any meta data that was added to provide additional information about the
    stop.
    """

    name: Optional[str] = None
    """
    Returns the name of the stop that was provided when configuring this stop for
    the trip.
    """
