# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.fleetify.routes import (
    RouteStepCompletionMode,
    step_create_params,
    step_delete_params,
    step_update_params,
    step_complete_params,
)
from ....types.fleetify.routes.step_create_response import StepCreateResponse
from ....types.fleetify.routes.step_delete_response import StepDeleteResponse
from ....types.fleetify.routes.step_update_response import StepUpdateResponse
from ....types.fleetify.routes.document_submission_param import DocumentSubmissionParam
from ....types.fleetify.routes.route_step_completion_mode import RouteStepCompletionMode
from ....types.fleetify.routes.route_step_geofence_config_param import RouteStepGeofenceConfigParam

__all__ = ["StepsResource", "AsyncStepsResource"]


class StepsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StepsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return StepsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StepsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return StepsResourceWithStreamingResponse(self)

    def create(
        self,
        route_id: str,
        *,
        key: str,
        arrival: int,
        location: Iterable[float],
        position: int,
        type: Literal["start", "job", "pickup", "delivery", "break", "layover", "end"],
        address: str | NotGiven = NOT_GIVEN,
        completion_mode: RouteStepCompletionMode | NotGiven = NOT_GIVEN,
        document_template_id: str | NotGiven = NOT_GIVEN,
        duration: int | NotGiven = NOT_GIVEN,
        geofence_config: RouteStepGeofenceConfigParam | NotGiven = NOT_GIVEN,
        meta: step_create_params.Meta | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepCreateResponse:
        """
        Insert a new step

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          arrival: Specify the scheduled arrival time of the driver, as an UNIX timestamp in
              seconds, at the step. Please note that:

              - Arrival time for each step should be equal to or greater than the previous
                step.
              - Past times can not be provided.
              - The time provided is used only for informative display on the driver app and
                it does not impact or get affected by the route generated.

          location: Specify the location coordinates where the steps should be performed in
              [latitude, longitude].

          position: Indicates the index at which to insert the step, starting from 0 up to the total
              number of steps in the route.

          type: Specify the step type. It can belong to one of the following: start, job ,
              pickup, delivery, end. A duration is mandatory when the step type is either
              layover or a break.

          address: Specify the postal address for the step.

          completion_mode: Specify the mode of completion to be used for the step. Currently, following
              values are allowed:

              - manual: Steps must be marked as completed manually through the Driver App.
              - geofence: Steps are marked as completed automatically based on the entry
                conditions and geofence specified.
              - geofence_manual_fallback: Steps will be marked as completed automatically
                based on geofence and entry condition configurations but there will also be a
                provision for manually updating the status in case, geofence detection fails.

          document_template_id: Specify the ID of the document template to be used for collecting proof of
              completion for the step. If not specified, the document template specified at
              the route level will be used for the step. Use the
              [Documents API](https://docs.nextbillion.ai/docs/dispatches/documents-api) to
              create, read and manage the document templates.

              Please note that the document template ID can not be assigned to following step
              types - start, end, break, layover.

          duration: Specify the duration of the layover or break type steps, in seconds. Please note
              it is mandatory when step type is either "layover" or "break".

          geofence_config: Specify the configurations of the geofence which will be used to detect presence
              of the driver and complete the tasks automatically. Please note that this
              attribute is required when completion_mode is either "geofence" or
              "geofence_manual_fallback".

          meta: An object to specify any additional details about the task to be associated with
              the step in the response. The information provided here will be available on the
              Driver's app under step details. This attribute can be used to provide context
              about or instructions to the driver for performing the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        return self._post(
            f"/fleetify/routes/{route_id}/steps",
            body=maybe_transform(
                {
                    "arrival": arrival,
                    "location": location,
                    "position": position,
                    "type": type,
                    "address": address,
                    "completion_mode": completion_mode,
                    "document_template_id": document_template_id,
                    "duration": duration,
                    "geofence_config": geofence_config,
                    "meta": meta,
                },
                step_create_params.StepCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, step_create_params.StepCreateParams),
            ),
            cast_to=StepCreateResponse,
        )

    def update(
        self,
        step_id: str,
        *,
        route_id: str,
        key: str,
        arrival: int,
        position: int,
        address: str | NotGiven = NOT_GIVEN,
        completion_mode: RouteStepCompletionMode | NotGiven = NOT_GIVEN,
        document_template_id: str | NotGiven = NOT_GIVEN,
        duration: int | NotGiven = NOT_GIVEN,
        geofence_config: RouteStepGeofenceConfigParam | NotGiven = NOT_GIVEN,
        location: Iterable[float] | NotGiven = NOT_GIVEN,
        meta: step_update_params.Meta | NotGiven = NOT_GIVEN,
        type: Literal["start", "job", "pickup", "delivery", "break", "layover", "end"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepUpdateResponse:
        """
        Update a step

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          arrival: Specify the scheduled arrival time of the driver, as an UNIX timestamp in
              seconds, at the step. Please note that:

              - Arrival time for each step should be equal to or greater than the previous
                step.
              - Past times can not be provided.
              - The time provided is used only for informative display on the driver app and
                it does not impact or get affected by the route generated.

          position: Specify the new position of the step. Provide a position different from the
              current position of the step to update sequence in which the step get completed.

          address: Specify the postal address for the step.

          completion_mode: Specify the mode of completion to be used for the step. Currently, following
              values are allowed:

              - manual: Steps must be marked as completed manually through the Driver App.
              - geofence: Steps are marked as completed automatically based on the entry
                conditions and geofence specified.
              - geofence_manual_fallback: Steps will be marked as completed automatically
                based on geofence and entry condition configurations but there will also be a
                provision for manually updating the status in case, geofence detection fails.

          document_template_id: Update the ID of the document template to be used for collecting proof of
              completion for the step. If an empty string "" is provided, the current document
              template associated to the step will be removed.

          duration: Specify the duration of the layover or break type steps, in seconds. Please note
              it is mandatory when step type is either "layover" or "break".

          geofence_config: Specify the configurations of the geofence which will be used to detect presence
              of the driver and complete the tasks automatically. Please note that this
              attribute is required when completion_mode is either "geofence" or
              "geofence_manual_fallback".

          location: Specify the location coordinates where the steps should be performed in
              [latitude, longitude].

          meta: An object to specify any additional details about the task to be associated with
              the step in the response. The information provided here will be available on the
              Driver's app under step details. This attribute can be used to provide context
              about or instructions to the driver for performing the task

          type: Specify the step type. It can belong to one of the following: start, job ,
              pickup, delivery, end. A duration is mandatory when the step type is either
              layover or a break.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        return self._put(
            f"/fleetify/routes/{route_id}/steps/{step_id}",
            body=maybe_transform(
                {
                    "arrival": arrival,
                    "position": position,
                    "address": address,
                    "completion_mode": completion_mode,
                    "document_template_id": document_template_id,
                    "duration": duration,
                    "geofence_config": geofence_config,
                    "location": location,
                    "meta": meta,
                    "type": type,
                },
                step_update_params.StepUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, step_update_params.StepUpdateParams),
            ),
            cast_to=StepUpdateResponse,
        )

    def delete(
        self,
        step_id: str,
        *,
        route_id: str,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepDeleteResponse:
        """
        Delete a step

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        return self._delete(
            f"/fleetify/routes/{route_id}/steps/{step_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, step_delete_params.StepDeleteParams),
            ),
            cast_to=StepDeleteResponse,
        )

    def complete(
        self,
        step_id: str,
        *,
        route_id: str,
        key: str,
        document: DocumentSubmissionParam | NotGiven = NOT_GIVEN,
        mode: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Complete a route step with document submission, or update the document of a
        completed route step.

        When all steps are completed, the encapsulating route’s status will change to
        completed automatically.

        Either Session Token must be provided to authenticate the request.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          document: A key-value map storing form submission data, where keys correspond to field
              labels and values can be of any type depend on the type of according document
              item.

          mode: Sets the status of the route step. Currently only completed is supported.

              Note: once marked completed, a step cannot transition to other statuses. You can
              only update the document afterwards.

          status: Sets the status of the route step. Currently only completed is supported.

              Note: once marked completed, a step cannot transition to other statuses. You can
              only update the document afterwards.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._patch(
            f"/fleetify/routes/{route_id}/steps/{step_id}",
            body=maybe_transform(
                {
                    "document": document,
                    "mode": mode,
                    "status": status,
                },
                step_complete_params.StepCompleteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, step_complete_params.StepCompleteParams),
            ),
            cast_to=NoneType,
        )


class AsyncStepsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStepsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStepsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStepsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncStepsResourceWithStreamingResponse(self)

    async def create(
        self,
        route_id: str,
        *,
        key: str,
        arrival: int,
        location: Iterable[float],
        position: int,
        type: Literal["start", "job", "pickup", "delivery", "break", "layover", "end"],
        address: str | NotGiven = NOT_GIVEN,
        completion_mode: RouteStepCompletionMode | NotGiven = NOT_GIVEN,
        document_template_id: str | NotGiven = NOT_GIVEN,
        duration: int | NotGiven = NOT_GIVEN,
        geofence_config: RouteStepGeofenceConfigParam | NotGiven = NOT_GIVEN,
        meta: step_create_params.Meta | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepCreateResponse:
        """
        Insert a new step

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          arrival: Specify the scheduled arrival time of the driver, as an UNIX timestamp in
              seconds, at the step. Please note that:

              - Arrival time for each step should be equal to or greater than the previous
                step.
              - Past times can not be provided.
              - The time provided is used only for informative display on the driver app and
                it does not impact or get affected by the route generated.

          location: Specify the location coordinates where the steps should be performed in
              [latitude, longitude].

          position: Indicates the index at which to insert the step, starting from 0 up to the total
              number of steps in the route.

          type: Specify the step type. It can belong to one of the following: start, job ,
              pickup, delivery, end. A duration is mandatory when the step type is either
              layover or a break.

          address: Specify the postal address for the step.

          completion_mode: Specify the mode of completion to be used for the step. Currently, following
              values are allowed:

              - manual: Steps must be marked as completed manually through the Driver App.
              - geofence: Steps are marked as completed automatically based on the entry
                conditions and geofence specified.
              - geofence_manual_fallback: Steps will be marked as completed automatically
                based on geofence and entry condition configurations but there will also be a
                provision for manually updating the status in case, geofence detection fails.

          document_template_id: Specify the ID of the document template to be used for collecting proof of
              completion for the step. If not specified, the document template specified at
              the route level will be used for the step. Use the
              [Documents API](https://docs.nextbillion.ai/docs/dispatches/documents-api) to
              create, read and manage the document templates.

              Please note that the document template ID can not be assigned to following step
              types - start, end, break, layover.

          duration: Specify the duration of the layover or break type steps, in seconds. Please note
              it is mandatory when step type is either "layover" or "break".

          geofence_config: Specify the configurations of the geofence which will be used to detect presence
              of the driver and complete the tasks automatically. Please note that this
              attribute is required when completion_mode is either "geofence" or
              "geofence_manual_fallback".

          meta: An object to specify any additional details about the task to be associated with
              the step in the response. The information provided here will be available on the
              Driver's app under step details. This attribute can be used to provide context
              about or instructions to the driver for performing the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        return await self._post(
            f"/fleetify/routes/{route_id}/steps",
            body=await async_maybe_transform(
                {
                    "arrival": arrival,
                    "location": location,
                    "position": position,
                    "type": type,
                    "address": address,
                    "completion_mode": completion_mode,
                    "document_template_id": document_template_id,
                    "duration": duration,
                    "geofence_config": geofence_config,
                    "meta": meta,
                },
                step_create_params.StepCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, step_create_params.StepCreateParams),
            ),
            cast_to=StepCreateResponse,
        )

    async def update(
        self,
        step_id: str,
        *,
        route_id: str,
        key: str,
        arrival: int,
        position: int,
        address: str | NotGiven = NOT_GIVEN,
        completion_mode: RouteStepCompletionMode | NotGiven = NOT_GIVEN,
        document_template_id: str | NotGiven = NOT_GIVEN,
        duration: int | NotGiven = NOT_GIVEN,
        geofence_config: RouteStepGeofenceConfigParam | NotGiven = NOT_GIVEN,
        location: Iterable[float] | NotGiven = NOT_GIVEN,
        meta: step_update_params.Meta | NotGiven = NOT_GIVEN,
        type: Literal["start", "job", "pickup", "delivery", "break", "layover", "end"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepUpdateResponse:
        """
        Update a step

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          arrival: Specify the scheduled arrival time of the driver, as an UNIX timestamp in
              seconds, at the step. Please note that:

              - Arrival time for each step should be equal to or greater than the previous
                step.
              - Past times can not be provided.
              - The time provided is used only for informative display on the driver app and
                it does not impact or get affected by the route generated.

          position: Specify the new position of the step. Provide a position different from the
              current position of the step to update sequence in which the step get completed.

          address: Specify the postal address for the step.

          completion_mode: Specify the mode of completion to be used for the step. Currently, following
              values are allowed:

              - manual: Steps must be marked as completed manually through the Driver App.
              - geofence: Steps are marked as completed automatically based on the entry
                conditions and geofence specified.
              - geofence_manual_fallback: Steps will be marked as completed automatically
                based on geofence and entry condition configurations but there will also be a
                provision for manually updating the status in case, geofence detection fails.

          document_template_id: Update the ID of the document template to be used for collecting proof of
              completion for the step. If an empty string "" is provided, the current document
              template associated to the step will be removed.

          duration: Specify the duration of the layover or break type steps, in seconds. Please note
              it is mandatory when step type is either "layover" or "break".

          geofence_config: Specify the configurations of the geofence which will be used to detect presence
              of the driver and complete the tasks automatically. Please note that this
              attribute is required when completion_mode is either "geofence" or
              "geofence_manual_fallback".

          location: Specify the location coordinates where the steps should be performed in
              [latitude, longitude].

          meta: An object to specify any additional details about the task to be associated with
              the step in the response. The information provided here will be available on the
              Driver's app under step details. This attribute can be used to provide context
              about or instructions to the driver for performing the task

          type: Specify the step type. It can belong to one of the following: start, job ,
              pickup, delivery, end. A duration is mandatory when the step type is either
              layover or a break.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        return await self._put(
            f"/fleetify/routes/{route_id}/steps/{step_id}",
            body=await async_maybe_transform(
                {
                    "arrival": arrival,
                    "position": position,
                    "address": address,
                    "completion_mode": completion_mode,
                    "document_template_id": document_template_id,
                    "duration": duration,
                    "geofence_config": geofence_config,
                    "location": location,
                    "meta": meta,
                    "type": type,
                },
                step_update_params.StepUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, step_update_params.StepUpdateParams),
            ),
            cast_to=StepUpdateResponse,
        )

    async def delete(
        self,
        step_id: str,
        *,
        route_id: str,
        key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepDeleteResponse:
        """
        Delete a step

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        return await self._delete(
            f"/fleetify/routes/{route_id}/steps/{step_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, step_delete_params.StepDeleteParams),
            ),
            cast_to=StepDeleteResponse,
        )

    async def complete(
        self,
        step_id: str,
        *,
        route_id: str,
        key: str,
        document: DocumentSubmissionParam | NotGiven = NOT_GIVEN,
        mode: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Complete a route step with document submission, or update the document of a
        completed route step.

        When all steps are completed, the encapsulating route’s status will change to
        completed automatically.

        Either Session Token must be provided to authenticate the request.

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          document: A key-value map storing form submission data, where keys correspond to field
              labels and values can be of any type depend on the type of according document
              item.

          mode: Sets the status of the route step. Currently only completed is supported.

              Note: once marked completed, a step cannot transition to other statuses. You can
              only update the document afterwards.

          status: Sets the status of the route step. Currently only completed is supported.

              Note: once marked completed, a step cannot transition to other statuses. You can
              only update the document afterwards.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not route_id:
            raise ValueError(f"Expected a non-empty value for `route_id` but received {route_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._patch(
            f"/fleetify/routes/{route_id}/steps/{step_id}",
            body=await async_maybe_transform(
                {
                    "document": document,
                    "mode": mode,
                    "status": status,
                },
                step_complete_params.StepCompleteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, step_complete_params.StepCompleteParams),
            ),
            cast_to=NoneType,
        )


class StepsResourceWithRawResponse:
    def __init__(self, steps: StepsResource) -> None:
        self._steps = steps

        self.create = to_raw_response_wrapper(
            steps.create,
        )
        self.update = to_raw_response_wrapper(
            steps.update,
        )
        self.delete = to_raw_response_wrapper(
            steps.delete,
        )
        self.complete = to_raw_response_wrapper(
            steps.complete,
        )


class AsyncStepsResourceWithRawResponse:
    def __init__(self, steps: AsyncStepsResource) -> None:
        self._steps = steps

        self.create = async_to_raw_response_wrapper(
            steps.create,
        )
        self.update = async_to_raw_response_wrapper(
            steps.update,
        )
        self.delete = async_to_raw_response_wrapper(
            steps.delete,
        )
        self.complete = async_to_raw_response_wrapper(
            steps.complete,
        )


class StepsResourceWithStreamingResponse:
    def __init__(self, steps: StepsResource) -> None:
        self._steps = steps

        self.create = to_streamed_response_wrapper(
            steps.create,
        )
        self.update = to_streamed_response_wrapper(
            steps.update,
        )
        self.delete = to_streamed_response_wrapper(
            steps.delete,
        )
        self.complete = to_streamed_response_wrapper(
            steps.complete,
        )


class AsyncStepsResourceWithStreamingResponse:
    def __init__(self, steps: AsyncStepsResource) -> None:
        self._steps = steps

        self.create = async_to_streamed_response_wrapper(
            steps.create,
        )
        self.update = async_to_streamed_response_wrapper(
            steps.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            steps.delete,
        )
        self.complete = async_to_streamed_response_wrapper(
            steps.complete,
        )
