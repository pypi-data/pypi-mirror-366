# swagger_client.ClustersApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cleanup_cluster**](ClustersApi.md#cleanup_cluster) | **DELETE** /clusters/{uuid}/cleanup | Cleanup a Cluster
[**create_cluster**](ClustersApi.md#create_cluster) | **POST** /clusters | Create a Cluster
[**delete_cluster**](ClustersApi.md#delete_cluster) | **DELETE** /clusters/{uuid} | Delete a Cluster
[**delete_cluster_group_param**](ClustersApi.md#delete_cluster_group_param) | **DELETE** /clusters/{uuid}/group/params/{key} | Delete a single cluster group profile parameter
[**delete_cluster_param**](ClustersApi.md#delete_cluster_param) | **DELETE** /clusters/{uuid}/params/{key} | Delete a single cluster parameter
[**get_cluster**](ClustersApi.md#get_cluster) | **GET** /clusters/{uuid} | Get a Cluster
[**get_cluster_action**](ClustersApi.md#get_cluster_action) | **GET** /clusters/{uuid}/actions/{cmd} | List specific action for a cluster Cluster
[**get_cluster_actions**](ClustersApi.md#get_cluster_actions) | **GET** /clusters/{uuid}/actions | List cluster actions Cluster
[**get_cluster_group_param**](ClustersApi.md#get_cluster_group_param) | **GET** /clusters/{uuid}/group/params/{key} | Get a single cluster group profile parameter
[**get_cluster_group_params**](ClustersApi.md#get_cluster_group_params) | **GET** /clusters/{uuid}/group/params | List cluster group profile params Cluster
[**get_cluster_group_pub_key**](ClustersApi.md#get_cluster_group_pub_key) | **GET** /clusters/{uuid}/group/pubkey | Get the public key for secure params on a cluster group profile
[**get_cluster_param**](ClustersApi.md#get_cluster_param) | **GET** /clusters/{uuid}/params/{key} | Get a single cluster parameter
[**get_cluster_params**](ClustersApi.md#get_cluster_params) | **GET** /clusters/{uuid}/params | List cluster params Cluster
[**get_cluster_pub_key**](ClustersApi.md#get_cluster_pub_key) | **GET** /clusters/{uuid}/pubkey | Get the public key for secure params on a cluster
[**get_cluster_token**](ClustersApi.md#get_cluster_token) | **GET** /clusters/{uuid}/token | Get a Cluster Token
[**head_cluster**](ClustersApi.md#head_cluster) | **HEAD** /clusters/{uuid} | See if a Cluster exists
[**list_clusters**](ClustersApi.md#list_clusters) | **GET** /clusters | Lists Clusters filtered by some parameters.
[**list_stats_clusters**](ClustersApi.md#list_stats_clusters) | **HEAD** /clusters | Stats of the List Clusters filtered by some parameters.
[**patch_cluster**](ClustersApi.md#patch_cluster) | **PATCH** /clusters/{uuid} | Patch a Cluster
[**patch_cluster_group_params**](ClustersApi.md#patch_cluster_group_params) | **PATCH** /clusters/{uuid}/group/params | 
[**patch_cluster_params**](ClustersApi.md#patch_cluster_params) | **PATCH** /clusters/{uuid}/params | 
[**post_cluster_action**](ClustersApi.md#post_cluster_action) | **POST** /clusters/{uuid}/actions/{cmd} | Call an action on the node.
[**post_cluster_group_param**](ClustersApi.md#post_cluster_group_param) | **POST** /clusters/{uuid}/group/params/{key} | 
[**post_cluster_group_params**](ClustersApi.md#post_cluster_group_params) | **POST** /clusters/{uuid}/group/params | 
[**post_cluster_param**](ClustersApi.md#post_cluster_param) | **POST** /clusters/{uuid}/params/{key} | 
[**post_cluster_params**](ClustersApi.md#post_cluster_params) | **POST** /clusters/{uuid}/params | 
[**put_cluster**](ClustersApi.md#put_cluster) | **PUT** /clusters/{uuid} | Put a Cluster
[**start_cluster**](ClustersApi.md#start_cluster) | **PATCH** /clusters/{uuid}/start | Start a Cluster


# **cleanup_cluster**
> Machine cleanup_cluster(uuid)

Cleanup a Cluster

Cleanup a Cluster specified by {uuid}.  If 202 is returned, the on-delete-workflow has been started.

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Cleanup a Cluster
    api_response = api_instance.cleanup_cluster(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->cleanup_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cluster**
> Machine create_cluster(body, force=force)

Create a Cluster

Create a Cluster from the provided object

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Machine()  # Machine | 
force = 'force_example'  # str |  (optional)

try:
    # Create a Cluster
    api_response = api_instance.create_cluster(body, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->create_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Machine**](Machine.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster**
> Machine delete_cluster(uuid)

Delete a Cluster

Delete a Cluster specified by {uuid}.

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Delete a Cluster
    api_response = api_instance.delete_cluster(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->delete_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster_group_param**
> object delete_cluster_group_param()

Delete a single cluster group profile parameter

Delete a single group profile parameter {key} for a Cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    # Delete a single cluster group profile parameter
    api_response = api_instance.delete_cluster_group_param()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->delete_cluster_group_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster_param**
> object delete_cluster_param(uuid, key)

Delete a single cluster parameter

Delete a single parameter {key} for a Cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 

try:
    # Delete a single cluster parameter
    api_response = api_instance.delete_cluster_param(uuid, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->delete_cluster_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **key** | **str**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster**
> Machine get_cluster(uuid, aggregate=aggregate, decode=decode, params=params)

Get a Cluster

Get the Cluster specified by {uuid} or return NotFound.

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # Get a Cluster
    api_response = api_instance.get_cluster(uuid, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **aggregate** | **str**|  | [optional] 
 **decode** | **str**|  | [optional] 
 **params** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_action**
> AvailableAction get_cluster_action(uuid, cmd, plugin=plugin)

List specific action for a cluster Cluster

List specific {cmd} action for a Cluster specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a cluster Cluster
    api_response = api_instance.get_cluster_action(uuid, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_action: %s\n" % e)
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

# **get_cluster_actions**
> list[AvailableAction] get_cluster_actions(uuid, plugin=plugin)

List cluster actions Cluster

List Cluster actions for a Cluster specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List cluster actions Cluster
    api_response = api_instance.get_cluster_actions(uuid, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_actions: %s\n" % e)
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

# **get_cluster_group_param**
> object get_cluster_group_param()

Get a single cluster group profile parameter

Get a single parameter {key} for a Cluster group profile specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    # Get a single cluster group profile parameter
    api_response = api_instance.get_cluster_group_param()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_group_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_group_params**
> dict(str, object) get_cluster_group_params()

List cluster group profile params Cluster

List Cluster params for a Cluster group profile specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    # List cluster group profile params Cluster
    api_response = api_instance.get_cluster_group_params()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_group_params: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_group_pub_key**
> get_cluster_group_pub_key()

Get the public key for secure params on a cluster group profile

Get the public key for a Cluster group profile specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    # Get the public key for secure params on a cluster group profile
    api_instance.get_cluster_group_pub_key()
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_group_pub_key: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_param**
> object get_cluster_param(uuid, key, aggregate=aggregate, decode=decode)

Get a single cluster parameter

Get a single parameter {key} for a Cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)

try:
    # Get a single cluster parameter
    api_response = api_instance.get_cluster_param(uuid, key, aggregate=aggregate, decode=decode)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
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

# **get_cluster_params**
> dict(str, object) get_cluster_params(uuid, aggregate=aggregate, decode=decode, params=params)

List cluster params Cluster

List Cluster parms for a Cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
aggregate = 'aggregate_example'  # str |  (optional)
decode = 'decode_example'  # str |  (optional)
params = 'params_example'  # str |  (optional)

try:
    # List cluster params Cluster
    api_response = api_instance.get_cluster_params(uuid, aggregate=aggregate, decode=decode, params=params)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
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

# **get_cluster_pub_key**
> get_cluster_pub_key(uuid)

Get the public key for secure params on a cluster

Get the public key for a Cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get the public key for secure params on a cluster
    api_instance.get_cluster_pub_key(uuid)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_pub_key: %s\n" % e)
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

# **get_cluster_token**
> UserToken get_cluster_token(uuid)

Get a Cluster Token

Get a Cluster Token specified by {uuid} or return NotFound.

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get a Cluster Token
    api_response = api_instance.get_cluster_token(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->get_cluster_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**UserToken**](UserToken.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_cluster**
> head_cluster(uuid)

See if a Cluster exists

Return 200 if the Cluster specifiec by {uuid} exists, or return NotFound.

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # See if a Cluster exists
    api_instance.head_cluster(uuid)
except ApiException as e:
    print("Exception when calling ClustersApi->head_cluster: %s\n" % e)
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

# **list_clusters**
> list[Machine] list_clusters(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, address=address, arch=arch, available=available, boot_env=boot_env, bundle=bundle, context=context, current_job=current_job, current_task=current_task, description=description, endpoint=endpoint, errors=errors, hardware_addr=hardware_addr, hardware_addrs=hardware_addrs, key=key, locked=locked, meta=meta, name=name, os=os, partial=partial, pending_work_orders=pending_work_orders, pool=pool, pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles, read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable, running_work_orders=running_work_orders, stage=stage, task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid, work_order_mode=work_order_mode, workflow=workflow, workflow_complete=workflow_complete)

Lists Clusters filtered by some parameters.

This will show all Clusters by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Uuid = UUID string Name = string BootEnv = string Address = IP Address Runnable = true/false Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
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
address = 'address_example'  # str |  (optional)
arch = 'arch_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
current_job = 'current_job_example'  # str |  (optional)
current_task = 'current_task_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
hardware_addr = 'hardware_addr_example'  # str |  (optional)
hardware_addrs = 'hardware_addrs_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
locked = 'locked_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)
partial = 'partial_example'  # str |  (optional)
pending_work_orders = 'pending_work_orders_example'  # str |  (optional)
pool = 'pool_example'  # str |  (optional)
pool_allocated = 'pool_allocated_example'  # str |  (optional)
pool_status = 'pool_status_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
retry_task_attempt = 'retry_task_attempt_example'  # str |  (optional)
runnable = 'runnable_example'  # str |  (optional)
running_work_orders = 'running_work_orders_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
task_error_stacks = 'task_error_stacks_example'  # str |  (optional)
tasks = 'tasks_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order_mode = 'work_order_mode_example'  # str |  (optional)
workflow = 'workflow_example'  # str |  (optional)
workflow_complete = 'workflow_complete_example'  # str |  (optional)

try:
    # Lists Clusters filtered by some parameters.
    api_response = api_instance.list_clusters(offset=offset, limit=limit, aggregate=aggregate,
                                              exclude_self=exclude_self, filter=filter, raw=raw, decode=decode,
                                              group_by=group_by, params=params, range_only=range_only, reverse=reverse,
                                              slim=slim, sort=sort, address=address, arch=arch, available=available,
                                              boot_env=boot_env, bundle=bundle, context=context,
                                              current_job=current_job, current_task=current_task,
                                              description=description, endpoint=endpoint, errors=errors,
                                              hardware_addr=hardware_addr, hardware_addrs=hardware_addrs, key=key,
                                              locked=locked, meta=meta, name=name, os=os, partial=partial,
                                              pending_work_orders=pending_work_orders, pool=pool,
                                              pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles,
                                              read_only=read_only, retry_task_attempt=retry_task_attempt,
                                              runnable=runnable, running_work_orders=running_work_orders, stage=stage,
                                              task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid,
                                              work_order_mode=work_order_mode, workflow=workflow,
                                              workflow_complete=workflow_complete)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->list_clusters: %s\n" % e)
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
 **address** | **str**|  | [optional] 
 **arch** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **current_job** | **str**|  | [optional] 
 **current_task** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **hardware_addr** | **str**|  | [optional] 
 **hardware_addrs** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **locked** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 
 **partial** | **str**|  | [optional] 
 **pending_work_orders** | **str**|  | [optional] 
 **pool** | **str**|  | [optional] 
 **pool_allocated** | **str**|  | [optional] 
 **pool_status** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **retry_task_attempt** | **str**|  | [optional] 
 **runnable** | **str**|  | [optional] 
 **running_work_orders** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **task_error_stacks** | **str**|  | [optional] 
 **tasks** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order_mode** | **str**|  | [optional] 
 **workflow** | **str**|  | [optional] 
 **workflow_complete** | **str**|  | [optional] 

### Return type

[**list[Machine]**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_clusters**
> list_stats_clusters(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, address=address, arch=arch, available=available, boot_env=boot_env, bundle=bundle, context=context, current_job=current_job, current_task=current_task, description=description, endpoint=endpoint, errors=errors, hardware_addr=hardware_addr, hardware_addrs=hardware_addrs, key=key, locked=locked, meta=meta, name=name, os=os, partial=partial, pending_work_orders=pending_work_orders, pool=pool, pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles, read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable, running_work_orders=running_work_orders, stage=stage, task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid, work_order_mode=work_order_mode, workflow=workflow, workflow_complete=workflow_complete)

Stats of the List Clusters filtered by some parameters.

This will return headers with the stats of the list.  X-DRP-LIST-COUNT - number of objects in the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Uuid = UUID string Name = string BootEnv = string Address = IP Address Runnable = true/false Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Name=fred - returns items named fred Name=Lt(fred) - returns items that alphabetically less than fred. Name=Lt(fred)&Available=true - returns items with Name less than fred and Available is true

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
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
address = 'address_example'  # str |  (optional)
arch = 'arch_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
current_job = 'current_job_example'  # str |  (optional)
current_task = 'current_task_example'  # str |  (optional)
description = 'description_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
hardware_addr = 'hardware_addr_example'  # str |  (optional)
hardware_addrs = 'hardware_addrs_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
locked = 'locked_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
name = 'name_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)
partial = 'partial_example'  # str |  (optional)
pending_work_orders = 'pending_work_orders_example'  # str |  (optional)
pool = 'pool_example'  # str |  (optional)
pool_allocated = 'pool_allocated_example'  # str |  (optional)
pool_status = 'pool_status_example'  # str |  (optional)
profiles = 'profiles_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
retry_task_attempt = 'retry_task_attempt_example'  # str |  (optional)
runnable = 'runnable_example'  # str |  (optional)
running_work_orders = 'running_work_orders_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
task_error_stacks = 'task_error_stacks_example'  # str |  (optional)
tasks = 'tasks_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order_mode = 'work_order_mode_example'  # str |  (optional)
workflow = 'workflow_example'  # str |  (optional)
workflow_complete = 'workflow_complete_example'  # str |  (optional)

try:
    # Stats of the List Clusters filtered by some parameters.
    api_instance.list_stats_clusters(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                     filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                     range_only=range_only, reverse=reverse, slim=slim, sort=sort, address=address,
                                     arch=arch, available=available, boot_env=boot_env, bundle=bundle, context=context,
                                     current_job=current_job, current_task=current_task, description=description,
                                     endpoint=endpoint, errors=errors, hardware_addr=hardware_addr,
                                     hardware_addrs=hardware_addrs, key=key, locked=locked, meta=meta, name=name, os=os,
                                     partial=partial, pending_work_orders=pending_work_orders, pool=pool,
                                     pool_allocated=pool_allocated, pool_status=pool_status, profiles=profiles,
                                     read_only=read_only, retry_task_attempt=retry_task_attempt, runnable=runnable,
                                     running_work_orders=running_work_orders, stage=stage,
                                     task_error_stacks=task_error_stacks, tasks=tasks, uuid=uuid, valid=valid,
                                     work_order_mode=work_order_mode, workflow=workflow,
                                     workflow_complete=workflow_complete)
except ApiException as e:
    print("Exception when calling ClustersApi->list_stats_clusters: %s\n" % e)
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
 **address** | **str**|  | [optional] 
 **arch** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **current_job** | **str**|  | [optional] 
 **current_task** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **hardware_addr** | **str**|  | [optional] 
 **hardware_addrs** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **locked** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 
 **partial** | **str**|  | [optional] 
 **pending_work_orders** | **str**|  | [optional] 
 **pool** | **str**|  | [optional] 
 **pool_allocated** | **str**|  | [optional] 
 **pool_status** | **str**|  | [optional] 
 **profiles** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **retry_task_attempt** | **str**|  | [optional] 
 **runnable** | **str**|  | [optional] 
 **running_work_orders** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **task_error_stacks** | **str**|  | [optional] 
 **tasks** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order_mode** | **str**|  | [optional] 
 **workflow** | **str**|  | [optional] 
 **workflow_complete** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_cluster**
> Machine patch_cluster(body, uuid, force=force)

Patch a Cluster

Update a Cluster specified by {uuid} using a RFC6902 Patch structure

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Patch a Cluster
    api_response = api_instance.patch_cluster(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->patch_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_cluster_group_params**
> dict(str, object) patch_cluster_group_params()



Update group profile params for Cluster {uuid} with the passed-in patch

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    api_response = api_instance.patch_cluster_group_params()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->patch_cluster_group_params: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_cluster_params**
> dict(str, object) patch_cluster_params(body, uuid)



Update params for Cluster {uuid} with the passed-in patch

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 

try:
    api_response = api_instance.patch_cluster_params(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->patch_cluster_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_cluster_action**
> object post_cluster_action(uuid, cmd, body, plugin=plugin)

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_cluster_action(uuid, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->post_cluster_action: %s\n" % e)
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

# **post_cluster_group_param**
> object post_cluster_group_param()



Set as single Parameter {key} for a cluster group profile specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    api_response = api_instance.post_cluster_group_param()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->post_cluster_group_param: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_cluster_group_params**
> dict(str, object) post_cluster_group_params()



Sets parameters for a cluster group profile specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))

try:
    api_response = api_instance.post_cluster_group_params()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->post_cluster_group_params: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_cluster_param**
> object post_cluster_param(body, uuid, key)



Set as single Parameter {key} for a cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
uuid = 'uuid_example'  # str | 
key = 'key_example'  # str | 

try:
    api_response = api_instance.post_cluster_param(body, uuid, key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->post_cluster_param: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | 
 **uuid** | [**str**](.md)|  | 
 **key** | **str**|  | 

### Return type

**object**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_cluster_params**
> dict(str, object) post_cluster_params(body, uuid)



Sets parameters for a cluster specified by {uuid}

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
uuid = 'uuid_example'  # str | 

try:
    api_response = api_instance.post_cluster_params(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->post_cluster_params: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

**dict(str, object)**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_cluster**
> Machine put_cluster(body, uuid, force=force)

Put a Cluster

Update a Cluster specified by {uuid} using a JSON Cluster

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Machine()  # Machine | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Put a Cluster
    api_response = api_instance.put_cluster(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->put_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Machine**](Machine.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_cluster**
> Machine start_cluster(body, uuid, force=force)

Start a Cluster

Update a Cluster specified by {uuid} using a RFC6902 Patch structure after clearing workflow and runnable.

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
api_instance = drppy_client.ClustersApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 
force = 'force_example'  # str |  (optional)

try:
    # Start a Cluster
    api_response = api_instance.start_cluster(body, uuid, force=force)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClustersApi->start_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 
 **force** | **str**|  | [optional] 

### Return type

[**Machine**](Machine.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

