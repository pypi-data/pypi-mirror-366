# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BatchCreateResponse"]


class BatchCreateResponse(BaseModel):
    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    status: Optional[str] = None
    """Returns the overall status of the API request.

    Its value will belong to one of success, failed, and pending. It can also
    contain HTTP error codes in case of a failed request or operation.
    """

    track_id: Optional[str] = None
    """Returns the unique ID of the batch processing task.

    Use this ID using the GET request to retrieve the solution once the task
    processing is completed.
    """
