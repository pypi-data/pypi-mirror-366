# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["StepDeleteParams"]


class StepDeleteParams(TypedDict, total=False):
    route_id: Required[Annotated[str, PropertyInfo(alias="routeID")]]

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """
