# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TripStartParams", "Stop"]


class TripStartParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    asset_id: Required[str]
    """Specify the ID of the asset which is making this trip.

    The asset will be linked to this trip.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    attributes: object
    """
    attributes can be used to store custom information about a trip in key:value
    format. Use attributes to add any useful information or context to your trips
    like the driver name, destination etc.

    Please note that the maximum number of key:value pairs that can be added to an
    attributes object is 100. Also, the overall size of attributes object should not
    exceed 65kb.
    """

    custom_id: str
    """Set a unique ID for the new trip.

    If not provided, an ID will be automatically generated in UUID format. A valid
    custom_id can contain letters, numbers, “-”, & “\\__” only.

    Please note that the ID of a trip can not be changed once it is created.
    """

    description: str
    """Add a custom description for the trip."""

    meta_data: object
    """An JSON object to collect additional details about the trip.

    Use this property to add any custom information / context about the trip. The
    input will be passed on to the response as-is and can be used to display useful
    information on, for example, a UI app.
    """

    name: str
    """Specify a name for the trip."""

    stops: Iterable[Stop]
    """
    An array of objects to collect the details about all the stops that need to be
    made before the trip ends. Each object represents one stop.
    """


class Stop(TypedDict, total=False):
    geofence_id: str
    """
    Specify the ID of the geofence indicating the area where the asset needs to make
    a stop, during the trip. Only the IDs of geofences created using
    [NextBillion.ai's Geofence API](https://docs.nextbillion.ai/docs/tracking/api/geofence#create-a-geofence)
    are accepted.
    """

    meta_data: object
    """An JSON object to collect additional details about the stop.

    Use this property to add any custom information / context about the stop. The
    input will be passed on to the response as-is and can be used to display useful
    information on, for example, a UI app.
    """

    name: str
    """Specify a custom name for the stop."""
