# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .track_location import TrackLocation

__all__ = ["LocationGetLastResponse", "Data"]


class Data(BaseModel):
    location: Optional[TrackLocation] = None
    """An object with details of the tracked location.

    Please note that if there are no tracking records for an asset, no location data
    will be returned.
    """


class LocationGetLastResponse(BaseModel):
    data: Optional[Data] = None
    """
    An object containing the information about the last tracked location of the
    requested asset.
    """

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
