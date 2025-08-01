# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["IsochroneComputeResponse", "Feature", "FeatureGeometry", "FeatureProperties"]


class FeatureGeometry(BaseModel):
    coordinates: Optional[List[float]] = None
    """
    An array of coordinate points, in [longitude,latitude] format representing the
    isochrone contour line.
    """

    type: Optional[str] = None
    """Type of the geoJSON geometry."""


class FeatureProperties(BaseModel):
    color: Optional[str] = None
    """The hex code of the color of the isochrone contour line"""

    contour: Optional[float] = None
    """The value of the metric used in this contour.

    See the metric property to determine whether this is a time or distance contour.
    When the metric is time this value denotes the travel time in minutes and when
    the metric is distance this value denotes the travel distance in kilometers.
    """

    fill: Optional[str] = None
    """The hex code for the fill color of the isochrone contour line."""

    fill_color: Optional[str] = FieldInfo(alias="fillColor", default=None)
    """The hex code for the fill color of the isochrone contour line"""

    fill_opacity: Optional[float] = FieldInfo(alias="fillOpacity", default=None)
    """The fill opacity for the isochrone contour line.

    It is a float value starting from 0.0 with a max value of 1.0. Higher number
    indicates a higher fill opacity.
    """

    metric: Optional[str] = None
    """The metric that the contour represents - either distance or time"""

    opacity: Optional[float] = None
    """The opacity of the isochrone contour line.

    It is a float value starting from 0.0 with a max value of 1.0. Higher number
    indicates a higher line opacity
    """


class Feature(BaseModel):
    geometry: Optional[FeatureGeometry] = None
    """
    A [GeoJSON geometry](https://datatracker.ietf.org/doc/html/rfc7946#page-7)
    object with details of the contour line.
    """

    properties: Optional[FeatureProperties] = None
    """An object with details of how the isochrone contour can be drawn on a map."""

    type: Optional[str] = None
    """Type of the GeoJSON object.

    Its value is Feature as per the
    [GeoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946#section-1.4)
    object.
    """


class IsochroneComputeResponse(BaseModel):
    features: Optional[List[Feature]] = None
    """
    A
    [GeoJSON FeatureCollection](https://datatracker.ietf.org/doc/html/rfc7946#section-3.3)
    object with details of the isochrone contours. Each feature object in this
    collection represents an isochrone.
    """

    msg: Optional[str] = None
    """Displays the error message in case of a failed request or operation.

    Please note that this parameter is not returned in the response in case of a
    successful request.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On normal responses, the value will be Ok. Indicative HTTP error codes are
    returned for different errors. See the [API Errors Codes](#api-error-codes)
    section below for more information.
    """

    type: Optional[str] = None
    """Type of the GeoJSON object.

    As prescribed in
    [GeoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946#section-1.4),
    its value is FeatureCollection as the feature property contains a list of
    geoJSON feature objects.
    """
