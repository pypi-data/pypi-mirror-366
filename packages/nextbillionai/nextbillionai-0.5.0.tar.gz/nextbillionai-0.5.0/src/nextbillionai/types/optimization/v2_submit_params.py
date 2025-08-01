# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

from .job_param import JobParam
from .vehicle_param import VehicleParam
from .shipment_param import ShipmentParam

__all__ = [
    "V2SubmitParams",
    "Locations",
    "Depot",
    "Options",
    "OptionsConstraint",
    "OptionsGrouping",
    "OptionsGroupingOrderGrouping",
    "OptionsGroupingRouteGrouping",
    "OptionsObjective",
    "OptionsObjectiveCustom",
    "OptionsRouting",
    "Relation",
    "RelationStep",
    "Solution",
    "SolutionStep",
    "Unassigned",
    "Zone",
    "ZoneGeometry",
]


class V2SubmitParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    locations: Required[Locations]
    """
    The locations object is used to define all the locations that will be used
    during the optimization process. Read more about this attribute in the
    [Location Object](#location-object) section.
    """

    vehicles: Required[Iterable[VehicleParam]]
    """
    The vehicles attribute describes the characteristics and constraints of the
    vehicles that will be used for fulfilling the tasks. Read more about this
    attribute in the [Vehicle Object](#vehicle-object) section.
    """

    cost_matrix: Iterable[Iterable[int]]
    """
    An array of arrays to denote the user-defined costs of traveling between each
    pair of geographic coordinates mentioned in the location array. The number of
    arrays should be equal to the number of coordinate points mentioned in the
    location array and each array should contain the same number of elements as
    well. Please note that cost_matrix is effective only when
    travel_cost=customized. Read more about this attribute in the
    [Custom Cost Matrix](#custom-cost-matrix) section.
    """

    depots: Iterable[Depot]
    """depots object is used to collect the details of a depot.

    Depots can be used as a starting point and/or ending point for the routes and
    vehicles. They also can be used to fulfil pickup and delivery typejobs . The
    loads which are to be delivered at task locations will be picked from depots and
    loads picked-up from task locations will be delivered back to the depots. A
    depot can be configured using the following fields:
    """

    description: str
    """Define the optimization job using any custom message.

    This description is returned as is in the response.
    """

    distance_matrix: Iterable[Iterable[int]]
    """
    An array of arrays to denote the user-defined distances, in meters, for
    travelling between each pair of geographic coordinates mentioned in the location
    array. When this input is provided, actual distances between the locations will
    be ignored in favor of the values provided in this input for any distance
    calculations during the optimization process. The values provided here will also
    be used for cost calculations when travel_cost is “distance”.

    The number of arrays in the input should be equal to the number of coordinate
    points mentioned in the location array and each array, in turn, should contain
    the same number of elements as well.

    **Note:**

    - duration_matrix is mandatory when usingdistance_matrix.
    - When using distance_matrix route geometry will not be available in the
      optimized solution.
    """

    duration_matrix: Iterable[Iterable[int]]
    """
    An array of arrays to denote the user-defined durations, in seconds, for
    travelling between each pair of geographic coordinates mentioned in the location
    array. When this input is provided, actual durations between the locations will
    be ignored in favor of the values provided in the matrix for any ETA
    calculations during the optimization process. The values provided in the matrix
    will also be used for cost calculations when travel_cost is “duration”.

    The number of arrays in the input should be equal to the number of coordinate
    points mentioned in the location array and each array, in turn, should contain
    the same number of elements as well.

    Please note that, unlike distance_matrix, duration_matrix can be used
    independently in following cases:

    - when travel_cost is “duration”
    - when travel_cost is “customized” and a cost_matrix is provided

    Also, the route geometry will not be available in the optimized solution when
    using duration_matrix.
    """

    existing_solution_id: str
    """
    The previous optimization request id used to retrieve solution for
    reoptimization
    """

    jobs: Iterable[JobParam]
    """
    jobs object is used to collect the details of a particular job or task that
    needs to be completed as part of the optimization process. Each job can have
    either a pickup or delivery step, but not both. Read more about this attribute
    in the [Job Object](#job-object) section.

    Please note that either the jobs or the shipments attribute should be specified
    to build a valid request.
    """

    options: Options
    """
    It represents the set of options that can be used to configure optimization
    algorithms so that the solver provides a solution that meets the desired
    business objectives.
    """

    relations: Iterable[Relation]
    """relations attribute is an array of individual relation objects.

    type parameter and steps object are mandatory when using this attribute.

    Please note:

    - The soft constraints are **not** effective when using the relations attribute.
    - In case a given relation can't be satisfied, the optimizer will flag all the
      tasks involved in that "relation" as unassigned.

    Read more about this attribute in the [Relations Object](#relations-object)
    section.
    """

    shipments: Iterable[ShipmentParam]
    """
    The shipments object is used to collect the details of shipments that need to be
    completed as part of the optimization process.

    Each shipment should have a pickup and the corresponding delivery step.

    Please note that either the jobs or the shipments attribute should be specified
    to build a valid request.
    """

    solution: Iterable[Solution]
    """This attribute is related to the re-optimization feature.

    It allows for the previous optimization result to be provided in case new orders
    are received and the solution needs to be re-planned. The solution attribute
    should contain the same routes as the previous optimization result. solution
    attribute is an array of objects with each object corresponding to one route.
    """

    unassigned: Unassigned
    """unassigned attribute is related to the re-optimization feature.

    This attribute should contain the tasks that were not assigned during an earlier
    optimization process. Please note that the unassigned part in request should be
    consistent with the unassigned part in the previous optimization result.

    Users can reduce the number of unassigned tasks in the re-optimized solution, by
    following strategies such as:

    - Extending the time windows for vehicles or tasks to give more flexibility
    - Adding more vehicles to the optimization problem
    - Adjusting the priority of different tasks to balance the workload more evenly
    - Modifying other constraints or parameters to make the problem more solvable

    Ultimately, the goal is to minimize the number of unassigned tasks while still
    meeting all the necessary constraints and objectives.
    """

    zones: Iterable[Zone]
    """An array of objects to specify geometry of all the zones involved.

    Each object corresponds to a single zone. A valid zone can be a
    [geoJSON](https://datatracker.ietf.org/doc/html/rfc7946#page-9) polygon,
    multi-polygon or a geofence created using
    [NextBillion.ai](http://NextBillion.ai)’s
    [Geofence API](https://docs.nextbillion.ai/docs/tracking/api/geofence).

    Please note that

    - Each zone should have a geometry specified either throughgeometry or through
      the geofence_id parameter.
    - When zone IDs are not provided for individual tasks (jobs or shipments) then
      the API will automatically allocate zones based on the task’s geolocation and
      the geometries of the zones provided here. Otherwise, if the zone IDs are
      provided while configuring individual tasks, the zone IDs will override the
      geometries provided here.
    """


