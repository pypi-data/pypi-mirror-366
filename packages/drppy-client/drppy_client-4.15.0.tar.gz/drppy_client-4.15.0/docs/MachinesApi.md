# swagger_client.MachinesApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cleanup_machine**](MachinesApi.md#cleanup_machine) | **DELETE** /machines/{uuid}/cleanup | Cleanup a Machine
[**create_machine**](MachinesApi.md#create_machine) | **POST** /machines | Create a Machine
[**delete_machine**](MachinesApi.md#delete_machine) | **DELETE** /machines/{uuid} | Delete a Machine
[**delete_machine_param**](MachinesApi.md#delete_machine_param) | **DELETE** /machines/{uuid}/params/{key} | Delete a single machine parameter
[**get_machine**](MachinesApi.md#get_machine) | **GET** /machines/{uuid} | Get a Machine
[**get_machine_action**](MachinesApi.md#get_machine_action) | **GET** /machines/{uuid}/actions/{cmd} | List specific action for a machine Machine
[**get_machine_actions**](MachinesApi.md#get_machine_actions) | **GET** /machines/{uuid}/actions | List machine actions Machine
[**get_machine_param**](MachinesApi.md#get_machine_param) | **GET** /machines/{uuid}/params/{key} | Get a single machine parameter
[**get_machine_params**](MachinesApi.md#get_machine_params) | **GET** /machines/{uuid}/params | List machine params Machine
[**get_machine_pub_key**](MachinesApi.md#get_machine_pub_key) | **GET** /machines/{uuid}/pubkey | Get the public key for secure params on a machine
[**get_machine_token**](MachinesApi.md#get_machine_token) | **GET** /machines/{uuid}/token | Get a Machine Token
[**head_machine**](MachinesApi.md#head_machine) | **HEAD** /machines/{uuid} | See if a Machine exists
[**list_machines**](MachinesApi.md#list_machines) | **GET** /machines | Lists Machines filtered by some parameters.
[**list_stats_machines**](MachinesApi.md#list_stats_machines) | **HEAD** /machines | Stats of the List Machines filtered by some parameters.
[**patch_machine**](MachinesApi.md#patch_machine) | **PATCH** /machines/{uuid} | Patch a Machine
[**patch_machine_params**](MachinesApi.md#patch_machine_params) | **PATCH** /machines/{uuid}/params | 
[**pick_machine_work_order**](MachinesApi.md#pick_machine_work_order) | **POST** /machines/{id}/pick/{key} | Pick a workorder for this agent.  This can return the current work order.
[**post_machine_action**](MachinesApi.md#post_machine_action) | **POST** /machines/{uuid}/actions/{cmd} | Call an action on the node.
[**post_machine_param**](MachinesApi.md#post_machine_param) | **POST** /machines/{uuid}/params/{key} | 
[**post_machine_params**](MachinesApi.md#post_machine_params) | **POST** /machines/{uuid}/params | 
[**put_machine**](MachinesApi.md#put_machine) | **PUT** /machines/{uuid} | Put a Machine
[**start_machine**](MachinesApi.md#start_machine) | **PATCH** /machines/{uuid}/start | Start a Machine


# **cleanup_machine**
> Machine cleanup_machine(uuid)

Cleanup a Machine

Cleanup Machine specified by {uuid}.  If 202 is returned, the on-delete-workflow has been started.

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Cleanup a Machine
    api_response = api_instance.cleanup_machine(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->cleanup_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_machine**
> Machine create_machine(body, force=force)

Create a Machine

Create a Machine from the provided object

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Machine()  # Machine | 
force = 'force_example'  # str |  (optional)

try:
    # Create a Machine
    api_response = api_instance.create_machine(body, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->create_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Machine**](Machine.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_machine**
> Machine delete_machine(uuid)

Delete a Machine

Delete a Machine specified by {uuid}.  If 202 is returned, the on-delete-workflow has been started.

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Delete a Machine
    api_response = api_instance.delete_machine(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->delete_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_machine_param**
> object delete_machine_param(uuid, key)

Delete a single machine parameter

Delete a single parameter {key} for a Machine specified by {uuid}

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 

try:
    # Delete a single machine parameter
    api_response = api_instance.delete_machine_param(uuid, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->delete_machine_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **key** | **str**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_machine**
> Machine get_machine(uuid, aggregate=aggregate, decode=decode, params=params)

Get a Machine

Get the Machine specified by {uuid} or return NotFound.

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get a Machine
    api_response = api_instance.get_machine(uuid, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **aggregate** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_machine_action**
> AvailableAction get_machine_action(uuid, cmd, plugin=plugin)

List specific action for a machine Machine

List specific {cmd} action for a Machine specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a machine Machine
    api_response = api_instance.get_machine_action(uuid, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine_action: %s\n" % e)
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

# **get_machine_actions**
> list[AvailableAction] get_machine_actions(uuid, plugin=plugin)

List machine actions Machine

List Machine actions for a Machine specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List machine actions Machine
    api_response = api_instance.get_machine_actions(uuid, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **plugin** | **str**|  | [optional] 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_machine_param**
> object get_machine_param(uuid, key, aggregate=aggregate, decode=decode)

Get a single machine parameter

Get a single parameter {key} for a Machine specified by {uuid}

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)

try:
    # Get a single machine parameter
    api_response = api_instance.get_machine_param(uuid, key, aggregate=aggregate, decode=decode)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **key** | **str**|  | 
 **aggregate** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_machine_params**
> dict(str, object) get_machine_params(uuid, aggregate=aggregate, decode=decode, params=params)

List machine params Machine

List Machine parms for a Machine specified by {uuid}

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # List machine params Machine
    api_response = api_instance.get_machine_params(uuid, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **aggregate** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_machine_pub_key**
> get_machine_pub_key(uuid)

Get the public key for secure params on a machine

Get the public key for a Machine specified by {uuid}

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get the public key for secure params on a machine
    api_instance.get_machine_pub_key(uuid)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine_pub_key: %s\n" % e)
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

# **get_machine_token**
> UserToken get_machine_token(uuid, ttl=ttl)

Get a Machine Token

Get a Machine Token specified by {uuid} or return NotFound.

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
ttl = 789  # int |  (optional)

try:
    # Get a Machine Token
    api_response = api_instance.get_machine_token(uuid, ttl=ttl)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->get_machine_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **ttl** | **int**|  | [optional] 

### Return type

[**UserToken**](UserToken.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_machine**
> head_machine(uuid)

See if a Machine exists

Return 200 if the Machine specifiec by {uuid} exists, or return NotFound.

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # See if a Machine exists
    api_instance.head_machine(uuid)
except ApiException as e:
    print("Exception when calling MachinesApi->head_machine: %s\n" % e)
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

# **list_machines**
> list[Machine] list_machines(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, address=address, arch=arch, available=available, boot_env=boot_env, bundle=bundle, context=context, current_job=current_job, current_task=current_task, description=description, endpoint=endpoint, errors=errors, hardware_addr=hardware_addr, hardware_addrs=hardware_addrs, key=key, locked=locked, meta=meta, name=name, os=os, partial=partial, pending_work_orders=pending_work_orders, pool=pool, pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles, read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable, running_work_orders=running_work_orders, stage=stage, task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid, work_order_mode=work_order_mode, workflow=workflow, workflow_complete=workflow_complete)

Lists Machines filtered by some parameters.

This will show all Machines by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Uuid = UUID string Name = string BootEnv = string Address = IP Address Runnable = true/false Available = boolean Valid = boolean ReadOnly = boolean  exclude-self = boolean = true means to not include self-runners  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
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
address = 'address_example'  # str |  (optional)
arch = 'arch_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
current_job = 'current_job_example'  # str |  (optional)
current_task = 'current_task_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
hardware_addr = 'hardware_addr_example'  # str |  (optional)
hardware_addrs = 'hardware_addrs_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
locked = 'locked_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)
partial = 'partial_example'  # str |  (optional)
pending_work_orders = 'pending_work_orders_example'  # str |  (optional)
pool = 'pool_example'  # str |  (optional)
pool_allocated = 'pool_allocated_example'  # str |  (optional)
pool_status = 'pool_status_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
retry_task_attempt = 'retry_task_attempt_example'  # str |  (optional)
runnable = 'runnable_example'  # str |  (optional)
running_work_orders = 'running_work_orders_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
task_error_stacks = 'task_error_stacks_example'  # str |  (optional)
tasks = 'tasks_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order_mode = 'work_order_mode_example'  # str |  (optional)
workflow = 'workflow_example'  # str |  (optional)
workflow_complete = 'workflow_complete_example'  # str |  (optional)

try:
    # Lists Machines filtered by some parameters.
    api_response = api_instance.list_machines(offset=offset, limit=limit, aggregate=aggregate,
                                              exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                              group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                              slim=slim, sort=sort, address=address, arch=arch, available=available,
                                              boot_env=boot_env, bundle=bundle, context=context,
                                              current_job=current_job, current_task=current_task,
                                              description=description, endpoint=endpoint, errors=errors,
                                              hardware_addr=hardware_addr, hardware_addrs=hardware_addrs, key=key,
                                              locked=locked, meta=meta, name=name, os=os, partial=partial,
                                              pending_work_orders=pending_work_orders, pool=pool,
                                              pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles,
                                              read_only=read_only, retry_task_attempt=retry_task_attempt,
                                              runnable=runnable, running_work_orders=running_work_orders, stage=stage,
                                              task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid,
                                              work_order_mode=work_order_mode, workflow=workflow,
                                              workflow_complete=workflow_complete)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->list_machines: %s\n" % e)
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
 **address** | **str**|  | [optional] 
 **arch** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **current_job** | **str**|  | [optional] 
 **current_task** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **hardware_addr** | **str**|  | [optional] 
 **hardware_addrs** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **locked** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 
 **partial** | **str**|  | [optional] 
 **pending_work_orders** | **str**|  | [optional] 
 **pool** | **str**|  | [optional] 
 **pool_allocated** | **str**|  | [optional] 
 **pool_status** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **retry_task_attempt** | **str**|  | [optional] 
 **runnable** | **str**|  | [optional] 
 **running_work_orders** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **task_error_stacks** | **str**|  | [optional] 
 **tasks** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order_mode** | **str**|  | [optional] 
 **workflow** | **str**|  | [optional] 
 **workflow_complete** | **str**|  | [optional] 

### Return type

[**list[Machine]**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_machines**
> list_stats_machines(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, address=address, arch=arch, available=available, boot_env=boot_env, bundle=bundle, context=context, current_job=current_job, current_task=current_task, description=description, endpoint=endpoint, errors=errors, hardware_addr=hardware_addr, hardware_addrs=hardware_addrs, key=key, locked=locked, meta=meta, name=name, os=os, partial=partial, pending_work_orders=pending_work_orders, pool=pool, pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles, read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable, running_work_orders=running_work_orders, stage=stage, task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid, work_order_mode=work_order_mode, workflow=workflow, workflow_complete=workflow_complete)

Stats of the List Machines filtered by some parameters.

This will return headers with the stats of the list.  X-DRP-LIST-COUNT - number of objects in the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Uuid = UUID string Name = string BootEnv = string Address = IP Address Runnable = true/false Available = boolean Valid = boolean ReadOnly = boolean  exclude-self = boolean = true means to not include self-runners  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
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
address = 'address_example'  # str |  (optional)
arch = 'arch_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
current_job = 'current_job_example'  # str |  (optional)
current_task = 'current_task_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
hardware_addr = 'hardware_addr_example'  # str |  (optional)
hardware_addrs = 'hardware_addrs_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
locked = 'locked_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)
partial = 'partial_example'  # str |  (optional)
pending_work_orders = 'pending_work_orders_example'  # str |  (optional)
pool = 'pool_example'  # str |  (optional)
pool_allocated = 'pool_allocated_example'  # str |  (optional)
pool_status = 'pool_status_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
retry_task_attempt = 'retry_task_attempt_example'  # str |  (optional)
runnable = 'runnable_example'  # str |  (optional)
running_work_orders = 'running_work_orders_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
task_error_stacks = 'task_error_stacks_example'  # str |  (optional)
tasks = 'tasks_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order_mode = 'work_order_mode_example'  # str |  (optional)
workflow = 'workflow_example'  # str |  (optional)
workflow_complete = 'workflow_complete_example'  # str |  (optional)

try:
    # Stats of the List Machines filtered by some parameters.
    api_instance.list_stats_machines(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                     filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                     range_only=range_only, reverse=reverse, slim=slim, sort=sort, address=address,
                                     arch=arch, available=available, boot_env=boot_env, bundle=bundle, context=context,
                                     current_job=current_job, current_task=current_task, description=description,
                                     endpoint=endpoint, errors=errors, hardware_addr=hardware_addr,
                                     hardware_addrs=hardware_addrs, key=key, locked=locked, meta=meta, name=name, os=os,
                                     partial=partial, pending_work_orders=pending_work_orders, pool=pool,
                                     pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles,
                                     read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable,
                                     running_work_orders=running_work_orders, stage=stage,
                                     task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid,
                                     work_order_mode=work_order_mode, workflow=workflow,
                                     workflow_complete=workflow_complete)
except ApiException as e:
    print("Exception when calling MachinesApi->list_stats_machines: %s\n" % e)
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
 **address** | **str**|  | [optional] 
 **arch** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **current_job** | **str**|  | [optional] 
 **current_task** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **hardware_addr** | **str**|  | [optional] 
 **hardware_addrs** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **locked** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 
 **partial** | **str**|  | [optional] 
 **pending_work_orders** | **str**|  | [optional] 
 **pool** | **str**|  | [optional] 
 **pool_allocated** | **str**|  | [optional] 
 **pool_status** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **retry_task_attempt** | **str**|  | [optional] 
 **runnable** | **str**|  | [optional] 
 **running_work_orders** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **task_error_stacks** | **str**|  | [optional] 
 **tasks** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order_mode** | **str**|  | [optional] 
 **workflow** | **str**|  | [optional] 
 **workflow_complete** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_machine**
> Machine patch_machine(body, uuid, force=force)

Patch a Machine

Update a Machine specified by {uuid} using a RFC6902 Patch structure

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Patch a Machine
    api_response = api_instance.patch_machine(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->patch_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_machine_params**
> dict(str, object) patch_machine_params(body, uuid)



Update params for Machine {uuid} with the passed-in patch

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 

try:
    api_response = api_instance.patch_machine_params(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->patch_machine_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **pick_machine_work_order**
> WorkOrder pick_machine_work_order(uuid, key)

Pick a workorder for this agent.  This can return the current work order.

No input. (optional WorkOrder may be provided)

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 

try:
    # Pick a workorder for this agent.  This can return the current work order.
    api_response = api_instance.pick_machine_work_order(uuid, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->pick_machine_work_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **key** | **str**|  | 

### Return type

[**WorkOrder**](WorkOrder.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_machine_action**
> object post_machine_action(uuid, cmd, body, plugin=plugin)

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_machine_action(uuid, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->post_machine_action: %s\n" % e)
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

# **post_machine_param**
> object post_machine_param(body, uuid, key)



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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 

try:
    api_response = api_instance.post_machine_param(body, uuid, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->post_machine_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | 
 **uuid** | [**str**](.md)|  | 
 **key** | **str**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_machine_params**
> dict(str, object) post_machine_params(body, uuid)



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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
uuid = 'uuid_example'  # str | 

try:
    api_response = api_instance.post_machine_params(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->post_machine_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_machine**
> Machine put_machine(body, uuid, force=force)

Put a Machine

Update a Machine specified by {uuid} using a JSON Machine

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Machine()  # Machine | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Put a Machine
    api_response = api_instance.put_machine(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->put_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Machine**](Machine.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_machine**
> Machine start_machine(body, uuid, force=force)

Start a Machine

Update a Machine specified by {uuid} using a RFC6902 Patch structure after clearing Workflow and Runnable.

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
api_instance = drppy_client.MachinesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Start a Machine
    api_response = api_instance.start_machine(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MachinesApi->start_machine: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

