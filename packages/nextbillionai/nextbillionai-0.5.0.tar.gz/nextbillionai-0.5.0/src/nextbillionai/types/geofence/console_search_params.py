# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ConsoleSearchParams"]


class ConsoleSearchParams(TypedDict, total=False):
    query: Required[str]
    """string to be searched, will used to match name or id of geofence."""
