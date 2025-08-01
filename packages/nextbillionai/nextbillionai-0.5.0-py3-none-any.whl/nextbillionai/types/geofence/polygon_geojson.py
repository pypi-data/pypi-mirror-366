# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["PolygonGeojson"]


class PolygonGeojson(BaseModel):
    coordinates: Optional[List[List[float]]] = None
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    geofence boundary.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry. Will always be Polygon."""
