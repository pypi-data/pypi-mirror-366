# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .routing_response import RoutingResponse

__all__ = [
    "RouteRedispatchResponse",
    "Data",
    "DataCompletion",
    "DataDriver",
    "DataSteps",
    "DataStepsCompletion",
    "DataStepsMeta",
]


class DataCompletion(BaseModel):
    status: Optional[Literal["scheduled", "completed"]] = None
    """Returns the status of the route.

    It can take one of the following values - "scheduled", "completed".
    """


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


class DataStepsCompletion(BaseModel):
    status: Optional[str] = None
    """Returns the status of the step.

    It can take one of the following values - "scheduled", "completed".
    """


class DataStepsMeta(BaseModel):
    customer_name: Optional[str] = None
    """Returns the customer name associated with the step.

    It can configured in the input request using the metadata attribute of the step.
    """

    customer_phone_number: Optional[str] = None
    """Returns the customer's phone number associated with the step.

    It can configured in the input request using the metadata attribute of the step.
    """

    instructions: Optional[str] = None
    """Returns the custom instructions to carry out while performing the task.

    These instructions can be provided at the time of configuring the step details
    in the input request.
    """


class DataSteps(BaseModel):
    id: Optional[str] = None
    """Returns the unique ID of the step."""

    address: Optional[str] = None
    """Returns the postal address where the step is executed.

    Its value is the same as that specified in the input request when configuring
    the step details.
    """

    arrival: Optional[int] = None
    """
    Returns the scheduled arrival time of the driver at the step as an UNIX
    timestamp, in seconds precision. It is the same as that specified in the input
    request while configuring the step details.

    The timestamp returned here is only for informative display on the driver's app
    and it does not impact or get affected by the route generated.
    """

    completion: Optional[DataStepsCompletion] = None
    """Returns the completion status of the step."""

    created_at: Optional[int] = None
    """
    Returns the UNIX timestamp, in seconds precision, at which this step was
    created.
    """

    document_snapshot: Optional[List[object]] = None
    """
    Returns the details of the document that was used for collecting the proof of
    completion for the step. In case no document template ID was provided for the
    given step, then a null value is returned. Each object represents a new field in
    the document.
    """

    duration: Optional[int] = None
    """Returns the duration for layover or break type steps."""

    location: Optional[List[float]] = None
    """Returns the location coordinates where the step is executed."""

    meta: Optional[DataStepsMeta] = None
    """
    An object returning custom details about the step that were configured in the
    input request while configuring the step details. The information returned here
    will be available for display on the Driver's app under step details.
    """

    short_id: Optional[str] = None
    """
    Returns a unique short ID of the step for easier referencing and displaying
    purposes.
    """

    type: Optional[str] = None
    """Returns the step type.

    It can belong to one of the following: start, job , pickup, delivery, break,
    layover , and end. For any given step, it would be the same as that specified in
    the input request while configuring the step details.
    """

    updated_at: Optional[int] = None
    """
    Returns the UNIX timestamp, in seconds precision, at which this step was last
    updated.
    """


class Data(BaseModel):
    id: Optional[str] = None
    """Returns the unique ID of the route."""

    completed_steps: Optional[int] = None
    """Returns the number of steps already completed in the route."""

    completion: Optional[DataCompletion] = None
    """Returns the completion status of the route."""

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
    Returns a shorter unique ID of the route for easier referencing and displaying
    purposes.
    """

    steps: Optional[DataSteps] = None

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


class RouteRedispatchResponse(BaseModel):
    data: Optional[Data] = None
    """An array of objects containing the details of each step in the dispatched route.

    Each object represents a single step.
    """

    message: Optional[str] = None
    """Returns the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[int] = None
    """Returns the status code of the response."""
