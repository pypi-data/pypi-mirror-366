# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .route_step_completion_mode import RouteStepCompletionMode
from .route_step_geofence_config_param import RouteStepGeofenceConfigParam

__all__ = ["StepCreateParams", "Meta"]


class StepCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    arrival: Required[int]
    """
    Specify the scheduled arrival time of the driver, as an UNIX timestamp in
    seconds, at the step. Please note that:

    - Arrival time for each step should be equal to or greater than the previous
      step.
    - Past times can not be provided.
    - The time provided is used only for informative display on the driver app and
      it does not impact or get affected by the route generated.
    """

    location: Required[Iterable[float]]
    """
    Specify the location coordinates where the steps should be performed in
    [latitude, longitude].
    """

    position: Required[int]
    """
    Indicates the index at which to insert the step, starting from 0 up to the total
    number of steps in the route.
    """

    type: Required[Literal["start", "job", "pickup", "delivery", "break", "layover", "end"]]
    """Specify the step type.

    It can belong to one of the following: start, job , pickup, delivery, end. A
    duration is mandatory when the step type is either layover or a break.
    """

    address: str
    """Specify the postal address for the step."""

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
    completion for the step. If not specified, the document template specified at
    the route level will be used for the step. Use the
    [Documents API](https://docs.nextbillion.ai/docs/dispatches/documents-api) to
    create, read and manage the document templates.

    Please note that the document template ID can not be assigned to following step
    types - start, end, break, layover.
    """

    duration: int
    """Specify the duration of the layover or break type steps, in seconds.

    Please note it is mandatory when step type is either "layover" or "break".
    """

    geofence_config: RouteStepGeofenceConfigParam
    """
    Specify the configurations of the geofence which will be used to detect presence
    of the driver and complete the tasks automatically. Please note that this
    attribute is required when completion_mode is either "geofence" or
    "geofence_manual_fallback".
    """

    meta: Meta
    """
    An object to specify any additional details about the task to be associated with
    the step in the response. The information provided here will be available on the
    Driver's app under step details. This attribute can be used to provide context
    about or instructions to the driver for performing the task
    """


class Meta(TypedDict, total=False):
    customer_name: str
    """Specify the name of the customer for which the step has to be performed."""

    customer_phone_number: str
    """Specify the phone number of the person to be contacted when at step location."""

    instructions: str
    """Specify custom instructions to be carried out while performing the step."""
