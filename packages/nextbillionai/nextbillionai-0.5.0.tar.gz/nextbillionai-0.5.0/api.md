# Fleetify

## Routes

Types:

```python
from nextbillionai.types.fleetify import (
    RoutingResponse,
    RouteCreateResponse,
    RouteRedispatchResponse,
)
```

Methods:

- <code title="post /fleetify/routes">client.fleetify.routes.<a href="./src/nextbillionai/resources/fleetify/routes/routes.py">create</a>(\*\*<a href="src/nextbillionai/types/fleetify/route_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/route_create_response.py">RouteCreateResponse</a></code>
- <code title="post /fleetify/routes/{routeID}/redispatch">client.fleetify.routes.<a href="./src/nextbillionai/resources/fleetify/routes/routes.py">redispatch</a>(route_id, \*\*<a href="src/nextbillionai/types/fleetify/route_redispatch_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/route_redispatch_response.py">RouteRedispatchResponse</a></code>

### Steps

Types:

```python
from nextbillionai.types.fleetify.routes import (
    DocumentSubmission,
    RouteStepCompletionMode,
    RouteStepGeofenceConfig,
    RouteStepsRequest,
    RouteStepsResponse,
    StepCreateResponse,
    StepUpdateResponse,
    StepDeleteResponse,
)
```

Methods:

- <code title="post /fleetify/routes/{routeID}/steps">client.fleetify.routes.steps.<a href="./src/nextbillionai/resources/fleetify/routes/steps.py">create</a>(route_id, \*\*<a href="src/nextbillionai/types/fleetify/routes/step_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/routes/step_create_response.py">StepCreateResponse</a></code>
- <code title="put /fleetify/routes/{routeID}/steps/{stepID}">client.fleetify.routes.steps.<a href="./src/nextbillionai/resources/fleetify/routes/steps.py">update</a>(step_id, \*, route_id, \*\*<a href="src/nextbillionai/types/fleetify/routes/step_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/routes/step_update_response.py">StepUpdateResponse</a></code>
- <code title="delete /fleetify/routes/{routeID}/steps/{stepID}">client.fleetify.routes.steps.<a href="./src/nextbillionai/resources/fleetify/routes/steps.py">delete</a>(step_id, \*, route_id, \*\*<a href="src/nextbillionai/types/fleetify/routes/step_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/routes/step_delete_response.py">StepDeleteResponse</a></code>
- <code title="patch /fleetify/routes/{routeID}/steps/{stepID}">client.fleetify.routes.steps.<a href="./src/nextbillionai/resources/fleetify/routes/steps.py">complete</a>(step_id, \*, route_id, \*\*<a href="src/nextbillionai/types/fleetify/routes/step_complete_params.py">params</a>) -> None</code>

## DocumentTemplates

Types:

```python
from nextbillionai.types.fleetify import (
    DocumentTemplateContentRequest,
    DocumentTemplateContentResponse,
    DocumentTemplateCreateResponse,
    DocumentTemplateRetrieveResponse,
    DocumentTemplateUpdateResponse,
    DocumentTemplateListResponse,
    DocumentTemplateDeleteResponse,
)
```

Methods:

- <code title="post /fleetify/document_templates">client.fleetify.document_templates.<a href="./src/nextbillionai/resources/fleetify/document_templates.py">create</a>(\*\*<a href="src/nextbillionai/types/fleetify/document_template_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/document_template_create_response.py">DocumentTemplateCreateResponse</a></code>
- <code title="get /fleetify/document_templates/{id}">client.fleetify.document_templates.<a href="./src/nextbillionai/resources/fleetify/document_templates.py">retrieve</a>(id, \*\*<a href="src/nextbillionai/types/fleetify/document_template_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/document_template_retrieve_response.py">DocumentTemplateRetrieveResponse</a></code>
- <code title="put /fleetify/document_templates/{id}">client.fleetify.document_templates.<a href="./src/nextbillionai/resources/fleetify/document_templates.py">update</a>(id, \*\*<a href="src/nextbillionai/types/fleetify/document_template_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/document_template_update_response.py">DocumentTemplateUpdateResponse</a></code>
- <code title="get /fleetify/document_templates">client.fleetify.document_templates.<a href="./src/nextbillionai/resources/fleetify/document_templates.py">list</a>(\*\*<a href="src/nextbillionai/types/fleetify/document_template_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/document_template_list_response.py">DocumentTemplateListResponse</a></code>
- <code title="delete /fleetify/document_templates/{id}">client.fleetify.document_templates.<a href="./src/nextbillionai/resources/fleetify/document_templates.py">delete</a>(id, \*\*<a href="src/nextbillionai/types/fleetify/document_template_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/fleetify/document_template_delete_response.py">DocumentTemplateDeleteResponse</a></code>

# Skynet

Types:

```python
from nextbillionai.types import SkynetSubscribeResponse
```

Methods:

- <code title="post /skynet/subscribe">client.skynet.<a href="./src/nextbillionai/resources/skynet/skynet.py">subscribe</a>(\*\*<a href="src/nextbillionai/types/skynet_subscribe_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet_subscribe_response.py">SkynetSubscribeResponse</a></code>

## Asset

Types:

```python
from nextbillionai.types.skynet import (
    MetaData,
    SimpleResp,
    AssetCreateResponse,
    AssetRetrieveResponse,
    AssetListResponse,
)
```

Methods:

- <code title="post /skynet/asset">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">create</a>(\*\*<a href="src/nextbillionai/types/skynet/asset_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/asset_create_response.py">AssetCreateResponse</a></code>
- <code title="get /skynet/asset/{id}">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">retrieve</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/asset_retrieve_response.py">AssetRetrieveResponse</a></code>
- <code title="put /skynet/asset/{id}">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">update</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/asset/list">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">list</a>(\*\*<a href="src/nextbillionai/types/skynet/asset_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/asset_list_response.py">AssetListResponse</a></code>
- <code title="delete /skynet/asset/{id}">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">delete</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="post /skynet/asset/{id}/bind">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">bind</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset_bind_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="post /skynet/asset/{id}/track">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">track</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset_track_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="put /skynet/asset/{id}/attributes">client.skynet.asset.<a href="./src/nextbillionai/resources/skynet/asset/asset.py">update_attributes</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset_update_attributes_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>

### Event

Types:

```python
from nextbillionai.types.skynet.asset import EventListResponse
```

Methods:

- <code title="get /skynet/asset/{id}/event/list">client.skynet.asset.event.<a href="./src/nextbillionai/resources/skynet/asset/event.py">list</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset/event_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/asset/event_list_response.py">EventListResponse</a></code>

### Location

Types:

```python
from nextbillionai.types.skynet.asset import (
    TrackLocation,
    LocationListResponse,
    LocationGetLastResponse,
)
```

Methods:

- <code title="get /skynet/asset/{id}/location/list">client.skynet.asset.location.<a href="./src/nextbillionai/resources/skynet/asset/location.py">list</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset/location_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/asset/location_list_response.py">LocationListResponse</a></code>
- <code title="get /skynet/asset/{id}/location/last">client.skynet.asset.location.<a href="./src/nextbillionai/resources/skynet/asset/location.py">get_last</a>(id, \*\*<a href="src/nextbillionai/types/skynet/asset/location_get_last_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/asset/location_get_last_response.py">LocationGetLastResponse</a></code>

## Monitor

Types:

```python
from nextbillionai.types.skynet import (
    Metadata,
    Monitor,
    Pagination,
    MonitorCreateResponse,
    MonitorRetrieveResponse,
    MonitorListResponse,
)
```

Methods:

- <code title="post /skynet/monitor">client.skynet.monitor.<a href="./src/nextbillionai/resources/skynet/monitor.py">create</a>(\*\*<a href="src/nextbillionai/types/skynet/monitor_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/monitor_create_response.py">MonitorCreateResponse</a></code>
- <code title="get /skynet/monitor/{id}">client.skynet.monitor.<a href="./src/nextbillionai/resources/skynet/monitor.py">retrieve</a>(id, \*\*<a href="src/nextbillionai/types/skynet/monitor_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/monitor_retrieve_response.py">MonitorRetrieveResponse</a></code>
- <code title="put /skynet/monitor/{id}">client.skynet.monitor.<a href="./src/nextbillionai/resources/skynet/monitor.py">update</a>(id, \*\*<a href="src/nextbillionai/types/skynet/monitor_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/monitor/list">client.skynet.monitor.<a href="./src/nextbillionai/resources/skynet/monitor.py">list</a>(\*\*<a href="src/nextbillionai/types/skynet/monitor_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/monitor_list_response.py">MonitorListResponse</a></code>
- <code title="delete /skynet/monitor/{id}">client.skynet.monitor.<a href="./src/nextbillionai/resources/skynet/monitor.py">delete</a>(id, \*\*<a href="src/nextbillionai/types/skynet/monitor_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>

## Trip

Types:

```python
from nextbillionai.types.skynet import (
    AssetDetails,
    TripStop,
    TripRetrieveResponse,
    TripGetSummaryResponse,
    TripStartResponse,
)
```

Methods:

- <code title="get /skynet/trip/{id}">client.skynet.trip.<a href="./src/nextbillionai/resources/skynet/trip.py">retrieve</a>(id, \*\*<a href="src/nextbillionai/types/skynet/trip_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/trip_retrieve_response.py">TripRetrieveResponse</a></code>
- <code title="put /skynet/trip/{id}">client.skynet.trip.<a href="./src/nextbillionai/resources/skynet/trip.py">update</a>(id, \*\*<a href="src/nextbillionai/types/skynet/trip_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="delete /skynet/trip/{id}">client.skynet.trip.<a href="./src/nextbillionai/resources/skynet/trip.py">delete</a>(id, \*\*<a href="src/nextbillionai/types/skynet/trip_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="post /skynet/trip/end">client.skynet.trip.<a href="./src/nextbillionai/resources/skynet/trip.py">end</a>(\*\*<a href="src/nextbillionai/types/skynet/trip_end_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/trip/{id}/summary">client.skynet.trip.<a href="./src/nextbillionai/resources/skynet/trip.py">get_summary</a>(id, \*\*<a href="src/nextbillionai/types/skynet/trip_get_summary_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/trip_get_summary_response.py">TripGetSummaryResponse</a></code>
- <code title="post /skynet/trip/start">client.skynet.trip.<a href="./src/nextbillionai/resources/skynet/trip.py">start</a>(\*\*<a href="src/nextbillionai/types/skynet/trip_start_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/trip_start_response.py">TripStartResponse</a></code>

## NamespacedApikeys

Types:

```python
from nextbillionai.types.skynet import (
    NamespacedApikeyCreateResponse,
    NamespacedApikeyDeleteResponse,
)
```

Methods:

- <code title="post /skynet/namespaced-apikeys">client.skynet.namespaced_apikeys.<a href="./src/nextbillionai/resources/skynet/namespaced_apikeys.py">create</a>(\*\*<a href="src/nextbillionai/types/skynet/namespaced_apikey_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/namespaced_apikey_create_response.py">NamespacedApikeyCreateResponse</a></code>
- <code title="delete /skynet/namespaced-apikeys">client.skynet.namespaced_apikeys.<a href="./src/nextbillionai/resources/skynet/namespaced_apikeys.py">delete</a>(\*\*<a href="src/nextbillionai/types/skynet/namespaced_apikey_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/namespaced_apikey_delete_response.py">NamespacedApikeyDeleteResponse</a></code>

## Config

Types:

```python
from nextbillionai.types.skynet import ConfigRetrieveResponse, ConfigTestWebhookResponse
```

Methods:

- <code title="get /skynet/config">client.skynet.config.<a href="./src/nextbillionai/resources/skynet/config.py">retrieve</a>(\*\*<a href="src/nextbillionai/types/skynet/config_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/config_retrieve_response.py">ConfigRetrieveResponse</a></code>
- <code title="put /skynet/config">client.skynet.config.<a href="./src/nextbillionai/resources/skynet/config.py">update</a>(\*\*<a href="src/nextbillionai/types/skynet/config_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="post /skynet/config/testwebhook">client.skynet.config.<a href="./src/nextbillionai/resources/skynet/config.py">test_webhook</a>(\*\*<a href="src/nextbillionai/types/skynet/config_test_webhook_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/config_test_webhook_response.py">ConfigTestWebhookResponse</a></code>

## Search

Types:

```python
from nextbillionai.types.skynet import SearchResponse
```

Methods:

- <code title="get /skynet/search/around">client.skynet.search.<a href="./src/nextbillionai/resources/skynet/search/search.py">around</a>(\*\*<a href="src/nextbillionai/types/skynet/search_around_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/search_response.py">SearchResponse</a></code>
- <code title="get /skynet/search/bound">client.skynet.search.<a href="./src/nextbillionai/resources/skynet/search/search.py">bound</a>(\*\*<a href="src/nextbillionai/types/skynet/search_bound_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/search_response.py">SearchResponse</a></code>

### Polygon

Methods:

- <code title="post /skynet/search/polygon">client.skynet.search.polygon.<a href="./src/nextbillionai/resources/skynet/search/polygon.py">create</a>(\*\*<a href="src/nextbillionai/types/skynet/search/polygon_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/search_response.py">SearchResponse</a></code>
- <code title="get /skynet/search/polygon">client.skynet.search.polygon.<a href="./src/nextbillionai/resources/skynet/search/polygon.py">get</a>(\*\*<a href="src/nextbillionai/types/skynet/search/polygon_get_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/search_response.py">SearchResponse</a></code>

# Geocode

Types:

```python
from nextbillionai.types import (
    Access,
    Address,
    Categories,
    ContactObject,
    Contacts,
    MapView,
    Position,
    GeocodeRetrieveResponse,
    GeocodeBatchCreateResponse,
    GeocodeStructuredRetrieveResponse,
)
```

Methods:

- <code title="get /geocode">client.geocode.<a href="./src/nextbillionai/resources/geocode.py">retrieve</a>(\*\*<a href="src/nextbillionai/types/geocode_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/geocode_retrieve_response.py">GeocodeRetrieveResponse</a></code>
- <code title="post /geocode/batch">client.geocode.<a href="./src/nextbillionai/resources/geocode.py">batch_create</a>(\*\*<a href="src/nextbillionai/types/geocode_batch_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/geocode_batch_create_response.py">GeocodeBatchCreateResponse</a></code>
- <code title="get /geocode/structured">client.geocode.<a href="./src/nextbillionai/resources/geocode.py">structured_retrieve</a>(\*\*<a href="src/nextbillionai/types/geocode_structured_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/geocode_structured_retrieve_response.py">GeocodeStructuredRetrieveResponse</a></code>

# Optimization

Types:

```python
from nextbillionai.types import PostResponse, OptimizationComputeResponse
```

Methods:

- <code title="get /optimization/json">client.optimization.<a href="./src/nextbillionai/resources/optimization/optimization.py">compute</a>(\*\*<a href="src/nextbillionai/types/optimization_compute_params.py">params</a>) -> <a href="./src/nextbillionai/types/optimization_compute_response.py">OptimizationComputeResponse</a></code>
- <code title="post /optimization/re_optimization">client.optimization.<a href="./src/nextbillionai/resources/optimization/optimization.py">re_optimize</a>(\*\*<a href="src/nextbillionai/types/optimization_re_optimize_params.py">params</a>) -> <a href="./src/nextbillionai/types/post_response.py">PostResponse</a></code>

## DriverAssignment

Types:

```python
from nextbillionai.types.optimization import Location, Vehicle, DriverAssignmentAssignResponse
```

Methods:

- <code title="post /optimization/driver-assignment/v1">client.optimization.driver_assignment.<a href="./src/nextbillionai/resources/optimization/driver_assignment.py">assign</a>(\*\*<a href="src/nextbillionai/types/optimization/driver_assignment_assign_params.py">params</a>) -> <a href="./src/nextbillionai/types/optimization/driver_assignment_assign_response.py">DriverAssignmentAssignResponse</a></code>

## V2

Types:

```python
from nextbillionai.types.optimization import Job, Shipment, V2RetrieveResultResponse
```

Methods:

- <code title="get /optimization/v2/result">client.optimization.v2.<a href="./src/nextbillionai/resources/optimization/v2.py">retrieve_result</a>(\*\*<a href="src/nextbillionai/types/optimization/v2_retrieve_result_params.py">params</a>) -> <a href="./src/nextbillionai/types/optimization/v2_retrieve_result_response.py">V2RetrieveResultResponse</a></code>
- <code title="post /optimization/v2">client.optimization.v2.<a href="./src/nextbillionai/resources/optimization/v2.py">submit</a>(\*\*<a href="src/nextbillionai/types/optimization/v2_submit_params.py">params</a>) -> <a href="./src/nextbillionai/types/post_response.py">PostResponse</a></code>

# Geofence

Types:

```python
from nextbillionai.types import (
    Geofence,
    GeofenceEntityCreate,
    GeofenceCreateResponse,
    GeofenceRetrieveResponse,
    GeofenceListResponse,
    GeofenceContainsResponse,
)
```

Methods:

- <code title="post /geofence">client.geofence.<a href="./src/nextbillionai/resources/geofence/geofence.py">create</a>(\*\*<a href="src/nextbillionai/types/geofence_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence_create_response.py">GeofenceCreateResponse</a></code>
- <code title="get /geofence/{id}">client.geofence.<a href="./src/nextbillionai/resources/geofence/geofence.py">retrieve</a>(id, \*\*<a href="src/nextbillionai/types/geofence_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence_retrieve_response.py">GeofenceRetrieveResponse</a></code>
- <code title="put /geofence/{id}">client.geofence.<a href="./src/nextbillionai/resources/geofence/geofence.py">update</a>(id, \*\*<a href="src/nextbillionai/types/geofence_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /geofence/list">client.geofence.<a href="./src/nextbillionai/resources/geofence/geofence.py">list</a>(\*\*<a href="src/nextbillionai/types/geofence_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence_list_response.py">GeofenceListResponse</a></code>
- <code title="delete /geofence/{id}">client.geofence.<a href="./src/nextbillionai/resources/geofence/geofence.py">delete</a>(id, \*\*<a href="src/nextbillionai/types/geofence_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /geofence/contain">client.geofence.<a href="./src/nextbillionai/resources/geofence/geofence.py">contains</a>(\*\*<a href="src/nextbillionai/types/geofence_contains_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence_contains_response.py">GeofenceContainsResponse</a></code>

## Console

Types:

```python
from nextbillionai.types.geofence import (
    PolygonGeojson,
    ConsolePreviewResponse,
    ConsoleSearchResponse,
)
```

Methods:

- <code title="post /geofence/console/preview">client.geofence.console.<a href="./src/nextbillionai/resources/geofence/console.py">preview</a>(\*\*<a href="src/nextbillionai/types/geofence/console_preview_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence/console_preview_response.py">ConsolePreviewResponse</a></code>
- <code title="get /geofence/console/search">client.geofence.console.<a href="./src/nextbillionai/resources/geofence/console.py">search</a>(\*\*<a href="src/nextbillionai/types/geofence/console_search_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence/console_search_response.py">ConsoleSearchResponse</a></code>

## Batch

Types:

```python
from nextbillionai.types.geofence import BatchCreateResponse, BatchListResponse
```

Methods:

- <code title="post /geofence/batch">client.geofence.batch.<a href="./src/nextbillionai/resources/geofence/batch.py">create</a>(\*\*<a href="src/nextbillionai/types/geofence/batch_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /geofence/batch">client.geofence.batch.<a href="./src/nextbillionai/resources/geofence/batch.py">list</a>(\*\*<a href="src/nextbillionai/types/geofence/batch_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/geofence/batch_list_response.py">BatchListResponse</a></code>
- <code title="delete /geofence/batch">client.geofence.batch.<a href="./src/nextbillionai/resources/geofence/batch.py">delete</a>(\*\*<a href="src/nextbillionai/types/geofence/batch_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/skynet/simple_resp.py">SimpleResp</a></code>

# Discover

Types:

```python
from nextbillionai.types import DiscoverRetrieveResponse
```

Methods:

- <code title="get /discover">client.discover.<a href="./src/nextbillionai/resources/discover.py">retrieve</a>(\*\*<a href="src/nextbillionai/types/discover_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/discover_retrieve_response.py">DiscoverRetrieveResponse</a></code>

# Browse

Types:

```python
from nextbillionai.types import BrowseSearchResponse
```

Methods:

- <code title="get /browse">client.browse.<a href="./src/nextbillionai/resources/browse.py">search</a>(\*\*<a href="src/nextbillionai/types/browse_search_params.py">params</a>) -> <a href="./src/nextbillionai/types/browse_search_response.py">BrowseSearchResponse</a></code>

# Mdm

Types:

```python
from nextbillionai.types import MdmCreateDistanceMatrixResponse, MdmGetDistanceMatrixStatusResponse
```

Methods:

- <code title="post /mdm/create">client.mdm.<a href="./src/nextbillionai/resources/mdm.py">create_distance_matrix</a>(\*\*<a href="src/nextbillionai/types/mdm_create_distance_matrix_params.py">params</a>) -> <a href="./src/nextbillionai/types/mdm_create_distance_matrix_response.py">MdmCreateDistanceMatrixResponse</a></code>
- <code title="get /mdm/status">client.mdm.<a href="./src/nextbillionai/resources/mdm.py">get_distance_matrix_status</a>(\*\*<a href="src/nextbillionai/types/mdm_get_distance_matrix_status_params.py">params</a>) -> <a href="./src/nextbillionai/types/mdm_get_distance_matrix_status_response.py">MdmGetDistanceMatrixStatusResponse</a></code>

# Isochrone

Types:

```python
from nextbillionai.types import IsochroneComputeResponse
```

Methods:

- <code title="get /isochrone/json">client.isochrone.<a href="./src/nextbillionai/resources/isochrone.py">compute</a>(\*\*<a href="src/nextbillionai/types/isochrone_compute_params.py">params</a>) -> <a href="./src/nextbillionai/types/isochrone_compute_response.py">IsochroneComputeResponse</a></code>

# Restrictions

Types:

```python
from nextbillionai.types import (
    RichGroupRequest,
    RichGroupResponse,
    RestrictionListResponse,
    RestrictionDeleteResponse,
    RestrictionListByBboxResponse,
)
```

Methods:

- <code title="post /restrictions/{restriction_type}">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">create</a>(restriction_type, \*\*<a href="src/nextbillionai/types/restriction_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/rich_group_response.py">RichGroupResponse</a></code>
- <code title="get /restrictions/{id}">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">retrieve</a>(id, \*\*<a href="src/nextbillionai/types/restriction_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/rich_group_response.py">RichGroupResponse</a></code>
- <code title="patch /restrictions/{id}">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">update</a>(id, \*\*<a href="src/nextbillionai/types/restriction_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/rich_group_response.py">RichGroupResponse</a></code>
- <code title="get /restrictions/list">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">list</a>(\*\*<a href="src/nextbillionai/types/restriction_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/restriction_list_response.py">RestrictionListResponse</a></code>
- <code title="delete /restrictions/{id}">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">delete</a>(id, \*\*<a href="src/nextbillionai/types/restriction_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/restriction_delete_response.py">RestrictionDeleteResponse</a></code>
- <code title="get /restrictions">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">list_by_bbox</a>(\*\*<a href="src/nextbillionai/types/restriction_list_by_bbox_params.py">params</a>) -> <a href="./src/nextbillionai/types/restriction_list_by_bbox_response.py">RestrictionListByBboxResponse</a></code>
- <code title="put /restrictions/{id}/state">client.restrictions.<a href="./src/nextbillionai/resources/restrictions.py">set_state</a>(id, \*\*<a href="src/nextbillionai/types/restriction_set_state_params.py">params</a>) -> <a href="./src/nextbillionai/types/rich_group_response.py">RichGroupResponse</a></code>

# RestrictionsItems

Types:

```python
from nextbillionai.types import RestrictionsItemListResponse
```

Methods:

- <code title="get /restrictions_items">client.restrictions_items.<a href="./src/nextbillionai/resources/restrictions_items.py">list</a>(\*\*<a href="src/nextbillionai/types/restrictions_item_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/restrictions_item_list_response.py">RestrictionsItemListResponse</a></code>

# DistanceMatrix

## Json

Types:

```python
from nextbillionai.types.distance_matrix import JsonRetrieveResponse
```

Methods:

- <code title="post /distancematrix/json">client.distance_matrix.json.<a href="./src/nextbillionai/resources/distance_matrix/json.py">create</a>() -> None</code>
- <code title="get /distancematrix/json">client.distance_matrix.json.<a href="./src/nextbillionai/resources/distance_matrix/json.py">retrieve</a>(\*\*<a href="src/nextbillionai/types/distance_matrix/json_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/distance_matrix/json_retrieve_response.py">JsonRetrieveResponse</a></code>

# Autocomplete

Types:

```python
from nextbillionai.types import AutocompleteSuggestResponse
```

Methods:

- <code title="get /autocomplete">client.autocomplete.<a href="./src/nextbillionai/resources/autocomplete.py">suggest</a>(\*\*<a href="src/nextbillionai/types/autocomplete_suggest_params.py">params</a>) -> <a href="./src/nextbillionai/types/autocomplete_suggest_response.py">AutocompleteSuggestResponse</a></code>

# Navigation

Types:

```python
from nextbillionai.types import NavigationRetrieveRouteResponse
```

Methods:

- <code title="get /navigation/json">client.navigation.<a href="./src/nextbillionai/resources/navigation.py">retrieve_route</a>(\*\*<a href="src/nextbillionai/types/navigation_retrieve_route_params.py">params</a>) -> <a href="./src/nextbillionai/types/navigation_retrieve_route_response.py">NavigationRetrieveRouteResponse</a></code>

# Map

Methods:

- <code title="post /map/segments">client.map.<a href="./src/nextbillionai/resources/map.py">create_segment</a>() -> None</code>

# Autosuggest

Types:

```python
from nextbillionai.types import AutosuggestSuggestResponse
```

Methods:

- <code title="get /autosuggest">client.autosuggest.<a href="./src/nextbillionai/resources/autosuggest.py">suggest</a>(\*\*<a href="src/nextbillionai/types/autosuggest_suggest_params.py">params</a>) -> <a href="./src/nextbillionai/types/autosuggest_suggest_response.py">AutosuggestSuggestResponse</a></code>

# Directions

Types:

```python
from nextbillionai.types import DirectionComputeRouteResponse
```

Methods:

- <code title="post /directions/json">client.directions.<a href="./src/nextbillionai/resources/directions.py">compute_route</a>(\*\*<a href="src/nextbillionai/types/direction_compute_route_params.py">params</a>) -> <a href="./src/nextbillionai/types/direction_compute_route_response.py">DirectionComputeRouteResponse</a></code>

# Batch

Types:

```python
from nextbillionai.types import BatchCreateResponse, BatchRetrieveResponse
```

Methods:

- <code title="post /batch">client.batch.<a href="./src/nextbillionai/resources/batch.py">create</a>(\*\*<a href="src/nextbillionai/types/batch_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /batch">client.batch.<a href="./src/nextbillionai/resources/batch.py">retrieve</a>(\*\*<a href="src/nextbillionai/types/batch_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/batch_retrieve_response.py">BatchRetrieveResponse</a></code>

# Multigeocode

Types:

```python
from nextbillionai.types import MultigeocodeSearchResponse
```

Methods:

- <code title="post /multigeocode/search">client.multigeocode.<a href="./src/nextbillionai/resources/multigeocode/multigeocode.py">search</a>(\*\*<a href="src/nextbillionai/types/multigeocode_search_params.py">params</a>) -> <a href="./src/nextbillionai/types/multigeocode_search_response.py">MultigeocodeSearchResponse</a></code>

## Place

Types:

```python
from nextbillionai.types.multigeocode import (
    PlaceItem,
    PlaceCreateResponse,
    PlaceRetrieveResponse,
    PlaceUpdateResponse,
    PlaceDeleteResponse,
)
```

Methods:

- <code title="post /multigeocode/place">client.multigeocode.place.<a href="./src/nextbillionai/resources/multigeocode/place.py">create</a>(\*\*<a href="src/nextbillionai/types/multigeocode/place_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/multigeocode/place_create_response.py">PlaceCreateResponse</a></code>
- <code title="get /multigeocode/place/{docId}">client.multigeocode.place.<a href="./src/nextbillionai/resources/multigeocode/place.py">retrieve</a>(doc_id, \*\*<a href="src/nextbillionai/types/multigeocode/place_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/multigeocode/place_retrieve_response.py">PlaceRetrieveResponse</a></code>
- <code title="put /multigeocode/place/{docId}">client.multigeocode.place.<a href="./src/nextbillionai/resources/multigeocode/place.py">update</a>(doc_id, \*\*<a href="src/nextbillionai/types/multigeocode/place_update_params.py">params</a>) -> <a href="./src/nextbillionai/types/multigeocode/place_update_response.py">PlaceUpdateResponse</a></code>
- <code title="delete /multigeocode/place/{docId}">client.multigeocode.place.<a href="./src/nextbillionai/resources/multigeocode/place.py">delete</a>(doc_id, \*\*<a href="src/nextbillionai/types/multigeocode/place_delete_params.py">params</a>) -> <a href="./src/nextbillionai/types/multigeocode/place_delete_response.py">PlaceDeleteResponse</a></code>

# Revgeocode

Types:

```python
from nextbillionai.types import RevgeocodeRetrieveResponse
```

Methods:

- <code title="get /revgeocode">client.revgeocode.<a href="./src/nextbillionai/resources/revgeocode.py">retrieve</a>(\*\*<a href="src/nextbillionai/types/revgeocode_retrieve_params.py">params</a>) -> <a href="./src/nextbillionai/types/revgeocode_retrieve_response.py">RevgeocodeRetrieveResponse</a></code>

# RouteReport

Types:

```python
from nextbillionai.types import RouteReportCreateResponse
```

Methods:

- <code title="post /route_report">client.route_report.<a href="./src/nextbillionai/resources/route_report.py">create</a>(\*\*<a href="src/nextbillionai/types/route_report_create_params.py">params</a>) -> <a href="./src/nextbillionai/types/route_report_create_response.py">RouteReportCreateResponse</a></code>

# SnapToRoads

Types:

```python
from nextbillionai.types import SnapToRoadSnapResponse
```

Methods:

- <code title="get /snapToRoads/json">client.snap_to_roads.<a href="./src/nextbillionai/resources/snap_to_roads.py">snap</a>(\*\*<a href="src/nextbillionai/types/snap_to_road_snap_params.py">params</a>) -> <a href="./src/nextbillionai/types/snap_to_road_snap_response.py">SnapToRoadSnapResponse</a></code>

# Postalcode

Types:

```python
from nextbillionai.types import PostalcodeRetrieveCoordinatesResponse
```

Methods:

- <code title="post /postalcode">client.postalcode.<a href="./src/nextbillionai/resources/postalcode.py">retrieve_coordinates</a>(\*\*<a href="src/nextbillionai/types/postalcode_retrieve_coordinates_params.py">params</a>) -> <a href="./src/nextbillionai/types/postalcode_retrieve_coordinates_response.py">PostalcodeRetrieveCoordinatesResponse</a></code>

# Lookup

Types:

```python
from nextbillionai.types import LookupByIDResponse
```

Methods:

- <code title="get /lookup">client.lookup.<a href="./src/nextbillionai/resources/lookup.py">by_id</a>(\*\*<a href="src/nextbillionai/types/lookup_by_id_params.py">params</a>) -> <a href="./src/nextbillionai/types/lookup_by_id_response.py">LookupByIDResponse</a></code>

# Areas

Types:

```python
from nextbillionai.types import AreaListResponse
```

Methods:

- <code title="get /areas">client.areas.<a href="./src/nextbillionai/resources/areas.py">list</a>(\*\*<a href="src/nextbillionai/types/area_list_params.py">params</a>) -> <a href="./src/nextbillionai/types/area_list_response.py">AreaListResponse</a></code>
