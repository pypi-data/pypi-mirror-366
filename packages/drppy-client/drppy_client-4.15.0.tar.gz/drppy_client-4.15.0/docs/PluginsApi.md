# swagger_client.PluginsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_plugin**](PluginsApi.md#create_plugin) | **POST** /plugins | Create a Plugin
[**delete_plugin**](PluginsApi.md#delete_plugin) | **DELETE** /plugins/{name} | Delete a Plugin
[**delete_plugin_param**](PluginsApi.md#delete_plugin_param) | **DELETE** /plugins/{uuid}/params/{key} | Delete a single plugin parameter
[**get_plugin**](PluginsApi.md#get_plugin) | **GET** /plugins/{name} | Get a Plugin
[**get_plugin_action**](PluginsApi.md#get_plugin_action) | **GET** /plugins/{name}/actions/{cmd} | List specific action for a plugin Plugin
[**get_plugin_actions**](PluginsApi.md#get_plugin_actions) | **GET** /plugins/{name}/actions | List plugin actions Plugin
[**get_plugin_param**](PluginsApi.md#get_plugin_param) | **GET** /plugins/{name}/params/{key} | Get a single plugin parameter
[**get_plugin_params**](PluginsApi.md#get_plugin_params) | **GET** /plugins/{name}/params | List plugin params Plugin
[**get_plugin_pub_key**](PluginsApi.md#get_plugin_pub_key) | **GET** /plugins/{name}/pubkey | Get the public key for secure params on a plugin
[**head_plugin**](PluginsApi.md#head_plugin) | **HEAD** /plugins/{name} | See if a Plugin exists
[**list_plugins**](PluginsApi.md#list_plugins) | **GET** /plugins | Lists Plugins filtered by some parameters.
[**list_stats_plugins**](PluginsApi.md#list_stats_plugins) | **HEAD** /plugins | Stats of the List Plugins filtered by some parameters.
[**patch_plugin**](PluginsApi.md#patch_plugin) | **PATCH** /plugins/{name} | Patch a Plugin
[**patch_plugin_params**](PluginsApi.md#patch_plugin_params) | **PATCH** /plugins/{name}/params | 
[**post_plugin_action**](PluginsApi.md#post_plugin_action) | **POST** /plugins/{name}/actions/{cmd} | Call an action on the node.
[**post_plugin_param**](PluginsApi.md#post_plugin_param) | **POST** /plugins/{name}/params/{key} | 
[**post_plugin_params**](PluginsApi.md#post_plugin_params) | **POST** /plugins/{name}/params | 
[**put_plugin**](PluginsApi.md#put_plugin) | **PUT** /plugins/{name} | Put a Plugin


# **create_plugin**
> Plugin create_plugin(body)

Create a Plugin

Create a Plugin from the provided object

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Plugin()  # Plugin | 

try:
    # Create a Plugin
    api_response = api_instance.create_plugin(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->create_plugin: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Plugin**](Plugin.md)|  | 

### Return type

[**Plugin**](Plugin.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_plugin**
> Plugin delete_plugin(name, decode=decode, params=params)

Delete a Plugin

Delete a Plugin specified by {name}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Delete a Plugin
    api_response = api_instance.delete_plugin(name, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->delete_plugin: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Plugin**](Plugin.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_plugin_param**
> object delete_plugin_param(name, key)

Delete a single plugin parameter

Delete a single parameter {key} for a Plugin specified by {uuid}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
key = 'key_example'  # str | 

try:
    # Delete a single plugin parameter
    api_response = api_instance.delete_plugin_param(name, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->delete_plugin_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **key** | **str**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_plugin**
> Plugin get_plugin(name, decode=decode, params=params)

Get a Plugin

Get the Plugin specified by {name} or return NotFound.

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get a Plugin
    api_response = api_instance.get_plugin(name, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->get_plugin: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Plugin**](Plugin.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_plugin_action**
> AvailableAction get_plugin_action(name, cmd, plugin=plugin)

List specific action for a plugin Plugin

List specific {cmd} action for a Plugin specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a plugin Plugin
    api_response = api_instance.get_plugin_action(name, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->get_plugin_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **get_plugin_actions**
> list[AvailableAction] get_plugin_actions(name, plugin=plugin)

List plugin actions Plugin

List Plugin actions for a Plugin specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List plugin actions Plugin
    api_response = api_instance.get_plugin_actions(name, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->get_plugin_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **plugin** | **str**|  | [optional] 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_plugin_param**
> object get_plugin_param(name, key, decode=decode)

Get a single plugin parameter

Get a single parameter {key} for a Plugin specified by {name}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
key = 'key_example'  # str | 
decode = 'decode_example'  # str |  (optional)

try:
    # Get a single plugin parameter
    api_response = api_instance.get_plugin_param(name, key, decode=decode)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->get_plugin_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **get_plugin_params**
> dict(str, object) get_plugin_params(name, decode=decode, params=params)

List plugin params Plugin

List Plugin parms for a Plugin specified by {name}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # List plugin params Plugin
    api_response = api_instance.get_plugin_params(name, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->get_plugin_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **get_plugin_pub_key**
> get_plugin_pub_key(name, decode=decode, params=params)

Get the public key for secure params on a plugin

Get the public key for a Plugin specified by {name}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get the public key for secure params on a plugin
    api_instance.get_plugin_pub_key(name, decode=decode, params=params)
except ApiException as e:
    print("Exception when calling PluginsApi->get_plugin_pub_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **head_plugin**
> head_plugin(name, decode=decode, params=params)

See if a Plugin exists

Return 200 if the Plugin specifiec by {name} exists, or return NotFound.

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # See if a Plugin exists
    api_instance.head_plugin(name, decode=decode, params=params)
except ApiException as e:
    print("Exception when calling PluginsApi->head_plugin: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **list_plugins**
> list[Plugin] list_plugins(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, key=key, meta=meta, name=name, partial=partial, plugin_errors=plugin_errors, provider=provider, read_only=read_only, valid=valid)

Lists Plugins filtered by some parameters.

This will show all Plugins by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexes: Name = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
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
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
partial = 'partial_example'  # str |  (optional)
plugin_errors = 'plugin_errors_example'  # str |  (optional)
provider = 'provider_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists Plugins filtered by some parameters.
    api_response = api_instance.list_plugins(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                             filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                             range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                             available=available, bundle=bundle, description=description,
                                             documentation=documentation, endpoint=endpoint, errors=errors, key=key,
                                             meta=meta, name=name, partial=partial, plugin_errors=plugin_errors,
                                             provider=provider, read_only=read_only, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->list_plugins: %s\n" % e)
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
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **partial** | **str**|  | [optional] 
 **plugin_errors** | **str**|  | [optional] 
 **provider** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[Plugin]**](Plugin.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_plugins**
> list_stats_plugins(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, key=key, meta=meta, name=name, partial=partial, plugin_errors=plugin_errors, provider=provider, read_only=read_only, valid=valid)

Stats of the List Plugins filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Name = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
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
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
partial = 'partial_example'  # str |  (optional)
plugin_errors = 'plugin_errors_example'  # str |  (optional)
provider = 'provider_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List Plugins filtered by some parameters.
    api_instance.list_stats_plugins(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                    filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                    range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available,
                                    bundle=bundle, description=description, documentation=documentation,
                                    endpoint=endpoint, errors=errors, key=key, meta=meta, name=name, partial=partial,
                                    plugin_errors=plugin_errors, provider=provider, read_only=read_only, valid=valid)
except ApiException as e:
    print("Exception when calling PluginsApi->list_stats_plugins: %s\n" % e)
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
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **partial** | **str**|  | [optional] 
 **plugin_errors** | **str**|  | [optional] 
 **provider** | **str**|  | [optional] 
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

# **patch_plugin**
> Plugin patch_plugin(body, name, decode=decode, params=params)

Patch a Plugin

Update a Plugin specified by {name} using a RFC6902 Patch structure

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Patch a Plugin
    api_response = api_instance.patch_plugin(body, name, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->patch_plugin: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **name** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Plugin**](Plugin.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_plugin_params**
> dict(str, object) patch_plugin_params(name, decode=decode, params=params)



Update params for Plugin {name} with the passed-in patch

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    api_response = api_instance.patch_plugin_params(name, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->patch_plugin_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **post_plugin_action**
> object post_plugin_action(name, cmd, body, plugin=plugin)

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_plugin_action(name, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->post_plugin_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **post_plugin_param**
> object post_plugin_param(name, key, body)



Set as single Parameter {key} for a plugin specified by {name}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
key = 'key_example'  # str | 
body = NULL  # object | 

try:
    api_response = api_instance.post_plugin_param(name, key, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->post_plugin_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **post_plugin_params**
> dict(str, object) post_plugin_params(name, body, decode=decode, params=params)



Sets parameters for a plugin specified by {name}

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
body = NULL  # object | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    api_response = api_instance.post_plugin_params(name, body, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->post_plugin_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **put_plugin**
> Plugin put_plugin(body, name, decode=decode, params=params)

Put a Plugin

Update a Plugin specified by {name} using a JSON Plugin

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
api_instance = drppy_client.PluginsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Plugin()  # Plugin | 
name = 'name_example'  # str | 
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Put a Plugin
    api_response = api_instance.put_plugin(body, name, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PluginsApi->put_plugin: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Plugin**](Plugin.md)|  | 
 **name** | **str**|  | 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Plugin**](Plugin.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

