# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .location_param import LocationParam

__all__ = ["VehicleParam", "Location"]


class Location(TypedDict, total=False):
    lat: float
    """Latitude of the vehicle's current location."""

    lng: float
    """Longitude of the vehicle's current location."""


class VehicleParam(TypedDict, total=False):
    id: Required[str]
    """Specify a unique ID for the vehicle."""

    location: Required[Location]
    """Specify the location coordinates where the vehicle is currently located.

    This input is mandatory for each vehicle.
    """

    attributes: object
    """Specify custom attributes for the vehicle.

    Each attribute should be created as a key:value pair. These attributes can be
    used in the orders.vehicle_preferences input to refine the search of vehicles
    for each order.

    The maximum number of key:value pairs that can be specified under attributes for
    a given vehicle, is limited to 30.
    """

    priority: int
    """Specify the priority for this vehicle.

    A higher value indicates a higher priority. When specified, it will override any
    priority score deduced from vehicle_attribute_priority_mappings for this
    vehicle. Valid values are \\[[1, 10\\]] and default is 0.
    """

    remaining_waypoints: Iterable[LocationParam]
    """
    An array of objects to collect the location coordinates of the stops remaining
    on an ongoing trip of the vehicle. The service can assign new orders to the
    vehicle if they are cost-effective. Once a new order is assigned, the vehicle
    must complete all the steps in the ongoing trip before proceeding to pickup the
    newly assigned order.

    Please note that a maximum of 10 waypoints can be specified for a given vehicle.
    """
