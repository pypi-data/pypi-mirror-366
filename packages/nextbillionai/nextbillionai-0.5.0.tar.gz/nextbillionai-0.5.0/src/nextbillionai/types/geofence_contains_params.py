# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["GeofenceContainsParams"]


class GeofenceContainsParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    locations: Required[str]
    """
    Pipe (|) separated coordinates, in [latitude,longitude] format, of the locations
    to be searched against the geofences.
    """

    geofences: str
    """A , separated list geofence IDs against which the locations will be searched.

    If not provided, then the 'locations' will be searched against all your existing
    geofences.

    Maximum length of the string can be 256 characters.
    """

    verbose: str
    """When true, an array with detailed information of geofences is returned.

    When false, an array containing only the IDs of the geofences is returned.
    """
