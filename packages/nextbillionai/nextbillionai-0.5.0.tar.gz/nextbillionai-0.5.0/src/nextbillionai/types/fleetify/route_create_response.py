# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .routing_response import RoutingResponse
from .routes.route_steps_response import RouteStepsResponse

__all__ = ["RouteCreateResponse", "Data", "DataDriver"]


class DataDriver(BaseModel):
    id: Optional[str] = None
    """
    Returns the ID of the driver as specified in the
    [NextBillion.ai](http://NextBillion.ai) Cloud Console.
    """

    email: Optional[str] = None
    """
    Returns the email of the driver as specified in the
    [NextBillion.ai](http://NextBillion.ai) Cloud Console.
    """

    fullname: Optional[str] = None
    """
    Returns the full name of the driver as specified in
    [NextBillion.ai](http://NextBillion.ai) Cloud Console.
    """


class Data(BaseModel):
    id: Optional[str] = None
    """Returns the unique ID of the dispatched route."""

    created_at: Optional[int] = None
    """
    Returns the UNIX timestamp, in seconds precision, at which this route dispatch
    request was created.
    """

    distance: Optional[int] = None
    """
    Returns the total route distance, in meters, for informative display in the
    driver app. It is the same as the value provided for distance field in the input
    request.
    """

    document_snapshot: Optional[List[object]] = None
    """
    Returns the details of the document that was specified in the input for
    collecting the proof-of-completion for all steps in the dispatched routes. Each
    object represents a new field in the document.
    """

    driver: Optional[DataDriver] = None
    """An object returning the details of the driver to whom the route was dispatched."""

    ro_request_id: Optional[str] = None
    """Returns the route optimization request ID which was used to dispatch the route.

    An empty string is returned if the corresponding input was not provided.
    """

    routing: Optional[RoutingResponse] = None
    """
    An object returning the routing characteristics that are used to generate the
    route and turn-by-turn navigation steps for the dispatched route. The route and
    navigation steps are available when driver uses the in-app navigation.

    Please note the routing characteristics returned here are the same as those
    configured in the input request. The fields which were not specified in the
    input will be returned as blanks.
    """

    short_id: Optional[str] = None
    """
    Returns a shorter unique ID of the dispatched route for easier referencing and
    displaying purposes.
    """

    steps: Optional[List[RouteStepsResponse]] = None
    """
    An array of objects containing the details of all steps to be performed as part
    of the dispatched route. Each object represents a single step during the route.
    """

    total_steps: Optional[int] = None
    """Returns the total number of steps in the dispatched route."""

    updated_at: Optional[int] = None
    """
    Returns the UNIX timestamp, in seconds precision, at which this route dispatch
    request was updated.
    """

    vehicle_id: Optional[str] = None
    """Returns the ID of the vehicle to which the route was dispatched.

    The vehicle ID returned here is the same as the one used in the route
    optimization request for the given vehicle. An empty string is returned if the
    ro_request_id was not provided in the input.
    """


class RouteCreateResponse(BaseModel):
    data: Optional[Data] = None
    """An array of objects containing the details of each step in the dispatched route.

    Each object represents a single step.
    """

    status: Optional[int] = None
    """Returns the status code of the response."""
