# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ConfigUpdateParams"]


class ConfigUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    webhook: List[str]
    """Use this array to update information about the webhooks.

    Please note that the webhooks will be overwritten every time this method is
    used.
    """
