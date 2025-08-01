# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["V2RetrieveResultResponse", "Result", "ResultRoute", "ResultRouteStep", "ResultSummary", "ResultUnassigned"]


class ResultRouteStep(BaseModel):
    id: Optional[str] = None
    """Returns the ID of the task.

    The ID returned here are the same values that were provided for the given task
    in the jobs or the shipments objects of the input POST optimization request.

    **Note:** Since both integer and string value types are supported for job IDs,
    the value type returned for this field will depend on the value type provided in
    the input request.
    """

    arrival: Optional[int] = None
    """Returns the time at which the vehicle arrives at the step location.

    If time_windows is provided for the task it will be returned as an UNIX
    timestamp expressed in seconds. When time_windows is not provided, it is
    returned as the total duration, in seconds, elapsed since the start of the
    route.

    Please note it includes all the other durations as well (setup, service,
    waiting).
    """

    depot: Optional[str] = None
    """
    For step type "start" or "end", this field returns the ID of the depot relevant
    to that step. For "start" steps, the field will contain the ID of the depot from
    which the vehicle commenced its journey. Conversely, for "end" steps, the field
    will hold the ID of the depot where the vehicle concluded its trip.

    Please note that start_depot_ids or end_depot_ids input for the vehicle must be
    configured to get this field in the response for respective step types in a
    route.
    """

    description: Optional[str] = None
    """Returns the description of this step.

    The description returned here are the same values that were provided for the
    given task in the jobs or the shipments objects of the input POST optimization
    request.
    """

    distance: Optional[int] = None
    """
    Returns the distance covered, in meters, from the start of the route and up
    until the current step.

    Please note that the value of this parameter accumulates with each step. In case
    , the travel_cost: air_distance, then the distance here represents straight line
    distance.
    """

    duration: Optional[int] = None
    """
    Returns the total drive time, in seconds, from the start of the route up until
    the start of the step. Please note that this value does not include any other
    category of durations (service, wait, setup) and the value of this parameter
    accumulates with each step.
    """

    late_by: Optional[str] = None
    """
    Returns the amount of time, in seconds, by which the vehicle is late when
    arriving at this step. Please note this field is present only when there is a
    non-zero value for vehicle lateness, otherwise it is not present in the
    response.
    """

    load: Optional[List[int]] = None
    """Returns the load on the vehicle after completing this step.

    In case of multiple dimensions, loads of each type are returned by a matching
    number of elements in the array.
    """

    location: Optional[List[float]] = None
    """
    Returns the location coordinates of the step in the \\[[latitude, longitude\\]]
    format.

    The index of this location is also returned by the location_index parameter.
    """

    location_index: Optional[int] = None
    """
    Returns the index (in the location array) of the location coordinates where the
    step is performed. The index will always be in the range of \\[[0, length of
    location array).

    Actual coordinates are also returned by the location parameter.
    """

    metadata: Optional[object] = None
    """
    Returns the custom information that was provided when the given task (job /
    pickup / delivery) was configured. This field would not be present for the tasks
    that were not provided with any metadata. It will also be not present for
    “start” and “end” steps.
    """

    projected_location: Optional[List[float]] = None
    """
    In case this step is part of a task group, this field returns the location
    coordinates of the point, in \\[[latitude, longitude\\]] format, which was used as a
    common stop for all grouped tasks.
    """

    run: Optional[int] = None
    """
    When a vehicle is configured to make multiple runs to the depot (via
    max_depot_runs), this field returns the iteration to which the step belongs to.
    Each run will begin with a "start" step from the depot's location and conclude
    with an "end" step at either the last task's or the configured end location.
    """

    service: Optional[int] = None
    """
    Returns the service time, in seconds, for the task when the step type is not
    start or end.

    When the step type is start or end , the field also returns the service time, in
    seconds, spent at the depot when if the vehicle is starting or completing the
    trip at one of the depots.
    """

    setup: Optional[int] = None
    """Returns the setup time, in seconds, for the task."""

    snapped_location: Optional[List[float]] = None
    """
    Returns the coordinates after snapping the location of this step to a nearby
    road. Please note that this field will not be available in the response when
    custom duration or distance matrix were used for cost calculations.
    """

    type: Optional[str] = None
    """Returns the type of the step.

    Its value will always be one of the following: start, job, pickup, delivery,
    end. In case the type is start or end, steps object will not have the id field.
    """

    waiting_time: Optional[int] = None
    """Returns the wait time of the vehicle at this step, in seconds."""


