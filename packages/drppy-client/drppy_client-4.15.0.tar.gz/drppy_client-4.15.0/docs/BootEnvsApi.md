# swagger_client.BootEnvsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_boot_env**](BootEnvsApi.md#create_boot_env) | **POST** /bootenvs | Create a BootEnv
[**delete_boot_env**](BootEnvsApi.md#delete_boot_env) | **DELETE** /bootenvs/{name} | Delete a BootEnv
[**get_boot_env**](BootEnvsApi.md#get_boot_env) | **GET** /bootenvs/{name} | Get a BootEnv
[**get_boot_env_action**](BootEnvsApi.md#get_boot_env_action) | **GET** /bootenvs/{name}/actions/{cmd} | List specific action for a bootenv BootEnv
[**get_boot_env_actions**](BootEnvsApi.md#get_boot_env_actions) | **GET** /bootenvs/{name}/actions | List bootenv actions BootEnv
[**head_boot_env**](BootEnvsApi.md#head_boot_env) | **HEAD** /bootenvs/{name} | See if a BootEnv exists
[**list_boot_envs**](BootEnvsApi.md#list_boot_envs) | **GET** /bootenvs | Lists BootEnvs filtered by some parameters.
[**list_stats_boot_envs**](BootEnvsApi.md#list_stats_boot_envs) | **HEAD** /bootenvs | Stats of the List BootEnvs filtered by some parameters.
[**patch_boot_env**](BootEnvsApi.md#patch_boot_env) | **PATCH** /bootenvs/{name} | Patch a BootEnv
[**post_boot_env_action**](BootEnvsApi.md#post_boot_env_action) | **POST** /bootenvs/{name}/actions/{cmd} | Call an action on the node.
[**purge_local_boot_env**](BootEnvsApi.md#purge_local_boot_env) | **DELETE** /bootenvs/{name}/purgeLocal | Purge local install files (ISOS and install trees) for a bootenv
[**put_boot_env**](BootEnvsApi.md#put_boot_env) | **PUT** /bootenvs/{name} | Put a BootEnv


# **create_boot_env**
> BootEnv create_boot_env(body)

Create a BootEnv

Create a BootEnv from the provided object

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
body = drppy_client.BootEnv()  # BootEnv | 

try:
    # Create a BootEnv
    api_response = api_instance.create_boot_env(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->create_boot_env: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BootEnv**](BootEnv.md)|  | 

### Return type

[**BootEnv**](BootEnv.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_boot_env**
> BootEnv delete_boot_env(name)

Delete a BootEnv

Delete a BootEnv specified by {name}

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Delete a BootEnv
    api_response = api_instance.delete_boot_env(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->delete_boot_env: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**BootEnv**](BootEnv.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_boot_env**
> BootEnv get_boot_env(name)

Get a BootEnv

Get the BootEnv specified by {name} or return NotFound.

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Get a BootEnv
    api_response = api_instance.get_boot_env(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->get_boot_env: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**BootEnv**](BootEnv.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_boot_env_action**
> AvailableAction get_boot_env_action(name, cmd, plugin=plugin)

List specific action for a bootenv BootEnv

List specific {cmd} action for a BootEnv specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a bootenv BootEnv
    api_response = api_instance.get_boot_env_action(name, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->get_boot_env_action: %s\n" % e)
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

# **get_boot_env_actions**
> list[AvailableAction] get_boot_env_actions(name, plugin=plugin)

List bootenv actions BootEnv

List BootEnv actions for a BootEnv specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List bootenv actions BootEnv
    api_response = api_instance.get_boot_env_actions(name, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->get_boot_env_actions: %s\n" % e)
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

# **head_boot_env**
> head_boot_env(name)

See if a BootEnv exists

Return 200 if the BootEnv specifiec by {name} exists, or return NotFound.

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # See if a BootEnv exists
    api_instance.head_boot_env(name)
except ApiException as e:
    print("Exception when calling BootEnvsApi->head_boot_env: %s\n" % e)
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

# **list_boot_envs**
> list[BootEnv] list_boot_envs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, boot_params=boot_params, bundle=bundle, description=description, documentation=documentation, end_delimiter=end_delimiter, endpoint=endpoint, errors=errors, initrds=initrds, kernel=kernel, key=key, loaders=loaders, meta=meta, name=name, only_unknown=only_unknown, optional_params=optional_params, os_name=os_name, read_only=read_only, required_params=required_params, start_delimiter=start_delimiter, templates=templates, valid=valid)

Lists BootEnvs filtered by some parameters.

This will show all BootEnvs by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Name = string Available = boolean Valid = boolean ReadOnly = boolean OnlyUnknown = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
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
boot_params = 'boot_params_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
end_delimiter = 'end_delimiter_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
initrds = 'initrds_example'  # str |  (optional)
kernel = 'kernel_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
loaders = 'loaders_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
only_unknown = 'only_unknown_example'  # str |  (optional)
optional_params = 'optional_params_example'  # str |  (optional)
os_name = 'os_name_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
required_params = 'required_params_example'  # str |  (optional)
start_delimiter = 'start_delimiter_example'  # str |  (optional)
templates = 'templates_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists BootEnvs filtered by some parameters.
    api_response = api_instance.list_boot_envs(offset=offset, limit=limit, aggregate=aggregate,
                                               exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                               group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                               slim=slim, sort=sort, available=available, boot_params=boot_params,
                                               bundle=bundle, description=description, documentation=documentation,
                                               end_delimiter=end_delimiter, endpoint=endpoint, errors=errors,
                                               initrds=initrds, kernel=kernel, key=key, loaders=loaders, meta=meta,
                                               name=name, only_unknown=only_unknown, optional_params=optional_params,
                                               os_name=os_name, read_only=read_only, required_params=required_params,
                                               start_delimiter=start_delimiter, templates=templates, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->list_boot_envs: %s\n" % e)
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
 **boot_params** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **end_delimiter** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **initrds** | **str**|  | [optional] 
 **kernel** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **loaders** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **only_unknown** | **str**|  | [optional] 
 **optional_params** | **str**|  | [optional] 
 **os_name** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **required_params** | **str**|  | [optional] 
 **start_delimiter** | **str**|  | [optional] 
 **templates** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[BootEnv]**](BootEnv.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_boot_envs**
> list_stats_boot_envs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, boot_params=boot_params, bundle=bundle, description=description, documentation=documentation, end_delimiter=end_delimiter, endpoint=endpoint, errors=errors, initrds=initrds, kernel=kernel, key=key, loaders=loaders, meta=meta, name=name, only_unknown=only_unknown, optional_params=optional_params, os_name=os_name, read_only=read_only, required_params=required_params, start_delimiter=start_delimiter, templates=templates, valid=valid)

Stats of the List BootEnvs filtered by some parameters.

This will return headers with the stats of the list.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Name = string Available = boolean Valid = boolean ReadOnly = boolean OnlyUnknown = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
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
boot_params = 'boot_params_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
end_delimiter = 'end_delimiter_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
initrds = 'initrds_example'  # str |  (optional)
kernel = 'kernel_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
loaders = 'loaders_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
only_unknown = 'only_unknown_example'  # str |  (optional)
optional_params = 'optional_params_example'  # str |  (optional)
os_name = 'os_name_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
required_params = 'required_params_example'  # str |  (optional)
start_delimiter = 'start_delimiter_example'  # str |  (optional)
templates = 'templates_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List BootEnvs filtered by some parameters.
    api_instance.list_stats_boot_envs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                      filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                      range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available,
                                      boot_params=boot_params, bundle=bundle, description=description,
                                      documentation=documentation, end_delimiter=end_delimiter, endpoint=endpoint,
                                      errors=errors, initrds=initrds, kernel=kernel, key=key, loaders=loaders,
                                      meta=meta, name=name, only_unknown=only_unknown, optional_params=optional_params,
                                      os_name=os_name, read_only=read_only, required_params=required_params,
                                      start_delimiter=start_delimiter, templates=templates, valid=valid)
except ApiException as e:
    print("Exception when calling BootEnvsApi->list_stats_boot_envs: %s\n" % e)
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
 **boot_params** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **end_delimiter** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **initrds** | **str**|  | [optional] 
 **kernel** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **loaders** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **only_unknown** | **str**|  | [optional] 
 **optional_params** | **str**|  | [optional] 
 **os_name** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **required_params** | **str**|  | [optional] 
 **start_delimiter** | **str**|  | [optional] 
 **templates** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_boot_env**
> BootEnv patch_boot_env(body, name)

Patch a BootEnv

Update a BootEnv specified by {name} using a RFC6902 Patch structure

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
name = 'name_example'  # str | 

try:
    # Patch a BootEnv
    api_response = api_instance.patch_boot_env(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->patch_boot_env: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **name** | **str**|  | 

### Return type

[**BootEnv**](BootEnv.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_boot_env_action**
> object post_boot_env_action(name, cmd, body, plugin=plugin)

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_boot_env_action(name, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->post_boot_env_action: %s\n" % e)
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

# **purge_local_boot_env**
> purge_local_boot_env(name, body, reexplode_isos=reexplode_isos)

Purge local install files (ISOS and install trees) for a bootenv

Purges ISO files and local install files for a bootenv on an arch by arch basis.

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
body = [drppy_client.list[str]()]  # list[str] | 
reexplode_isos = true  # bool |  (optional)

try:
    # Purge local install files (ISOS and install trees) for a bootenv
    api_instance.purge_local_boot_env(name, body, reexplode_isos=reexplode_isos)
except ApiException as e:
    print("Exception when calling BootEnvsApi->purge_local_boot_env: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **body** | **list[str]**|  | 
 **reexplode_isos** | **bool**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_boot_env**
> BootEnv put_boot_env(body, name)

Put a BootEnv

Update a BootEnv specified by {name} using a JSON BootEnv

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
api_instance = drppy_client.BootEnvsApi(drppy_client.ApiClient(configuration))
body = drppy_client.BootEnv()  # BootEnv | 
name = 'name_example'  # str | 

try:
    # Put a BootEnv
    api_response = api_instance.put_boot_env(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BootEnvsApi->put_boot_env: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BootEnv**](BootEnv.md)|  | 
 **name** | **str**|  | 

### Return type

[**BootEnv**](BootEnv.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

