# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, TypedDict

from .optimization.job_param import JobParam
from .optimization.vehicle_param import VehicleParam
from .optimization.shipment_param import ShipmentParam

__all__ = ["OptimizationReOptimizeParams", "JobChanges", "ShipmentChanges", "VehicleChanges"]


class OptimizationReOptimizeParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    existing_request_id: Required[str]
    """Specify the unique request ID that needs to be re-optimized."""

    job_changes: JobChanges
    """
    This section gathers information on modifications to the number of jobs or their
    individual requirements for re-optimization. Any job from the original solution
    not specified here will be re-planned without alteration during the
    re-optimization process.
    """

    locations: List[str]
    """Provide the list of locations to be used during re-optimization process.

    Please note that

    - Providing the location input overwrites the list of locations used in the
      original request.
    - The location_indexes associated with all tasks and vehicles (both from the
      original and new re-optimization input requests) will follow the updated list
      of locations.

    As a best practice:

    1.  Don't provide the locations input when re-optimizing, if the original set
        contains all the required location coordinates.
    2.  If any new location coordinates are required for re-optimization, copy the
        full, original location list and update it in the following manner before
        adding it to the re-optimization input:

        1.  Ensure to not update the indexes of locations which just need to be
            "modified".
        2.  Add new location coordinates towards the end of the list.
    """

    shipment_changes: ShipmentChanges
    """
    This section gathers information on modifications to the number of shipments or
    their individual requirements for re-optimization. Any shipment from the
    original solution not specified here will be re-planned without alteration
    during the re-optimization process.
    """

    vehicle_changes: VehicleChanges
    """
    This section gathers information on modifications to the number of vehicles or
    individual vehicle configurations for re-optimizing an existing solution. Any
    vehicle from the original solution not specified here will be reused without
    alteration during the re-optimization process.
    """


class JobChanges(TypedDict, total=False):
    add: Iterable[JobParam]
    """
    An array of objects to collect the details of the new jobs to be added during
    re-optimization. Each object represents one job. Please make sure the IDs
    provided for new jobs are unique with respect to the IDs of the jobs in the
    original request.
    """

    modify: Iterable[JobParam]
    """
    An array of objects to collect the modified details of existing jobs used in the
    original request. Each object represents one job. Please make sure all the job
    IDs provided here are same as the ones in the original request.
    """

    remove: List[str]
    """An array of job IDs to be removed when during re-optimization.

    All job IDs provided must have been part of the original request.
    """


class ShipmentChanges(TypedDict, total=False):
    add: Iterable[ShipmentParam]
    """
    An array of objects to collect the details of the new shipments to be added
    during re-optimization. Each object represents one shipment. Please make sure
    the IDs provided for new shipments are unique with respect to the IDs of the
    shipments in the original request.
    """

    modify: Iterable[ShipmentParam]
    """
    An array of objects to collect the modified details of existing shipments used
    in the original request. Each object represents one shipment. Please make sure
    all the shipment IDs provided here are same as the ones in the original request.
    """

    remove: List[str]
    """An array of shipment IDs to be removed when during re-optimization.

    All shipment IDs provided must have been part of the original request.
    """


class VehicleChanges(TypedDict, total=False):
    add: Iterable[VehicleParam]
    """
    An array of objects to collect the details of the new vehicles to be added for
    re-optimization. Each object represents one vehicle. Please make sure the IDs
    provided for new vehicles are unique with respect to the IDs of the vehicles in
    the original request.
    """

    modify: VehicleParam

    remove: List[str]
    """An array of vehicle IDs to be removed when during re-optimization.

    All vehicle IDs provided must have been part of the original request.
    """
