# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["MdmCreateDistanceMatrixParams"]


class MdmCreateDistanceMatrixParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    option: Required[Literal["flexible"]]
    """
    Use this option to switch to truck-specific routing or time based routing or if
    you want to choose between the fastest and shortest route types.
    """

    origins: Required[str]
    """origins are the starting point of your route.

    Ensure that origins are routable land locations. Multiple origins should be
    separated by a pipe symbol (|).

    **Format:** latitude_1,longitude_1|latitude_2,longitude_2|…
    """

    spliter: Literal["od_number_spliter", "straight_distance_spliter", "location_spliter"]
    """Specify a spliter to split the matrix by. It accepts 2 values:

    - od_number_spliter:

    - straight_distance_spliter:

    Please note it is an internal, debug field only.

    _debug field. choose specific spliter to split matrix._
    """

    area: Literal["singapore", "usa", "india"]
    """Provide the country that the coordinates belong to.

    _the input coordinates area._
    """

    avoid: Literal["toll", "ferry", "highway", "sharp_turn", "service_road", "bbox", "left_turn", "right_turn", "none"]
    """Setting this will ensure the route avoids the object(s) specified as input.

    Multiple values should be separated by a pipe (|). If none is provided along
    with other values, an error is returned as a valid route is not feasible.

    - **Note:**

      - This parameter is effective only when route_type=fastest.
      - When this parameter is not provided in the input, ferries are set to be
        avoided by default. When avoid input is provided, only the mentioned objects
        are avoided.
      - When using avoid=bbox users also need to specify the boundaries of the
        bounding box to be avoid. Multiple bounding boxes can be specified
        simultaneously. Please note that bounding box is a hard filter and if it
        blocks all possible routes between given locations, a 4xx error is returned.

        - **Format:** bbox: min_latitude,min_longtitude,max_latitude,max_longitude.
        - **Example:** avoid=bbox: 34.0635,-118.2547, 34.0679,-118.2478 | bbox:
          34.0521,-118.2342, 34.0478,-118.2437

      - When using avoid=sharp_turn, default range of permissible turn angles is
        \\[[120,240\\]].
    """

    cross_border: bool
    """
    Specify if crossing an international border is expected for operations near
    border areas. When set to false, the API will prohibit routes going back & forth
    between countries. Consequently, routes within the same country will be
    preferred if they are feasible for the given set of destination or waypoints .
    When set to true, the routes will be allowed to go back & forth between
    countries as needed.

    This feature is available in North America region only. Please get in touch with
    [support@nextbillion.ai](mailto:support@nextbillion.ai) to enquire/enable other
    areas.
    """

    departure_time: int
    """
    This is a number in UNIX epoch timestamp in seconds format that can be used to
    provide the departure time. The response will return the distance and duration
    of the route based on typical traffic for at the given start time.If no input is
    provided for this parameter then the traffic conditions at the time of making
    the request are considered.

    Please note that when route_type is set to shortest then the departure_time will
    be ineffective as the service will return the result for the shortest path
    possible irrespective of the traffic conditions.
    """

    destinations: str
    """destinations are the ending coordinates of your route.

    Ensure that destinations are routable land locations. Multiple destinations
    should be separated by a pipe symbol (|).

    In case destinations are not provided or if it is left empty, then the input
    value of origins will be copied to destinations to create the OD matrix pairs.

    **Format:** latitude_1,longitude_1|latitude_2,longitude_2|…
    """

    destinations_approach: Literal["unrestricted", "curb"]
    """Specify the side of the road from which to approach destinations points.

    Please note that the given approach will be applied to all the destinations.
    """

    hazmat_type: Literal["general", "circumstantial", "explosive", "harmful_to_water"]
    """
    Specify the type of hazardous material being carried and the service will avoid
    roads which are not suitable for the type of goods specified. Multiple values
    can be separated using a pipe operator | .

    Please note that this parameter is effective only when mode=truck.
    """

    mode: Literal["car", "truck"]
    """Set which driving mode the service should use to determine a route.

    For example, if you use car, the API will return a route that a car can take.
    Using truck will return a route a truck can use, taking into account appropriate
    truck routing restrictions.
    """

    origins_approach: Literal["unrestricted", "curb"]
    """Specify the side of the road from which to approach origins points.

    Please note that the given approach will be applied to all the points provided
    as origins.
    """

    route_type: Literal["fastest", "shortest"]
    """Set the route type that needs to be returned.

    Please note that route_type is effective only when option=flexible.
    """

    truck_axle_load: float
    """
    Specify the total load per axle (including the weight of trailers and shipped
    goods) of the truck, in tonnes. When used, the service will return routes which
    are legally allowed to carry the load specified per axle.

    Please note this parameter is effective only when mode=truck.
    """

    truck_size: str
    """
    This defines the dimensions of a truck in centimeters (cm) in the format of
    "height,width,length". This parameter is effective only when mode=truck and
    option=flexible. Maximum dimensions are as follows:

    Height = 1000 cm Width = 5000 cm Length = 5000 cm
    """

    truck_weight: int
    """
    This parameter defines the weight of the truck including trailers and shipped
    goods in kilograms (kg). This parameter is effective only when mode=truck and
    option=flexible.
    """
