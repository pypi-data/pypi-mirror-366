# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from .route_step_completion_mode import RouteStepCompletionMode
from .route_step_geofence_config import RouteStepGeofenceConfig

__all__ = ["RouteStepsResponse", "Completion", "Meta"]


class Completion(BaseModel):
    completed_at: Optional[int] = None
    """Represents the timestamp of the completion in seconds since the Unix epoch.

    Example: 1738743999.
    """

    completed_by_mode: Optional[RouteStepCompletionMode] = None
    """Specify the mode of completion to be used for the step.

    Currently, following values are allowed:

    - manual: Steps must be marked as completed manually through the Driver App.
    - geofence: Steps are marked as completed automatically based on the entry
      conditions and geofence specified.
    - geofence_manual_fallback: Steps will be marked as completed automatically
      based on geofence and entry condition configurations but there will also be a
      provision for manually updating the status in case, geofence detection fails.
    """

    completion_mode: Optional[RouteStepCompletionMode] = None
    """Specify the mode of completion to be used for the step.

    Currently, following values are allowed:

    - manual: Steps must be marked as completed manually through the Driver App.
    - geofence: Steps are marked as completed automatically based on the entry
      conditions and geofence specified.
    - geofence_manual_fallback: Steps will be marked as completed automatically
      based on geofence and entry condition configurations but there will also be a
      provision for manually updating the status in case, geofence detection fails.
    """

    document: Optional[object] = None
    """
    A key-value map storing form submission data, where keys correspond to field
    labels and values can be of any type depend on the type of according document
    item.
    """

    document_modified_at: Optional[int] = None
    """
    Represents the timestamp of the last doc modification in seconds since the Unix
    epoch. Example: 1738743999.
    """

    geofence_config: Optional[RouteStepGeofenceConfig] = None
    """
    Specify the configurations of the geofence which will be used to detect presence
    of the driver and complete the tasks automatically. Please note that this
    attribute is required when completion_mode is either "geofence" or
    "geofence_manual_fallback".
    """

    status: Optional[Literal["scheduled", "completed", "canceled"]] = None
    """Status of the step."""


class Meta(BaseModel):
    customer_name: Optional[str] = None
    """Returns the customer name associated with the step.

    It can configured in the input request using the metadata attribute of the step.
    """

    customer_phone_number: Optional[str] = None
    """Returns the customer's phone number associated with the step.

    It can configured in the input request using the metadata attribute of the step.
    """

    instructions: Optional[str] = None
    """Returns the custom instructions to carry out while performing the task.

    These instructions can be provided at the time of configuring the step details
    in the input request.
    """


class RouteStepsResponse(BaseModel):
    id: Optional[str] = None
    """Returns the unique ID of the step."""

    address: Optional[str] = None
    """Returns the postal address where the step is executed.

    Its value is the same as that specified in the input request when configuring
    the step details.
    """

    arrival: Optional[int] = None
    """
    Returns the scheduled arrival time of the driver at the step as an UNIX
    timestamp, in seconds precision. It is the same as that specified in the input
    request while configuring the step details.

    The timestamp returned here is only for informative display on the driver's app
    and it does not impact or get affected by the route generated.
    """

    completion: Optional[Completion] = None

    created_at: Optional[int] = None
    """Represents the timestamp of the creation in seconds since the Unix epoch.

    Example: 1738743999.
    """

    document_snapshot: Optional[List[object]] = None
    """
    Returns the details of the document that was used for collecting the proof of
    completion for the step. In case no document template ID was provided for the
    given step, then a null value is returned. Each object represents a new field in
    the document.
    """

    duration: Optional[int] = None
    """Returns the duration for layover or break type steps."""

    location: Optional[List[float]] = None
    """Returns the location coordinates where the step is executed."""

    meta: Optional[Meta] = None
    """
    An object returning custom details about the step that were configured in the
    input request while configuring the step details. The information returned here
    will be available for display on the Driver's app under step details.
    """

    short_id: Optional[str] = None
    """
    Returns a unique short ID of the step for easier referencing and displaying
    purposes.
    """

    type: Optional[str] = None
    """Returns the step type.

    It can belong to one of the following: start, job , pickup, delivery, break,
    layover , and end. For any given step, it would be the same as that specified in
    the input request while configuring the step details.
    """

    updated_at: Optional[int] = None
    """Represents the timestamp of the last update in seconds since the Unix epoch.

    Example: 1738743999.
    """
