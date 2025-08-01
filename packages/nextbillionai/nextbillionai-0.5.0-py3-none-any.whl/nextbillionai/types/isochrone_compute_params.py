# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["IsochroneComputeParams"]


class IsochroneComputeParams(TypedDict, total=False):
    contours_meters: Required[int]
    """The distances, in meters, to use for each isochrone contour.

    You can specify up to four contours. Distances must be in increasing order. The
    maximum distance that can be specified is 60000 meters (60 km).
    """

    contours_minutes: Required[int]
    """The times, in minutes, to use for each isochrone contour.

    You can specify up to four contours. Times must be in increasing order. The
    maximum time that can be specified is 40 minutes.
    """

    coordinates: Required[str]
    """
    The coordinates of the location which acts as the starting point for which the
    isochrone lines need to be determined.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    contours_colors: str
    """The hex code of the color to fill isochrone contour.

    When requesting multiple contours, it is recommended to provide color codes for
    each of the requested contours, separated by a ",". If no colors are specified,
    the Isochrone API will assign a random color scheme to the output.
    """

    denoise: float
    """A floating point value from 0.0 to 1.0 can be used to remove smaller contours.

    The default is 1.0. A value of 1.0 will only return the largest contour for a
    given value. A value of 0.5 drops any contours that are less than half the area
    of the largest contour in the set of contours for that same value.
    """

    departure_time: int
    """
    Use this parameter to set a departure time, expressed as UNIX epoch timestamp in
    seconds, for calculating the isochrone contour. The response will consider the
    typical traffic conditions at the given time and return a contour which can be
    reached under those traffic conditions. Please note that if no input is provided
    for this parameter then the traffic conditions at the time of making the request
    are considered.
    """

    generalize: float
    """
    A positive floating point value, in meters, used as the tolerance for
    Douglas-Peucker generalization. There is no upper bound. If no value is
    specified in the request, the Isochrone API will choose the most optimized
    generalization to use for the request. Note that the generalization of contours
    can lead to self-intersections, as well as intersections of adjacent contours.
    """

    mode: Literal["car", "truck"]
    """Set which driving mode the service should use to determine the contour.

    For example, if you use "car", the API will return an isochrone contour that a
    car can reach within the specified time or after driving the specified distance.
    Using "truck" will return a contour that a truck can reach after taking into
    account appropriate truck routing restrictions.

    Note: Only the "car" profile is enabled by default. Please note that customized
    profiles (including "truck") might not be available for all regions. Please
    contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
    representative or reach out at
    [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
    additional profiles.
    """

    polygons: bool
    """
    Specify whether to return the contours as GeoJSON polygons (true) or linestrings
    (false, default). When polygons=true, any contour that forms a ring is returned
    as a polygon.
    """