class ResultRoute(BaseModel):
    adopted_capacity: Optional[List[int]] = None
    """Returns the capacity configuration of the vehicle that was used for this route.

    This field would return either the vehicle's capacity or one of the
    alternative_capacities provided in the input request.
    """

    cost: Optional[int] = None
    """Returns the cost of the route.

    The unit of cost type depends on the value of travel_cost attribute in the
    optimization request.
    """

    delivery: Optional[List[int]] = None
    """
    Returns the total quantities, for each dimension (or unit), of deliveries
    performed in the route. Please note that when both shipments and jobs are
    provided, this field corresponds to the sum of quantities delivered as part of
    the assigned shipments and jobs on the route.
    """

    description: Optional[str] = None
    """Return the description of the assigned vehicle.

    It would be the same as that provided in the description field of vehicles part
    of the input POST optimization request.
    """

    distance: Optional[float] = None
    """Returns the total distance of the route, in meters."""

    duration: Optional[int] = None
    """Returns the total drive duration of the route, in seconds."""

    geometry: Optional[str] = None
    """Returns the geometry of this route encoded in polyline format."""

    metadata: Optional[object] = None
    """Returns the custom information that was provided when the vehicle was
    configured.

    This field would not be present for the vehicles that were not provided with any
    metadata.
    """

    pickup: Optional[List[int]] = None
    """
    Returns the total quantities, for each dimension (or unit), of pickups performed
    in the route. Please note that when both shipments and jobs are provided, this
    field corresponds to the sum of quantities picked-up as part of the assigned
    shipments and jobs on the route.
    """

    priority: Optional[int] = None
    """Returns the sum of priorities of all tasks on the route."""

    profile: Optional[str] = None
    """Returns the profile of the vehicle."""

    revenue: Optional[int] = None
    """Returns the revenue earned by fulfilling the task on this route.

    Please note this field is present only when the revenue inputs are provided in
    the input, otherwise it is not present in the response.
    """

    service: Optional[int] = None
    """
    Returns the total service time spent on the tasks or depots on the route, in
    seconds.
    """

    setup: Optional[int] = None
    """Returns the total setup time, in seconds, for the tasks assigned on the route."""

    steps: Optional[List[ResultRouteStep]] = None
    """This attribute contains the details of all the steps involved in the route.

    It is an array of objects with each object representing one step.
    """

    vehicle: Optional[str] = None
    """Returns the ID of the vehicle that was assigned to the route.

    The value type will be same as the value type provided in the input request.
    """

    vehicle_overtime: Optional[int] = None
    """Returns the total vehicle overtime for the route, in seconds.

    Please note this field is present only when there is a non-zero value for
    vehicle overtime, otherwise it is not present in the response.
    """

    waiting_time: Optional[int] = None
    """Returns the total waiting time of the vehicle on the route, in seconds."""


class ResultSummary(BaseModel):
    cost: Optional[int] = None
    """Returns the total cost of all the routes returned in the solution.

    The unit of cost type depends on the value of travel_cost attribute in the
    optimization request.
    """

    delivery: Optional[List[int]] = None
    """Returns the sum of all quantities that were delivered in the optimized solution.

    If quantities of different dimensions were delivered, then a matching number of
    elements is returned in the delivery array.

    Please note that when both shipments and jobs are provided, this field
    corresponds to the sum of quantities delivered as part of all the assigned
    shipments and jobs .
    """

    distance: Optional[float] = None
    """Returns the total distance of all routes, in meters.

    It is equal to the sum of distances of individual routes.
    """

    duration: Optional[int] = None
    """Returns the total drive time, in seconds, needed to cover all routes.

    Please note that it does not include the service, setup or the waiting durations
    elapsed on these routes.
    """

    num_late_visits: Optional[int] = None
    """
    Returns the total number of tasks across all routes that failed to start within
    their scheduled time windows.
    """

    pickup: Optional[List[int]] = None
    """Returns the sum of all quantities that were picked-up in the optimized solution.

    If quantities of different dimensions were picked-up, then a matching number of
    elements is returned in the pickup array.

    Please note that when both shipments and jobs are provided, this field
    corresponds to the sum of quantities picked-up as part of all the assigned
    shipments and jobs .
    """

    priority: Optional[int] = None
    """Returns the sum of priorities of all tasks that were assigned."""

    revenue: Optional[int] = None
    """Returns the revenue earned by completing all the assigned tasks.

    Overall profit earned by following the suggested route plan can be inferred by
    subtracting the cost of the solution from the reported revenue.
    """

    routes: Optional[int] = None
    """Returns the total number of routes in the solution."""

    service: Optional[int] = None
    """Returns the total service time, in seconds, for all the routes in the solution.

    It is equal to the sum of service time of individual tasks that were assigned
    and the time spent loading/unloading items at designated depots by all vehicles.
    """

    setup: Optional[int] = None
    """Returns the total setup time, in seconds, of all assigned tasks.

    It is equal to the sum of setup time of individual tasks that were assigned.
    """

    total_visit_lateness: Optional[int] = None
    """
    Returns the total duration, in seconds, that tasks across all routes were
    delayed from starting after their scheduled time windows had passed.
    """

    unassigned: Optional[int] = None
    """Returns the number of unfulfilled tasks in the solution."""

    waiting_time: Optional[int] = None
    """
    Returns the sum of durations spent waiting, in seconds, by vehicles on all
    routes.
    """


