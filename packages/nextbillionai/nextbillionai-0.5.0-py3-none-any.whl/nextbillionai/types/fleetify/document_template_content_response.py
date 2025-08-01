# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["DocumentTemplateContentResponse", "Meta", "MetaOption", "Validation"]


class MetaOption(BaseModel):
    label: Optional[str] = None
    """Returns the label for the option."""

    value: Optional[str] = None
    """Returns the value associated with the option.

    This value gets submitted when the option is checked in the Driver app.
    """


class Meta(BaseModel):
    options: Optional[List[MetaOption]] = None
    """
    An array of objects returning the options for multi_choices or single_choice
    type document field. Each object represents one configured option.
    """


class Validation(BaseModel):
    max: Optional[int] = None
    """
    Returns the maximum allowed value for number type document item, as specified at
    the time of configuring the field. This parameter is not present in the response
    if it was not provided in the input.
    """

    max_items: Optional[str] = None
    """
    Returns the maximum number of items required for multi_choices, photos type
    document items. This parameter will not be present in the response if it was not
    provided in the input.
    """

    min: Optional[int] = None
    """
    Returns the minimum allowed value for number type document item, as specified at
    the time of configuring the field. This parameter is not present in the response
    if it was not provided in the input.
    """

    min_items: Optional[str] = None
    """
    Returns the minimum number of items required for multi_choices, photos type
    document items. This parameter will not be present in the response if it was not
    provided in the input.
    """


class DocumentTemplateContentResponse(BaseModel):
    label: Optional[str] = None
    """Returns the label of the document field."""

    meta: Optional[Meta] = None
    """
    Returns the options configured for single_choice or multi_choices type document
    items.
    """

    name: Optional[str] = None
    """Returns the name of the document field."""

    required: Optional[bool] = None
    """Indicates if the document field is mandatory or not."""

    type: Optional[str] = None
    """Returns the data type of the document field.

    It will always belong to one of string, number, date_time, photos,
    multi_choices, signature, barcode, and single_choice.
    """

    validation: Optional[Validation] = None
    """
    Returns the validation rules for number , multi_choices , and photos document
    field types.
    """
