# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .vehicle_param import VehicleParam

__all__ = [
    "DriverAssignmentAssignParams",
    "Filter",
    "Order",
    "OrderPickup",
    "OrderDropoff",
    "OrderVehiclePreferences",
    "OrderVehiclePreferencesExcludeAllOfAttribute",
    "OrderVehiclePreferencesRequiredAllOfAttribute",
    "OrderVehiclePreferencesRequiredAnyOfAttribute",
    "Options",
    "OptionsOrderAttributePriorityMapping",
    "OptionsVehicleAttributePriorityMapping",
]


class DriverAssignmentAssignParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    filter: Required[Filter]
    """
    Specify the filtering criterion for the vehicles with respect to each order's
    location. filter is a mandatory input for all requests.
    """

    orders: Required[Iterable[Order]]
    """Collects the details of open orders to be fulfilled.

    Each object represents one order. All requests must include orders as a
    mandatory input. A maximum of 200 orders is allowed per request.
    """

    vehicles: Required[Iterable[VehicleParam]]
    """Collects the details of vehicles available to fulfill the orders.

    Each object represents one vehicle. All requests must include vehicles as a
    mandatory input. A maximum of 100 vehicles is allowed per request.
    """

    options: Options
    """Configure the assignment constraints and response settings."""


class Filter(TypedDict, total=False):
    driving_distance: float
    """Defines a driving_distance filter, in meters.

    If a vehicle needs to drive further than this distance to reach a pickup
    location, it will not be assigned to that order. Valid range of values for this
    filter is \\[[1, 10000\\]].
    """

    pickup_eta: int
    """
    Specify a duration, in seconds, which will be used to filter out ineligible
    vehicles for each order. Any vehicle which would take more time than specified
    here, to reach the pickup location of a given order, will be ruled out for
    assignment for that particular order. Valid values for pickup_eta are \\[[1,
    3600\\]].
    """

    radius: float
    """
    Specify a radius, in meters, which will be used to filter out ineligible
    vehicles for each order. The pickup location of an order will act as the center
    of the circle when identifying eligible vehicles. Valid values for radius are
    \\[[1, 10000\\]].
    """


class OrderPickup(TypedDict, total=False):
    lat: float
    """Latitude of the pickup location."""

    lng: float
    """Longitude of the pickup location."""


class OrderDropoff(TypedDict, total=False):
    lat: float
    """Latitude of the stop location."""

    lng: float
    """Longitude of the stop location."""


class OrderVehiclePreferencesExcludeAllOfAttribute(TypedDict, total=False):
    attribute: Required[str]
    """Specify the name of the attribute.

    The attribute is compared to the keys (of each key:value pair) in
    vehicles.attributes during evaluation.
    """

    operator: Required[str]
    """
    Specify the operator to denote the relation between attribute and the value
    specified above. The attribute , operator and value together constitute the
    condition that a vehicle must meet to be eligible for assignment. Currently, we
    support following operators currently:

    - Equal to (==)
    - Less than (<)
    - Less tha equal to (<=)
    - Greater than (>)
    - Greater than equal to (>=)
    - Contains (contains)

    Please note that when using "contains" operator only one value can be specified
    and the corresponding attribute must contain multiple values when defined for a
    vehicle.
    """

    value: Required[str]
    """Specify the desired value of the attribute to be applied for this order.

    value provided here is compared to the values (of each key:value pair) in
    vehicles.attributes during evaluation.
    """


class OrderVehiclePreferencesRequiredAllOfAttribute(TypedDict, total=False):
    attribute: Required[str]
    """Specify the name of the attribute.

    The attribute is compared to the keys (of each key:value pair) in
    vehicles.attributes during evaluation.
    """

    operator: Required[str]
    """
    Specify the operator to denote the relation between attribute and the value
    specified above. The attribute , operator and value together constitute the
    condition that a vehicle must meet to be eligible for assignment. Currently, we
    support following operators currently:

    - Equal to (==)
    - Less than (<)
    - Less tha equal to (<=)
    - Greater than (>)
    - Greater than equal to (>=)
    - Contains (contains)

    Please note that when using "contains" operator only one value can be specified
    and the corresponding attribute must contain multiple values when defined for a
    vehicle.
    """

    value: Required[str]
    """Specify the desired value of the attribute to be applied for this order.

    value provided here is compared to the values (of each key:value pair) in
    vehicles.attributes during evaluation.
    """