class Locations(TypedDict, total=False):
    location: Required[List[str]]
    """Indicate all the location coordinates that will be used during optimization.

    The coordinates should be specified in the format “latitude, longitude”. It is
    recommended to avoid adding duplicate location coordinates to this array. In
    case there are multiple tasks at the same location, users can repeat the index
    of the location while configuring all such tasks.

    Please use this array to determine the index of a location when setting the
    location_index parameter in jobs, shipments, vehicles or other parts of the
    request. The length of this array determines the valid values for location_index
    parameter.
    """

    id: int
    """A unique ID for the set of locations. It should be a positive integer."""

    approaches: List[Literal["unrestricted", "curb", '""(empty string)']]
    """Describe if the location is curbside.

    An array of strings indicates the side of the road from which to approach the
    location in the calculated route. If provided, the number of approaches must be
    equal to the number of locations. However, you can skip a coordinate and show
    its position in the list using “” (empty string). Please note these values are
    case-sensitive.
    """


class Depot(TypedDict, total=False):
    id: Required[str]
    """Provide an unique ID for the depot. The IDs are case sensitive."""

    location_index: Required[int]
    """
    Specify the index of coordinates (in the location array) denoting the depot’s
    location. The valid range of values is \\[[0, length of location array). If the
    location index exceeds the count of input locations in the location array, the
    API will report an error.

    Please note the location_index is mandatory when using the depots object.
    """

    description: str
    """Add a custom description for the depot."""

    service: int
    """
    Specify the time duration, in seconds, needed to load or unload the vehicle each
    time it starts or arrives at a depot, respectively. Default value is 0.
    """

    time_windows: Iterable[Iterable[int]]
    """
    Specify the time-windows during which the depot is operational and allows
    vehicles to be loaded / unloaded. The time periods should be expressed as a UNIX
    timestamp in seconds.

    Please note that:

    - Multiple time-windows can be provided but those time windows should not
      overlap with each other.
    - Time windows should always be specified in the format of \\[[start_timestamp,
      end_timestamp\\]].
    - Depot's time-windows are ineffective used when max_activity_waiting_time is
      specified in the input.
    - Using relations along with depot time-window is not allowed and the service
      will return an error.
    """


