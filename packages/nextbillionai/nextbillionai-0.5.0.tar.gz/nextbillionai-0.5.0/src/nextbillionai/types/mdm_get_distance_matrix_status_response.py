# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["MdmGetDistanceMatrixStatusResponse"]


class MdmGetDistanceMatrixStatusResponse(BaseModel):
    code: Optional[Literal["Ok", "Processing", "Failed"]] = None
    """A code representing the status of the request."""

    output_addr: Optional[str] = None
    """Returns the GCS result of a successful task.

    Please note that this is an internal field.

    _internal field, the gcs result of specific task if task is success._
    """

    result_link: Optional[str] = None
    """
    Returns the link for the result file (csv format) once the task is completed
    successfully.
    """

    status: Optional[str] = None
    """Returns the status detail of the result.

    Indicative error messages/codes are returned in case of errors. See the
    [API Error Codes](#api-error-codes) section below for more information.
    """