class OrderVehiclePreferencesRequiredAnyOfAttribute(TypedDict, total=False):
    attribute: Required[str]
    """Specify the name of the attribute.

    The attribute is compared to the keys (of each key:value pair) in
    vehicles.attributes during evaluation.
    """

    operator: Required[str]
    """
    Specify the operator to denote the relation between attribute and the value
    specified above. The attribute , operator and value together constitute the
    condition that a vehicle must meet to be eligible for assignment. Currently, we
    support following operators currently:

    - Equal to (==)
    - Less than (<)
    - Less tha equal to (<=)
    - Greater than (>)
    - Greater than equal to (>=)
    - Contains (contains)

    Please note that when using "contains" operator only one value can be specified
    and the corresponding attribute must contain multiple values when defined for a
    vehicle.
    """

    value: Required[str]
    """Specify the desired value of the attribute to be applied for this order.

    value provided here is compared to the values (of each key:value pair) in
    vehicles.attributes during evaluation.
    """


class OrderVehiclePreferences(TypedDict, total=False):
    exclude_all_of_attributes: Iterable[OrderVehiclePreferencesExcludeAllOfAttribute]
    """An array of objects to add exclusion requirements for the order.

    A vehicle must **not meet any of the conditions** specified here to be
    considered for assignment. Each object represents a single condition. Please
    note that a maximum of 10 conditions can be added here for a given order.
    """

    required_all_of_attributes: Iterable[OrderVehiclePreferencesRequiredAllOfAttribute]
    """An array of objects to add mandatory requirements for the order.

    A vehicle must **meet** **all conditions** specified here to be considered for
    assignment. Each object represents a single condition. Please note that a
    maximum of 10 conditions can be added here for a given order.
    """

    required_any_of_attributes: Iterable[OrderVehiclePreferencesRequiredAnyOfAttribute]
    """An array of objects to add optional requirements for the order.

    A vehicle must **meet** **at least one of the conditions** specified here to be
    considered for assignment. Each object represents a single condition. Please
    note that a maximum of 10 conditions can be added here for a given order.
    """


class Order(TypedDict, total=False):
    id: Required[str]
    """Specify a unique ID for the order."""

    pickup: Required[OrderPickup]
    """Specify the location coordinates of the pickup location of the order.

    This input is mandatory for each order.
    """

    attributes: object
    """Specify custom attributes for the orders.

    Each attribute should be created as a key:value pair. The **keys** provided can
    be used in options.order_attribute_priority_mappings to assign a custom priority
    for this order based on its attributes.

    The maximum number of key:value pairs that can be specified under attributes for
    a given order, is limited to 30.
    """

    dropoffs: Iterable[OrderDropoff]
    """
    Use this parameter to specify the location coordinates of the destination of the
    trip or the intermediate stops to be completed before it.

    Please note

    - The last location provided is treated as the destination of the trip.
    - dropoffs is mandatory when dropoff_details is set to **true**.
    """

    priority: int
    """Specify the priority for this order.

    A higher value indicates a higher priority. When specified, it will override any
    priority score deduced from order_attribute_priority_mappings for this order.
    Valid values are \\[[1, 10\\]] and default is 0.
    """

    service_time: int
    """Specify the service time, in seconds, for the order.

    Service time is the duration that the driver is likely to wait at the pickup
    location after arriving. The impact of the service time is realized in the ETA
    for the "dropoff" type step.
    """

    vehicle_preferences: OrderVehiclePreferences
    """Define custom preferences for task assignment based on vehicle's attributes.

    If multiple criteria are provided, they are evaluated using an AND
    condition—meaning all specified criteria must be met individually for a vehicle
    to be considered.

    For example, if required_all_of_attributes, required_any_of_attributes, and
    exclude_all_of_attributes are all provided, an eligible vehicle must satisfy the
    following to be considered for assignments:

    1.  Meet all conditions specified in required_all_of_attributes.
    2.  Meet at least one of the conditions listed in required_any_of_attributes.
    3.  Not meet any conditions mentioned in exclude_all_of_attributes.

    Consequently, a vehicle which does not have any attributes defined can't be
    assigned to an order which has vehicle_preferences configured.
    """