class OptionsConstraint(TypedDict, total=False):
    max_activity_waiting_time: int
    """
    This is a hard constraint which specifies the maximum waiting time, in seconds,
    for each step. It ensures that the vehicles do not have unreasonable wait times
    between jobs or shipments. This feature is useful for use cases where avoiding
    long wait times between jobs or shipments is a primary concern.

    Please note that the waiting time constraint applies to all tasks in the
    optimization request, ensuring that no single task exceeds the specified maximum
    waiting time. When being used together with relations attribute, this parameter
    is effective only for in_same_route relation type.
    """

    max_vehicle_overtime: int
    """This is a soft constraint for vehicle overtime.

    Overtime is defined as the time that a vehicle spends to complete a set of jobs
    after its time window has ended. max_vehicle_overtime attribute specifies the
    maximum amount of overtime a vehicle can have, in seconds. If a vehicle’s
    overtime exceeds this value, it will be considered a violation of this
    constraint.

    Please note that this constraint applies to all vehicles in the optimization
    request.
    """

    max_visit_lateness: int
    """
    This is a soft constraint for permissible delay, in seconds, to complete a job
    or shipment after its time window is over. If a job or shipment’s lateness
    exceeds this value, it will be considered a violation of this constraint.

    Please note that this constraint applies to all tasks in the optimization
    request. In case lateness duration needs to be applied for individual tasks,
    please use the max_visit_lateness parameter under jobs and shipments
    """


class OptionsGroupingOrderGrouping(TypedDict, total=False):
    grouping_diameter: float
    """
    Specify the straight line distance, in meters, which will be used to identify
    the tasks that should be grouped together. The default value is null.
    """


class OptionsGroupingRouteGrouping(TypedDict, total=False):
    penalty_factor: float
    """
    Specify a non-negative value which indicates the penalty of crossing zones on
    the same route. Default penalty value is 0.

    A higher value, for example 30.0, will place a higher penalty on zone violations
    and hence push the optimizer to prefer a solution without any zone violations,
    where all tasks in a single region are fulfilled before any tasks in other
    regions or outside the current region. Whereas a lower value, say 5.0, will
    place a lower penalty allowing the optimizer to return solutions which may have
    few violations, say a couple of routing zone violations in our example. A still
    lower penalty factor, like 1.0, may have several zone violations.
    """

    zone_diameter: float
    """
    Specify the diameter of the zone, routes within which will be prioritised before
    routes falling in other zones. Please note that zone_diameter is the straight
    line distance, in meters.
    """

    zone_source: Literal["system_generated", "custom_definition"]
    """Specify the source for creating boundaries of the routing zones.

    The default value is “system_generated”.

    - system_generated - Routing zone boundaries are created automatically by the
      optimizer based on the zone_diameter provided.
    - custom_definition - Custom routing zone boundaries should be provided by the
      user in input using the zones attribute. An error would be returned if the
      zones attribute is null or missing in the input request.
    """


class OptionsGrouping(TypedDict, total=False):
    order_grouping: OptionsGroupingOrderGrouping
    """Specify the criteria for grouping nearby tasks.

    The grouped tasks will be treated as one stop by the optimizer and no cost would
    be incurred when driver travels to different tasks within a group. Users can use
    this feature to model use cases like multiple deliveries in a building complex
    or a condo.

    Please note that when the multiple tasks are grouped together, only one setup
    time is considered for all such tasks. The durations of this setup time is equal
    to maximum setup time among all grouped tasks, if provided. On the other hand,
    the service time is applied to each task individually, as per the input provided
    when configuring those tasks.
    """

    proximity_factor: float
    """
    When specified, routes are built taking into account the distance to the nearest
    tasks. A higher proximity factor helps build routes with closer distances
    between neighboring tasks, whereas a lower proximity factor helps build routes
    with farther distances between neighboring tasks. As a result, the total number
    of routes in the solution can vary based on the configured proximity factor -
    more routes for higher factor and less routes with lower factor.

    In practice, such routes are more resistant to changes in task time windows:
    when the time window is postponed, the driver can drive to the next task and
    then return to the previous one.

    Please note that:

    - Valid values are \\[[0,10\\]]
    - Default value is 0.0.
    - It is recommended to use values lower values, in the range of \\[[0, 1\\]]. Higher
      values may adversely impact the solution metrics due to higher number of
      resulting routes: costs, mileage etc.
    """

    route_grouping: OptionsGroupingRouteGrouping
    """
    Specify the criteria for prioritising routes in a zone over routes that are part
    of another zone. As a result, all the tasks falling in a zone will be fulfilled
    before any tasks that are part of a different zone.
    """


class OptionsObjectiveCustom(TypedDict, total=False):
    type: Required[Literal["min", "min-max"]]
    """The type parameter accepts two inputs:

    - min: This type of customized objective will minimize the metric provided in
      the value parameter.
    - min-max: This type of customized objective will approximate an even
      distribution of the metric provided in the value parameter, among all the
      routes in solution.

    Please note that type is mandatory only when using custom attribute.
    """

    value: Required[Literal["vehicles", "completion_time", "travel_cost", "tasks"]]
    """
    The value parameter accepts four inputs, two of them are valid for min type and
    other two are valid for min-max type custom objective. Let’s look at the values
    for min type objective:

    - vehicles: Solver will minimize the number of vehicles used in the solution.
    - completion_time: Solver will minimize the total time taken to complete all
      tasks.

    The next set of values are acceptable when type is set to min-max.

    - tasks: Solver will evenly distribute the tasks on each route.
    - travel_cost: Solver will assign tasks such that the traveling cost of each
      route is within a close range of other routes. The travel cost metric
      considered here is the one set using objective.travel_cost .

    Please note that value is mandatory only when using custom attribute. The above
    values provide flexibility to tune the optimization algorithm to fulfill
    practical objectives beyond the relatively simpler time or distance minimization
    approaches.
    """


