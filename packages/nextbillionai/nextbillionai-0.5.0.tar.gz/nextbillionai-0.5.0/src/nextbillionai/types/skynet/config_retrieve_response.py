# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ConfigRetrieveResponse", "Data", "DataConfig"]


class DataConfig(BaseModel):
    webhook: Optional[List[str]] = None
    """An array of strings representing the list of webhooks.

    Webhooks are used to receive information, through POST requests, whenever any
    event is triggered.
    """


class Data(BaseModel):
    config: Optional[DataConfig] = None


class ConfigRetrieveResponse(BaseModel):
    data: Optional[Data] = None
    """A data object containing the config response."""

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
