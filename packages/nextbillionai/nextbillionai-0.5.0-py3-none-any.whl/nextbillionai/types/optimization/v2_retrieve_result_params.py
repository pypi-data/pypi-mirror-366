# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["V2RetrieveResultParams"]


class V2RetrieveResultParams(TypedDict, total=False):
    id: Required[str]
    """
    The unique ID that was returned on successful submission of the Optimization
    POST request.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """
