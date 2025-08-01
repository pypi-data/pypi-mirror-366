# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .polygon_geojson import PolygonGeojson

__all__ = ["ConsolePreviewResponse", "Data"]


class Data(BaseModel):
    geojson: Optional[PolygonGeojson] = None
    """An object with geoJSON details of the geofence.

    The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """


class ConsolePreviewResponse(BaseModel):
    data: Optional[Data] = None

    message: Optional[str] = None
