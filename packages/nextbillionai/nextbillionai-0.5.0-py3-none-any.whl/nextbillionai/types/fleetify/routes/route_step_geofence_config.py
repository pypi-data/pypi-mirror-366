# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["RouteStepGeofenceConfig"]


class RouteStepGeofenceConfig(BaseModel):
    radius: Optional[float] = None
    """Specify the radius of the cicular geofence, in meters.

    Once specified, the service will create a geofence with task's location as the
    center of the circle having the given radius. Valid values for radius are \\[[10,
    5000\\]].
    """

    type: Optional[Literal["circle"]] = None
    """Specify the type of the geofence.

    Currently, circle is the only suppoeted value.
    """
