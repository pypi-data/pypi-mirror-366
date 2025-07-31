# swagger_client.StagesApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_stage**](StagesApi.md#create_stage) | **POST** /stages | Create a Stage
[**delete_stage**](StagesApi.md#delete_stage) | **DELETE** /stages/{name} | Delete a Stage
[**delete_stage_param**](StagesApi.md#delete_stage_param) | **DELETE** /stages/{name}/params/{key} | Delete a single stage parameter
[**get_stage**](StagesApi.md#get_stage) | **GET** /stages/{name} | Get a Stage
[**get_stage_action**](StagesApi.md#get_stage_action) | **GET** /stages/{name}/actions/{cmd} | List specific action for a stage Stage
[**get_stage_actions**](StagesApi.md#get_stage_actions) | **GET** /stages/{name}/actions | List stage actions Stage
[**get_stage_param**](StagesApi.md#get_stage_param) | **GET** /stages/{name}/params/{key} | Get a single stage parameter
[**get_stage_params**](StagesApi.md#get_stage_params) | **GET** /stages/{name}/params | List stage params Stage
[**get_stage_pub_key**](StagesApi.md#get_stage_pub_key) | **GET** /stages/{name}/pubkey | Get the public key for secure params on a stage
[**head_stage**](StagesApi.md#head_stage) | **HEAD** /stages/{name} | See if a Stage exists
[**list_stages**](StagesApi.md#list_stages) | **GET** /stages | Lists Stages filtered by some parameters.
[**list_stats_stages**](StagesApi.md#list_stats_stages) | **HEAD** /stages | Stats of the List Stages filtered by some parameters.
[**patch_stage**](StagesApi.md#patch_stage) | **PATCH** /stages/{name} | Patch a Stage
[**patch_stage_params**](StagesApi.md#patch_stage_params) | **PATCH** /stages/{name}/params | 
[**post_stage_action**](StagesApi.md#post_stage_action) | **POST** /stages/{name}/actions/{cmd} | Call an action on the node.
[**post_stage_param**](StagesApi.md#post_stage_param) | **POST** /stages/{name}/params/{key} | 
[**post_stage_params**](StagesApi.md#post_stage_params) | **POST** /stages/{name}/params | 
[**put_stage**](StagesApi.md#put_stage) | **PUT** /stages/{name} | Put a Stage


# **create_stage**
> Stage create_stage(body)

Create a Stage

Create a Stage from the provided object

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Stage()  # Stage | 

try:
    # Create a Stage
    api_response = api_instance.create_stage(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->create_stage: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Stage**](Stage.md)|  | 

### Return type

[**Stage**](Stage.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_stage**
> Stage delete_stage(name)

Delete a Stage

Delete a Stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Delete a Stage
    api_response = api_instance.delete_stage(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->delete_stage: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**Stage**](Stage.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_stage_param**
> object delete_stage_param(name, key)

Delete a single stage parameter

Delete a single parameter {key} for a Stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
key = 'key_example'  # str | 

try:
    # Delete a single stage parameter
    api_response = api_instance.delete_stage_param(name, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->delete_stage_param: %s\n" % e)
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

# **get_stage**
> Stage get_stage(name, aggregate=aggregate, decode=decode, params=params)

Get a Stage

Get the Stage specified by {name} or return NotFound.

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get a Stage
    api_response = api_instance.get_stage(name, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->get_stage: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **aggregate** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Stage**](Stage.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stage_action**
> AvailableAction get_stage_action(name, cmd, plugin=plugin)

List specific action for a stage Stage

List specific {cmd} action for a Stage specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a stage Stage
    api_response = api_instance.get_stage_action(name, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->get_stage_action: %s\n" % e)
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

# **get_stage_actions**
> list[AvailableAction] get_stage_actions(name, plugin=plugin)

List stage actions Stage

List Stage actions for a Stage specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List stage actions Stage
    api_response = api_instance.get_stage_actions(name, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->get_stage_actions: %s\n" % e)
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

# **get_stage_param**
> object get_stage_param(name, key, aggregate=aggregate, decode=decode)

Get a single stage parameter

Get a single parameter {key} for a Stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
key = 'key_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)

try:
    # Get a single stage parameter
    api_response = api_instance.get_stage_param(name, key, aggregate=aggregate, decode=decode)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->get_stage_param: %s\n" % e)
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

# **get_stage_params**
> dict(str, object) get_stage_params(name, aggregate=aggregate, decode=decode, params=params)

List stage params Stage

List Stage parms for a Stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # List stage params Stage
    api_response = api_instance.get_stage_params(name, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->get_stage_params: %s\n" % e)
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

# **get_stage_pub_key**
> get_stage_pub_key(name)

Get the public key for secure params on a stage

Get the public key for a Stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Get the public key for secure params on a stage
    api_instance.get_stage_pub_key(name)
except ApiException as e:
    print("Exception when calling StagesApi->get_stage_pub_key: %s\n" % e)
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

# **head_stage**
> head_stage(name)

See if a Stage exists

Return 200 if the Stage specifiec by {name} exists, or return NotFound.

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # See if a Stage exists
    api_instance.head_stage(name)
except ApiException as e:
    print("Exception when calling StagesApi->head_stage: %s\n" % e)
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

# **list_stages**
> list[Stage] list_stages(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, valid=valid, read_only=read_only, name=name, reboot=reboot, boot_env=boot_env)

Lists Stages filtered by some parameters.

This will show all Stages by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Name = string Reboot = boolean BootEnv = string Available = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
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
valid = 'valid_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
reboot = 'reboot_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)

try:
    # Lists Stages filtered by some parameters.
    api_response = api_instance.list_stages(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                            filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                            range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                            available=available, valid=valid, read_only=read_only, name=name,
                                            reboot=reboot, boot_env=boot_env)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->list_stages: %s\n" % e)
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
 **valid** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **reboot** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 

### Return type

[**list[Stage]**](Stage.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_stages**
> list_stats_stages(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, valid=valid, read_only=read_only, name=name, reboot=reboot, boot_env=boot_env)

Stats of the List Stages filtered by some parameters.

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
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
valid = 'valid_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
reboot = 'reboot_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)

try:
    # Stats of the List Stages filtered by some parameters.
    api_instance.list_stats_stages(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                   filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                   range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available,
                                   valid=valid, read_only=read_only, name=name, reboot=reboot, boot_env=boot_env)
except ApiException as e:
    print("Exception when calling StagesApi->list_stats_stages: %s\n" % e)
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
 **valid** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **reboot** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_stage**
> Stage patch_stage(body, name)

Patch a Stage

Update a Stage specified by {name} using a RFC6902 Patch structure

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
name = 'name_example'  # str | 

try:
    # Patch a Stage
    api_response = api_instance.patch_stage(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->patch_stage: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **name** | **str**|  | 

### Return type

[**Stage**](Stage.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_stage_params**
> dict(str, object) patch_stage_params(name, body)



Update params for Stage {name} with the passed-in patch

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
body = drppy_client.Patch()  # Patch | 

try:
    api_response = api_instance.patch_stage_params(name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->patch_stage_params: %s\n" % e)
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

# **post_stage_action**
> object post_stage_action(name, cmd, body, plugin=plugin)

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_stage_action(name, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->post_stage_action: %s\n" % e)
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

# **post_stage_param**
> object post_stage_param(body, name, key)



Set as single Parameter {key} for a stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
name = 'name_example'  # str | 
key = 'key_example'  # str | 

try:
    api_response = api_instance.post_stage_param(body, name, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->post_stage_param: %s\n" % e)
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

# **post_stage_params**
> dict(str, object) post_stage_params(name, body)



Sets parameters for a stage specified by {name}

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
body = NULL  # object | 

try:
    api_response = api_instance.post_stage_params(name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->post_stage_params: %s\n" % e)
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

# **put_stage**
> Stage put_stage(body, name)

Put a Stage

Update a Stage specified by {name} using a JSON Stage

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
api_instance = drppy_client.StagesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Stage()  # Stage | 
name = 'name_example'  # str | 

try:
    # Put a Stage
    api_response = api_instance.put_stage(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StagesApi->put_stage: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Stage**](Stage.md)|  | 
 **name** | **str**|  | 

### Return type

[**Stage**](Stage.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