class ResultUnassigned(BaseModel):
    id: Optional[str] = None
    """Returns the ID of the unassigned task.

    The ID returned is the same as that provided for the given task in the jobs or
    the shipments part in the input POST optimization request.

    **Note:** Since both integer and string value types are supported for task IDs,
    the value type returned for this field will depend on the value type provided in
    the input request for the unassigned task.
    """

    location: Optional[List[float]] = None
    """
    Returns the location of the unassigned tasks in the \\[[latitude, longitude\\]]
    format.
    """

    outsourcing_cost: Optional[int] = None
    """Returns the cost of outsourcing the task.

    This is the same value as provided in the input. The field is present only if a
    outsourcing_cost was provided for the unassigned task.
    """

    reason: Optional[str] = None
    """Returns the most likely reason due to which the task remained unassigned.

    The optimization service can capture the following causes of tasks remaining
    unassigned, among others:

    - unmatched skills of the tasks
    - insufficient capacity of vehicle to accommodate the tasks
    - time_window requirements of the tasks or the vehicles
    - violation of vehicle’s max_activity_waiting_time constraint
    - violation of vehicle’s max_tasks or max_stops constraints
    - violation of vehicle’s max_distance or max_travel_time constraints
    - task unassigned due to zone constraints
    - task unassigned due to depot constraints
    - task unassigned due to load type incompatibility constraints
    - task unassigned due to max time in vehicle constraint
    - task unassigned as it is unprofitable
    - task unassigned due to low outsourcing cost
    - task unassigned due to infeasible conditions specified in relations attribute
    """

    type: Optional[str] = None
    """Returns the type of the task that was unassigned.

    Will always belong to one of job, pickup, or delivery.
    """


class Result(BaseModel):
    code: Optional[int] = None
    """A custom code representing the status of the result.

    A code other than 0, represents an internal error. In case of codes other than
    0, please verify the parameter values, constraints and locations. If the issue
    does not resolve, please reach out to NextBillion at
    [support@nextbillion.ai](mailto:support@nextbillion.ai).
    """

    error: Optional[str] = None
    """Returns the error message for unfulfilled optimization jobs.

    This field will not be present in the response in case there are no errors.
    """

    routes: Optional[List[ResultRoute]] = None
    """
    An array of objects containing the details of each route in the optimized
    solution. Each object represents one route.
    """

    routing_profiles: Optional[object] = None
    """Returns all the routing profiles used in the solution.

    If no routing profiles were provided in the input or if the vehicles tagged to
    profiles were not used in the solution, the "default" routing properties are
    returned. Default routing properties are indicated by options.routing in the
    input.
    """

    summary: Optional[ResultSummary] = None
    """An object to describe the summarized result of the optimization request.

    This object can be useful to quickly get an overview of the important result
    parameters.
    """

    unassigned: Optional[List[ResultUnassigned]] = None
    """
    An array of objects containing the details of unassigned tasks in the optimized
    solution. Each object represents one task.
    """


class V2RetrieveResultResponse(BaseModel):
    description: Optional[str] = None
    """
    Returns the description of the optimization job as given in the input POST
    optimization request. This field will not be present in the response if no
    description was provided in the input request.
    """

    message: Optional[str] = None
    """
    Returns the message in case of errors or failures, otherwise a blank string is
    returned.
    """

    result: Optional[Result] = None
    """An object containing the details of the optimized routes."""

    status: Optional[Literal["Ok", "Error"]] = None
    """
    It indicates the overall status or result of the API request denoting whether
    the operation was successful or did it encounter any errors.
    """
