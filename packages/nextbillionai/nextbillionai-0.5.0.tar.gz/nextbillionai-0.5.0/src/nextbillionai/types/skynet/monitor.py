# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Monitor", "GeofenceConfig", "IdleConfig", "MatchFilter", "SpeedingConfig"]


class GeofenceConfig(BaseModel):
    geofence_ids: Optional[List[str]] = None
    """An array of geofence IDs that are linked to the monitor.

    Geofences are geographic boundaries that can be used to trigger events based on
    an asset's location.
    """


class IdleConfig(BaseModel):
    distance_tolerance: Optional[float] = None
    """
    This parameter returns the distance threshold that was used to determine if the
    asset was idle or not. The value returned for this parameter is the same as that
    provided while creating or updating a idle type monitor.
    """

    time_tolerance: Optional[int] = None
    """
    This parameter returns the time duration for which the monitor tracks the
    distance covered by an asset before triggering an idle event. The value returned
    for this parameter is the same as that provided while creating or updating a
    idle type monitor.
    """


class MatchFilter(BaseModel):
    include_all_of_attributes: Optional[object] = None
    """
    A string type dictionary object to specify the attributes which will be used to
    identify the asset(s) on which the monitor would be applied. Please note that
    using this parameter overwrites the existing attributes of the monitor.

    If the attributes added to a monitor do not match fully with the attributes
    added to any asset, the monitor will be ineffective.

    Please note that the maximum number of key:value pairs that
    'include_all_of_attributes' can take is 100. Also, the overall size of the
    match_filter object should not exceed 65kb.
    """

    include_any_of_attributes: Optional[object] = None
    """A string dictionary object to specify the attributes, separated by a ,.

    Only the assets with any one of the attributes added to this parameter will be
    linked to this monitor. Once an asset and a monitor are linked, the monitor will
    be able to create events for the asset when an activity specified in type is
    detected.

    If no input is provided for this object or if the attributes added here do not
    match at least one of the attributes added to any asset, the monitor will be
    ineffective.

    Please note that the maximum number of key:value pairs that
    include_any_of_attributes can take is 100. Also, the overall size of
    match_filter object should not exceed 65kb.
    """


class SpeedingConfig(BaseModel):
    customer_speed_limit: Optional[int] = None
    """
    This property returns the actual speed limit that the monitor uses as a
    threshold for generating a speed limit event. The value returned for this
    parameter is the same as that provided while creating or updating a speeding
    type monitor.
    """

    time_tolerance: Optional[int] = None
    """
    This property returns the time duration value, in milliseconds, for which the
    monitor will track the speed of the asset. An event is triggered if the speed
    remains higher than the specified limit for a duration more than the tolerance
    value.

    The value returned for this parameter is the same as that provided while
    creating or updating a speeding type monitor.
    """

    use_admin_speed_limit: Optional[bool] = None
    """
    A boolean value denoting if the administrative speed limit of the road was used
    as speed limit threshold for triggering events. The value returned for this
    parameter is the same as that provided while creating or updating a speeding
    type monitor.
    """


class Monitor(BaseModel):
    id: Optional[str] = None
    """Unique ID of the monitor.

    This is the same ID that was generated at the time of creating the monitor.
    """

    created_at: Optional[int] = None
    """
    A UNIX epoch timestamp in seconds representing the time at which the monitor was
    created.
    """

    description: Optional[str] = None
    """Description of the monitor.

    The value would be the same as that provided for the description parameter at
    the time of creating or updating the monitor.
    """

    geofence_config: Optional[GeofenceConfig] = None
    """
    An object returning the details of the geofence that are associated with the
    monitor for an enter, exit or enter_and_exit type of monitor.
    """

    geofences: Optional[List[str]] = None
    """Geofence IDs that are linked to the monitor.

    These IDs were associated with the monitor at the time of creating or updating
    it.

    The monitor uses the geofences mentioned here to create events of type nature
    for the eligible asset(s).
    """

    idle_config: Optional[IdleConfig] = None
    """
    An object returning the details of the idle activity constraints for a idle type
    of monitor.
    """

    match_filter: Optional[MatchFilter] = None
    """Use this object to update the attributes of the monitor."""

    meta_data: Optional[object] = None
    """Any valid json object data.

    Can be used to save customized data. Max size is 65kb.
    """

    name: Optional[str] = None
    """Name of the monitor.

    The value would be the same as that provided for the name parameter at the time
    of creating or updating the monitor.
    """

    speeding_config: Optional[SpeedingConfig] = None
    """
    An object returning the details of the over-speeding constraints for a speeding
    type of monitor.
    """

    tags: Optional[List[str]] = None
    """Tags of the monitor.

    The values would be the same as that provided for the tags parameter at the time
    of creating or updating the monitor.
    """

    type: Optional[Literal["enter", "exit", "enter_and_exit", "speeding", "idle"]] = None
    """Type of the monitor.

    It represents the type of asset activity that the monitor is configured to
    detect.
    """

    updated_at: Optional[int] = None
    """
    A UNIX epoch timestamp in seconds representing the time at which the monitor was
    last updated.
    """
