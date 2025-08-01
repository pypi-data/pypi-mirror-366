# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["BatchRetrieveResponse", "Response"]


class Response(BaseModel):
    response: Optional[object] = None
    """An object returning the routing solution of an individual query.

    The JSON format and structure of the response would vary depending on the
    routing endpoint used in each individual query. However, it will be consistent
    with standard response for a given routing endpoint.
    """

    status_code: Optional[int] = None
    """Returns the HTTP status code for the individual routing request.

    See the [API Errors Codes](#api-error-codes) section below for more information.
    """


class BatchRetrieveResponse(BaseModel):
    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    responses: Optional[List[Response]] = None
    """
    An array of objects returning the results of all the individual routing queries
    specified in the input. Each object represents the solution to an individual
    query in the input.
    """

    status: Optional[str] = None
    """Returns the overall status of the API request.

    Its value will always be one of success, failed, and pending.
    """

    track_id: Optional[str] = None
    """Returns the unique ID of the batch processing task."""
