# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["AssetCreateResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Unique ID of the asset created.

    It will be the same as custom_id, if provided. Else it will be an auto generated
    UUID. Please note this ID cannot be updated.
    """


class AssetCreateResponse(BaseModel):
    data: Optional[Data] = None
    """An object containing the ID of the asset created."""

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
