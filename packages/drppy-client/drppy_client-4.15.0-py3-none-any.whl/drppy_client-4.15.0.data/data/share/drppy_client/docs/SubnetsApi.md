# swagger_client.SubnetsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_subnet**](SubnetsApi.md#create_subnet) | **POST** /subnets | Create a Subnet
[**delete_subnet**](SubnetsApi.md#delete_subnet) | **DELETE** /subnets/{name} | Delete a Subnet
[**get_subnet**](SubnetsApi.md#get_subnet) | **GET** /subnets/{name} | Get a Subnet
[**get_subnet_action**](SubnetsApi.md#get_subnet_action) | **GET** /subnets/{name}/actions/{cmd} | List specific action for a subnet Subnet
[**get_subnet_actions**](SubnetsApi.md#get_subnet_actions) | **GET** /subnets/{name}/actions | List subnet actions Subnet
[**head_subnet**](SubnetsApi.md#head_subnet) | **HEAD** /subnets/{name} | See if a Subnet exists
[**list_stats_subnets**](SubnetsApi.md#list_stats_subnets) | **HEAD** /subnets | Stats of the List Subnets filtered by some parameters.
[**list_subnets**](SubnetsApi.md#list_subnets) | **GET** /subnets | Lists Subnets filtered by some parameters.
[**patch_subnet**](SubnetsApi.md#patch_subnet) | **PATCH** /subnets/{name} | Patch a Subnet
[**post_subnet_action**](SubnetsApi.md#post_subnet_action) | **POST** /subnets/{name}/actions/{cmd} | Call an action on the node.
[**put_subnet**](SubnetsApi.md#put_subnet) | **PUT** /subnets/{name} | Put a Subnet


# **create_subnet**
> Subnet create_subnet(body)

Create a Subnet

Create a Subnet from the provided object

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Subnet()  # Subnet | 

try:
    # Create a Subnet
    api_response = api_instance.create_subnet(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->create_subnet: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Subnet**](Subnet.md)|  | 

### Return type

[**Subnet**](Subnet.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_subnet**
> Subnet delete_subnet(name)

Delete a Subnet

Delete a Subnet specified by {name}

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Delete a Subnet
    api_response = api_instance.delete_subnet(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->delete_subnet: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**Subnet**](Subnet.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_subnet**
> Subnet get_subnet(name)

Get a Subnet

Get the Subnet specified by {name} or return NotFound.

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # Get a Subnet
    api_response = api_instance.get_subnet(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->get_subnet: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**Subnet**](Subnet.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_subnet_action**
> AvailableAction get_subnet_action(name, cmd, plugin=plugin)

List specific action for a subnet Subnet

List specific {cmd} action for a Subnet specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a subnet Subnet
    api_response = api_instance.get_subnet_action(name, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->get_subnet_action: %s\n" % e)
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

# **get_subnet_actions**
> list[AvailableAction] get_subnet_actions(name, plugin=plugin)

List subnet actions Subnet

List Subnet actions for a Subnet specified by {name}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List subnet actions Subnet
    api_response = api_instance.get_subnet_actions(name, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->get_subnet_actions: %s\n" % e)
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

# **head_subnet**
> head_subnet(name)

See if a Subnet exists

Return 200 if the Subnet specifiec by {name} exists, or return NotFound.

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 

try:
    # See if a Subnet exists
    api_instance.head_subnet(name)
except ApiException as e:
    print("Exception when calling SubnetsApi->head_subnet: %s\n" % e)
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

# **list_stats_subnets**
> list_stats_subnets(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, active_address=active_address, active_end=active_end, active_lease_time=active_lease_time, active_start=active_start, address=address, available=available, bundle=bundle, description=description, documentation=documentation, enabled=enabled, endpoint=endpoint, errors=errors, key=key, meta=meta, name=name, next_server=next_server, only_reservations=only_reservations, options=options, pickers=pickers, proxy=proxy, read_only=read_only, reserved_lease_time=reserved_lease_time, strategy=strategy, subnet=subnet, unmanaged=unmanaged, valid=valid)

Stats of the List Subnets filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Name = string NextServer = IP Address Subnet = CIDR Address Strategy = string Available = boolean Valid = boolean ReadOnly = boolean Enabled = boolean Proxy = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
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
active_address = 'active_address_example'  # str |  (optional)
active_end = 'active_end_example'  # str |  (optional)
active_lease_time = 'active_lease_time_example'  # str |  (optional)
active_start = 'active_start_example'  # str |  (optional)
address = 'address_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
enabled = 'enabled_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
next_server = 'next_server_example'  # str |  (optional)
only_reservations = 'only_reservations_example'  # str |  (optional)
options = 'options_example'  # str |  (optional)
pickers = 'pickers_example'  # str |  (optional)
proxy = 'proxy_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
reserved_lease_time = 'reserved_lease_time_example'  # str |  (optional)
strategy = 'strategy_example'  # str |  (optional)
subnet = 'subnet_example'  # str |  (optional)
unmanaged = 'unmanaged_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List Subnets filtered by some parameters.
    api_instance.list_stats_subnets(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                    filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                    range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                    active_address=active_address, active_end=active_end,
                                    active_lease_time=active_lease_time, active_start=active_start, address=address,
                                    available=available, bundle=bundle, description=description,
                                    documentation=documentation, enabled=enabled, endpoint=endpoint, errors=errors,
                                    key=key, meta=meta, name=name, next_server=next_server,
                                    only_reservations=only_reservations, options=options, pickers=pickers, proxy=proxy,
                                    read_only=read_only, reserved_lease_time=reserved_lease_time, strategy=strategy,
                                    subnet=subnet, unmanaged=unmanaged, valid=valid)
except ApiException as e:
    print("Exception when calling SubnetsApi->list_stats_subnets: %s\n" % e)
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
 **active_address** | **str**|  | [optional] 
 **active_end** | **str**|  | [optional] 
 **active_lease_time** | **str**|  | [optional] 
 **active_start** | **str**|  | [optional] 
 **address** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **enabled** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **next_server** | **str**|  | [optional] 
 **only_reservations** | **str**|  | [optional] 
 **options** | **str**|  | [optional] 
 **pickers** | **str**|  | [optional] 
 **proxy** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **reserved_lease_time** | **str**|  | [optional] 
 **strategy** | **str**|  | [optional] 
 **subnet** | **str**|  | [optional] 
 **unmanaged** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_subnets**
> list[Subnet] list_subnets(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, active_address=active_address, active_end=active_end, active_lease_time=active_lease_time, active_start=active_start, address=address, available=available, bundle=bundle, description=description, documentation=documentation, enabled=enabled, endpoint=endpoint, errors=errors, key=key, meta=meta, name=name, next_server=next_server, only_reservations=only_reservations, options=options, pickers=pickers, proxy=proxy, read_only=read_only, reserved_lease_time=reserved_lease_time, strategy=strategy, subnet=subnet, unmanaged=unmanaged, valid=valid)

Lists Subnets filtered by some parameters.

This will show all Subnets by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Name = string NextServer = IP Address Subnet = CIDR Address Strategy = string Available = boolean Valid = boolean ReadOnly = boolean Enabled = boolean Proxy = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
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
active_address = 'active_address_example'  # str |  (optional)
active_end = 'active_end_example'  # str |  (optional)
active_lease_time = 'active_lease_time_example'  # str |  (optional)
active_start = 'active_start_example'  # str |  (optional)
address = 'address_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
enabled = 'enabled_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
next_server = 'next_server_example'  # str |  (optional)
only_reservations = 'only_reservations_example'  # str |  (optional)
options = 'options_example'  # str |  (optional)
pickers = 'pickers_example'  # str |  (optional)
proxy = 'proxy_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
reserved_lease_time = 'reserved_lease_time_example'  # str |  (optional)
strategy = 'strategy_example'  # str |  (optional)
subnet = 'subnet_example'  # str |  (optional)
unmanaged = 'unmanaged_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists Subnets filtered by some parameters.
    api_response = api_instance.list_subnets(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                             filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                             range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                             active_address=active_address, active_end=active_end,
                                             active_lease_time=active_lease_time, active_start=active_start,
                                             address=address, available=available, bundle=bundle,
                                             description=description, documentation=documentation, enabled=enabled,
                                             endpoint=endpoint, errors=errors, key=key, meta=meta, name=name,
                                             next_server=next_server, only_reservations=only_reservations,
                                             options=options, pickers=pickers, proxy=proxy, read_only=read_only,
                                             reserved_lease_time=reserved_lease_time, strategy=strategy, subnet=subnet,
                                             unmanaged=unmanaged, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->list_subnets: %s\n" % e)
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
 **active_address** | **str**|  | [optional] 
 **active_end** | **str**|  | [optional] 
 **active_lease_time** | **str**|  | [optional] 
 **active_start** | **str**|  | [optional] 
 **address** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **enabled** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **next_server** | **str**|  | [optional] 
 **only_reservations** | **str**|  | [optional] 
 **options** | **str**|  | [optional] 
 **pickers** | **str**|  | [optional] 
 **proxy** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **reserved_lease_time** | **str**|  | [optional] 
 **strategy** | **str**|  | [optional] 
 **subnet** | **str**|  | [optional] 
 **unmanaged** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[Subnet]**](Subnet.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_subnet**
> Subnet patch_subnet(body, name)

Patch a Subnet

Update a Subnet specified by {name} using a RFC6902 Patch structure

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
name = 'name_example'  # str | 

try:
    # Patch a Subnet
    api_response = api_instance.patch_subnet(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->patch_subnet: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **name** | **str**|  | 

### Return type

[**Subnet**](Subnet.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_subnet_action**
> object post_subnet_action(name, cmd, body, plugin=plugin)

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
name = 'name_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_subnet_action(name, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->post_subnet_action: %s\n" % e)
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

# **put_subnet**
> Subnet put_subnet(body, name)

Put a Subnet

Update a Subnet specified by {name} using a JSON Subnet

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
api_instance = drppy_client.SubnetsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Subnet()  # Subnet | 
name = 'name_example'  # str | 

try:
    # Put a Subnet
    api_response = api_instance.put_subnet(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SubnetsApi->put_subnet: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Subnet**](Subnet.md)|  | 
 **name** | **str**|  | 

### Return type

[**Subnet**](Subnet.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

