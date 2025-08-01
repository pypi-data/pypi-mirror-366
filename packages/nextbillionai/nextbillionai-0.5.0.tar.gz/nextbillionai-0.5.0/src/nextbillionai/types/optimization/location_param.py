# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["LocationParam"]


class LocationParam(TypedDict, total=False):
    lat: Required[float]
    """Latitude of location."""

    lon: Required[float]
    """Longitude of location."""
