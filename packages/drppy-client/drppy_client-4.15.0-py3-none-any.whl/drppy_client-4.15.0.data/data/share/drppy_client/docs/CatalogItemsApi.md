# swagger_client.CatalogItemsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_catalog_item**](CatalogItemsApi.md#create_catalog_item) | **POST** /catalog_items | Create a CatalogItem
[**delete_catalog_item**](CatalogItemsApi.md#delete_catalog_item) | **DELETE** /catalog_items/{id} | Delete a CatalogItem
[**get_catalog_item**](CatalogItemsApi.md#get_catalog_item) | **GET** /catalog_items/{id} | Get a CatalogItem
[**head_catalog_item**](CatalogItemsApi.md#head_catalog_item) | **HEAD** /catalog_items/{id} | See if a CatalogItem exists
[**list_catalog_items**](CatalogItemsApi.md#list_catalog_items) | **GET** /catalog_items | Lists CatalogItems filtered by some parameters.
[**list_stats_catalog_items**](CatalogItemsApi.md#list_stats_catalog_items) | **HEAD** /catalog_items | Stats of the List CatalogItems filtered by some parameters.
[**patch_catalog_item**](CatalogItemsApi.md#patch_catalog_item) | **PATCH** /catalog_items/{id} | Patch a CatalogItem
[**put_catalog_item**](CatalogItemsApi.md#put_catalog_item) | **PUT** /catalog_items/{id} | Put a CatalogItem


# **create_catalog_item**
> CatalogItem create_catalog_item(body)

Create a CatalogItem

Create a CatalogItem from the provided object

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
body = drppy_client.CatalogItem()  # CatalogItem | 

try:
    # Create a CatalogItem
    api_response = api_instance.create_catalog_item(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->create_catalog_item: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CatalogItem**](CatalogItem.md)|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_catalog_item**
> CatalogItem delete_catalog_item(id)

Delete a CatalogItem

Delete a CatalogItem specified by {id}

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # Delete a CatalogItem
    api_response = api_instance.delete_catalog_item(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->delete_catalog_item: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_catalog_item**
> CatalogItem get_catalog_item(id)

Get a CatalogItem

Get the CatalogItem specified by {id} or return NotFound.

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # Get a CatalogItem
    api_response = api_instance.get_catalog_item(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->get_catalog_item: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_catalog_item**
> head_catalog_item(id)

See if a CatalogItem exists

Return 200 if the CatalogItem specifiec by {id} exists, or return NotFound.

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
id = 'id_example'  # str | 

try:
    # See if a CatalogItem exists
    api_instance.head_catalog_item(id)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->head_catalog_item: %s\n" % e)
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

# **list_catalog_items**
> list[CatalogItem] list_catalog_items(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, actual_version=actual_version, available=available, content_type=content_type, endpoint=endpoint, errors=errors, hot_fix=hot_fix, id=id, key=key, meta=meta, nojq_source=nojq_source, name=name, read_only=read_only, shasum256=shasum256, source=source, tip=tip, type=type, valid=valid, version=version)

Lists CatalogItems filtered by some parameters.

This will show all CatalogItems by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: ID = string Provider = string Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: ID=fred - returns items named fred ID=Lt(fred) - returns items that alphabetically less than fred. ID=Lt(fred)&Available=true - returns items with ID less than fred and Available is true

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
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
actual_version = 'actual_version_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
content_type = 'content_type_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
hot_fix = 'hot_fix_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
nojq_source = 'nojq_source_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
shasum256 = 'shasum256_example'  # str |  (optional)
source = 'source_example'  # str |  (optional)
tip = 'tip_example'  # str |  (optional)
type = 'type_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
version = 'version_example'  # str |  (optional)

try:
    # Lists CatalogItems filtered by some parameters.
    api_response = api_instance.list_catalog_items(offset=offset, limit=limit, aggregate=aggregate,
                                                   exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                                   group_by=group_by, params=params, range_only=range_only,
                                                   reverse=reverse, slim=slim, sort=sort, actual_version=actual_version,
                                                   available=available, content_type=content_type, endpoint=endpoint,
                                                   errors=errors, hot_fix=hot_fix, id=id, key=key, meta=meta,
                                                   nojq_source=nojq_source, name=name, read_only=read_only,
                                                   shasum256=shasum256, source=source, tip=tip, type=type, valid=valid,
                                                   version=version)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->list_catalog_items: %s\n" % e)
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
 **actual_version** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **content_type** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **hot_fix** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **nojq_source** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **shasum256** | **str**|  | [optional] 
 **source** | **str**|  | [optional] 
 **tip** | **str**|  | [optional] 
 **type** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **version** | **str**|  | [optional] 

### Return type

[**list[CatalogItem]**](CatalogItem.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_catalog_items**
> list_stats_catalog_items(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, actual_version=actual_version, available=available, content_type=content_type, endpoint=endpoint, errors=errors, hot_fix=hot_fix, id=id, key=key, meta=meta, nojq_source=nojq_source, name=name, read_only=read_only, shasum256=shasum256, source=source, tip=tip, type=type, valid=valid, version=version)

Stats of the List CatalogItems filtered by some parameters.

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
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
actual_version = 'actual_version_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
content_type = 'content_type_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
hot_fix = 'hot_fix_example'  # str |  (optional)
id = 'id_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
nojq_source = 'nojq_source_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
shasum256 = 'shasum256_example'  # str |  (optional)
source = 'source_example'  # str |  (optional)
tip = 'tip_example'  # str |  (optional)
type = 'type_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
version = 'version_example'  # str |  (optional)

try:
    # Stats of the List CatalogItems filtered by some parameters.
    api_instance.list_stats_catalog_items(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                          filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                          range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                          actual_version=actual_version, available=available, content_type=content_type,
                                          endpoint=endpoint, errors=errors, hot_fix=hot_fix, id=id, key=key, meta=meta,
                                          nojq_source=nojq_source, name=name, read_only=read_only, shasum256=shasum256,
                                          source=source, tip=tip, type=type, valid=valid, version=version)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->list_stats_catalog_items: %s\n" % e)
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
 **actual_version** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **content_type** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **hot_fix** | **str**|  | [optional] 
 **id** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **nojq_source** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **shasum256** | **str**|  | [optional] 
 **source** | **str**|  | [optional] 
 **tip** | **str**|  | [optional] 
 **type** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **version** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_catalog_item**
> CatalogItem patch_catalog_item(body, id)

Patch a CatalogItem

Update a CatalogItem specified by {id} using a RFC6902 Patch structure

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
id = 'id_example'  # str | 

try:
    # Patch a CatalogItem
    api_response = api_instance.patch_catalog_item(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->patch_catalog_item: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **id** | **str**|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_catalog_item**
> CatalogItem put_catalog_item(body, id)

Put a CatalogItem

Update a CatalogItem specified by {id} using a JSON CatalogItem

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
api_instance = drppy_client.CatalogItemsApi(drppy_client.ApiClient(configuration))
body = drppy_client.CatalogItem()  # CatalogItem | 
id = 'id_example'  # str | 

try:
    # Put a CatalogItem
    api_response = api_instance.put_catalog_item(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CatalogItemsApi->put_catalog_item: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CatalogItem**](CatalogItem.md)|  | 
 **id** | **str**|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

