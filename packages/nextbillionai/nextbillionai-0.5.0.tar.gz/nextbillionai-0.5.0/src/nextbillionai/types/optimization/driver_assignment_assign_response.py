# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .location import Location
from ..._models import BaseModel

__all__ = [
    "DriverAssignmentAssignResponse",
    "Result",
    "ResultAlternateAssignment",
    "ResultAlternateAssignmentAssignment",
    "ResultTrip",
    "ResultTripVehicle",
    "ResultTripVehicleSteps",
    "ResultUnassignedOrder",
]


class ResultAlternateAssignmentAssignment(BaseModel):
    pickup_eta: Optional[int] = None
    """Returns the ETA to the order's pickup location for the given vehicle."""

    vehicle_id: Optional[str] = None
    """Returns the vehicle ID which could potentially be assigned to the given order."""


class ResultAlternateAssignment(BaseModel):
    assignments: Optional[List[ResultAlternateAssignmentAssignment]] = None
    """An array of objects containing the details of the alternate vehicle assignments.

    Each object represents an alternate vehicle assignment.
    """

    order_id: Optional[str] = None
    """Returns the order ID associated with the alternate assignments."""


class ResultTripVehicleSteps(BaseModel):
    distance: Optional[int] = None
    """
    Returns the driving distance, in meters, to the step's location from previous
    step's location. For the first step of a trip, distance indicates the driving
    distance from vehicle_current_location to the step's location.
    """

    eta: Optional[int] = None
    """
    Returns the driving duration, in seconds, to the step's location from previous
    step's location. For the first step of a trip, eta indicates the driving
    duration from vehicle_current_location to the step's location.
    """

    location: Optional[Location] = None
    """Location info."""

    order_id: Optional[str] = None
    """Returns the ID of the order.

    In case the step type is **ongoing**, an empty string is returned.
    """

    type: Optional[Literal["pickup", "dropoff", "ongoing"]] = None
    """Returns the type of the step. Currently, it can take following values:

    - **pickup:** Indicates the pickup step for an order
    - **dropoff:** Indicates the dropoff step for an order. It is returned only if
      dropoff_details was **true** in the input request.
    - **ongoing:** Indicates a step that the vehicle needs to complete on its
      current trip. This is returned in the response only when remaining_waypoints
      input was provided for the given vehicle.
    - **intermediate_waypoint:** Indicates an intermediate stop that the vehicle
      needs to complete in case multiple dropoffs are provided in the input.
    """


class ResultTripVehicle(BaseModel):
    id: Optional[str] = None
    """Returns the ID of the vehicle."""

    steps: Optional[ResultTripVehicleSteps] = None
    """
    A collection of objects returning the sequence of steps that the vehicle needs
    to perform for a trip.
    """

    vehicle_current_location: Optional[Location] = None
    """Location info."""


class ResultTrip(BaseModel):
    trip_id: Optional[str] = None
    """Returns a unique trip ID."""

    vehicle: Optional[ResultTripVehicle] = None
    """Returns the details of the vehicle, assigned order and the trip steps."""


class ResultUnassignedOrder(BaseModel):
    order_id: Optional[str] = None
    """Returns the ID of the order which remained unassigned."""

    unassigned_reason: Optional[str] = None
    """Returns the most probable reason due to which the order remained unassigned."""


class Result(BaseModel):
    alternate_assignments: Optional[List[ResultAlternateAssignment]] = None
    """
    An array of objects containing the details of the potential, alternate vehicle
    assignments for the orders in the input. This attribute will not be returned in
    the response if the alternate_assignments was not provided in the input. Each
    object represents alternate assignments for a single order.
    """

    available_vehicles: Optional[List[str]] = None
    """A collection of vehicles IDs that were not assigned to any orders.

    A null value is returned if there are no vehicles without an order assignment.
    """

    trips: Optional[List[ResultTrip]] = None
    """
    An collection of objects returning the trip details for each vehicle which was
    assigned to an order. Each object corresponds to one vehicle.
    """

    unassigned_orders: Optional[List[ResultUnassignedOrder]] = None
    """A collection of objects listing the details of orders which remained unassigned.

    Each object represents a single order. A null value is returned if there are no
    unassigned orders.
    """


class DriverAssignmentAssignResponse(BaseModel):
    message: Optional[str] = None
    """Displays indicative error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    result: Optional[Result] = None
    """An object containing the details of the assignments."""

    status: Optional[int] = None
    """An integer indicating the HTTP response code.

    See the
    [API Error Handling](https://docs.nextbillion.ai/optimization/driver-assignment-api#api-error-handling)
    section below for more information.
    """
