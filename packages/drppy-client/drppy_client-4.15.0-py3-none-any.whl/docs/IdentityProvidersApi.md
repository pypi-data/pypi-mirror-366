# swagger_client.IdentityProvidersApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_identity_provider**](IdentityProvidersApi.md#create_identity_provider) | **POST** /identity_providers | Create a IdentityProvider
[**delete_identity_provider**](IdentityProvidersApi.md#delete_identity_provider) | **DELETE** /identity_providers/{name} | Delete a IdentityProvider
[**get_identity_provider**](IdentityProvidersApi.md#get_identity_provider) | **GET** /identity_providers/{name} | Get a IdentityProvider
[**get_identity_provider_action**](IdentityProvidersApi.md#get_identity_provider_action) | **GET** /identity_providers/{name}/actions/{cmd} | List specific action for a identity_provider IdentityProvider
[**get_identity_provider_actions**](IdentityProvidersApi.md#get_identity_provider_actions) | **GET** /identity_providers/{name}/actions | List identity_provider actions IdentityProvider
[**head_identity_provider**](IdentityProvidersApi.md#head_identity_provider) | **HEAD** /identity_providers/{name} | See if a IdentityProvider exists
[**list_identity_providers**](IdentityProvidersApi.md#list_identity_providers) | **GET** /identity_providers | Lists IdentityProviders filtered by some parameters.
[**list_stats_identity_providers**](IdentityProvidersApi.md#list_stats_identity_providers) | **HEAD** /identity_providers | Stats of the List IdentityProviders filtered by some parameters.
[**patch_identity_provider**](IdentityProvidersApi.md#patch_identity_provider) | **PATCH** /identity_providers/{name} | Patch a IdentityProvider
[**post_identity_provider_action**](IdentityProvidersApi.md#post_identity_provider_action) | **POST** /identity_providers/{name}/actions/{cmd} | Call an action on the node.
[**put_identity_provider**](IdentityProvidersApi.md#put_identity_provider) | **PUT** /identity_providers/{name} | Put a IdentityProvider


# **create_identity_provider**
> IdentityProvider create_identity_provider(body)

Create a IdentityProvider

Create a IdentityProvider from the provided object

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
body = drppy_client.IdentityProvider()  # IdentityProvider | 

try:
    # Create a IdentityProvider
    api_response = api_instance.create_identity_provider(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->create_identity_provider: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**IdentityProvider**](IdentityProvider.md)|  | 

### Return type

[**IdentityProvider**](IdentityProvider.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_identity_provider**
> IdentityProvider delete_identity_provider(name)

Delete a IdentityProvider

Delete a IdentityProvider specified by {name}

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Delete a IdentityProvider
    api_response = api_instance.delete_identity_provider(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->delete_identity_provider: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**IdentityProvider**](IdentityProvider.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_identity_provider**
> IdentityProvider get_identity_provider(name)

Get a IdentityProvider

Get the IdentityProvider specified by {name} or return NotFound.

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Get a IdentityProvider
    api_response = api_instance.get_identity_provider(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->get_identity_provider: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**IdentityProvider**](IdentityProvider.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_identity_provider_action**
> AvailableAction get_identity_provider_action(name, cmd, plugin=plugin)

List specific action for a identity_provider IdentityProvider

List specific {cmd} action for a IdentityProvider specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a identity_provider IdentityProvider
    api_response = api_instance.get_identity_provider_action(name, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->get_identity_provider_action: %s\n" % e)
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

# **get_identity_provider_actions**
> list[AvailableAction] get_identity_provider_actions(name, plugin=plugin)

List identity_provider actions IdentityProvider

List IdentityProvider actions for a IdentityProvider specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List identity_provider actions IdentityProvider
    api_response = api_instance.get_identity_provider_actions(name, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->get_identity_provider_actions: %s\n" % e)
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

# **head_identity_provider**
> head_identity_provider(name)

See if a IdentityProvider exists

Return 200 if the IdentityProvider specific by {name} exists, or return NotFound.

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # See if a IdentityProvider exists
    api_instance.head_identity_provider(name)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->head_identity_provider: %s\n" % e)
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

# **list_identity_providers**
> list[IdentityProvider] list_identity_providers(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, default_role=default_role, deny_if_no_groups=deny_if_no_groups, description=description, display_name=display_name, documentation=documentation, endpoint=endpoint, errors=errors, group_attribute=group_attribute, group_to_roles=group_to_roles, logo_path=logo_path, meta=meta, meta_data_blob=meta_data_blob, meta_data_url=meta_data_url, name=name, read_only=read_only, user_attribute=user_attribute, valid=valid)

Lists IdentityProviders filtered by some parameters.

This will show all IdentityProviders by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Name = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
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
default_role = 'default_role_example'  # str |  (optional)
deny_if_no_groups = 'deny_if_no_groups_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
display_name = 'display_name_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
group_attribute = 'group_attribute_example'  # str |  (optional)
group_to_roles = 'group_to_roles_example'  # str |  (optional)
logo_path = 'logo_path_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
meta_data_blob = 'meta_data_blob_example'  # str |  (optional)
meta_data_url = 'meta_data_url_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
user_attribute = 'user_attribute_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists IdentityProviders filtered by some parameters.
    api_response = api_instance.list_identity_providers(offset=offset, limit=limit, aggregate=aggregate,
                                                        exclude_self=exclude_self, filter=filter, raw=raw,
                                                        decode=decode, group_by=group_by, params=params,
                                                        range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                                        available=available, bundle=bundle, default_role=default_role,
                                                        deny_if_no_groups=deny_if_no_groups, description=description,
                                                        display_name=display_name, documentation=documentation,
                                                        endpoint=endpoint, errors=errors,
                                                        group_attribute=group_attribute, group_to_roles=group_to_roles,
                                                        logo_path=logo_path, meta=meta, meta_data_blob=meta_data_blob,
                                                        meta_data_url=meta_data_url, name=name, read_only=read_only,
                                                        user_attribute=user_attribute, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->list_identity_providers: %s\n" % e)
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
 **default_role** | **str**|  | [optional] 
 **deny_if_no_groups** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **display_name** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **group_attribute** | **str**|  | [optional] 
 **group_to_roles** | **str**|  | [optional] 
 **logo_path** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **meta_data_blob** | **str**|  | [optional] 
 **meta_data_url** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **user_attribute** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[IdentityProvider]**](IdentityProvider.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_identity_providers**
> list_stats_identity_providers(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, default_role=default_role, deny_if_no_groups=deny_if_no_groups, description=description, display_name=display_name, documentation=documentation, endpoint=endpoint, errors=errors, group_attribute=group_attribute, group_to_roles=group_to_roles, logo_path=logo_path, meta=meta, meta_data_blob=meta_data_blob, meta_data_url=meta_data_url, name=name, read_only=read_only, user_attribute=user_attribute, valid=valid)

Stats of the List IdentityProviders filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Name = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
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
default_role = 'default_role_example'  # str |  (optional)
deny_if_no_groups = 'deny_if_no_groups_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
display_name = 'display_name_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
group_attribute = 'group_attribute_example'  # str |  (optional)
group_to_roles = 'group_to_roles_example'  # str |  (optional)
logo_path = 'logo_path_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
meta_data_blob = 'meta_data_blob_example'  # str |  (optional)
meta_data_url = 'meta_data_url_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
user_attribute = 'user_attribute_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List IdentityProviders filtered by some parameters.
    api_instance.list_stats_identity_providers(offset=offset, limit=limit, aggregate=aggregate,
                                               exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                               group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                               slim=slim, sort=sort, available=available, bundle=bundle,
                                               default_role=default_role, deny_if_no_groups=deny_if_no_groups,
                                               description=description, display_name=display_name,
                                               documentation=documentation, endpoint=endpoint, errors=errors,
                                               group_attribute=group_attribute, group_to_roles=group_to_roles,
                                               logo_path=logo_path, meta=meta, meta_data_blob=meta_data_blob,
                                               meta_data_url=meta_data_url, name=name, read_only=read_only,
                                               user_attribute=user_attribute, valid=valid)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->list_stats_identity_providers: %s\n" % e)
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
 **default_role** | **str**|  | [optional] 
 **deny_if_no_groups** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **display_name** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **group_attribute** | **str**|  | [optional] 
 **group_to_roles** | **str**|  | [optional] 
 **logo_path** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **meta_data_blob** | **str**|  | [optional] 
 **meta_data_url** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **user_attribute** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_identity_provider**
> IdentityProvider patch_identity_provider(body, name)

Patch a IdentityProvider

Update a IdentityProvider specified by {name} using a RFC6902 Patch structure

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
name = 'name_example'  # str | 

try:
    # Patch a IdentityProvider
    api_response = api_instance.patch_identity_provider(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->patch_identity_provider: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **name** | **str**|  | 

### Return type

[**IdentityProvider**](IdentityProvider.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_identity_provider_action**
> object post_identity_provider_action(name, cmd, body, plugin=plugin)

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_identity_provider_action(name, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->post_identity_provider_action: %s\n" % e)
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

# **put_identity_provider**
> IdentityProvider put_identity_provider(body, name)

Put a IdentityProvider

Update a IdentityProvider specified by {name} using a JSON IdentityProvider

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
api_instance = drppy_client.IdentityProvidersApi(drppy_client.ApiClient(configuration))
body = drppy_client.IdentityProvider()  # IdentityProvider | 
name = 'name_example'  # str | 

try:
    # Put a IdentityProvider
    api_response = api_instance.put_identity_provider(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IdentityProvidersApi->put_identity_provider: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**IdentityProvider**](IdentityProvider.md)|  | 
 **name** | **str**|  | 

### Return type

[**IdentityProvider**](IdentityProvider.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

