# swagger_client.PoolsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_pool**](PoolsApi.md#create_pool) | **POST** /pools | Create a Pool
[**delete_pool**](PoolsApi.md#delete_pool) | **DELETE** /pools/{id} | Delete a Pool
[**get_pool**](PoolsApi.md#get_pool) | **GET** /pools/{id} | Get a Pool
[**get_pool_action**](PoolsApi.md#get_pool_action) | **GET** /pools/{id}/actions/{cmd} | List specific action for a task Pool
[**get_pool_actions**](PoolsApi.md#get_pool_actions) | **GET** /pools/{id}/actions | List task actions Pool
[**get_pool_status**](PoolsApi.md#get_pool_status) | **GET** /pools/{id}/status | 
[**head_pool**](PoolsApi.md#head_pool) | **HEAD** /pools/{id} | See if a Pool exists
[**list_active_pools**](PoolsApi.md#list_active_pools) | **GET** /pools-active | Lists active Pools
[**list_pools**](PoolsApi.md#list_pools) | **GET** /pools | Lists Pools filtered by some parameters.
[**list_stats_pools**](PoolsApi.md#list_stats_pools) | **HEAD** /pools | Stats of the List Pools filtered by some parameters.
[**patch_pool**](PoolsApi.md#patch_pool) | **PATCH** /pools/{id} | Patch a Pool
[**post_pool_action**](PoolsApi.md#post_pool_action) | **POST** /pools/{id}/actions/{cmd} | Call an action on the node.
[**post_pool_add_machines**](PoolsApi.md#post_pool_add_machines) | **POST** /pools/{id}/addMachines | Add machines to this pool from default.
[**post_pool_allocate_machines**](PoolsApi.md#post_pool_allocate_machines) | **POST** /pools/{id}/allocateMachines | Allocate machines in this pool.
[**post_pool_release_machines**](PoolsApi.md#post_pool_release_machines) | **POST** /pools/{id}/releaseMachines | Release machines in this pool.
[**post_pool_remove_machines**](PoolsApi.md#post_pool_remove_machines) | **POST** /pools/{id}/removeMachines | Remove machines from this pool to default.
[**put_pool**](PoolsApi.md#put_pool) | **PUT** /pools/{id} | Put a Pool


# **create_pool**
> Pool create_pool(body)

Create a Pool

Create a Pool from the provided object

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Pool()  # Pool | 

try:
    # Create a Pool
    api_response = api_instance.create_pool(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->create_pool: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Pool**](Pool.md)|  | 

### Return type

[**Pool**](Pool.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_pool**
> Pool delete_pool(id, force=force, source_pool=source_pool)

Delete a Pool

Delete a Pool specified by {id}

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Delete a Pool
    api_response = api_instance.delete_pool(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->delete_pool: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**Pool**](Pool.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_pool**
> Pool get_pool(id, force=force, source_pool=source_pool)

Get a Pool

Get the Pool specified by {id} or return NotFound.

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Get a Pool
    api_response = api_instance.get_pool(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->get_pool: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**Pool**](Pool.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_pool_action**
> AvailableAction get_pool_action(id, cmd, plugin=plugin)

List specific action for a task Pool

List specific {cmd} action for a Pool specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a task Pool
    api_response = api_instance.get_pool_action(id, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->get_pool_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
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

# **get_pool_actions**
> list[AvailableAction] get_pool_actions(id, plugin=plugin)

List task actions Pool

List Pool actions for a Pool specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List task actions Pool
    api_response = api_instance.get_pool_actions(id, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->get_pool_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **plugin** | **str**|  | [optional] 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_pool_status**
> PoolStatus get_pool_status(id, force=force, source_pool=source_pool)



Returns the status of the machines in the pool

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    api_response = api_instance.get_pool_status(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->get_pool_status: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**PoolStatus**](PoolStatus.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_pool**
> head_pool(id, force=force, source_pool=source_pool)

See if a Pool exists

Return 200 if the Pool specifiec by {id} exists, or return NotFound.

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # See if a Pool exists
    api_instance.head_pool(id, force=force, source_pool=source_pool)
except ApiException as e:
    print("Exception when calling PoolsApi->head_pool: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_active_pools**
> list[str] list_active_pools(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, id=id, key=key, meta=meta, parent_pool=parent_pool, read_only=read_only, valid=valid)

Lists active Pools

Returns the list of active pools

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
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
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
parent_pool = 'parent_pool_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists active Pools
    api_response = api_instance.list_active_pools(offset=offset, limit=limit, aggregate=aggregate,
                                                  exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                                  group_by=group_by, params=params, range_only=range_only,
                                                  reverse=reverse, slim=slim, sort=sort, available=available,
                                                  bundle=bundle, description=description, documentation=documentation,
                                                  endpoint=endpoint, errors=errors, id=id, key=key, meta=meta,
                                                  parent_pool=parent_pool, read_only=read_only, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->list_active_pools: %s\n" % e)
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
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **parent_pool** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

**list[str]**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_pools**
> list[Pool] list_pools(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, id=id, key=key, meta=meta, parent_pool=parent_pool, read_only=read_only, valid=valid)

Lists Pools filtered by some parameters.

This will show all Pools by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: ID = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred. ID=Lt(fred)&Available=true - returns items with ID less than fred and Available is true

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
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
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
parent_pool = 'parent_pool_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists Pools filtered by some parameters.
    api_response = api_instance.list_pools(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                           filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                           range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                           available=available, bundle=bundle, description=description,
                                           documentation=documentation, endpoint=endpoint, errors=errors, id=id,
                                           key=key, meta=meta, parent_pool=parent_pool, read_only=read_only,
                                           valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->list_pools: %s\n" % e)
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
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **parent_pool** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[Pool]**](Pool.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_pools**
> list_stats_pools(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, id=id, key=key, meta=meta, parent_pool=parent_pool, read_only=read_only, valid=valid)

Stats of the List Pools filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: ID = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred. ID=Lt(fred)&Available=true - returns items with ID less than fred and Available is true

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
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
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
parent_pool = 'parent_pool_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List Pools filtered by some parameters.
    api_instance.list_stats_pools(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                  filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                  range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available,
                                  bundle=bundle, description=description, documentation=documentation,
                                  endpoint=endpoint, errors=errors, id=id, key=key, meta=meta, parent_pool=parent_pool,
                                  read_only=read_only, valid=valid)
except ApiException as e:
    print("Exception when calling PoolsApi->list_stats_pools: %s\n" % e)
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
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **parent_pool** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_pool**
> Pool patch_pool(body, id, force=force, source_pool=source_pool)

Patch a Pool

Update a Pool specified by {id} using a RFC6902 Patch structure

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Patch a Pool
    api_response = api_instance.patch_pool(body, id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->patch_pool: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**Pool**](Pool.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_pool_action**
> object post_pool_action(id, cmd, body, force=force, source_pool=source_pool, plugin=plugin)

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_pool_action(id, cmd, body, force=force, source_pool=source_pool, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->post_pool_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **cmd** | **str**|  | 
 **body** | **object**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 
 **plugin** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_pool_add_machines**
> list[PoolResult] post_pool_add_machines(id, force=force, source_pool=source_pool)

Add machines to this pool from default.

Input is a map with the following fields.  These fields override the pool definitions if they exist on the pool. pool/workflow = workflow of to set on transition pool/add-profiles pool/add-parameters pool/remove-profiles pool/remove-parameters  These fields define what to operate. pool/count = how many nodes to change pool/minimum = minimum machnies to allocate or fail pool/filter = list of list-style filters (e.g. Runnable=Eq(true)) pool/wait-timeout = Time to delay in seconds or time string (30m) pool/machine-list - a list of machine UUID or Name:name pool/all-machines - boolean for all machines in pool

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Add machines to this pool from default.
    api_response = api_instance.post_pool_add_machines(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->post_pool_add_machines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**list[PoolResult]**](PoolResult.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_pool_allocate_machines**
> list[PoolResult] post_pool_allocate_machines(id, force=force, source_pool=source_pool)

Allocate machines in this pool.

Input is a map with the following fields.  These fields override the pool definitions if they exist on the pool. pool/workflow = workflow of to set on transition pool/add-profiles pool/add-parameters pool/remove-profiles pool/remove-parameters  These fields define what to operate. pool/count = how many nodes to change pool/minimum = minimum machnies to allocate or fail pool/filter = list of list-style filters (e.g. Runnable=Eq(true)) pool/wait-timeout = Time to delay in seconds or time string (30m) pool/machine-list - a list of machine UUID or Name:name pool/all-machines - boolean for all machines in pool

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Allocate machines in this pool.
    api_response = api_instance.post_pool_allocate_machines(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->post_pool_allocate_machines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**list[PoolResult]**](PoolResult.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_pool_release_machines**
> list[PoolResult] post_pool_release_machines(id, force=force, source_pool=source_pool)

Release machines in this pool.

Input is a map with the following fields.  These fields override the pool definitions if they exist on the pool. pool/workflow = workflow of to set on transition pool/add-profiles pool/add-parameters pool/remove-profiles pool/remove-parameters  These fields define what to operate. pool/count = how many nodes to change pool/minimum = minimum machnies to allocate or fail pool/filter = list of list-style filters (e.g. Runnable=Eq(true)) pool/wait-timeout = Time to delay in seconds or time string (30m) pool/machine-list - a list of machine UUID or Name:name pool/all-machines - boolean for all machines in pool

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Release machines in this pool.
    api_response = api_instance.post_pool_release_machines(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->post_pool_release_machines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**list[PoolResult]**](PoolResult.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_pool_remove_machines**
> list[PoolResult] post_pool_remove_machines(id, force=force, source_pool=source_pool)

Remove machines from this pool to default.

Input is a map with the following fields.  These fields override the pool definitions if they exist on the pool. pool/workflow = workflow of to set on transition pool/add-profiles pool/add-parameters pool/remove-profiles pool/remove-parameters  These fields define what to operate. pool/count = how many nodes to change pool/minimum = minimum machnies to allocate or fail pool/filter = list of list-style filters (e.g. Runnable=Eq(true)) pool/wait-timeout = Time to delay in seconds or time string (30m) pool/machine-list - a list of machine UUID or Name:name pool/all-machines - boolean for all machines in pool

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Remove machines from this pool to default.
    api_response = api_instance.post_pool_remove_machines(id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->post_pool_remove_machines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**list[PoolResult]**](PoolResult.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_pool**
> Pool put_pool(body, id, force=force, source_pool=source_pool)

Put a Pool

Update a Pool specified by {id} using a JSON Pool

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
api_instance = drppy_client.PoolsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Pool()  # Pool | 
id = 'id_example'  # str | 
force = 'force_example'  # str |  (optional)
source_pool = 'source_pool_example'  # str |  (optional)

try:
    # Put a Pool
    api_response = api_instance.put_pool(body, id, force=force, source_pool=source_pool)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoolsApi->put_pool: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Pool**](Pool.md)|  | 
 **id** | **str**|  | 
 **force** | **str**|  | [optional] 
 **source_pool** | **str**|  | [optional] 

### Return type

[**Pool**](Pool.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

