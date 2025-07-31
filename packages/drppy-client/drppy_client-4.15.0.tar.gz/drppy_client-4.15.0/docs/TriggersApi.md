# swagger_client.TriggersApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_trigger**](TriggersApi.md#create_trigger) | **POST** /triggers | Create a Trigger
[**delete_trigger**](TriggersApi.md#delete_trigger) | **DELETE** /triggers/{name} | Delete a Trigger
[**delete_trigger_param**](TriggersApi.md#delete_trigger_param) | **DELETE** /triggers/{name}/params/{key} | Delete a single trigger parameter
[**get_trigger**](TriggersApi.md#get_trigger) | **GET** /triggers/{name} | Get a Trigger
[**get_trigger_action**](TriggersApi.md#get_trigger_action) | **GET** /triggers/{name}/actions/{cmd} | List specific action for a trigger Trigger
[**get_trigger_actions**](TriggersApi.md#get_trigger_actions) | **GET** /triggers/{name}/actions | List trigger actions Trigger
[**get_trigger_param**](TriggersApi.md#get_trigger_param) | **GET** /triggers/{name}/params/{key} | Get a single trigger parameter
[**get_trigger_params**](TriggersApi.md#get_trigger_params) | **GET** /triggers/{name}/params | List trigger params Trigger
[**get_trigger_pub_key**](TriggersApi.md#get_trigger_pub_key) | **GET** /triggers/{name}/pubkey | Get the public key for secure params on a trigger
[**head_trigger**](TriggersApi.md#head_trigger) | **HEAD** /triggers/{name} | See if a Trigger exists
[**list_stats_triggers**](TriggersApi.md#list_stats_triggers) | **HEAD** /triggers | Stats of the List Triggers filtered by some parameters.
[**list_triggers**](TriggersApi.md#list_triggers) | **GET** /triggers | Lists Triggers filtered by some parameters.
[**patch_trigger**](TriggersApi.md#patch_trigger) | **PATCH** /triggers/{name} | Patch a Trigger
[**patch_trigger_params**](TriggersApi.md#patch_trigger_params) | **PATCH** /triggers/{name}/params | 
[**post_trigger_action**](TriggersApi.md#post_trigger_action) | **POST** /triggers/{name}/actions/{cmd} | Call an action on the node.
[**post_trigger_param**](TriggersApi.md#post_trigger_param) | **POST** /triggers/{name}/params/{key} | 
[**post_trigger_params**](TriggersApi.md#post_trigger_params) | **POST** /triggers/{name}/params | 
[**put_trigger**](TriggersApi.md#put_trigger) | **PUT** /triggers/{name} | Put a Trigger


# **create_trigger**
> Trigger create_trigger(body)

Create a Trigger

Create a Trigger from the provided object

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Trigger()  # Trigger | 

try:
    # Create a Trigger
    api_response = api_instance.create_trigger(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->create_trigger: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Trigger**](Trigger.md)|  | 

### Return type

[**Trigger**](Trigger.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_trigger**
> Trigger delete_trigger(name)

Delete a Trigger

Delete a Trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Delete a Trigger
    api_response = api_instance.delete_trigger(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->delete_trigger: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**Trigger**](Trigger.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_trigger_param**
> object delete_trigger_param()

Delete a single trigger parameter

Delete a single parameter {key} for a Trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))

try:
    # Delete a single trigger parameter
    api_response = api_instance.delete_trigger_param()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->delete_trigger_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_trigger**
> Trigger get_trigger(name)

Get a Trigger

Get the Trigger specified by {name} or return NotFound.

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Get a Trigger
    api_response = api_instance.get_trigger(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->get_trigger: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**Trigger**](Trigger.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_trigger_action**
> AvailableAction get_trigger_action(name, cmd, plugin=plugin)

List specific action for a trigger Trigger

List specific {cmd} action for a Trigger specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a trigger Trigger
    api_response = api_instance.get_trigger_action(name, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->get_trigger_action: %s\n" % e)
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

# **get_trigger_actions**
> list[AvailableAction] get_trigger_actions(name, plugin=plugin)

List trigger actions Trigger

List Trigger actions for a Trigger specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List trigger actions Trigger
    api_response = api_instance.get_trigger_actions(name, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->get_trigger_actions: %s\n" % e)
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

# **get_trigger_param**
> object get_trigger_param(name, key, aggregate=aggregate, decode=decode)

Get a single trigger parameter

Get a single parameter {key} for a Trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
key = 'key_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)

try:
    # Get a single trigger parameter
    api_response = api_instance.get_trigger_param(name, key, aggregate=aggregate, decode=decode)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->get_trigger_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **get_trigger_params**
> dict(str, object) get_trigger_params(name, aggregate=aggregate, decode=decode, params=params)

List trigger params Trigger

List Trigger parms for a Trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # List trigger params Trigger
    api_response = api_instance.get_trigger_params(name, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->get_trigger_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
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

# **get_trigger_pub_key**
> get_trigger_pub_key(name)

Get the public key for secure params on a trigger

Get the public key for a Trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Get the public key for secure params on a trigger
    api_instance.get_trigger_pub_key(name)
except ApiException as e:
    print("Exception when calling TriggersApi->get_trigger_pub_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_trigger**
> head_trigger(name)

See if a Trigger exists

Return 200 if the Trigger specifiec by {name} exists, or return NotFound.

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # See if a Trigger exists
    api_instance.head_trigger(name)
except ApiException as e:
    print("Exception when calling TriggersApi->head_trigger: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_triggers**
> list_stats_triggers(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, all_in_filter=all_in_filter, available=available, blueprint=blueprint, bundle=bundle, description=description, documentation=documentation, enabled=enabled, endpoint=endpoint, errors=errors, filter_count=filter_count, key=key, merge_data_into_params=merge_data_into_params, meta=meta, name=name, profiles=profiles, queue_mode=queue_mode, read_only=read_only, store_data_in_parameter=store_data_in_parameter, trigger_provider=trigger_provider, valid=valid, work_order_params=work_order_params, work_order_profiles=work_order_profiles)

Stats of the List Triggers filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Name = string Reboot = boolean BootEnv = string Available = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
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
all_in_filter = 'all_in_filter_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
blueprint = 'blueprint_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
enabled = 'enabled_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
filter_count = 'filter_count_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
merge_data_into_params = 'merge_data_into_params_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
queue_mode = 'queue_mode_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
store_data_in_parameter = 'store_data_in_parameter_example'  # str |  (optional)
trigger_provider = 'trigger_provider_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order_params = 'work_order_params_example'  # str |  (optional)
work_order_profiles = 'work_order_profiles_example'  # str |  (optional)

try:
    # Stats of the List Triggers filtered by some parameters.
    api_instance.list_stats_triggers(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                     filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                     range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                     all_in_filter=all_in_filter, available=available, blueprint=blueprint,
                                     bundle=bundle, description=description, documentation=documentation,
                                     enabled=enabled, endpoint=endpoint, errors=errors, filter_count=filter_count,
                                     key=key, merge_data_into_params=merge_data_into_params, meta=meta, name=name,
                                     profiles=profiles, queue_mode=queue_mode, read_only=read_only,
                                     store_data_in_parameter=store_data_in_parameter, trigger_provider=trigger_provider,
                                     valid=valid, work_order_params=work_order_params,
                                     work_order_profiles=work_order_profiles)
except ApiException as e:
    print("Exception when calling TriggersApi->list_stats_triggers: %s\n" % e)
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
 **all_in_filter** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **blueprint** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **enabled** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **filter_count** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **merge_data_into_params** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **queue_mode** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **store_data_in_parameter** | **str**|  | [optional] 
 **trigger_provider** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order_params** | **str**|  | [optional] 
 **work_order_profiles** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_triggers**
> list[Trigger] list_triggers(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, all_in_filter=all_in_filter, available=available, blueprint=blueprint, bundle=bundle, description=description, documentation=documentation, enabled=enabled, endpoint=endpoint, errors=errors, filter_count=filter_count, key=key, merge_data_into_params=merge_data_into_params, meta=meta, name=name, profiles=profiles, queue_mode=queue_mode, read_only=read_only, store_data_in_parameter=store_data_in_parameter, trigger_provider=trigger_provider, valid=valid, work_order_params=work_order_params, work_order_profiles=work_order_profiles)

Lists Triggers filtered by some parameters.

This will show all Triggers by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Name = string Available = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
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
all_in_filter = 'all_in_filter_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
blueprint = 'blueprint_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
enabled = 'enabled_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
filter_count = 'filter_count_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
merge_data_into_params = 'merge_data_into_params_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
queue_mode = 'queue_mode_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
store_data_in_parameter = 'store_data_in_parameter_example'  # str |  (optional)
trigger_provider = 'trigger_provider_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order_params = 'work_order_params_example'  # str |  (optional)
work_order_profiles = 'work_order_profiles_example'  # str |  (optional)

try:
    # Lists Triggers filtered by some parameters.
    api_response = api_instance.list_triggers(offset=offset, limit=limit, aggregate=aggregate,
                                              exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                              group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                              slim=slim, sort=sort, all_in_filter=all_in_filter, available=available,
                                              blueprint=blueprint, bundle=bundle, description=description,
                                              documentation=documentation, enabled=enabled, endpoint=endpoint,
                                              errors=errors, filter_count=filter_count, key=key,
                                              merge_data_into_params=merge_data_into_params, meta=meta, name=name,
                                              profiles=profiles, queue_mode=queue_mode, read_only=read_only,
                                              store_data_in_parameter=store_data_in_parameter,
                                              trigger_provider=trigger_provider, valid=valid,
                                              work_order_params=work_order_params,
                                              work_order_profiles=work_order_profiles)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->list_triggers: %s\n" % e)
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
 **all_in_filter** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **blueprint** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **enabled** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **filter_count** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **merge_data_into_params** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **queue_mode** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **store_data_in_parameter** | **str**|  | [optional] 
 **trigger_provider** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order_params** | **str**|  | [optional] 
 **work_order_profiles** | **str**|  | [optional] 

### Return type

[**list[Trigger]**](Trigger.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_trigger**
> Trigger patch_trigger(body, name)

Patch a Trigger

Update a Trigger specified by {name} using a RFC6902 Patch structure

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
name = 'name_example'  # str | 

try:
    # Patch a Trigger
    api_response = api_instance.patch_trigger(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->patch_trigger: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **name** | **str**|  | 

### Return type

[**Trigger**](Trigger.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_trigger_params**
> dict(str, object) patch_trigger_params(name, body)



Update params for Trigger {name} with the passed-in patch

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
body = drppy_client.Patch()  # Patch | 

try:
    api_response = api_instance.patch_trigger_params(name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->patch_trigger_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **body** | [**Patch**](Patch.md)|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_trigger_action**
> object post_trigger_action(name, cmd, body, plugin=plugin)

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_trigger_action(name, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->post_trigger_action: %s\n" % e)
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

# **post_trigger_param**
> object post_trigger_param(body, name, key)



Set as single Parameter {key} for a trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
name = 'name_example'  # str | 
key = 'key_example'  # str | 

try:
    api_response = api_instance.post_trigger_param(body, name, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->post_trigger_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | 
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

# **post_trigger_params**
> dict(str, object) post_trigger_params(name, body)



Sets parameters for a trigger specified by {name}

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
body = NULL  # object | 

try:
    api_response = api_instance.post_trigger_params(name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->post_trigger_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **body** | **object**|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_trigger**
> Trigger put_trigger(body, name)

Put a Trigger

Update a Trigger specified by {name} using a JSON Trigger

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
api_instance = drppy_client.TriggersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Trigger()  # Trigger | 
name = 'name_example'  # str | 

try:
    # Put a Trigger
    api_response = api_instance.put_trigger(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TriggersApi->put_trigger: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Trigger**](Trigger.md)|  | 
 **name** | **str**|  | 

### Return type

[**Trigger**](Trigger.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

