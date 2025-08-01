# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["ConsoleSearchResponse", "Data", "DataResult"]


class DataResult(BaseModel):
    id: str
    """ID of goefence. Could be empty string."""

    name: str
    """Name of goefence. Could be empty string."""


class Data(BaseModel):
    result: List[DataResult]


class ConsoleSearchResponse(BaseModel):
    data: Data

    status: str
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
