# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["MdmCreateDistanceMatrixResponse"]


class MdmCreateDistanceMatrixResponse(BaseModel):
    code: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages/codes
    are returned in case of errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """

    message: Optional[str] = None
    """Returns the error message in case a request fails.

    This field will not be present in the response, if a request is successfully
    submitted.
    """

    task_id: Optional[str] = None
    """
    A unique ID which can be used in the Asynchronous Distance Matrix GET method to
    retrieve the final result.
    """

    warning: Optional[List[str]] = None
    """Display the warnings, if any, for the given input parameters and values.

    In case there are no warnings then this field would not be present in the
    response.
    """
