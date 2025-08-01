# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["RouteStepGeofenceConfigParam"]


class RouteStepGeofenceConfigParam(TypedDict, total=False):
    radius: float
    """Specify the radius of the cicular geofence, in meters.

    Once specified, the service will create a geofence with task's location as the
    center of the circle having the given radius. Valid values for radius are \\[[10,
    5000\\]].
    """

    type: Literal["circle"]
    """Specify the type of the geofence.

    Currently, circle is the only suppoeted value.
    """
