# swagger_client.UxViewsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_ux_view**](UxViewsApi.md#create_ux_view) | **POST** /ux_views | Create a UxView
[**delete_ux_view**](UxViewsApi.md#delete_ux_view) | **DELETE** /ux_views/{id} | Delete a UxView
[**get_ux_view**](UxViewsApi.md#get_ux_view) | **GET** /ux_views/{id} | Get a UxView
[**get_ux_view_action**](UxViewsApi.md#get_ux_view_action) | **GET** /ux_views/{id}/actions/{cmd} | List specific action for a task UxView
[**get_ux_view_actions**](UxViewsApi.md#get_ux_view_actions) | **GET** /ux_views/{id}/actions | List task actions UxView
[**head_ux_view**](UxViewsApi.md#head_ux_view) | **HEAD** /ux_views/{id} | See if a UxView exists
[**list_stats_ux_views**](UxViewsApi.md#list_stats_ux_views) | **HEAD** /ux_views | Stats of the List UxViews filtered by some parameters.
[**list_ux_views**](UxViewsApi.md#list_ux_views) | **GET** /ux_views | Lists UxViews filtered by some parameters.
[**patch_ux_view**](UxViewsApi.md#patch_ux_view) | **PATCH** /ux_views/{id} | Patch a UxView
[**post_ux_view_action**](UxViewsApi.md#post_ux_view_action) | **POST** /ux_views/{id}/actions/{cmd} | Call an action on the node.
[**put_ux_view**](UxViewsApi.md#put_ux_view) | **PUT** /ux_views/{id} | Put a UxView


# **create_ux_view**
> UxView create_ux_view(body)

Create a UxView

Create a UxView from the provided object

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
body = drppy_client.UxView()  # UxView | 

try:
    # Create a UxView
    api_response = api_instance.create_ux_view(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->create_ux_view: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UxView**](UxView.md)|  | 

### Return type

[**UxView**](UxView.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_ux_view**
> UxView delete_ux_view(id)

Delete a UxView

Delete a UxView specified by {id}

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # Delete a UxView
    api_response = api_instance.delete_ux_view(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->delete_ux_view: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**UxView**](UxView.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ux_view**
> UxView get_ux_view(id)

Get a UxView

Get the UxView specified by {id} or return NotFound.

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # Get a UxView
    api_response = api_instance.get_ux_view(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->get_ux_view: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**UxView**](UxView.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ux_view_action**
> AvailableAction get_ux_view_action(id, cmd, plugin=plugin)

List specific action for a task UxView

List specific {cmd} action for a UxView specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a task UxView
    api_response = api_instance.get_ux_view_action(id, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->get_ux_view_action: %s\n" % e)
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

# **get_ux_view_actions**
> list[AvailableAction] get_ux_view_actions(id, plugin=plugin)

List task actions UxView

List UxView actions for a UxView specified by {id}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List task actions UxView
    api_response = api_instance.get_ux_view_actions(id, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->get_ux_view_actions: %s\n" % e)
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

# **head_ux_view**
> head_ux_view(id)

See if a UxView exists

Return 200 if the UxView specifiec by {id} exists, or return NotFound.

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # See if a UxView exists
    api_instance.head_ux_view(id)
except ApiException as e:
    print("Exception when calling UxViewsApi->head_ux_view: %s\n" % e)
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

# **list_stats_ux_views**
> list_stats_ux_views(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, airgap=airgap, applicable_roles=applicable_roles, available=available, branding_image=branding_image, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, id=id, key=key, landing_page=landing_page, menu=menu, meta=meta, read_only=read_only, show_activiation=show_activiation, valid=valid)

Stats of the List UxViews filtered by some parameters.

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
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
airgap = 'airgap_example'  # str |  (optional)
applicable_roles = 'applicable_roles_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
branding_image = 'branding_image_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
landing_page = 'landing_page_example'  # str |  (optional)
menu = 'menu_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
show_activiation = 'show_activiation_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List UxViews filtered by some parameters.
    api_instance.list_stats_ux_views(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                     filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                     range_only=range_only, reverse=reverse, slim=slim, sort=sort, airgap=airgap,
                                     applicable_roles=applicable_roles, available=available,
                                     branding_image=branding_image, bundle=bundle, description=description,
                                     documentation=documentation, endpoint=endpoint, errors=errors, id=id, key=key,
                                     landing_page=landing_page, menu=menu, meta=meta, read_only=read_only,
                                     show_activiation=show_activiation, valid=valid)
except ApiException as e:
    print("Exception when calling UxViewsApi->list_stats_ux_views: %s\n" % e)
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
 **airgap** | **str**|  | [optional] 
 **applicable_roles** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **branding_image** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **landing_page** | **str**|  | [optional] 
 **menu** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **show_activiation** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_ux_views**
> list[UxView] list_ux_views(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, airgap=airgap, applicable_roles=applicable_roles, available=available, branding_image=branding_image, bundle=bundle, description=description, documentation=documentation, endpoint=endpoint, errors=errors, id=id, key=key, landing_page=landing_page, menu=menu, meta=meta, read_only=read_only, show_activiation=show_activiation, valid=valid)

Lists UxViews filtered by some parameters.

This will show all UxViews by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: ID = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred. ID=Lt(fred)&Available=true - returns items with ID less than fred and Available is true

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
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
airgap = 'airgap_example'  # str |  (optional)
applicable_roles = 'applicable_roles_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
branding_image = 'branding_image_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
landing_page = 'landing_page_example'  # str |  (optional)
menu = 'menu_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
show_activiation = 'show_activiation_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists UxViews filtered by some parameters.
    api_response = api_instance.list_ux_views(offset=offset, limit=limit, aggregate=aggregate,
                                              exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                              group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                              slim=slim, sort=sort, airgap=airgap, applicable_roles=applicable_roles,
                                              available=available, branding_image=branding_image, bundle=bundle,
                                              description=description, documentation=documentation, endpoint=endpoint,
                                              errors=errors, id=id, key=key, landing_page=landing_page, menu=menu,
                                              meta=meta, read_only=read_only, show_activiation=show_activiation,
                                              valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->list_ux_views: %s\n" % e)
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
 **airgap** | **str**|  | [optional] 
 **applicable_roles** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **branding_image** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **landing_page** | **str**|  | [optional] 
 **menu** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **show_activiation** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[UxView]**](UxView.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_ux_view**
> UxView patch_ux_view(body, id)

Patch a UxView

Update a UxView specified by {id} using a RFC6902 Patch structure

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
id = 'id_example'  # str | 

try:
    # Patch a UxView
    api_response = api_instance.patch_ux_view(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->patch_ux_view: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **id** | **str**|  | 

### Return type

[**UxView**](UxView.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_ux_view_action**
> object post_ux_view_action(id, cmd, body, plugin=plugin)

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_ux_view_action(id, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->post_ux_view_action: %s\n" % e)
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

# **put_ux_view**
> UxView put_ux_view(body, id)

Put a UxView

Update a UxView specified by {id} using a JSON UxView

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
api_instance = drppy_client.UxViewsApi(drppy_client.ApiClient(configuration))
body = drppy_client.UxView()  # UxView | 
id = 'id_example'  # str | 

try:
    # Put a UxView
    api_response = api_instance.put_ux_view(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UxViewsApi->put_ux_view: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UxView**](UxView.md)|  | 
 **id** | **str**|  | 

### Return type

[**UxView**](UxView.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