class OptionsObjective(TypedDict, total=False):
    allow_early_arrival: bool
    """Choose where the optimizer should schedule the driver’s wait time.

    When set to true the driver waits at the location of the task until its time
    window allows him to start the task. When set to false the driver waits at the
    location of the previous task and starts driving only at such a time that makes
    him arrive at the next task location in time to start the task as soon as he
    reaches.
    """

    custom: OptionsObjectiveCustom
    """
    The custom parameter is used to define special objectives apart from the simpler
    travel cost minimization objectives.
    """

    minimise_num_depots: bool
    """Specify whether to minimize the number of depots used in optimization routes."""

    solver_mode: Literal["flexible", "fast", "internal"]
    """
    If the input doesn’t include features of soft constraints, customized
    objectives, re-optimization, relations, max travel cost or automatic fixed cost,
    then user can select “optimal” to achieve a higher-speed and higher-quality
    optimization.

    If “optimal” mode is unable to process some features in the input, then it will
    still goes to “flexible” mode.
    """

    solving_time_limit: int
    """
    Specify the number of seconds within which the optimizer should ideally solve
    the optimization request.

    Please note that:

    - In case the specified time limit is not enough to generate a solution for a
      given problem set, the optimizer will continue processing until it arrives at
      a solution.
    - It is recommended to specify a duration of at least 5-7 minutes in case the
      input problem contains a large set of tasks or vehicles.
    """

    travel_cost: Literal["duration", "distance", "air_distance", "customized"]
    """
    The travel_cost parameter specifies the type of cost used by the solver to
    determine the routes.

    If the travel_cost parameter is set to distance, the solver will minimize the
    total distance traveled by vehicles while determining a solution. This objective
    would be useful in cases where the primary objective is to reduce fuel
    consumption or travel expenses.

    If the travel_cost parameter is set to duration, the solver will minimize the
    total time taken by the vehicles to complete all tasks while determining a
    solution. This objective would be useful in cases where the primary objective is
    to minimize completion time or maximize the number of orders fulfilled within a
    given time window.

    If the travel_cost parameter is set to air_distance, the solver will try to
    calculate the distance,in meters, between two points using the great-circle
    distance formula (i.e., the shortest distance between two points on a sphere)
    instead of the actual road distance. This would be useful in cases where the
    delivery locations are far apart and the road distance between them is
    significantly longer than the actual straight-line distance. For example, in
    Drone Delivery services.

    If the travel_cost is set to customized the solver would use the custom cost
    values provided by the user (in cost_matrix attribute) and prefer a solution
    with lower overall cost. This enables the user to have greater control over the
    routes preferred by the solver and hence the sequence in which the jobs are
    completed.
    """


class OptionsRouting(TypedDict, total=False):
    allow: List[Literal["taxi", "hov"]]

    avoid: List[
        Literal[
            "toll",
            "highway",
            "bbox",
            "left_turn",
            "right_turn",
            "sharp_turn",
            "uturn",
            "service_road",
            "ferry",
            "none ",
        ]
    ]
    """Specify the type of objects/maneuvers that the route should avoid.

    Please note that:

    - The values are case-sensitive.
    - When using avoid:bbox feature, users need to specify the boundaries of the
      bounding box to be avoided. Multiple bounding boxes can be provided
      simultaneously. Please note that bounding box is a hard filter and if it
      blocks all possible routes between given locations, a 4xx error is returned.
      Mention the bounding box boundaries in the following format: bbox:
      min_latitude,min_longitude,max_latitude,max_longitude.
    - When using avoid=sharp_turn, the range of allowed turn angles is \\[[120,240\\]]
      in the clockwise direction from the current road. Any roads with turn angles
      outside the range will be avoided.
    - If none is provided along with other values, an error is returned as a valid
      route is not feasible.
    """

    context: Literal["avgspeed"]
    """
    Use this parameter to apply a single speed value for all ETA and drive time
    calculations. In case, the travel_cost is set to duration then setting this
    parameter also impacts the cost of the solution.
    """

    cross_border: bool
    """
    Specify if crossing an international border is allowed for operations near
    border areas. When set to false, the API will prohibit any routes crossing
    international borders. When set to true, the service will return routes which
    cross the borders between countries, if required for the given set locations

    This feature is available in North America region only. Please get in touch with
    [support@nextbillion.ai](mailto:support@nextbillion.ai) to enquire/enable other
    areas.
    """

    disable_cache: bool
    """
    Specify if the optimizer should cache the matrix result set (containing ETAs and
    distances) for the given set of locations in the request. Once the results are
    cached, the optimizer can use it during the next 60 mins if exactly the same set
    of locations are provided again. Please note that if a cached result is
    retrieved, the timer is reset and that result will be available for another 60
    mins.

    If the users want to regenerate the result set, they can set this parameter to
    true and optimizer will not use the cached results.

    This feature is helpful in expediting the optimization process and generate
    results quickly. It also helps users to quickly simulate route plans for
    different combinations of constraints for a given set of locations.
    """

    hazmat_type: List[Literal["general", "circumstantial", "explosive", "harmful_to_water"]]
    """
    Specify the type of hazardous material being carried and the service will avoid
    roads which are not suitable for the type of goods specified. Provide multiple
    values separated by a comma , .

    Please note that this parameter is effective only when mode=truck.
    """

    mode: Literal["car", "truck"]
    """Define the traveling mode to be used for determining the optimized routes."""

    profiles: object
    """Defines all the vehicle profiles.

    profiles is implemented as a dictionary of objects where each profile name is
    the unique key and the associated value is an object describing the routing
    properties of that profile. All routing properties available in options.routing
    can be added as values for a given profile.

    Please note:

    - The routing properties configured using options.routing (and not part of any
      \\pprofiles\\)) are considered as default route settings i.e. they are applied to
      vehicles which are not associated with any profile.
    - The default route settings are independent from those defined for any profiles
      . Consequently, for vehicles which are tagged to a given profile, only the
      routing properties configured for the given profile will apply.
    - If the "mode" is not specified for any profile, by default it is considered to
      be car .
    - "default" is a reserved keyword and can not be used as the name for any custom
      profile.
    - profiles can't be nested in other profiles.
    - The number of profiles, including default route settings, are limited to

      - 15, if 0 < number of location <= 100
      - 6, if 100 < number of location <= 600，
      - 2, if 600 < number of location <= 1200,
      - 1, if number of location > 1200

    Routing profiles attribute is useful for configuring fleets containing multiple
    vehicles types. Check
    [Routing Profiles](https://docs.nextbillion.ai/docs/optimization/api/route-optimization-flexible/tutorials/routing-profiles)
    tutorial to learn more.
    """

    traffic_timestamp: int
    """Specify the general time when the job needs to be carried out.

    The time should be expressed as an UNIX timestamp in seconds format. The solver
    will take into account the general traffic conditions at the given time to
    determine the routes and their ETAs.
    """

    truck_axle_load: float
    """
    Specify the total load per axle (including the weight of trailers and shipped
    goods) of the truck, in tonnes. When used, the optimizer will use only those
    routes which are legally allowed to carry the load specified per axle.

    Please note this parameter is effective only when mode=truck.
    """

    truck_size: str
    """
    Specify the truck dimensions, in centimeters, in the format of
    “height,width,length”. Please note that this parameter is effective only when
    mode=truck.
    """

    truck_weight: int
    """Specify the truck weight including the trailers and shipped goods, in kilograms.

    Please note that this parameter is effective only when mode=truck.
    """


