# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["OptimizationComputeParams"]


class OptimizationComputeParams(TypedDict, total=False):
    coordinates: Required[str]
    """This is a pipe-separated list of coordinates.

    Minimum 3 pairs of coordinates and Maximum 12 pairs of coordinates are allowed.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    approaches: Literal["unrestricted", "curb"]
    """
    A semicolon-separated list indicating the side of the road from which to
    approach waypoints in a requested route. If provided, the number of approaches
    must be the same as the number of coordinates. However, you can skip a
    coordinate and show its position in the list with the ; separator.
    """

    destination: Literal["any", "last"]
    """Specify the destination coordinate of the returned route.

    If the input is last, the last coordinate will be the destination.
    """

    geometries: Literal["polyline", "polyline6", "geojson"]
    """Sets the output format of the route geometry in the response.

    On providing polyline and polyline6 as input, respective encoded geometry is
    returned. However, when geojson is provided as the input value, polyline encoded
    geometry is returned in the response along with a geojson details of the route.
    """

    mode: Literal["car", "truck"]
    """Set which driving mode the service should use to determine a route.

    For example, if you use "car", the API will return a route that a car can take.
    Using "truck" will return a route a truck can use, taking into account
    appropriate truck routing restrictions.

    When "mode=truck", following are the default dimensions that are used:

    \\-- truck_height = 214 centimeters

    \\-- truck_width = 183 centimeters

    \\-- truck_length = 519 centimeters

    \\-- truck_weight = 5000 kg

    Please use the Directions Flexible version if you want to use custom truck
    dimensions.

    Note: Only the "car" profile is enabled by default. Please note that customized
    profiles (including "truck") might not be available for all regions. Please
    contact your [NextBillion.ai](http://NextBillion.ai) account manager, sales
    representative or reach out at
    [support@nextbillion.ai](mailto:support@nextbillion.ai) in case you need
    additional profiles.
    """

    roundtrip: bool
    """Indicates whether the returned route is a roundtrip."""

    source: Literal["any", "first"]
    """The coordinate at which to start the returned route.

    If this is not configured, the return route’s destination will be the first
    coordinate.
    """

    with_geometry: bool
    """Indicates whether the return geometry should be computed or not."""
