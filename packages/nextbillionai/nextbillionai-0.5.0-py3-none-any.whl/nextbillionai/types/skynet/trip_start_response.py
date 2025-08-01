# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["TripStartResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Returns the ID of the newly created trip.

    It will be same as the custom_id if that input was provided in the input
    request. Use this ID to manage this trip using other available Trip methods.
    """


class TripStartResponse(BaseModel):
    data: Optional[Data] = None

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