class Options(TypedDict, total=False):
    constraint: OptionsConstraint
    """
    This attribute defines both the soft and hard constraints for an optimization
    job.

    Soft constraints are constraints that do not necessarily have to be satisfied,
    but the optimization algorithm will try to satisfy them as much as possible.
    Whereas the hard constraints are the constraints that will not be violated by
    the solver. Users can use multiple constraints together.

    Please note that soft constraints are ineffective when using relations attribute
    in a request. The hard constraint, max_activity_waiting_time, is effective only
    when relation type is in_same_route and ineffective for all other types.
    """

    grouping: OptionsGrouping
    """Set grouping rules for the tasks and routes.

    - Use order_grouping to group nearby tasks
    - Use route_grouping to control route sequencing.
    """

    objective: OptionsObjective
    """This attribute is used to configure the objective of the optimization job."""

    routing: OptionsRouting
    """
    This attribute is used to define the routing configurations for the optimization
    job.
    """


class RelationStep(TypedDict, total=False):
    type: Required[Literal["start", "end", "job", "pickup", "delivery"]]
    """Specifies the type of the step.

    The start and end step types have to be the first and last steps, respectively,
    in a relation.

    Please note that the type is mandatory when using the relations object.
    """

    id: str
    """
    This represents the ID of the task and should be consistent with the input IDs
    provided in the jobs or shipments objects for a given step. The id is required
    for all steps other than start and end.
    """


