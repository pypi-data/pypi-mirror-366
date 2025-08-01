# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RouteReportCreateParams"]


class RouteReportCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    original_shape: Required[str]
    """Takes a route geometry as input and returns the route details.

    Accepts polyline and polyline6 encoded geometry as input.

    **Note**: Route geometries generated from sources other than
    [NextBillion.ai](http://NextBillion.ai) services, are not supported in this
    version.
    """

    original_shape_type: Required[Literal["polyline", "polyline6"]]
    """Specify the encoding type of route geometry provided in original_shape input.

    Please note that an error is returned when this parameter is not specified while
    an input is added to original_shape parameter.
    """
