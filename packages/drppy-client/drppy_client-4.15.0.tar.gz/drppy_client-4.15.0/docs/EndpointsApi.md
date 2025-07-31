# swagger_client.EndpointsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_endpoint**](EndpointsApi.md#create_endpoint) | **POST** /endpoints | Create a Endpoint
[**delete_endpoint**](EndpointsApi.md#delete_endpoint) | **DELETE** /endpoints/{id} | Delete a Endpoint
[**delete_endpoint_param**](EndpointsApi.md#delete_endpoint_param) | **DELETE** /endpoints/{uuid}/params/{key} | Delete a single endpoint parameter
[**get_endpoint**](EndpointsApi.md#get_endpoint) | **GET** /endpoints/{id} | Get a Endpoint
[**get_endpoint_action**](EndpointsApi.md#get_endpoint_action) | **GET** /endpoints/{id}/actions/{cmd} | List specific action for a endpoint Endpoint
[**get_endpoint_actions**](EndpointsApi.md#get_endpoint_actions) | **GET** /endpoints/{id}/actions | List endpoint actions Endpoint
[**get_endpoint_param**](EndpointsApi.md#get_endpoint_param) | **GET** /endpoints/{id}/params/{key} | Get a single endpoint parameter
[**get_endpoint_params**](EndpointsApi.md#get_endpoint_params) | **GET** /endpoints/{id}/params | List endpoint params Endpoint
[**get_endpoint_pub_key**](EndpointsApi.md#get_endpoint_pub_key) | **GET** /endpoints/{id}/pubkey | Get the public key for secure params on a endpoint
[**head_endpoint**](EndpointsApi.md#head_endpoint) | **HEAD** /endpoints/{id} | See if a Endpoint exists
[**list_endpoints**](EndpointsApi.md#list_endpoints) | **GET** /endpoints | Lists Endpoints filtered by some parameters.
[**list_stats_endpoints**](EndpointsApi.md#list_stats_endpoints) | **HEAD** /endpoints | Stats of the List Endpoints filtered by some parameters.
[**patch_endpoint**](EndpointsApi.md#patch_endpoint) | **PATCH** /endpoints/{id} | Patch a Endpoint
[**patch_endpoint_params**](EndpointsApi.md#patch_endpoint_params) | **PATCH** /endpoints/{id}/params | 
[**post_endpoint_action**](EndpointsApi.md#post_endpoint_action) | **POST** /endpoints/{id}/actions/{cmd} | Call an action on the node.
[**post_endpoint_param**](EndpointsApi.md#post_endpoint_param) | **POST** /endpoints/{id}/params/{key} | 
[**post_endpoint_params**](EndpointsApi.md#post_endpoint_params) | **POST** /endpoints/{id}/params | 
[**put_endpoint**](EndpointsApi.md#put_endpoint) | **PUT** /endpoints/{id} | Put a Endpoint


# **create_endpoint**
> Endpoint create_endpoint(body)

Create a Endpoint

Create a Endpoint from the provided object

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Endpoint()  # Endpoint | 

try:
    # Create a Endpoint
    api_response = api_instance.create_endpoint(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->create_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Endpoint**](Endpoint.md)|  | 

### Return type

[**Endpoint**](Endpoint.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_endpoint**
> Endpoint delete_endpoint(id, decode=decode, params=params)

Delete a Endpoint

Delete a Endpoint specified by {id}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Delete a Endpoint
    api_response = api_instance.delete_endpoint(id, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->delete_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Endpoint**](Endpoint.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_endpoint_param**
> object delete_endpoint_param(id, key)

Delete a single endpoint parameter

Delete a single parameter {key} for a Endpoint specified by {uuid}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
key = 'key_example'  # str | 

try:
    # Delete a single endpoint parameter
    api_response = api_instance.delete_endpoint_param(id, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->delete_endpoint_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **key** | **str**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_endpoint**
> Endpoint get_endpoint(id, decode=decode, params=params)

Get a Endpoint

Get the Endpoint specified by {id} or return NotFound.

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get a Endpoint
    api_response = api_instance.get_endpoint(id, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Endpoint**](Endpoint.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_endpoint_action**
> AvailableAction get_endpoint_action(id, cmd, plugin=plugin)

List specific action for a endpoint Endpoint

List specific {cmd} action for a Endpoint specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a endpoint Endpoint
    api_response = api_instance.get_endpoint_action(id, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_endpoint_action: %s\n" % e)
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

# **get_endpoint_actions**
> list[AvailableAction] get_endpoint_actions(id, plugin=plugin)

List endpoint actions Endpoint

List Endpoint actions for a Endpoint specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List endpoint actions Endpoint
    api_response = api_instance.get_endpoint_actions(id, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_endpoint_actions: %s\n" % e)
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

# **get_endpoint_param**
> object get_endpoint_param(id, key, decode=decode)

Get a single endpoint parameter

Get a single parameter {key} for a Endpoint specified by {id}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
key = 'key_example'  # str | 
decode = 'decode_example'  # str |  (optional)

try:
    # Get a single endpoint parameter
    api_response = api_instance.get_endpoint_param(id, key, decode=decode)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_endpoint_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **key** | **str**|  | 
 **decode** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_endpoint_params**
> dict(str, object) get_endpoint_params(id, decode=decode, params=params)

List endpoint params Endpoint

List Endpoint parms for a Endpoint specified by {id}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # List endpoint params Endpoint
    api_response = api_instance.get_endpoint_params(id, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_endpoint_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
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

# **get_endpoint_pub_key**
> get_endpoint_pub_key(id, decode=decode, params=params)

Get the public key for secure params on a endpoint

Get the public key for a Endpoint specified by {id}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get the public key for secure params on a endpoint
    api_instance.get_endpoint_pub_key(id, decode=decode, params=params)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_endpoint_pub_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_endpoint**
> head_endpoint(id, decode=decode, params=params)

See if a Endpoint exists

Return 200 if the Endpoint specifiec by {id} exists, or return NotFound.

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # See if a Endpoint exists
    api_instance.head_endpoint(id, decode=decode, params=params)
except ApiException as e:
    print("Exception when calling EndpointsApi->head_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_endpoints**
> list[Endpoint] list_endpoints(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, actions=actions, apply=apply, arch=arch, available=available, bundle=bundle, components=components, connection_status=connection_status, drpux_version=drpux_version, drp_version=drp_version, description=description, documentation=documentation, endpoint=endpoint, errors=errors, _global=_global, ha_id=ha_id, id=id, key=key, meta=meta, os=os, plugins=plugins, prefs=prefs, read_only=read_only, valid=valid, version_set=version_set, version_sets=version_sets)

Lists Endpoints filtered by some parameters.

This will show all Endpoints by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: ID = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred.

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
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
actions = 'actions_example'  # str |  (optional)
apply = 'apply_example'  # str |  (optional)
arch = 'arch_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
components = 'components_example'  # str |  (optional)
connection_status = 'connection_status_example'  # str |  (optional)
drpux_version = 'drpux_version_example'  # str |  (optional)
drp_version = 'drp_version_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
_global = '_global_example'  # str |  (optional)
ha_id = 'ha_id_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)
plugins = 'plugins_example'  # str |  (optional)
prefs = 'prefs_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
version_set = 'version_set_example'  # str |  (optional)
version_sets = 'version_sets_example'  # str |  (optional)

try:
    # Lists Endpoints filtered by some parameters.
    api_response = api_instance.list_endpoints(offset=offset, limit=limit, aggregate=aggregate,
                                               exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                               group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                               slim=slim, sort=sort, actions=actions, apply=apply, arch=arch,
                                               available=available, bundle=bundle, components=components,
                                               connection_status=connection_status, drpux_version=drpux_version,
                                               drp_version=drp_version, description=description,
                                               documentation=documentation, endpoint=endpoint, errors=errors,
                                               _global=_global, ha_id=ha_id, id=id, key=key, meta=meta, os=os,
                                               plugins=plugins, prefs=prefs, read_only=read_only, valid=valid,
                                               version_set=version_set, version_sets=version_sets)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->list_endpoints: %s\n" % e)
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
 **actions** | **str**|  | [optional] 
 **apply** | **str**|  | [optional] 
 **arch** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **components** | **str**|  | [optional] 
 **connection_status** | **str**|  | [optional] 
 **drpux_version** | **str**|  | [optional] 
 **drp_version** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **_global** | **str**|  | [optional] 
 **ha_id** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 
 **plugins** | **str**|  | [optional] 
 **prefs** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **version_set** | **str**|  | [optional] 
 **version_sets** | **str**|  | [optional] 

### Return type

[**list[Endpoint]**](Endpoint.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_endpoints**
> list_stats_endpoints(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, actions=actions, apply=apply, arch=arch, available=available, bundle=bundle, components=components, connection_status=connection_status, drpux_version=drpux_version, drp_version=drp_version, description=description, documentation=documentation, endpoint=endpoint, errors=errors, _global=_global, ha_id=ha_id, id=id, key=key, meta=meta, os=os, plugins=plugins, prefs=prefs, read_only=read_only, valid=valid, version_set=version_set, version_sets=version_sets)

Stats of the List Endpoints filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: ID = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred.

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
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
actions = 'actions_example'  # str |  (optional)
apply = 'apply_example'  # str |  (optional)
arch = 'arch_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
components = 'components_example'  # str |  (optional)
connection_status = 'connection_status_example'  # str |  (optional)
drpux_version = 'drpux_version_example'  # str |  (optional)
drp_version = 'drp_version_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
_global = '_global_example'  # str |  (optional)
ha_id = 'ha_id_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)
plugins = 'plugins_example'  # str |  (optional)
prefs = 'prefs_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
version_set = 'version_set_example'  # str |  (optional)
version_sets = 'version_sets_example'  # str |  (optional)

try:
    # Stats of the List Endpoints filtered by some parameters.
    api_instance.list_stats_endpoints(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                      filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                      range_only=range_only, reverse=reverse, slim=slim, sort=sort, actions=actions,
                                      apply=apply, arch=arch, available=available, bundle=bundle, components=components,
                                      connection_status=connection_status, drpux_version=drpux_version,
                                      drp_version=drp_version, description=description, documentation=documentation,
                                      endpoint=endpoint, errors=errors, _global=_global, ha_id=ha_id, id=id, key=key,
                                      meta=meta, os=os, plugins=plugins, prefs=prefs, read_only=read_only, valid=valid,
                                      version_set=version_set, version_sets=version_sets)
except ApiException as e:
    print("Exception when calling EndpointsApi->list_stats_endpoints: %s\n" % e)
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
 **actions** | **str**|  | [optional] 
 **apply** | **str**|  | [optional] 
 **arch** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **components** | **str**|  | [optional] 
 **connection_status** | **str**|  | [optional] 
 **drpux_version** | **str**|  | [optional] 
 **drp_version** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **_global** | **str**|  | [optional] 
 **ha_id** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 
 **plugins** | **str**|  | [optional] 
 **prefs** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **version_set** | **str**|  | [optional] 
 **version_sets** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_endpoint**
> Endpoint patch_endpoint(body, id, decode=decode, params=params)

Patch a Endpoint

Update a Endpoint specified by {id} using a RFC6902 Patch structure

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Patch a Endpoint
    api_response = api_instance.patch_endpoint(body, id, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->patch_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **id** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Endpoint**](Endpoint.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_endpoint_params**
> dict(str, object) patch_endpoint_params(body, id, decode=decode, params=params)



Update params for Endpoint {id} with the passed-in patch

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    api_response = api_instance.patch_endpoint_params(body, id, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->patch_endpoint_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **id** | **str**|  | 
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

# **post_endpoint_action**
> object post_endpoint_action(id, cmd, body, plugin=plugin)

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_endpoint_action(id, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->post_endpoint_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
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

# **post_endpoint_param**
> object post_endpoint_param(id, key, body)



Set as single Parameter {key} for a endpoint specified by {id}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
key = 'key_example'  # str | 
body = NULL  # object | 

try:
    api_response = api_instance.post_endpoint_param(id, key, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->post_endpoint_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **key** | **str**|  | 
 **body** | **object**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_endpoint_params**
> dict(str, object) post_endpoint_params(id, body, decode=decode, params=params)



Sets parameters for a endpoint specified by {id}

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
body = NULL  # object | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    api_response = api_instance.post_endpoint_params(id, body, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->post_endpoint_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **body** | **object**|  | 
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

# **put_endpoint**
> Endpoint put_endpoint(body, id, decode=decode, params=params)

Put a Endpoint

Update a Endpoint specified by {id} using a JSON Endpoint

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
api_instance = drppy_client.EndpointsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Endpoint()  # Endpoint | 
id = 'id_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Put a Endpoint
    api_response = api_instance.put_endpoint(body, id, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->put_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Endpoint**](Endpoint.md)|  | 
 **id** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Endpoint**](Endpoint.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

