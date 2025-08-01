# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ConfigTestWebhookResponse"]


class ConfigTestWebhookResponse(BaseModel):
    status: Optional[str] = None
    """A string indicating the state of the response.

    Please note this value will always be Ok.

    The sample event information will be received on the webhook, if they were
    successfully configured. If no event information is received by the webhook,
    please reconfigure the webhook or else reach out to
    [support@nextbillion.ai](mailto:support@nextbillion.ai) for help.
    """
