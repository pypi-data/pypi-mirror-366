# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from .metadata_param import MetadataParam

__all__ = ["MonitorCreateParams", "GeofenceConfig", "IdleConfig", "MatchFilter", "SpeedingConfig"]


class MonitorCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    tags: Required[List[str]]
    """Use this parameter to add tags to the monitor.

    tags can be used for filtering monitors in the _Get Monitor List_ operation.
    They can also be used for easy identification of monitors.

    Please note that valid tags are strings, consisting of alphanumeric characters
    (A-Z, a-z, 0-9) along with the underscore ('\\__') and hyphen ('-') symbols.
    """

    type: Required[Literal["enter", "exit", "enter_and_exit", "speeding", "idle"]]
    """Specify the type of activity the monitor would detect.

    The monitor will be able to detect the specified type of activity and create
    events for eligible asset. A monitor can detect following types of asset
    activity:

    - enter: The monitor will create an event when a linked asset enters into the
      specified geofence.

    - exit: The monitor will create an event when a linked asset exits the specified
      geofence.

    - enter_and_exit: The monitor will create an event when a linked asset either
      enters or exits the specified geofence.

    - speeding: The monitor will create an event when a linked asset exceeds a given
      speed limit.

    - idle: The monitor will create an event when a linked asset exhibits idle
      activity.

    Please note that assets and geofences can be linked to a monitor using the
    match_filter and geofence_config attributes respectively.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    custom_id: str
    """Set a unique ID for the new monitor.

    If not provided, an ID will be automatically generated in UUID format. A valid
    custom*id can contain letters, numbers, "-", & "*" only.

    Please note that the ID of an monitor can not be changed once it is created.
    """

    description: str
    """Add a description for your monitor using this parameter."""

    geofence_config: GeofenceConfig
    """Geofences are geographic boundaries surrounding an area of interest.

    geofence_config is used to specify the geofences for creating enter or exit type
    of events based on the asset's location. When an asset associated with the
    monitor enters the given geofence, an enter type event is created, whereas when
    the asset moves out of the geofence an exit type event is created.

    Please note that this object is mandatory when the monitor type belongs to one
    of enter, exit or enter_and_exit.
    """

    geofence_ids: List[str]
    """\\**\\**Deprecated.

    Please use the geofence_config to specify the geofence_ids for this monitor.\\**\\**

    An array of strings to collect the geofence IDs that should be linked to the
    monitor. Geofences are geographic boundaries that can be used to trigger events
    based on an asset's location.
    """

    idle_config: IdleConfig
    """idle_config is used to set up constraints for creating idle events.

    When an asset associated with the monitor has not moved a given distance within
    a given time, the Live Tracking API can create events to denote such instances.
    Please note that this object is mandatory when the monitor type is idle.

    Let's look at the properties of this object.
    """

    match_filter: MatchFilter
    """
    This object is used to identify the asset(s) on which the monitor would be
    applied.
    """

    meta_data: MetadataParam
    """Any valid json object data.

    Can be used to save customized data. Max size is 65kb.
    """

    name: str
    """Name of the monitor.

    Use this field to assign a meaningful, custom name to the monitor being created.
    """

    speeding_config: SpeedingConfig
    """speeding_config is used to set up constraints for creating over-speed events.

    When an asset associated with a monitor is traveling at a speed above the given
    limits, the Live Tracking API can create events to denote such instances. There
    is also an option to set up a tolerance before creating an event. Please note
    that this object is mandatory when type=speeding.

    Let's look at the properties of this object.
    """


class GeofenceConfig(TypedDict, total=False):
    geofence_ids: Required[List[str]]
    """
    An array of strings to collect the geofence IDs that should be linked to the
    monitor. Please note geofence_ids are mandatory when using the geofence_config
    attribute.
    """


class IdleConfig(TypedDict, total=False):
    distance_tolerance: Required[float]
    """
    Use this parameter to configure a distance threshold that will be used to
    determine if the asset was idle or not. If the asset moves by a distance less
    than the value of this parameter within a certain time period, the monitor would
    create an idle event against the asset. The distance_tolerance should be
    provided in meters.

    Users can set an appropriate value for this parameter, along with appropriate
    time_tolerance value, to avoid triggering idle events when the asset is crossing
    a busy intersection or waiting at the traffic lights.
    """

    time_tolerance: int
    """
    Use this parameter to configure a time duration for which the monitor would
    track the distance covered by an asset before triggering an idle event. The
    time_tolerance should be provided in milliseconds.

    If the distance covered by the asset during a time_tolerance is less than that
    specified in distance_tolerance the asset will be assumed to be idle.

    Please observe that this attribute along with distance_tolerance parameter can
    be used to control the "sensitivity" of the monitor with respect to idle alerts.
    If the distance_tolerance is set a high value, then setting time_tolerance to a
    low value may result in a situation where asset is always judged as idle. On the
    contrary, it might never be judged as idle if distance_tolerance is set to a low
    value but time_tolerance is set to a high value.

    It is recommended to use these properties with appropriate values to trigger
    genuine idle events. The appropriate values might depend on the traffic
    conditions, nature of operations that the asset is involved in, type of asset
    and other factors.
    """


class MatchFilter(TypedDict, total=False):
    include_all_of_attributes: object
    """A string type dictionary object to specify the attributes.

    Only the assets having all of the attributes added to this parameter will be
    linked to this monitor. Once an asset is linked to a monitor, the monitor will
    be able to create events for that asset whenever an activity specified in type
    is detected. Multiple attributes should be separated by a comma ,.

    Please note that this parameter can not be used in conjunction with
    include_any_of_attributes. Also, the maximum number of key:value pairs that this
    parameter can take is 100 and the overall size of the match_filter object should
    not exceed 65kb.
    """

    include_any_of_attributes: object
    """A string type dictionary object to specify the attributes.

    The assets having at least one of the attributes added to this parameter will be
    linked to this monitor. Once an asset is linked to a monitor, the monitor will
    be able to create events for that asset whenever an activity specified in type
    is detected. Multiple attributes should be separated by a comma ,.

    Please note that this parameter can not be used in conjunction with
    include_all_of_attributes. Also, the maximum number of key:value pairs that this
    parameter can take is 100 and the overall size of the match_filter object should
    not exceed 65kb.
    """


class SpeedingConfig(TypedDict, total=False):
    customer_speed_limit: int
    """
    Use this parameter to establish the speed limit that will allow the monitor to
    create events, depending on the time_tolerance value, when an asset's tracked
    speed exceeds it. The speed limit should be specified in meters per second.

    Please note that customer_speed_limit is mandatory when use_admin_speed_limit is
    false. However, when use_admin_speed_limit is true, customer_speed_limit is
    ineffective.
    """

    time_tolerance: int
    """Use this parameter to configure a time tolerance before triggering an event.

    Adding a tolerance would make the Tracking service wait for the specified time
    before triggering the event. Consequently, an event is triggered only when the
    time for which the asset has been over-speeding continuously, exceeds the
    configured tolerance time. The unit for this parameter is milliseconds.

    It can be seen that this attribute is used to control the "sensitivity" of the
    monitor with respect to speed alerts. Higher the value of time_tolerance the
    less sensitive the monitor would be to instances of over-speeding. Conversely,
    if 'time_tolerance' is set to 0, the monitor will be extremely sensitive and
    will create an event as soon as tracking information with a speed value greater
    than the specified limit is received.
    """

    use_admin_speed_limit: bool
    """
    A boolean attribute to indicate which speed limit values should be used by the
    monitor. When use_admin_speed_limit is true, the administrative speed limit of
    the road on which the asset is located, will be used to generate events when the
    asset’s tracked speed exceeds it. Whereas, when use_admin_speed_limit is false,
    the customer_speed_limit specified will be used to generate events when the
    asset's tracked speed exceeds it.

    Please note that if use_admin_speed_limit is false, customer_speed_limit is
    mandatory, however, when use_admin_speed_limit is true then customer_speed_limit
    is ineffective.
    """
