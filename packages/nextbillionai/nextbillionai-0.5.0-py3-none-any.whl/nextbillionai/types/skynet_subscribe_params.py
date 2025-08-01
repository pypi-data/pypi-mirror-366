# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SkynetSubscribeParams", "Params"]


class SkynetSubscribeParams(TypedDict, total=False):
    action: Required[Literal["TRIP_SUBSCRIBE", "TRIP_UNSUBSCRIBE", "HEARTBEAT"]]
    """Specify the behavior that needs to be achieved for the subscription.

    Following values are accepted:

    - TRIP_SUBSCRIBE: Enable a trip subscription.
    - TRIP_UNSUBSCRIBE: Unsubscribe from a trip
    - HEARTBEAT: Enable heartbeat mechanism for a web-socket connection. The action
      message need to be sent at a frequency higher than every 5 mins to keep the
      connection alive. Alternatively, users can chose to respond to the ping frame
      sent by web socket server to keep the connection alive. Refer to
      [connection details](https://188--nbai-docs-stg.netlify.app/docs/tracking/api/live-tracking-api#connect-to-web-socket-server)
      for more details.
    """

    id: str
    """Specify a custom ID for the subscription.

    It can be used to reference a given subscription in the downstream applications
    / systems.
    """

    params: Params


class Params(TypedDict, total=False):
    id: Required[str]
    """Specify the ID of an active trip that needs to be subscribed.

    The ID of a trip is returned in the response when _Start A Trip_ request is
    acknowledged.

    This attribute is mandatory when action is set to either "TRIP_SUBSCRIBE" or
    "TRIP_UNSUBSCRIBE"
    """
