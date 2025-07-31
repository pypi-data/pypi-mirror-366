# swagger_client.WorkOrdersApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_work_order**](WorkOrdersApi.md#create_work_order) | **POST** /work_orders | Create a WorkOrder
[**delete_work_order**](WorkOrdersApi.md#delete_work_order) | **DELETE** /work_orders/{uuid} | Delete a WorkOrder
[**delete_work_order_param**](WorkOrdersApi.md#delete_work_order_param) | **DELETE** /work_orders/{uuid}/params/{key} | Delete a single machine parameter
[**delete_work_orders**](WorkOrdersApi.md#delete_work_orders) | **DELETE** /work_orders | Delete WorkOrders that reference removed machines.
[**get_work_order**](WorkOrdersApi.md#get_work_order) | **GET** /work_orders/{uuid} | Get a WorkOrder
[**get_work_order_action**](WorkOrdersApi.md#get_work_order_action) | **GET** /work_orders/{uuid}/plugin_actions/{cmd} | List specific action for a work_order WorkOrder
[**get_work_order_actions**](WorkOrdersApi.md#get_work_order_actions) | **GET** /work_orders/{uuid}/plugin_actions | List work_order plugin_actions WorkOrder
[**get_work_order_param**](WorkOrdersApi.md#get_work_order_param) | **GET** /work_orders/{uuid}/params/{key} | Get a single machine parameter
[**get_work_order_pub_key**](WorkOrdersApi.md#get_work_order_pub_key) | **GET** /work_orders/{uuid}/pubkey | Get the public key for secure params on a machine
[**get_work_orders_params**](WorkOrdersApi.md#get_work_orders_params) | **GET** /work_orders/{uuid}/params | List work_order params WorkOrders
[**head_work_order**](WorkOrdersApi.md#head_work_order) | **HEAD** /work_orders/{uuid} | See if a WorkOrder exists
[**list_stats_work_orders**](WorkOrdersApi.md#list_stats_work_orders) | **HEAD** /work_orders | Stats of the List WorkOrders filtered by some parameters.
[**list_work_orders**](WorkOrdersApi.md#list_work_orders) | **GET** /work_orders | Lists WorkOrders filtered by some parameters.
[**patch_work_order**](WorkOrdersApi.md#patch_work_order) | **PATCH** /work_orders/{uuid} | Patch a WorkOrder
[**patch_work_order_params**](WorkOrdersApi.md#patch_work_order_params) | **PATCH** /work_orders/{uuid}/params | 
[**post_work_order_action**](WorkOrdersApi.md#post_work_order_action) | **POST** /work_orders/{uuid}/plugin_actions/{cmd} | Call an action on the node.
[**post_work_order_param**](WorkOrdersApi.md#post_work_order_param) | **POST** /work_orders/{uuid}/params/{key} | 
[**post_work_order_params**](WorkOrdersApi.md#post_work_order_params) | **POST** /work_orders/{uuid}/params | 
[**put_work_order**](WorkOrdersApi.md#put_work_order) | **PUT** /work_orders/{uuid} | Put a WorkOrder


# **create_work_order**
> WorkOrder create_work_order(body)

Create a WorkOrder

The provided WorkOrder object will be injected into the system.  The UUID field is optional and will be filled if not provided.  One of the Machine field or the Filter field must be provided.  The Machine is the UUID of a machine to run the WorkOrder.  The Filter is a List filter that should be used to find a Machine to run this WorkOrder.  One of the Blueprint field or the Tasks field must be provided to define what should be run by the Machine/Filter.  State should not be provided or set to \"created\".  It will be set to \"created\".

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
body = drppy_client.WorkOrder()  # WorkOrder | 

try:
    # Create a WorkOrder
    api_response = api_instance.create_work_order(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->create_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkOrder**](WorkOrder.md)|  | 

### Return type

[**WorkOrder**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_work_order**
> WorkOrder delete_work_order(uuid)

Delete a WorkOrder

Delete a WorkOrder specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Delete a WorkOrder
    api_response = api_instance.delete_work_order(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->delete_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**WorkOrder**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_work_order_param**
> delete_work_order_param()

Delete a single machine parameter

Delete a single parameter {key} for a WorkOrder specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))

try:
    # Delete a single machine parameter
    api_instance.delete_work_order_param()
except ApiException as e:
    print("Exception when calling WorkOrdersApi->delete_work_order_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_work_orders**
> delete_work_orders()

Delete WorkOrders that reference removed machines.

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))

try:
    # Delete WorkOrders that reference removed machines.
    api_instance.delete_work_orders()
except ApiException as e:
    print("Exception when calling WorkOrdersApi->delete_work_orders: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_order**
> WorkOrder get_work_order(uuid)

Get a WorkOrder

Get the WorkOrder specified by {uuid} or return NotFound.

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get a WorkOrder
    api_response = api_instance.get_work_order(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->get_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**WorkOrder**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_order_action**
> AvailableAction get_work_order_action(uuid, cmd, plugin=plugin)

List specific action for a work_order WorkOrder

List specific {cmd} action for a WorkOrder specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a work_order WorkOrder
    api_response = api_instance.get_work_order_action(uuid, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->get_work_order_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **cmd** | **str**|  | 
 **plugin** | **str**|  | [optional] 

### Return type

[**AvailableAction**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_order_actions**
> list[AvailableAction] get_work_order_actions(uuid)

List work_order plugin_actions WorkOrder

List WorkOrder plugin_actions for a WorkOrder specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # List work_order plugin_actions WorkOrder
    api_response = api_instance.get_work_order_actions(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->get_work_order_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_order_param**
> get_work_order_param()

Get a single machine parameter

Get a single parameter {key} for a WorkOrder specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))

try:
    # Get a single machine parameter
    api_instance.get_work_order_param()
except ApiException as e:
    print("Exception when calling WorkOrdersApi->get_work_order_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_order_pub_key**
> get_work_order_pub_key(uuid)

Get the public key for secure params on a machine

Get the public key for a WorkOrder specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get the public key for secure params on a machine
    api_instance.get_work_order_pub_key(uuid)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->get_work_order_pub_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_orders_params**
> dict(str, object) get_work_orders_params()

List work_order params WorkOrders

List WorkOrder parms for a WorkOrder specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))

try:
    # List work_order params WorkOrders
    api_response = api_instance.get_work_orders_params()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->get_work_orders_params: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_work_order**
> head_work_order(uuid)

See if a WorkOrder exists

Return 200 if the WorkOrder specifiec by {uuid} exists, or return NotFound.

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # See if a WorkOrder exists
    api_instance.head_work_order(uuid)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->head_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_work_orders**
> list_stats_work_orders(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, archived=archived, available=available, blueprint=blueprint, bundle=bundle, context=context, create_time=create_time, current_job=current_job, current_task=current_task, end_time=end_time, endpoint=endpoint, errors=errors, key=key, machine=machine, meta=meta, profiles=profiles, read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable, stage=stage, start_time=start_time, state=state, status=status, task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid)

Stats of the List WorkOrders filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Uuid = string Stage = string Task = string State = string Machine = string Archived = boolean StartTime = datetime EndTime = datetime Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Uuid=fred - returns items named fred Uuid=Lt(fred) - returns items that alphabetically less than fred. Uuid=Lt(fred)&Archived=true - returns items with Uuid less than fred and Archived is true

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
offset = 789  # int |  (optional)
limit = 789  # int |  (optional)
aggregate = 'aggregate_example'  # str |  (optional)
exclude_self = 'exclude_self_example'  # str |  (optional)
filter = 'filter_example'  # str |  (optional)
raw = 'raw_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
group_by = 'group_by_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)
range_only = 'range_only_example'  # str |  (optional)
reverse = 'reverse_example'  # str |  (optional)
slim = 'slim_example'  # str |  (optional)
sort = 'sort_example'  # str |  (optional)
archived = 'archived_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
blueprint = 'blueprint_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
create_time = 'create_time_example'  # str |  (optional)
current_job = 'current_job_example'  # str |  (optional)
current_task = 'current_task_example'  # str |  (optional)
end_time = 'end_time_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
machine = 'machine_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
retry_task_attempt = 'retry_task_attempt_example'  # str |  (optional)
runnable = 'runnable_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
start_time = 'start_time_example'  # str |  (optional)
state = 'state_example'  # str |  (optional)
status = 'status_example'  # str |  (optional)
task_error_stacks = 'task_error_stacks_example'  # str |  (optional)
tasks = 'tasks_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List WorkOrders filtered by some parameters.
    api_instance.list_stats_work_orders(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                        filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                        range_only=range_only, reverse=reverse, slim=slim, sort=sort, archived=archived,
                                        available=available, blueprint=blueprint, bundle=bundle, context=context,
                                        create_time=create_time, current_job=current_job, current_task=current_task,
                                        end_time=end_time, endpoint=endpoint, errors=errors, key=key, machine=machine,
                                        meta=meta, profiles=profiles, read_only=read_only,
                                        retry_task_attempt=retry_task_attempt, runnable=runnable, stage=stage,
                                        start_time=start_time, state=state, status=status,
                                        task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->list_stats_work_orders: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**|  | [optional] 
 **limit** | **int**|  | [optional] 
 **aggregate** | **str**|  | [optional] 
 **exclude_self** | **str**|  | [optional] 
 **filter** | **str**|  | [optional] 
 **raw** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **group_by** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 
 **range_only** | **str**|  | [optional] 
 **reverse** | **str**|  | [optional] 
 **slim** | **str**|  | [optional] 
 **sort** | **str**|  | [optional] 
 **archived** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **blueprint** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **create_time** | **str**|  | [optional] 
 **current_job** | **str**|  | [optional] 
 **current_task** | **str**|  | [optional] 
 **end_time** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **machine** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **retry_task_attempt** | **str**|  | [optional] 
 **runnable** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **start_time** | **str**|  | [optional] 
 **state** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **task_error_stacks** | **str**|  | [optional] 
 **tasks** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_orders**
> list[WorkOrder] list_work_orders(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, archived=archived, available=available, blueprint=blueprint, bundle=bundle, context=context, create_time=create_time, current_job=current_job, current_task=current_task, end_time=end_time, endpoint=endpoint, errors=errors, key=key, machine=machine, meta=meta, profiles=profiles, read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable, stage=stage, start_time=start_time, state=state, status=status, task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid)

Lists WorkOrders filtered by some parameters.

This will show all WorkOrders by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by   Functional Indexs: Uuid = string State = string Machine = string Archived = boolean StartTime = datetime EndTime = datetime Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Uuid=fred - returns items named fred Uuid=Lt(fred) - returns items that alphabetically less than fred. Uuid=Lt(fred)&Archived=true - returns items with Uuid less than fred and Archived is true

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
offset = 789  # int |  (optional)
limit = 789  # int |  (optional)
aggregate = 'aggregate_example'  # str |  (optional)
exclude_self = 'exclude_self_example'  # str |  (optional)
filter = 'filter_example'  # str |  (optional)
raw = 'raw_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
group_by = 'group_by_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)
range_only = 'range_only_example'  # str |  (optional)
reverse = 'reverse_example'  # str |  (optional)
slim = 'slim_example'  # str |  (optional)
sort = 'sort_example'  # str |  (optional)
archived = 'archived_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
blueprint = 'blueprint_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
create_time = 'create_time_example'  # str |  (optional)
current_job = 'current_job_example'  # str |  (optional)
current_task = 'current_task_example'  # str |  (optional)
end_time = 'end_time_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
machine = 'machine_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
retry_task_attempt = 'retry_task_attempt_example'  # str |  (optional)
runnable = 'runnable_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
start_time = 'start_time_example'  # str |  (optional)
state = 'state_example'  # str |  (optional)
status = 'status_example'  # str |  (optional)
task_error_stacks = 'task_error_stacks_example'  # str |  (optional)
tasks = 'tasks_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists WorkOrders filtered by some parameters.
    api_response = api_instance.list_work_orders(offset=offset, limit=limit, aggregate=aggregate,
                                                 exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                                 group_by=group_by, params=params, range_only=range_only,
                                                 reverse=reverse, slim=slim, sort=sort, archived=archived,
                                                 available=available, blueprint=blueprint, bundle=bundle,
                                                 context=context, create_time=create_time, current_job=current_job,
                                                 current_task=current_task, end_time=end_time, endpoint=endpoint,
                                                 errors=errors, key=key, machine=machine, meta=meta, profiles=profiles,
                                                 read_only=read_only, retry_task_attempt=retry_task_attempt,
                                                 runnable=runnable, stage=stage, start_time=start_time, state=state,
                                                 status=status, task_error_stacks=task_error_stacks, tasks=tasks,
                                                 uuid=uuid, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->list_work_orders: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**|  | [optional] 
 **limit** | **int**|  | [optional] 
 **aggregate** | **str**|  | [optional] 
 **exclude_self** | **str**|  | [optional] 
 **filter** | **str**|  | [optional] 
 **raw** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **group_by** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 
 **range_only** | **str**|  | [optional] 
 **reverse** | **str**|  | [optional] 
 **slim** | **str**|  | [optional] 
 **sort** | **str**|  | [optional] 
 **archived** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **blueprint** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **create_time** | **str**|  | [optional] 
 **current_job** | **str**|  | [optional] 
 **current_task** | **str**|  | [optional] 
 **end_time** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **machine** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **retry_task_attempt** | **str**|  | [optional] 
 **runnable** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **start_time** | **str**|  | [optional] 
 **state** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **task_error_stacks** | **str**|  | [optional] 
 **tasks** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[WorkOrder]**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_work_order**
> WorkOrder patch_work_order(body, uuid)

Patch a WorkOrder

Update a WorkOrder specified by {uuid} using a RFC6902 Patch structure

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 

try:
    # Patch a WorkOrder
    api_response = api_instance.patch_work_order(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->patch_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

[**WorkOrder**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_work_order_params**
> dict(str, object) patch_work_order_params()



Update params for WorkOrder {uuid} with the passed-in patch

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))

try:
    api_response = api_instance.patch_work_order_params()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->patch_work_order_params: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_work_order_action**
> object post_work_order_action(uuid, cmd, body, plugin=plugin)

Call an action on the node.

Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_work_order_action(uuid, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->post_work_order_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **cmd** | **str**|  | 
 **body** | **object**|  | 
 **plugin** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_work_order_param**
> post_work_order_param()



Set as single Parameter {key} for a machine specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))

try:
    api_instance.post_work_order_param()
except ApiException as e:
    print("Exception when calling WorkOrdersApi->post_work_order_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_work_order_params**
> dict(str, object) post_work_order_params(uuid, body)



Sets parameters for a machine specified by {uuid}

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
body = NULL  # object | 

try:
    api_response = api_instance.post_work_order_params(uuid, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->post_work_order_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **body** | **object**|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_work_order**
> WorkOrder put_work_order(body, uuid)

Put a WorkOrder

Update a WorkOrder specified by {uuid} using a JSON WorkOrder

### Example

```python
from __future__ import print_function
import time
import drppy_client
from drppy_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Bearer
configuration = drppy_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: basicAuth
configuration = drppy_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = drppy_client.WorkOrdersApi(drppy_client.ApiClient(configuration))
body = drppy_client.WorkOrder()  # WorkOrder | 
uuid = 'uuid_example'  # str | 

try:
    # Put a WorkOrder
    api_response = api_instance.put_work_order(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkOrdersApi->put_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkOrder**](WorkOrder.md)|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

[**WorkOrder**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

