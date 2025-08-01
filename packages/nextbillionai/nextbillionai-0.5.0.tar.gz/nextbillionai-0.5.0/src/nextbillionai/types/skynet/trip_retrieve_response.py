# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .trip_stop import TripStop
from .asset.track_location import TrackLocation

__all__ = ["TripRetrieveResponse", "Data", "DataTrip"]


class DataTrip(BaseModel):
    id: Optional[str] = None
    """Returns the unique identifier of the trip."""

    asset_id: Optional[str] = None
    """
    Returns the ID of the asset linked to the trip when the trip was started or
    updated.
    """

    attributes: Optional[object] = None
    """
    Returns the attributes provided for the trip at the time of starting or updating
    it.
    """

    created_at: Optional[int] = None
    """
    Returns the time, expressed as UNIX epoch timestamp in milliseconds, when the
    trip was created.
    """

    description: Optional[str] = None
    """
    Returns the custom description for the trip as provided at the time of starting
    or updating the trip.
    """

    ended_at: Optional[int] = None
    """
    Returns the time, expressed as UNIX epoch timestamp in milliseconds, when the
    trip ended.
    """

    meta_data: Optional[object] = None
    """
    Returns the metadata containing additional information about the trip as
    provided at the time of starting or updating the trip.
    """

    name: Optional[str] = None
    """
    Returns the name for the trip as provided at the time of starting or updating
    the trip.
    """

    route: Optional[List[TrackLocation]] = None
    """
    An array of object returning the details of the locations tracked for the asset
    during the trip which has ended. Each object represents a single location that
    was tracked.

    Please note that this attribute will not be present in the response if no
    locations were tracked/uploaded during the trip.
    """

    started_at: Optional[int] = None
    """
    Returns the time, expressed as UNIX epoch timestamp in milliseconds, when the
    trip started.
    """

    state: Optional[str] = None
    """Returns the current state of the trip.

    The value will be "active" if the trip is still going on, otherwise the value
    returned would be "ended".
    """

    stops: Optional[List[TripStop]] = None
    """An array of objects returning the details of the stops made during the trip.

    Each object represents a single stop.
    """

    updated_at: Optional[int] = None
    """
    Returns the timeme, expressed as UNIX epoch timestamp in milliseconds, when the
    trip was last updated.
    """


class Data(BaseModel):
    trip: Optional[DataTrip] = None
    """An object containing the returned trip details."""


class TripRetrieveResponse(BaseModel):
    data: Optional[Data] = None
    """An container for the trip returned by the service."""

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