class OptionsOrderAttributePriorityMapping(TypedDict, total=False):
    attribute: Required[str]
    """Specify the name of the attribute.

    The attribute is compared to the keys (of each key:value pair) in
    orders.attributes during evaluation.
    """

    operator: Required[str]
    """
    Specify the operator to denote the relation between attribute and the value
    specified above. The attribute , operator and value together constitute the
    condition that an order must meet to assume the specified priority. We support
    the following operators currently:

    - Equal to (==)
    - Less than (<)
    - Less tha equal to (<=)
    - Greater than (>)
    - Greater than equal to (>=)
    - Contains (contains)

    Please note that when using "contains" operator only one value can be specified
    and the corresponding attribute must contain multiple values when defined for an
    order.
    """

    priority: Required[str]
    """
    Specify the priority score that should be assigned when an order qualifies the
    criteria specified above. A higher value indicates a higher priority. Valid
    values are \\[[1,10\\]].
    """

    value: Required[str]
    """Specify the desired value of the attribute to be applied for this order.

    value provided here is compared to the values (of each key:value pair) in
    orders.attributes during evaluation.
    """


class OptionsVehicleAttributePriorityMapping(TypedDict, total=False):
    attribute: Required[str]
    """Specify the name of the attribute.

    The attribute is compared to the keys (of each key:value pair) in
    vehicles.attributes during evaluation.
    """

    operator: Required[str]
    """
    Specify the operator to denote the relation between attribute and the value
    specified above. The attribute , operator and value together constitute the
    condition that a vehicle must meet to assume the specified priority. We support
    the following operators currently:

    - Equal to (==)
    - Less than (<)
    - Less tha equal to (<=)
    - Greater than (>)
    - Greater than equal to (>=)
    - Contains (contains)

    Please note that when using "contains" operator only one value can be specified
    and the corresponding attribute must contain multiple values when defined for a
    vehicle.
    """

    priority: Required[str]
    """
    Specify the priority score that should be assigned when a vehicle qualifies the
    criteria specified above. A higher value indicates a higher priority. Valid
    values are \\[[1,10\\]].
    """

    value: Required[str]
    """Specify the desired value of the attribute to be applied for this vehicle.

    value provided here is compared to the values (of each key:value pair) in
    vehicles.attributes during evaluation.
    """


class Options(TypedDict, total=False):
    alternate_assignments: int
    """
    Specify the maximum number of potential, alternate vehicle assignments to be
    returned for each order, apart from the vehicle which was assigned as
    recommended. Please note that:

    - The maximum number of alternate assignments that can be requested are 3.
    - It is not necessary that the service will return the specified number of
      alternate assignments for each order. The number of alternate assignments
      returned will depend on the number of vehicles provided in the input.
    - Order which could not be assigned to any vehicles due to their filter or
      attribute matching criteria will not be eligible for alternate assignments as
      well.
    """

    dropoff_details: bool
    """
    When **true**, the service returns the drop-off steps for each trip and related
    details in the response. Defaults to **false**.
    """

    order_attribute_priority_mappings: Iterable[OptionsOrderAttributePriorityMapping]
    """
    Collection of rules for assigning custom priority to orders based on their
    attributes. In case an order satisfies more than one rule, the highest priority
    score from all the rules satisfied, would be the effective priority score for
    such an order.
    """

    travel_cost: Literal["driving_eta", "driving_distance", "straight_line_distance"]
    """
    Choose a travel cost that will be used by the service for assigning vehicles
    efficiently from a set of qualifying ones.
    """

    vehicle_attribute_priority_mappings: Iterable[OptionsVehicleAttributePriorityMapping]
    """
    Collection of rules for assigning custom priority to vehicles based on their
    attributes. In case a vehicle satisfies more than one rule, the highest priority
    score from all the rules satisfied, would be the effective priority score for
    such a vehicle.
    """
