# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RestrictionSetStateParams"]


class RestrictionSetStateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    state: Required[Literal["enabled", "disabled", "deleted"]]
    """Use this field to specify the new state of the restriction.

    Please note that this method cannot update the state of restrictions that are
    currently in 'deleted' state.
    """
