# swagger_client.LeasesApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_lease**](LeasesApi.md#delete_lease) | **DELETE** /leases/{address} | Delete a Lease
[**get_lease**](LeasesApi.md#get_lease) | **GET** /leases/{address} | Get a Lease
[**get_lease_action**](LeasesApi.md#get_lease_action) | **GET** /leases/{address}/actions/{cmd} | List specific action for a lease Lease
[**get_lease_actions**](LeasesApi.md#get_lease_actions) | **GET** /leases/{address}/actions | List lease actions Lease
[**head_lease**](LeasesApi.md#head_lease) | **HEAD** /leases/{address} | See if a Lease exists
[**list_leases**](LeasesApi.md#list_leases) | **GET** /leases | Lists Leases filtered by some parameters.
[**list_stats_leases**](LeasesApi.md#list_stats_leases) | **HEAD** /leases | Stats of the List Leases filtered by some parameters.
[**post_lease_action**](LeasesApi.md#post_lease_action) | **POST** /leases/{address}/actions/{cmd} | Call an action on the node.


# **delete_lease**
> Lease delete_lease(address)

Delete a Lease

Delete a Lease specified by {address}

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 

try:
    # Delete a Lease
    api_response = api_instance.delete_lease(address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LeasesApi->delete_lease: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 

### Return type

[**Lease**](Lease.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_lease**
> Lease get_lease(address)

Get a Lease

Get the Lease specified by {address} or return NotFound.

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 

try:
    # Get a Lease
    api_response = api_instance.get_lease(address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LeasesApi->get_lease: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 

### Return type

[**Lease**](Lease.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_lease_action**
> AvailableAction get_lease_action(address, cmd, plugin=plugin)

List specific action for a lease Lease

List specific {cmd} action for a Lease specified by {address}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a lease Lease
    api_response = api_instance.get_lease_action(address, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LeasesApi->get_lease_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 
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

# **get_lease_actions**
> list[AvailableAction] get_lease_actions(address, plugin=plugin)

List lease actions Lease

List Lease actions for a Lease specified by {address}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List lease actions Lease
    api_response = api_instance.get_lease_actions(address, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LeasesApi->get_lease_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 
 **plugin** | **str**|  | [optional] 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_lease**
> head_lease(address)

See if a Lease exists

Return 200 if the Lease specifiec by {address} exists, or return NotFound.

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 

try:
    # See if a Lease exists
    api_instance.head_lease(address)
except ApiException as e:
    print("Exception when calling LeasesApi->head_lease: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_leases**
> list[Lease] list_leases(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr, available=available, bundle=bundle, duration=duration, endpoint=endpoint, errors=errors, expire_time=expire_time, key=key, meta=meta, next_server=next_server, options=options, provided_options=provided_options, read_only=read_only, skip_boot=skip_boot, state=state, strategy=strategy, token=token, valid=valid, via=via)

Lists Leases filtered by some parameters.

This will show all Leases by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Addr = IP Address Token = string Strategy = string ExpireTime = Date/Time Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
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
addr = 'addr_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
duration = 'duration_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
expire_time = 'expire_time_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
next_server = 'next_server_example'  # str |  (optional)
options = 'options_example'  # str |  (optional)
provided_options = 'provided_options_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
skip_boot = 'skip_boot_example'  # str |  (optional)
state = 'state_example'  # str |  (optional)
strategy = 'strategy_example'  # str |  (optional)
token = 'token_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
via = 'via_example'  # str |  (optional)

try:
    # Lists Leases filtered by some parameters.
    api_response = api_instance.list_leases(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                            filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                            range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr,
                                            available=available, bundle=bundle, duration=duration, endpoint=endpoint,
                                            errors=errors, expire_time=expire_time, key=key, meta=meta,
                                            next_server=next_server, options=options, provided_options=provided_options,
                                            read_only=read_only, skip_boot=skip_boot, state=state, strategy=strategy,
                                            token=token, valid=valid, via=via)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LeasesApi->list_leases: %s\n" % e)
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
 **addr** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **duration** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **expire_time** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **next_server** | **str**|  | [optional] 
 **options** | **str**|  | [optional] 
 **provided_options** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **skip_boot** | **str**|  | [optional] 
 **state** | **str**|  | [optional] 
 **strategy** | **str**|  | [optional] 
 **token** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **via** | **str**|  | [optional] 

### Return type

[**list[Lease]**](Lease.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_leases**
> list_stats_leases(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr, available=available, bundle=bundle, duration=duration, endpoint=endpoint, errors=errors, expire_time=expire_time, key=key, meta=meta, next_server=next_server, options=options, provided_options=provided_options, read_only=read_only, skip_boot=skip_boot, state=state, strategy=strategy, token=token, valid=valid, via=via)

Stats of the List Leases filtered by some parameters.

This return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Addr = IP Address Token = string Strategy = string ExpireTime = Date/Time Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
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
addr = 'addr_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
duration = 'duration_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
expire_time = 'expire_time_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
next_server = 'next_server_example'  # str |  (optional)
options = 'options_example'  # str |  (optional)
provided_options = 'provided_options_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
skip_boot = 'skip_boot_example'  # str |  (optional)
state = 'state_example'  # str |  (optional)
strategy = 'strategy_example'  # str |  (optional)
token = 'token_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
via = 'via_example'  # str |  (optional)

try:
    # Stats of the List Leases filtered by some parameters.
    api_instance.list_stats_leases(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                   filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                   range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr,
                                   available=available, bundle=bundle, duration=duration, endpoint=endpoint,
                                   errors=errors, expire_time=expire_time, key=key, meta=meta, next_server=next_server,
                                   options=options, provided_options=provided_options, read_only=read_only,
                                   skip_boot=skip_boot, state=state, strategy=strategy, token=token, valid=valid,
                                   via=via)
except ApiException as e:
    print("Exception when calling LeasesApi->list_stats_leases: %s\n" % e)
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
 **addr** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **duration** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **expire_time** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **next_server** | **str**|  | [optional] 
 **options** | **str**|  | [optional] 
 **provided_options** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **skip_boot** | **str**|  | [optional] 
 **state** | **str**|  | [optional] 
 **strategy** | **str**|  | [optional] 
 **token** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **via** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_lease_action**
> object post_lease_action(address, cmd, body, plugin=plugin)

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
api_instance = drppy_client.LeasesApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_lease_action(address, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LeasesApi->post_lease_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 
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