class Relation(TypedDict, total=False):
    steps: Required[Iterable[RelationStep]]
    """
    The steps property specifies the tasks or steps that are part of the relation
    and must be carried out in a manner defined in the type parameter. Please note
    you can add any number of steps here, except when relation type is precedence
    where only 2 tasks can be added.
    """

    type: Required[Literal["in_same_route", "in_sequence", "in_direct_sequence", "precedence"]]
    """Specifies the type of relation constraint. The following types are supported:

    - in_same_route: Ensures that all steps are covered in the same route in
      solution.
    - in_sequence: Ensures that all steps are in the same route and their sequence
      matches the order specified in the steps field. Insertion of new steps between
      the steps specified, is allowed.
    - in_direct_sequence: Similar to in_sequence, but insertion of new steps is not
      allowed in the final route.
    - precedence: Restricts the travel time between the first step and second step.
      If the precedence requirement cannot be satisfied, then the task specified at
      the second step will not be assigned. Only 2 steps can be specified in a
      single precedence type relations. Please use multiple precedence relations to
      apply restrictions on more than 2 tasks.

    If the vehicle field is specified in the relations input, all steps will be
    served by that particular vehicle. Otherwise, the route can be allocated to any
    feasible vehicle.

    Please note that the type field is mandatory when using the relations object.
    """

    id: int
    """**Deprecated! Please use the** vehicle **parameter to specify the vehicle ID.**

    Specifies the ID of the vehicle that would fulfil the steps. ID should be
    consistent with input IDs provided in the vehicles object.
    """

    max_duration: int
    """This attribute is effective only when precedence type relation is used.

    max_duration restricts the travel time of the vehicle to go from location of
    first task to the location of second task specified in steps object. The unit
    for this parameter is seconds. It accepts values greater than 0 only.

    Please note that max_duration is a hard constraint. Hence, if aggressive
    durations are provided such that the second task cannot be reached within the
    specified max_duration, it might be done before the first task (usually in case
    of jobs) or remain un-assigned (usually in case of shipments).
    """

    min_duration: int
    """This attribute is effective only when precedence type relation is used.

    Use min_duration to enforce a minimum time-gap between the two tasks specified
    in steps object. When specified, the second task will get completed after a gap
    of min_duration with respect to the first task. The unit for this parameter is
    seconds.

    Please note that min_duration is implemented as a soft constraint and it can be
    violated in presence of other relation types. The optimizer will tend to provide
    solutions where min_duration is not violated, but it is not guaranteed.
    """

    vehicle: str
    """Specifies the ID of the vehicle that would fulfill the steps.

    Providing the same vehicle ID to multiple ‘relations’ is prohibited. The vehicle
    ID provided here should be consistent with ID provided in the vehicles
    attribute.
    """


class SolutionStep(TypedDict, total=False):
    id: Required[str]
    """The ID of the step.

    This field is mandatory for all steps except for start and end type.

    Please note that the ID provided here must also be present in either the jobs or
    the shipments objects.

    **Note:** We have modified the data type of this field. The latest change is
    backward compatible and both integer and string type IDs are valid for this
    field, as long as they match the IDs of the jobs or shipments already
    configured.
    """

    arrival: Required[int]
    """Specify the time at which the vehicle arrives at the step location.

    If time_windows is provided, then arrival will be an UNIX timestamp expressed in
    seconds. Otherwise, it will be the total duration, in seconds, elapsed since the
    start of the route.

    Please note that arrival is mandatory when using the solution object.
    """

    type: Required[Literal["start", "end", "job", "pickup", "delivery", "break"]]
    """Specify the type of the step."""

    description: str
    """Specify the description of this step."""

    distance: int
    """
    Specify the distance covered, in meters, from the start of the route up until
    the current step.

    Please note that the value of this parameter accumulates with each step. In case
    , the travel_cost: air_distance, then the distance here should be the straight
    line distance.
    """

    duration: int
    """
    Specify the drive time, in seconds, from the start of the route up until the
    start of the step. Please note that the value of this parameter accumulates with
    each step.
    """

    load: Iterable[int]
    """Specify the load on the vehicle after completing this step.

    In case of multiple dimensions, please specify the load for each type.
    """

    location: Iterable[float]
    """
    Specify the location coordinates of the step in the \\[[latitude, longitude\\]]
    format. Alternatively, location_index property can also be used to specify the
    location of the step.

    Please note that either location or location_index is mandatory.
    """

    location_index: int
    """
    Specify the index (in the location array) of the location coordinates where the
    step is performed. The valid range of values is \\[[0, length of location array).
    Alternatively, location property can also be used to specify the location.

    Please note that either location or location_index is mandatory.
    """

    service: int
    """Specify the service time, in seconds, at this step."""

    setup: int
    """Specify the set-up duration, in seconds, needed at the step."""

    waiting_time: int
    """Specify the wait time of the vehicle at this step, in seconds."""


