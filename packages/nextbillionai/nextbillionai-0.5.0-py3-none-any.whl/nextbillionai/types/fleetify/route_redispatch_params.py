# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .routes.route_steps_request_param import RouteStepsRequestParam
from .routes.route_step_completion_mode import RouteStepCompletionMode

__all__ = ["RouteRedispatchParams", "Operation", "OperationData"]


class RouteRedispatchParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    operations: Required[Iterable[Operation]]
    """A collection of objects with details of the steps to be modified.

    Each object corresponds to a single step.
    """

    distance: float
    """Specify the distance of the route."""


class OperationData(TypedDict, total=False):
    completion_mode: RouteStepCompletionMode
    """Specify the mode of completion to be used for the step.

    Currently, following values are allowed:

    - manual: Steps must be marked as completed manually through the Driver App.
    - geofence: Steps are marked as completed automatically based on the entry
      conditions and geofence specified.
    - geofence_manual_fallback: Steps will be marked as completed automatically
      based on geofence and entry condition configurations but there will also be a
      provision for manually updating the status in case, geofence detection fails.
    """

    document_template_id: str
    """
    Specify the ID of the document template to be used for collecting proof of
    completion for the step. It would be applied to step which not be bind to
    document template. Use the
    [Documents API](https://docs.nextbillion.ai/docs/dispatches/documents-api) to
    create, read and manage the document templates.

    Please note that the document template ID can not be assigned to following step
    types - start, end, break, layover.
    """

    step: RouteStepsRequestParam

    step_id: str
    """Specify the ID of the step to be updated or deleted.

    Either one of id or short_id of the step can be provided. This input will be
    ignored when operation: create .
    """


class Operation(TypedDict, total=False):
    data: Required[OperationData]

    operation: Required[Literal["create", "update", "delete"]]
    """Specify the type of operation to be performed for the step."""
