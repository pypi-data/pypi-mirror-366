# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .pagination import Pagination
from .asset_details import AssetDetails

__all__ = ["AssetListResponse", "Data"]


class Data(BaseModel):
    list: Optional[List[AssetDetails]] = None
    """An array of objects, with each object representing one asset."""

    page: Optional[Pagination] = None
    """An object with pagination details of the search results.

    Use this object to implement pagination in your application.
    """


class AssetListResponse(BaseModel):
    data: Optional[Data] = None
    """A data object containing the list of assets."""

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
