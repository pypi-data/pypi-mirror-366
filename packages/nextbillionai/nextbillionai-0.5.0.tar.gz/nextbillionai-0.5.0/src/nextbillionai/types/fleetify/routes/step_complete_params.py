# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .document_submission_param import DocumentSubmissionParam

__all__ = ["StepCompleteParams"]


class StepCompleteParams(TypedDict, total=False):
    route_id: Required[Annotated[str, PropertyInfo(alias="routeID")]]

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    document: DocumentSubmissionParam
    """
    A key-value map storing form submission data, where keys correspond to field
    labels and values can be of any type depend on the type of according document
    item.
    """

    mode: str
    """Sets the status of the route step. Currently only completed is supported.

    Note: once marked completed, a step cannot transition to other statuses. You can
    only update the document afterwards.
    """

    status: str
    """Sets the status of the route step. Currently only completed is supported.

    Note: once marked completed, a step cannot transition to other statuses. You can
    only update the document afterwards.
    """
