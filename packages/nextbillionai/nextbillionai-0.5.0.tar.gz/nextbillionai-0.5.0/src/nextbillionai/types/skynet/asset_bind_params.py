# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AssetBindParams"]


class AssetBindParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    device_id: Required[str]
    """Device ID to be linked to the asset identified by id.

    Please note that the device needs to be linked to an asset before using it in
    the _Upload locations of an Asset_ method for sending GPS information about the
    asset.
    """