class Solution(TypedDict, total=False):
    cost: Required[int]
    """Specify the cost of the route."""

    steps: Required[Iterable[SolutionStep]]
    """Describe the steps in this route."""

    vehicle: Required[str]
    """Specify the ID of the vehicle that was assigned to the route.

    This field is mandatory when using the solution attribute and providing an empty
    string would result in error. The IDs are case-sensitive.

    **Note:** Since the vehicles can be configured using either a string or an
    integer ID, please ensure that the same value type is provided for this field as
    was used in the original request.
    """

    delivery: Iterable[int]
    """
    Specify the total quantities, for each dimension (or unit), of deliveries
    performed in the route.
    """

    description: str
    """Specify the description of the assigned vehicle."""

    distance: int
    """Specify the total distance of the route, in meters."""

    duration: int
    """Specify the total drive duration of the route, in seconds."""

    geometry: str
    """Specify the geometry of this route encoded in polyline format."""

    pickup: Iterable[int]
    """
    Specify the total quantities, for each dimension (or unit), of pickups performed
    in the route.
    """

    priority: int
    """Specify the sum of priorities of all tasks on the route."""

    service: int
    """Specify the total service time for the route, in seconds."""

    setup: int
    """
    Specify the total set-up duration, in seconds, needed for the tasks on the
    route.
    """

    waiting_time: int
    """Specify the total waiting time of the vehicle on the route, in seconds."""


class Unassigned(TypedDict, total=False):
    jobs: List[str]
    """Specify the unassigned job IDs from the previous optimization result.

    Please note the IDs should also be present in the jobs part of the input.

    **Note:** We have modified the data type of this field. However, the latest
    change is backward compatible and both integer and string type job IDs are valid
    for this field, as long as they match the IDs of the jobs already configured.
    Providing mixed value types in the array, will lead to an error.
    """

    shipments: Iterable[List[str]]
    """
    Specify the unassigned shipment pickup & delivery IDs from the previous
    optimization result. Both the pickup & delivery steps of a shipment should be
    part of the same array.

    **Note:** We have modified the data type of this field. However, the latest
    change is backward compatible and both integer and string type shipment IDs are
    valid for this field, as long as they match the IDs of the shipments already
    configured. Providing mixed value types in the array, will lead to an error.
    """


class ZoneGeometry(TypedDict, total=False):
    coordinates: Iterable[Iterable[float]]
    """
    An array of coordinates in the \\[[longitude, latitude\\]] format, representing the
    zone boundary.
    """

    description: str
    """Provide a description to identify the zone"""

    type: Literal["Polygon", "MultiPolygon"]
    """Type of the geoJSON geometry. Should always be Polygon or MultiPolygon."""


class Zone(TypedDict, total=False):
    id: Required[int]
    """Provide an ID for the zone. This field is mandatory when adding zones."""

    geofence_id: str
    """
    Provide the ID of a pre-created geofence using the
    [Geofence API](https://docs.nextbillion.ai/docs/tracking/api/geofence).

    Please note that one of geometry or geofence_id should be provided.
    """

    geometry: ZoneGeometry
    """
    It is a [geoJSON object](https://datatracker.ietf.org/doc/html/rfc7946#page-9)
    with details of the geographic boundaries of the zone. Only “Polygon” and
    “MultiPolygon” geoJSON types are supported.

    Please note that one of geometry or geofence_id should be provided.
    """
