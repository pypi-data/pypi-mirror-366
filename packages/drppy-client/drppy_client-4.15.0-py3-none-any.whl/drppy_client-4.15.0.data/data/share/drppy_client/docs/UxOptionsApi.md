# swagger_client.UxOptionsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_ux_option**](UxOptionsApi.md#create_ux_option) | **POST** /ux_options | Create a UxOption
[**delete_ux_option**](UxOptionsApi.md#delete_ux_option) | **DELETE** /ux_options/{id} | Delete a UxOption
[**get_ux_option**](UxOptionsApi.md#get_ux_option) | **GET** /ux_options/{id} | Get a UxOption
[**get_ux_option_action**](UxOptionsApi.md#get_ux_option_action) | **GET** /ux_options/{id}/actions/{cmd} | List specific action for a task UxOption
[**get_ux_option_actions**](UxOptionsApi.md#get_ux_option_actions) | **GET** /ux_options/{id}/actions | List task actions UxOption
[**head_ux_option**](UxOptionsApi.md#head_ux_option) | **HEAD** /ux_options/{id} | See if a UxOption exists
[**list_stats_ux_options**](UxOptionsApi.md#list_stats_ux_options) | **HEAD** /ux_options | Stats of the List UxOptions filtered by some parameters.
[**list_ux_options**](UxOptionsApi.md#list_ux_options) | **GET** /ux_options | Lists UxOptions filtered by some parameters.
[**patch_ux_option**](UxOptionsApi.md#patch_ux_option) | **PATCH** /ux_options/{id} | Patch a UxOption
[**post_ux_option_action**](UxOptionsApi.md#post_ux_option_action) | **POST** /ux_options/{id}/actions/{cmd} | Call an action on the node.
[**put_ux_option**](UxOptionsApi.md#put_ux_option) | **PUT** /ux_options/{id} | Put a UxOption


# **create_ux_option**
> UxOption create_ux_option(body)

Create a UxOption

Create a UxOption from the provided object

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
body = drppy_client.UxOption()  # UxOption | 

try:
    # Create a UxOption
    api_response = api_instance.create_ux_option(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->create_ux_option: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UxOption**](UxOption.md)|  | 

### Return type

[**UxOption**](UxOption.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_ux_option**
> UxOption delete_ux_option(id)

Delete a UxOption

Delete a UxOption specified by {id}

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # Delete a UxOption
    api_response = api_instance.delete_ux_option(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->delete_ux_option: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**UxOption**](UxOption.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ux_option**
> UxOption get_ux_option(id)

Get a UxOption

Get the UxOption specified by {id} or return NotFound.

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # Get a UxOption
    api_response = api_instance.get_ux_option(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->get_ux_option: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**UxOption**](UxOption.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ux_option_action**
> AvailableAction get_ux_option_action(id, cmd, plugin=plugin)

List specific action for a task UxOption

List specific {cmd} action for a UxOption specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a task UxOption
    api_response = api_instance.get_ux_option_action(id, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->get_ux_option_action: %s\n" % e)
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

# **get_ux_option_actions**
> list[AvailableAction] get_ux_option_actions(id, plugin=plugin)

List task actions UxOption

List UxOption actions for a UxOption specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List task actions UxOption
    api_response = api_instance.get_ux_option_actions(id, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->get_ux_option_actions: %s\n" % e)
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

# **head_ux_option**
> head_ux_option(id)

See if a UxOption exists

Return 200 if the UxOption specifiec by {id} exists, or return NotFound.

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # See if a UxOption exists
    api_instance.head_ux_option(id)
except ApiException as e:
    print("Exception when calling UxOptionsApi->head_ux_option: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_ux_options**
> list_stats_ux_options(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, default=default, description=description, documentation=documentation, endpoint=endpoint, errors=errors, _global=_global, hidden=hidden, id=id, key=key, kind=kind, meta=meta, read_only=read_only, role=role, user=user, valid=valid)

Stats of the List UxOptions filtered by some parameters.

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
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
default = 'default_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
_global = '_global_example'  # str |  (optional)
hidden = 'hidden_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
kind = 'kind_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
role = 'role_example'  # str |  (optional)
user = 'user_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List UxOptions filtered by some parameters.
    api_instance.list_stats_ux_options(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                       filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                       range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                       available=available, bundle=bundle, default=default, description=description,
                                       documentation=documentation, endpoint=endpoint, errors=errors, _global=_global,
                                       hidden=hidden, id=id, key=key, kind=kind, meta=meta, read_only=read_only,
                                       role=role, user=user, valid=valid)
except ApiException as e:
    print("Exception when calling UxOptionsApi->list_stats_ux_options: %s\n" % e)
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
 **default** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **_global** | **str**|  | [optional] 
 **hidden** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **kind** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **role** | **str**|  | [optional] 
 **user** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_ux_options**
> list[UxOption] list_ux_options(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, default=default, description=description, documentation=documentation, endpoint=endpoint, errors=errors, _global=_global, hidden=hidden, id=id, key=key, kind=kind, meta=meta, read_only=read_only, role=role, user=user, valid=valid)

Lists UxOptions filtered by some parameters.

This will show all UxOptions by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: ID = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred. ID=Lt(fred)&Available=true - returns items with ID less than fred and Available is true

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
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
default = 'default_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
_global = '_global_example'  # str |  (optional)
hidden = 'hidden_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
kind = 'kind_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
role = 'role_example'  # str |  (optional)
user = 'user_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists UxOptions filtered by some parameters.
    api_response = api_instance.list_ux_options(offset=offset, limit=limit, aggregate=aggregate,
                                                exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                                group_by=group_by, params=params, range_only=range_only,
                                                reverse=reverse, slim=slim, sort=sort, available=available,
                                                bundle=bundle, default=default, description=description,
                                                documentation=documentation, endpoint=endpoint, errors=errors,
                                                _global=_global, hidden=hidden, id=id, key=key, kind=kind, meta=meta,
                                                read_only=read_only, role=role, user=user, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->list_ux_options: %s\n" % e)
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
 **default** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **_global** | **str**|  | [optional] 
 **hidden** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **kind** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **role** | **str**|  | [optional] 
 **user** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[UxOption]**](UxOption.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_ux_option**
> UxOption patch_ux_option(body, id)

Patch a UxOption

Update a UxOption specified by {id} using a RFC6902 Patch structure

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
id = 'id_example'  # str | 

try:
    # Patch a UxOption
    api_response = api_instance.patch_ux_option(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->patch_ux_option: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **id** | **str**|  | 

### Return type

[**UxOption**](UxOption.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_ux_option_action**
> object post_ux_option_action(id, cmd, body, plugin=plugin)

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_ux_option_action(id, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->post_ux_option_action: %s\n" % e)
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

# **put_ux_option**
> UxOption put_ux_option(body, id)

Put a UxOption

Update a UxOption specified by {id} using a JSON UxOption

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
api_instance = drppy_client.UxOptionsApi(drppy_client.ApiClient(configuration))
body = drppy_client.UxOption()  # UxOption | 
id = 'id_example'  # str | 

try:
    # Put a UxOption
    api_response = api_instance.put_ux_option(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxOptionsApi->put_ux_option: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UxOption**](UxOption.md)|  | 
 **id** | **str**|  | 

### Return type

[**UxOption**](UxOption.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

