# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TripUpdateParams", "Stop"]


class TripUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    asset_id: Required[str]
    """Use this param to update the ID of the asset which made this trip.

    Please be cautious when using this field as providing an ID other than what was
    provided at the time of starting the trip, will link a new asset to the trip and
    un-link the original asset, even if the trip is still active.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    attributes: object
    """Use this field to update the attributes of the trip.

    Please note that when updating the attributes field, previously added
    information will be overwritten.
    """

    description: str
    """Use this parameter to update the custom description of the trip."""

    meta_data: object
    """Use this JSON object to update additional details about the trip.

    This property is used to add any custom information / context about the trip.

    Please note that updating the meta_data field will overwrite the previously
    added information.
    """

    name: str
    """Use this property to update the name of the trip."""

    stops: Iterable[Stop]
    """Use this object to update the details of the stops made during the trip.

    Each object represents a single stop.

    Please note that when updating this field, the new stops will overwrite any
    existing stops configured for the trip.
    """


class Stop(TypedDict, total=False):
    geofence_id: str
    """
    Use this parameter to update the ID of the geofence indicating the area where
    the asset needs to make a stop, during the trip. Only the IDs of geofences
    created using
    [NextBillion.ai's Geofence API](https://docs.nextbillion.ai/docs/tracking/api/geofence#create-a-geofence)
    are accepted.

    Please note that updating this field will overwrite the previously added
    information.
    """

    meta_data: object
    """Use this JSON object to update additional details about the stop.

    This property is used to add any custom information / context about the stop.

    Please note that updating the meta_data field will overwrite the previously
    added information.
    """

    name: str
    """Use this filed to update the name of the stop."""
