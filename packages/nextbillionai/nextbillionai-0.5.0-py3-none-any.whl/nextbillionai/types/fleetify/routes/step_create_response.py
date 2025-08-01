# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .route_steps_response import RouteStepsResponse

__all__ = ["StepCreateResponse"]


class StepCreateResponse(BaseModel):
    data: Optional[RouteStepsResponse] = None

    message: Optional[str] = None
    """Returns the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[int] = None
    """Returns the status code of the response."""
