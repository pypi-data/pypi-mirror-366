# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DocumentTemplateContentRequestParam", "Meta", "MetaOption", "Validation"]


class MetaOption(TypedDict, total=False):
    label: Required[str]
    """Specify the label or name for the option."""

    value: Required[str]
    """Specify the value associated with the option.

    This value will be submitted when the option is checked in the Driver app.
    """


class Meta(TypedDict, total=False):
    options: Required[Iterable[MetaOption]]
    """
    An array of objects to define options for a multi_choices or single_choice type
    document field. Each object represents one option.
    """


class Validation(TypedDict, total=False):
    max: int
    """Specifies the maximum allowed value for number type document field.

    Input values must be less than or equal to this threshold.
    """

    max_items: int
    """
    Specifies the maximum number of items for multi_choices, photos type document
    fields. The number of provided input items must be less than or equal to this
    threshold.
    """

    min: int
    """Specifies the minimum allowed value for number type document field.

    Input values must be greater than or equal to this threshold.
    """

    min_items: int
    """
    Specifies the minimum number of items for multi_choices, photos type document
    fields. The number of provided input items must be greater than or equal to this
    threshold.
    """


class DocumentTemplateContentRequestParam(TypedDict, total=False):
    label: Required[str]
    """Specify the label or the name of the field.

    The label specified here can be used as field name when rendering the document
    in the Driver app.
    """

    type: Required[
        Literal["string", "number", "date_time", "photos", "multi_choices", "signature", "barcode", "single_choice"]
    ]
    """Specify the data type of the field.

    It corresponds to the type of information that the driver needs to collect.
    """

    meta: Meta
    """
    An object to define additional information required for single_choice or
    multi_choices type document items.
    """

    name: str
    """Specify the name of the document field.

    A field'sname can be used for internal references to the document field.
    """

    required: bool
    """Specify if it is mandatory to fill the field. Default value is false."""

    validation: Validation
    """Specify the validation rules for the field.

    This can be used to enforce data quality and integrity checks. For example, if
    the field is a number type, validation can define constraints like minimum /
    maximum number values.
    """
