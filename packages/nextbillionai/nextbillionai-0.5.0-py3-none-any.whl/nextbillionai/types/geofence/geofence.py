# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .polygon_geojson import PolygonGeojson

__all__ = ["Geofence", "CircleCenter"]


class CircleCenter(BaseModel):
    lat: Optional[float] = None
    """Latitude of the location."""

    lon: Optional[float] = None
    """Longitude of the location."""


class Geofence(BaseModel):
    id: Optional[str] = None
    """ID of the geofence provided/generated at the time of creating the geofence."""

    circle_center: Optional[CircleCenter] = None

    circle_radius: Optional[float] = None
    """
    When the type of the geofence is circle, this property returns the radius of the
    geofence in meters (m).
    """

    created_at: Optional[int] = None
    """
    Time at which the geofence was created, expressed as a UNIX timestamp in
    seconds.
    """

    geojson: Optional[PolygonGeojson] = None
    """An object with geoJSON details of the geofence.

    The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).
    """

    ic_contours_meter: Optional[int] = None
    """
    For a geofence based on isochrone contour determined using a specific driving
    distance, this property returns the duration value, in meters.

    The value would be the same as that provided for the contours_meter parameter at
    the time of creating or updating the geofence.
    """

    ic_contours_minute: Optional[int] = None
    """
    For a geofence based on isochrone contour determined using a specific driving
    duration, this property returns the duration value, in minutes. The value would
    be the same as the value provided for the contours_minute parameter at the time
    of creating or updating the geofence.
    """

    ic_coordinates: Optional[str] = None
    """
    For a geofence based on isochrone contour, this property returns the coordinates
    of the location, in [latitude,longitude] format, which was used as the starting
    point to identify the geofence boundary.

    The value would be the same as that provided for the coordinates parameter at
    the time of creating or updating the geofence.
    """

    ic_denoise: Optional[float] = None
    """
    For a geofence based on isochrone contour, this property returns the denoise
    value which would be the same as that provided for the denoise parameter at the
    time of creating or updating the geofence.
    """

    ic_departure_time: Optional[int] = None
    """
    For a geofence based on isochrone contour, this property returns the departure
    time, as a UNIX epoch timestamp in seconds, which was used to determine the
    geofence boundary after taking into account the traffic conditions at the time.

    The value would be the same as that provided for the departure_time parameter at
    the time of creating or updating the geofence.
    """

    ic_mode: Optional[float] = None
    """
    For a geofence based on isochrone contour, this property returns the driving
    mode used to determine the geofence boundary.

    The value would be the same as that provided for the mode parameter at the time
    of creating or updating the geofence.
    """

    meta_data: Optional[object] = None
    """Metadata of the geofence added at the time of creating or updating it."""

    name: Optional[str] = None
    """Name of the geofence added at the time of creating or updating it."""

    tags: Optional[List[str]] = None
    """
    An array of strings representing the tags associated with the geofence added at
    the time of creating or updating it.
    """

    type: Optional[Literal["circle", "polygon", "isochrone"]] = None
    """Type of the geofence."""

    updated_at: Optional[int] = None
    """
    Time at which the geofence was last updated, expressed as a UNIX timestamp in
    seconds.
    """
