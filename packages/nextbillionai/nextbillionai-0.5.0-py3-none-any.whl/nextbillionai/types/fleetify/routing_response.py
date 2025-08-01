# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["RoutingResponse"]


class RoutingResponse(BaseModel):
    approaches: Optional[str] = None
    """
    Returns the configuration of approaches for each step, that is used when
    generating the route to help the driver with turn-by-turn navigation.
    """

    avoid: Optional[str] = None
    """
    Returns the objects and maneuvers that will be avoided in the route that is
    built when driver starts the in-app turn-by-turn navigation.
    """

    hazmat_type: Optional[str] = None
    """Returns the hazardous cargo type that the truck is carrying.

    The hazardous cargo type is used to determine the compliant routes that the
    driver can take while navigating the dispatched route.
    """

    mode: Optional[str] = None
    """
    Returns the driving mode that is used to build the route when driver starts the
    in-app turn-by-turn navigation.
    """

    truck_axle_load: Optional[str] = None
    """
    Returns the total load per axle of the truck, in tonnes, used to determine
    compliant routes that the driver can take when he starts navigating the
    dispatched route.
    """

    truck_size: Optional[str] = None
    """
    Returns the truck dimensions, in centimeters, used to determine compliant routes
    that the driver can take when he starts navigating the dispatched route.
    """

    truck_weight: Optional[str] = None
    """
    Returns the truck weight that will determine compliant routes that can be used
    by the driver during navigation.
    """
