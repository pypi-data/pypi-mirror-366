# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["NamespacedApikeyDeleteResponse"]


class NamespacedApikeyDeleteResponse(BaseModel):
    msg: Optional[str] = None
    """Its value is OK in case of a successful delete operation.

    Indicative error messages are returned otherwise, for different errors.
    """

    status: Optional[int] = None
    """A string indicating the state of the response.

    A successful delete operation ins indicated by an HTTP code of200. See the
    [API Error Codes](https://docs.nextbillion.ai/docs/tracking/api/live-tracking-api#api-error-codes)
    section below for possible values in case of errors.
    """
