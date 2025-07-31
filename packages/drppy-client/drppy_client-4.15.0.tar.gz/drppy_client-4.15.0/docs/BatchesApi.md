# swagger_client.BatchesApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_batch**](BatchesApi.md#create_batch) | **POST** /batches | Create a Batch
[**delete_batch**](BatchesApi.md#delete_batch) | **DELETE** /batches/{uuid} | Delete a Batch
[**get_batch**](BatchesApi.md#get_batch) | **GET** /batches/{uuid} | Get a Batch
[**get_batch_action**](BatchesApi.md#get_batch_action) | **GET** /batches/{uuid}/actions/{cmd} | List specific action for a batch Batch
[**get_batch_actions**](BatchesApi.md#get_batch_actions) | **GET** /batches/{uuid}/actions | List batch actions Batch
[**head_batch**](BatchesApi.md#head_batch) | **HEAD** /batches/{uuid} | See if a Batch exists
[**list_batches**](BatchesApi.md#list_batches) | **GET** /batches | Lists Batches filtered by some parameters.
[**list_stats_batches**](BatchesApi.md#list_stats_batches) | **HEAD** /batches | Stats of the List Batches filtered by some parameters.
[**patch_batch**](BatchesApi.md#patch_batch) | **PATCH** /batches/{uuid} | Patch a Batch
[**post_batch_action**](BatchesApi.md#post_batch_action) | **POST** /batches/{uuid}/actions/{cmd} | Call an action on the node.
[**put_batch**](BatchesApi.md#put_batch) | **PUT** /batches/{uuid} | Put a Batch


# **create_batch**
> Batch create_batch(body, force=force)

Create a Batch

Create a Batch from the provided object

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Batch()  # Batch | 
force = 'force_example'  # str |  (optional)

try:
    # Create a Batch
    api_response = api_instance.create_batch(body, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->create_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Batch**](Batch.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Batch**](Batch.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_batch**
> Batch delete_batch(uuid)

Delete a Batch

Delete a Batch specified by {uuid}.  If 202 is returned, the on-delete-workflow has been started.

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Delete a Batch
    api_response = api_instance.delete_batch(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->delete_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Batch**](Batch.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_batch**
> Batch get_batch(uuid)

Get a Batch

Get the Batch specified by {uuid} or return NotFound.

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get a Batch
    api_response = api_instance.get_batch(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->get_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Batch**](Batch.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_batch_action**
> AvailableAction get_batch_action(uuid, cmd, plugin=plugin)

List specific action for a batch Batch

List specific {cmd} action for a Batch specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a batch Batch
    api_response = api_instance.get_batch_action(uuid, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->get_batch_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
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

# **get_batch_actions**
> list[AvailableAction] get_batch_actions(uuid, plugin=plugin)

List batch actions Batch

List Batch actions for a Batch specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List batch actions Batch
    api_response = api_instance.get_batch_actions(uuid, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->get_batch_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **plugin** | **str**|  | [optional] 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_batch**
> head_batch(uuid)

See if a Batch exists

Return 200 if the Batch specifiec by {uuid} exists, or return NotFound.

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # See if a Batch exists
    api_instance.head_batch(uuid)
except ApiException as e:
    print("Exception when calling BatchesApi->head_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_batches**
> list[Batch] list_batches(offset=offset, limit=limit, filter=filter, raw=raw, decode=decode, group_by=group_by, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, endpoint=endpoint, errors=errors, key=key, meta=meta, read_only=read_only, uuid=uuid, valid=valid)

Lists Batches filtered by some parameters.

This will show all Batches by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Uuid = UUID string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
offset = 789  # int |  (optional)
limit = 789  # int |  (optional)
filter = 'filter_example'  # str |  (optional)
raw = 'raw_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
group_by = 'group_by_example'  # str |  (optional)
range_only = 'range_only_example'  # str |  (optional)
reverse = 'reverse_example'  # str |  (optional)
slim = 'slim_example'  # str |  (optional)
sort = 'sort_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Lists Batches filtered by some parameters.
    api_response = api_instance.list_batches(offset=offset, limit=limit, filter=filter, raw=raw, decode=decode,
                                             group_by=group_by, range_only=range_only, reverse=reverse, slim=slim,
                                             sort=sort, available=available, bundle=bundle, description=description,
                                             endpoint=endpoint, errors=errors, key=key, meta=meta, read_only=read_only,
                                             uuid=uuid, valid=valid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->list_batches: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**|  | [optional] 
 **limit** | **int**|  | [optional] 
 **filter** | **str**|  | [optional] 
 **raw** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **group_by** | **str**|  | [optional] 
 **range_only** | **str**|  | [optional] 
 **reverse** | **str**|  | [optional] 
 **slim** | **str**|  | [optional] 
 **sort** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

[**list[Batch]**](Batch.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_batches**
> list_stats_batches(offset=offset, limit=limit, filter=filter, raw=raw, decode=decode, group_by=group_by, range_only=range_only, reverse=reverse, slim=slim, sort=sort, available=available, bundle=bundle, description=description, endpoint=endpoint, errors=errors, key=key, meta=meta, read_only=read_only, uuid=uuid, valid=valid)

Stats of the List Batches filtered by some parameters.

This will return headers with the stats of the list.  X-DRP-LIST-COUNT - number of objects in the list.  You may specify: filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Uuid = UUID string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
offset = 789  # int |  (optional)
limit = 789  # int |  (optional)
filter = 'filter_example'  # str |  (optional)
raw = 'raw_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
group_by = 'group_by_example'  # str |  (optional)
range_only = 'range_only_example'  # str |  (optional)
reverse = 'reverse_example'  # str |  (optional)
slim = 'slim_example'  # str |  (optional)
sort = 'sort_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)

try:
    # Stats of the List Batches filtered by some parameters.
    api_instance.list_stats_batches(offset=offset, limit=limit, filter=filter, raw=raw, decode=decode,
                                    group_by=group_by, range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                    available=available, bundle=bundle, description=description, endpoint=endpoint,
                                    errors=errors, key=key, meta=meta, read_only=read_only, uuid=uuid, valid=valid)
except ApiException as e:
    print("Exception when calling BatchesApi->list_stats_batches: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**|  | [optional] 
 **limit** | **int**|  | [optional] 
 **filter** | **str**|  | [optional] 
 **raw** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **group_by** | **str**|  | [optional] 
 **range_only** | **str**|  | [optional] 
 **reverse** | **str**|  | [optional] 
 **slim** | **str**|  | [optional] 
 **sort** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_batch**
> Batch patch_batch(body, uuid, force=force)

Patch a Batch

Update a Batch specified by {uuid} using a RFC6902 Patch structure

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Patch a Batch
    api_response = api_instance.patch_batch(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->patch_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Batch**](Batch.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_batch_action**
> object post_batch_action(uuid, cmd, body, plugin=plugin)

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_batch_action(uuid, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->post_batch_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
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

# **put_batch**
> Batch put_batch(body, uuid, force=force)

Put a Batch

Update a Batch specified by {uuid} using a JSON Batch

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
api_instance = drppy_client.BatchesApi(drppy_client.ApiClient(configuration))
body = drppy_client.Batch()  # Batch | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Put a Batch
    api_response = api_instance.put_batch(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchesApi->put_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Batch**](Batch.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Batch**](Batch.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

