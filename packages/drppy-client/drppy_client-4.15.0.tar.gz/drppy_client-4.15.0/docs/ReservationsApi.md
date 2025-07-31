# swagger_client.ReservationsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_reservation**](ReservationsApi.md#create_reservation) | **POST** /reservations | Create a Reservation
[**delete_reservation**](ReservationsApi.md#delete_reservation) | **DELETE** /reservations/{address} | Delete a Reservation
[**get_reservation**](ReservationsApi.md#get_reservation) | **GET** /reservations/{address} | Get a Reservation
[**get_reservation_action**](ReservationsApi.md#get_reservation_action) | **GET** /reservations/{address}/actions/{cmd} | List specific action for a reservation Reservation
[**get_reservation_actions**](ReservationsApi.md#get_reservation_actions) | **GET** /reservations/{address}/actions | List reservation actions Reservation
[**head_reservation**](ReservationsApi.md#head_reservation) | **HEAD** /reservations/{address} | See if a Reservation exists
[**list_reservations**](ReservationsApi.md#list_reservations) | **GET** /reservations | Lists Reservations filtered by some parameters.
[**list_stats_reservations**](ReservationsApi.md#list_stats_reservations) | **HEAD** /reservations | Stats of the List Reservations filtered by some parameters.
[**patch_reservation**](ReservationsApi.md#patch_reservation) | **PATCH** /reservations/{address} | Patch a Reservation
[**post_reservation_action**](ReservationsApi.md#post_reservation_action) | **POST** /reservations/{address}/actions/{cmd} | Call an action on the node.
[**put_reservation**](ReservationsApi.md#put_reservation) | **PUT** /reservations/{address} | Put a Reservation


# **create_reservation**
> Reservation create_reservation(body)

Create a Reservation

Create a Reservation from the provided object

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Reservation()  # Reservation | 

try:
    # Create a Reservation
    api_response = api_instance.create_reservation(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->create_reservation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Reservation**](Reservation.md)|  | 

### Return type

[**Reservation**](Reservation.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_reservation**
> Reservation delete_reservation(address)

Delete a Reservation

Delete a Reservation specified by {address}

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 

try:
    # Delete a Reservation
    api_response = api_instance.delete_reservation(address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->delete_reservation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 

### Return type

[**Reservation**](Reservation.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_reservation**
> Reservation get_reservation(address)

Get a Reservation

Get the Reservation specified by {address} or return NotFound.

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 

try:
    # Get a Reservation
    api_response = api_instance.get_reservation(address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->get_reservation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 

### Return type

[**Reservation**](Reservation.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_reservation_action**
> AvailableAction get_reservation_action(address, cmd, plugin=plugin)

List specific action for a reservation Reservation

List specific {cmd} action for a Reservation specified by {address}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a reservation Reservation
    api_response = api_instance.get_reservation_action(address, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->get_reservation_action: %s\n" % e)
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

# **get_reservation_actions**
> list[AvailableAction] get_reservation_actions(address, plugin=plugin)

List reservation actions Reservation

List Reservation actions for a Reservation specified by {address}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List reservation actions Reservation
    api_response = api_instance.get_reservation_actions(address, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->get_reservation_actions: %s\n" % e)
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

# **head_reservation**
> head_reservation(address)

See if a Reservation exists

Return 200 if the Reservation specific by {address} exists, or return NotFound.

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 

try:
    # See if a Reservation exists
    api_instance.head_reservation(address)
except ApiException as e:
    print("Exception when calling ReservationsApi->head_reservation: %s\n" % e)
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

# **list_reservations**
> list[Reservation] list_reservations(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr, available=available, bundle=bundle, description=description, documentation=documentation, duration=duration, endpoint=endpoint, errors=errors, key=key, meta=meta, next_server=next_server, options=options, read_only=read_only, scoped=scoped, strategy=strategy, subnet=subnet, token=token, valid=valid)

Lists Reservations filtered by some parameters.

This will show all Reservations by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Addr = IP Address Token = string Strategy = string NextServer = IP Address Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
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
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
duration = 'duration_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
next_server = 'next_server_example'  # str |  (optional)
options = 'options_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
scoped = 'scoped_example'  # str |  (optional)
strategy = 'strategy_example'  # str |  (optional)
subnet = 'subnet_example'  # str |  (optional)
token = 'token_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists Reservations filtered by some parameters.
    api_response = api_instance.list_reservations(offset=offset, limit=limit, aggregate=aggregate,
                                                  exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                                  group_by=group_by, params=params, range_only=range_only,
                                                  reverse=reverse, slim=slim, sort=sort, addr=addr, available=available,
                                                  bundle=bundle, description=description, documentation=documentation,
                                                  duration=duration, endpoint=endpoint, errors=errors, key=key,
                                                  meta=meta, next_server=next_server, options=options,
                                                  read_only=read_only, scoped=scoped, strategy=strategy, subnet=subnet,
                                                  token=token, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->list_reservations: %s\n" % e)
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
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **duration** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **next_server** | **str**|  | [optional] 
 **options** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **scoped** | **str**|  | [optional] 
 **strategy** | **str**|  | [optional] 
 **subnet** | **str**|  | [optional] 
 **token** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[Reservation]**](Reservation.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_reservations**
> list_stats_reservations(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr, available=available, bundle=bundle, description=description, documentation=documentation, duration=duration, endpoint=endpoint, errors=errors, key=key, meta=meta, next_server=next_server, options=options, read_only=read_only, scoped=scoped, strategy=strategy, subnet=subnet, token=token, valid=valid)

Stats of the List Reservations filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Addr = IP Address Token = string Strategy = string NextServer = IP Address Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
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
description = 'description_example'  # str |  (optional)
documentation = 'documentation_example'  # str |  (optional)
duration = 'duration_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
next_server = 'next_server_example'  # str |  (optional)
options = 'options_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
scoped = 'scoped_example'  # str |  (optional)
strategy = 'strategy_example'  # str |  (optional)
subnet = 'subnet_example'  # str |  (optional)
token = 'token_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List Reservations filtered by some parameters.
    api_instance.list_stats_reservations(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                         filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                         range_only=range_only, reverse=reverse, slim=slim, sort=sort, addr=addr,
                                         available=available, bundle=bundle, description=description,
                                         documentation=documentation, duration=duration, endpoint=endpoint,
                                         errors=errors, key=key, meta=meta, next_server=next_server, options=options,
                                         read_only=read_only, scoped=scoped, strategy=strategy, subnet=subnet,
                                         token=token, valid=valid)
except ApiException as e:
    print("Exception when calling ReservationsApi->list_stats_reservations: %s\n" % e)
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
 **description** | **str**|  | [optional] 
 **documentation** | **str**|  | [optional] 
 **duration** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **next_server** | **str**|  | [optional] 
 **options** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **scoped** | **str**|  | [optional] 
 **strategy** | **str**|  | [optional] 
 **subnet** | **str**|  | [optional] 
 **token** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_reservation**
> Reservation patch_reservation(body, address)

Patch a Reservation

Update a Reservation specified by {address} using a RFC6902 Patch structure

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
address = 'address_example'  # str | 

try:
    # Patch a Reservation
    api_response = api_instance.patch_reservation(body, address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->patch_reservation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **address** | **str**|  | 

### Return type

[**Reservation**](Reservation.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_reservation_action**
> object post_reservation_action(address, cmd, body, plugin=plugin)

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
address = 'address_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_reservation_action(address, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->post_reservation_action: %s\n" % e)
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

# **put_reservation**
> Reservation put_reservation(body, address)

Put a Reservation

Update a Reservation specified by {address} using a JSON Reservation

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
api_instance = drppy_client.ReservationsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Reservation()  # Reservation | 
address = 'address_example'  # str | 

try:
    # Put a Reservation
    api_response = api_instance.put_reservation(body, address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReservationsApi->put_reservation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Reservation**](Reservation.md)|  | 
 **address** | **str**|  | 

### Return type

[**Reservation**](Reservation.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

