# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Address"]


class Address(BaseModel):
    city: Optional[str] = None
    """The name of the primary locality of the place."""

    country_code: Optional[str] = FieldInfo(alias="countryCode", default=None)
    """A three-letter country code."""

    country_name: Optional[str] = FieldInfo(alias="countryName", default=None)
    """The localised country name."""

    county: Optional[str] = None
    """
    A division of a state; typically, a secondary-level administrative division of a
    country or equivalent.
    """

    district: Optional[str] = None
    """
    A division of city; typically an administrative unit within a larger city or a
    customary name of a city's neighborhood.
    """

    house_number: Optional[str] = FieldInfo(alias="houseNumber", default=None)
    """House number of the returned place, if available."""

    label: Optional[str] = None
    """
    Assembled address value built out of the address components according to the
    regional postal rules. These are the same rules for all endpoints. It may not
    include all the input terms.
    """

    postal_code: Optional[str] = FieldInfo(alias="postalCode", default=None)
    """
    An alphanumeric string included in a postal address to facilitate mail sorting,
    such as post code, postcode, or ZIP code.
    """

    state: Optional[str] = None
    """The state division of a country."""

    state_code: Optional[str] = FieldInfo(alias="stateCode", default=None)
    """A country specific state code or state name abbreviation.

    For example, in the United States it is the two letter state abbreviation: "CA"
    for California.
    """

    street: Optional[str] = None
    """Name of street of the returned place, if available."""
