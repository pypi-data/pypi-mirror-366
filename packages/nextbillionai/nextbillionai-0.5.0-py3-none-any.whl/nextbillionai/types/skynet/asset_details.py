# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["AssetDetails", "LatestLocation", "LatestLocationLocation"]


class LatestLocationLocation(BaseModel):
    lat: Optional[float] = None
    """Latitude of the tracked location of the asset."""

    lon: Optional[float] = None
    """Longitude of the tracked location of the asset."""


class LatestLocation(BaseModel):
    accuracy: Optional[float] = None
    """
    If available, this property returns the accuracy of the GPS information received
    at the last tracked location. It is represented as an estimated horizontal
    accuracy radius, in meters, at the 68th percentile confidence level.
    """

    altitude: Optional[float] = None
    """
    If available in the GPS information, this property returns the altitude of the
    asset at the last tracked location. It is represented as height, in meters,
    above the WGS84 reference ellipsoid.
    """

    bearing: Optional[float] = None
    """
    If available in the GPS information, this property returns the heading of the
    asset calculated from true north in clockwise direction at the last tracked
    location. Please note that the bearing is not affected by the device
    orientation.

    The bearing will always be in the range of [0, 360).
    """

    location: Optional[LatestLocationLocation] = None
    """An object with the coordinates of the last tracked location."""

    speed: Optional[float] = None
    """
    If available in the GPS information, this property returns the speed of the
    asset, in meters per second, at the last tracked location.
    """

    timestamp: Optional[int] = None
    """
    A UNIX epoch timestamp in milliseconds, representing the time at which the
    location was tracked.
    """


class AssetDetails(BaseModel):
    id: Optional[str] = None
    """ID of the asset.

    This is the same ID that was generated/provided at the time of creating the
    asset.
    """

    attributes: Optional[object] = None
    """A string dictionary object containing attributes of the asset.

    These attributes were associated with the asset at the time of creating or
    updating it.

    attributes can be added to an asset using the _Update Asset Attributes_ method.
    """

    created_at: Optional[int] = None
    """
    A UNIX epoch timestamp in seconds representing the time at which the asset was
    created.
    """

    description: Optional[str] = None
    """Description of the asset.

    The value would be the same as that provided for the description parameter at
    the time of creating or updating the asset.
    """

    device_id: Optional[str] = None
    """ID of the device that is linked to this asset.

    Please note that there can be multiple device_id linked to a single asset. An
    empty response is returned if no devices are linked to the asset.

    User can link a device to an asset using the _Bind Asset to Device_ method.
    """

    latest_location: Optional[LatestLocation] = None
    """An object with details of the last tracked location of the asset."""

    meta_data: Optional[object] = None
    """Any valid json object data.

    Can be used to save customized data. Max size is 65kb.
    """

    name: Optional[str] = None
    """Name of the asset.

    The value would be the same as that provided for the name parameter at the time
    of creating or updating the asset.
    """

    state: Optional[str] = None
    """State of the asset.

    It will be "active" when the asset is in use or available for use, and it will
    be "deleted" in case the asset has been deleted.
    """

    tags: Optional[List[str]] = None
    """
    **This parameter will be deprecated soon! Please move existing tags to
    attributes parameter.**

    Tags of the asset. These were associated with the asset when it was created or
    updated. tags can be used for filtering assets in operations like _Get Asset
    List_ and asset **Search** methods. They can also be used for monitoring of
    assets using **Monitor** methods after linking tags and asset.
    """

    tracked_at: Optional[int] = None
    """
    A UNIX epoch timestamp in seconds representing the last time when the asset was
    tracked.
    """

    updated_at: Optional[int] = None
    """
    A UNIX epoch timestamp in seconds representing the time at which the asset was
    last updated.
    """
