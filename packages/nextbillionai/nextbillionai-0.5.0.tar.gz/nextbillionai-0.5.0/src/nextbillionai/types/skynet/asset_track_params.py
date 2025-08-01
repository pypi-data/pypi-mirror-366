# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AssetTrackParams", "Locations", "LocationsLocation"]


class AssetTrackParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    device_id: Required[str]
    """ID of the device used to upload the tracking information of the asset.

    Please note that the device_id used here must already be linked to the asset.
    Use the _Bind Device to Asset_ method to link a device with your asset.
    """

    locations: Required[Locations]
    """An array of objects to collect the location tracking information for an asset.

    Each object must correspond to details of only one location.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""


class LocationsLocation(TypedDict, total=False):
    lat: Required[float]
    """Latitude of the tracked location of the asset."""

    lon: Required[float]
    """Longitude of the tracked location of the asset."""


class Locations(TypedDict, total=False):
    location: Required[LocationsLocation]
    """An object to collect the coordinate details of the tracked location.

    Please note this field is mandatory when uploading locations for an asset.
    """

    timestamp: Required[int]
    """
    Use this parameter to provide the time, expressed as UNIX epoch timestamp in
    milliseconds, when the location was tracked. Please note this field is mandatory
    when uploading locations for an asset.
    """

    accuracy: float
    """
    Use this parameter to provide the accuracy of the GPS information at the tracked
    location. It is the estimated horizontal accuracy radius, in meters.
    """

    altitude: float
    """
    Use this parameter to provide the altitude, in meters, of the asset at the
    tracked location.
    """

    battery_level: int
    """
    Use this parameter to provide the battery level of the GPS device, as a
    percentage, when the location is tracked. It should have a minimum value of 0
    and a maximum value of 100.
    """

    bearing: float
    """
    Use this parameter to provide the heading of the asset, in radians, calculated
    from true north in clockwise direction. This should always be in the range of
    [0, 360).
    """

    meta_data: object
    """Use this object to add any custom data about the location that is being
    uploaded.

    Recommended to use the key:value format for adding the desired information.

    Please note that the maximum size of meta_data object should not exceed 65Kb.
    """

    speed: float
    """
    Use this parameter to provide the speed of the asset, in meters per second, at
    the tracked location.
    """

    tracking_mode: str
    """NB tracking mode."""
