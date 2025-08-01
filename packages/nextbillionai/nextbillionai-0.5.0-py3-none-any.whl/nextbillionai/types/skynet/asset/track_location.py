# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["TrackLocation", "Location"]


class Location(BaseModel):
    lat: Optional[float] = None
    """Latitude of the tracked location of the asset."""

    lon: Optional[float] = None
    """Longitude of the tracked location of the asset."""


class TrackLocation(BaseModel):
    accuracy: Optional[float] = None
    """
    If available, this property returns the accuracy of the GPS information received
    at the tracked location. It is represented as an estimated horizontal accuracy
    radius, in meters, at the 68th percentile confidence level.
    """

    altitude: Optional[float] = None
    """
    If available in the GPS information, this property returns the altitude of the
    asset at the tracked location. It is represented as height, in meters, above the
    WGS84 reference ellipsoid.
    """

    battery_level: Optional[int] = None
    """
    Returns the battery level of the GPS device, as a percentage, when the location
    was tracked. It has a minimum value of 0 and a maximum value of 100.
    """

    bearing: Optional[float] = None
    """
    If available in the GPS information, this property returns the heading of the
    asset calculated from true north in clockwise direction at the tracked location.
    Please note that the bearing is not affected by the device orientation.

    The bearing will always be in the range of [0, 360).
    """

    location: Optional[Location] = None
    """An object with the coordinates of the last tracked location."""

    meta_data: Optional[object] = None
    """
    Specifies the custom data about the location that was added when the location
    was uploaded.
    """

    speed: Optional[float] = None
    """
    If available in the GPS information, this property returns the speed of the
    asset, in meters per second, at the tracked location.
    """

    timestamp: Optional[int] = None
    """
    A UNIX epoch timestamp in milliseconds, representing the time at which the
    location was tracked.
    """

    tracking_mode: Optional[str] = None
    """Internal parameter for tracking mode."""
