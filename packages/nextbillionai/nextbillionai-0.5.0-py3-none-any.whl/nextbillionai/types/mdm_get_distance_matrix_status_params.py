# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MdmGetDistanceMatrixStatusParams"]


class MdmGetDistanceMatrixStatusParams(TypedDict, total=False):
    id: Required[str]
    """
    Provide the unique ID that was returned on successful submission of the
    Asynchronous Distance Matrix POST request.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """
