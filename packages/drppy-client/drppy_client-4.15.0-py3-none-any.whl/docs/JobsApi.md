# swagger_client.JobsApi

All URIs are relative to *https://localhost/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_job**](JobsApi.md#create_job) | **POST** /jobs | Create a Job
[**delete_job**](JobsApi.md#delete_job) | **DELETE** /jobs/{uuid} | Delete a Job
[**get_job**](JobsApi.md#get_job) | **GET** /jobs/{uuid} | Get a Job
[**get_job_action**](JobsApi.md#get_job_action) | **GET** /jobs/{uuid}/plugin_actions/{cmd} | List specific action for a job Job
[**get_job_actions**](JobsApi.md#get_job_actions) | **GET** /jobs/{uuid}/actions | Get actions for this job
[**get_job_log**](JobsApi.md#get_job_log) | **GET** /jobs/{uuid}/log | Get the log for this job
[**get_job_log_archive**](JobsApi.md#get_job_log_archive) | **GET** /jobs/{uuid}/archive | Get the log archive entry for this job
[**get_job_plugin_actions**](JobsApi.md#get_job_plugin_actions) | **GET** /jobs/{uuid}/plugin_actions | List job plugin_actions Job
[**head_job**](JobsApi.md#head_job) | **HEAD** /jobs/{uuid} | See if a Job exists
[**head_job_log**](JobsApi.md#head_job_log) | **HEAD** /jobs/{uuid}/log | Get the log for this job
[**list_jobs**](JobsApi.md#list_jobs) | **GET** /jobs | Lists Jobs filtered by some parameters.
[**list_stats_jobs**](JobsApi.md#list_stats_jobs) | **HEAD** /jobs | Stats of the List Jobs filtered by some parameters.
[**patch_job**](JobsApi.md#patch_job) | **PATCH** /jobs/{uuid} | Patch a Job
[**post_job_action**](JobsApi.md#post_job_action) | **POST** /jobs/{uuid}/plugin_actions/{cmd} | Call an action on the node.
[**put_job**](JobsApi.md#put_job) | **PUT** /jobs/{uuid} | Put a Job
[**put_job_log**](JobsApi.md#put_job_log) | **PUT** /jobs/{uuid}/log | Append the string to the end of the job&#39;s log.


# **create_job**
> Job create_job(body)

Create a Job

Create a Job from the provided object, Only Machine and UUID are used.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Job()  # Job | 

try:
    # Create a Job
    api_response = api_instance.create_job(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->create_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Job**](Job.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_job**
> Job delete_job(uuid)

Delete a Job

Delete a Job specified by {uuid}

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Delete a Job
    api_response = api_instance.delete_job(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->delete_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job**
> Job get_job(uuid)

Get a Job

Get the Job specified by {uuid} or return NotFound.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get a Job
    api_response = api_instance.get_job(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_action**
> AvailableAction get_job_action(uuid, cmd, plugin=plugin)

List specific action for a job Job

List specific {cmd} action for a Job specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # List specific action for a job Job
    api_response = api_instance.get_job_action(uuid, cmd, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_action: %s\n" % e)
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

# **get_job_actions**
> JobActions get_job_actions(uuid, plugin=plugin, os=os)

Get actions for this job

Get actions for the Job specified by {uuid} or return NotFound.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)

try:
    # Get actions for this job
    api_response = api_instance.get_job_actions(uuid, plugin=plugin, os=os)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **plugin** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 

### Return type

[**JobActions**](JobActions.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_log**
> str get_job_log(uuid)

Get the log for this job

Get log for the Job specified by {uuid} or return NotFound.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get the log for this job
    api_response = api_instance.get_job_log(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_log: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

**str**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/octet-stream, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_log_archive**
> str get_job_log_archive()

Get the log archive entry for this job

Get log archive entry for the Job specified by {uuid} or return NotFound.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))

try:
    # Get the log archive entry for this job
    api_response = api_instance.get_job_log_archive()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_log_archive: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/octet-stream, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_plugin_actions**
> list[AvailableAction] get_job_plugin_actions(uuid, plugin=plugin, os=os)

List job plugin_actions Job

List Job plugin_actions for a Job specified by {uuid}  Optionally, a query parameter can be used to limit the scope to a specific plugin. e.g. ?plugin=fred

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
plugin = 'plugin_example'  # str |  (optional)
os = 'os_example'  # str |  (optional)

try:
    # List job plugin_actions Job
    api_response = api_instance.get_job_plugin_actions(uuid, plugin=plugin, os=os)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_plugin_actions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 
 **plugin** | **str**|  | [optional] 
 **os** | **str**|  | [optional] 

### Return type

[**list[AvailableAction]**](AvailableAction.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **head_job**
> head_job(uuid)

See if a Job exists

Return 200 if the Job specifiec by {uuid} exists, or return NotFound.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # See if a Job exists
    api_instance.head_job(uuid)
except ApiException as e:
    print("Exception when calling JobsApi->head_job: %s\n" % e)
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

# **head_job_log**
> str head_job_log(uuid)

Get the log for this job

Get log for the Job specified by {uuid} or return NotFound.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 

try:
    # Get the log for this job
    api_response = api_instance.head_job_log(uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->head_job_log: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | [**str**](.md)|  | 

### Return type

**str**

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/octet-stream, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_jobs**
> list[Job] list_jobs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, archived=archived, available=available, boot_env=boot_env, bundle=bundle, context=context, current=current, current_index=current_index, elevated=elevated, end_time=end_time, endpoint=endpoint, errors=errors, exit_state=exit_state, extra_claims=extra_claims, key=key, machine=machine, meta=meta, next_index=next_index, previous=previous, read_only=read_only, result_errors=result_errors, stage=stage, start_time=start_time, state=state, task=task, token=token, uuid=uuid, valid=valid, work_order=work_order, workflow=workflow)

Lists Jobs filtered by some parameters.

This will show all Jobs by default.  You may specify to control the search: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  You may specify to control the output: decode = boolean to indicate that the returned object have the secure parameters decoded. group-by = can be specified multiple times. An array of objects (nested) grouped by the value is returned. limit = integer, number of items to return offset = integer, 0-based inclusive starting point in filter data. params = a comma separated list of parameters, or list functions to allow for inclusion in the returned object (if appropriate) range-only = returns only counts of the objects in the groups. reverse = boolean to indicate to reverse the returned list slim = A comma separated list of fields to exclude (meta, params, or other field names) sort = A list of strings defining the fields or parameters to sort by  Functional Indexs: Uuid = string Stage = string Task = string State = string Machine = string Archived = boolean StartTime = datetime EndTime = datetime Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Uuid=fred - returns items named fred Uuid=Lt(fred) - returns items that alphabetically less than fred. Uuid=Lt(fred)&Archived=true - returns items with Uuid less than fred and Archived is true

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
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
archived = 'archived_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
current = 'current_example'  # str |  (optional)
current_index = 'current_index_example'  # str |  (optional)
elevated = 'elevated_example'  # str |  (optional)
end_time = 'end_time_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
exit_state = 'exit_state_example'  # str |  (optional)
extra_claims = 'extra_claims_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
machine = 'machine_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
next_index = 'next_index_example'  # str |  (optional)
previous = 'previous_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
result_errors = 'result_errors_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
start_time = 'start_time_example'  # str |  (optional)
state = 'state_example'  # str |  (optional)
task = 'task_example'  # str |  (optional)
token = 'token_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order = 'work_order_example'  # str |  (optional)
workflow = 'workflow_example'  # str |  (optional)

try:
    # Lists Jobs filtered by some parameters.
    api_response = api_instance.list_jobs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                          filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                          range_only=range_only, reverse=reverse, slim=slim, sort=sort,
                                          archived=archived, available=available, boot_env=boot_env, bundle=bundle,
                                          context=context, current=current, current_index=current_index,
                                          elevated=elevated, end_time=end_time, endpoint=endpoint, errors=errors,
                                          exit_state=exit_state, extra_claims=extra_claims, key=key, machine=machine,
                                          meta=meta, next_index=next_index, previous=previous, read_only=read_only,
                                          result_errors=result_errors, stage=stage, start_time=start_time, state=state,
                                          task=task, token=token, uuid=uuid, valid=valid, work_order=work_order,
                                          workflow=workflow)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->list_jobs: %s\n" % e)
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
 **archived** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **current** | **str**|  | [optional] 
 **current_index** | **str**|  | [optional] 
 **elevated** | **str**|  | [optional] 
 **end_time** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **exit_state** | **str**|  | [optional] 
 **extra_claims** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **machine** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **next_index** | **str**|  | [optional] 
 **previous** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **result_errors** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **start_time** | **str**|  | [optional] 
 **state** | **str**|  | [optional] 
 **task** | **str**|  | [optional] 
 **token** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order** | **str**|  | [optional] 
 **workflow** | **str**|  | [optional] 

### Return type

[**list[Job]**](Job.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stats_jobs**
> list_stats_jobs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self, filter=filter, raw=raw, decode=decode, group_by=group_by, params=params, range_only=range_only, reverse=reverse, slim=slim, sort=sort, archived=archived, available=available, boot_env=boot_env, bundle=bundle, context=context, current=current, current_index=current_index, elevated=elevated, end_time=end_time, endpoint=endpoint, errors=errors, exit_state=exit_state, extra_claims=extra_claims, key=key, machine=machine, meta=meta, next_index=next_index, previous=previous, read_only=read_only, result_errors=result_errors, stage=stage, start_time=start_time, state=state, task=task, token=token, uuid=uuid, valid=valid, work_order=work_order, workflow=workflow)

Stats of the List Jobs filtered by some parameters.

This will return headers with the stats of the list.  You may specify: aggregate = boolean to indicate if the parameters should be aggregated for search and return exclude-self = boolean to indicate that the returned list exclude the \"self\" runners (machines only) filter = a string that defines a Named filter raw = a string that is template expanded and then parsed for filter functions  Functional Indexs: Uuid = string Stage = string Task = string State = string Machine = string Archived = boolean StartTime = datetime EndTime = datetime Available = boolean Valid = boolean ReadOnly = boolean  Functions: Eq(value) = Return items that are equal to value Lt(value) = Return items that are less than value Lte(value) = Return items that less than or equal to value Gt(value) = Return items that are greater than value Gte(value) = Return items that greater than or equal to value Between(lower,upper) = Return items that are inclusively between lower and upper Except(lower,upper) = Return items that are not inclusively between lower and upper  Example: Uuid=fred - returns items named fred Uuid=Lt(fred) - returns items that alphabetically less than fred. Uuid=Lt(fred)&Archived=true - returns items with Uuid less than fred and Archived is true

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
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
archived = 'archived_example'  # str |  (optional)
available = 'available_example'  # str |  (optional)
boot_env = 'boot_env_example'  # str |  (optional)
bundle = 'bundle_example'  # str |  (optional)
context = 'context_example'  # str |  (optional)
current = 'current_example'  # str |  (optional)
current_index = 'current_index_example'  # str |  (optional)
elevated = 'elevated_example'  # str |  (optional)
end_time = 'end_time_example'  # str |  (optional)
endpoint = 'endpoint_example'  # str |  (optional)
errors = 'errors_example'  # str |  (optional)
exit_state = 'exit_state_example'  # str |  (optional)
extra_claims = 'extra_claims_example'  # str |  (optional)
key = 'key_example'  # str |  (optional)
machine = 'machine_example'  # str |  (optional)
meta = 'meta_example'  # str |  (optional)
next_index = 'next_index_example'  # str |  (optional)
previous = 'previous_example'  # str |  (optional)
read_only = 'read_only_example'  # str |  (optional)
result_errors = 'result_errors_example'  # str |  (optional)
stage = 'stage_example'  # str |  (optional)
start_time = 'start_time_example'  # str |  (optional)
state = 'state_example'  # str |  (optional)
task = 'task_example'  # str |  (optional)
token = 'token_example'  # str |  (optional)
uuid = 'uuid_example'  # str |  (optional)
valid = 'valid_example'  # str |  (optional)
work_order = 'work_order_example'  # str |  (optional)
workflow = 'workflow_example'  # str |  (optional)

try:
    # Stats of the List Jobs filtered by some parameters.
    api_instance.list_stats_jobs(offset=offset, limit=limit, aggregate=aggregate, exclude_self=exclude_self,
                                 filter=filter, raw=raw, decode=decode, group_by=group_by, params=params,
                                 range_only=range_only, reverse=reverse, slim=slim, sort=sort, archived=archived,
                                 available=available, boot_env=boot_env, bundle=bundle, context=context,
                                 current=current, current_index=current_index, elevated=elevated, end_time=end_time,
                                 endpoint=endpoint, errors=errors, exit_state=exit_state, extra_claims=extra_claims,
                                 key=key, machine=machine, meta=meta, next_index=next_index, previous=previous,
                                 read_only=read_only, result_errors=result_errors, stage=stage, start_time=start_time,
                                 state=state, task=task, token=token, uuid=uuid, valid=valid, work_order=work_order,
                                 workflow=workflow)
except ApiException as e:
    print("Exception when calling JobsApi->list_stats_jobs: %s\n" % e)
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
 **archived** | **str**|  | [optional] 
 **available** | **str**|  | [optional] 
 **boot_env** | **str**|  | [optional] 
 **bundle** | **str**|  | [optional] 
 **context** | **str**|  | [optional] 
 **current** | **str**|  | [optional] 
 **current_index** | **str**|  | [optional] 
 **elevated** | **str**|  | [optional] 
 **end_time** | **str**|  | [optional] 
 **endpoint** | **str**|  | [optional] 
 **errors** | **str**|  | [optional] 
 **exit_state** | **str**|  | [optional] 
 **extra_claims** | **str**|  | [optional] 
 **key** | **str**|  | [optional] 
 **machine** | **str**|  | [optional] 
 **meta** | **str**|  | [optional] 
 **next_index** | **str**|  | [optional] 
 **previous** | **str**|  | [optional] 
 **read_only** | **str**|  | [optional] 
 **result_errors** | **str**|  | [optional] 
 **stage** | **str**|  | [optional] 
 **start_time** | **str**|  | [optional] 
 **state** | **str**|  | [optional] 
 **task** | **str**|  | [optional] 
 **token** | **str**|  | [optional] 
 **uuid** | **str**|  | [optional] 
 **valid** | **str**|  | [optional] 
 **work_order** | **str**|  | [optional] 
 **workflow** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_job**
> Job patch_job(body, uuid)

Patch a Job

Update a Job specified by {uuid} using a RFC6902 Patch structure

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Patch()  # Patch | 
uuid = 'uuid_example'  # str | 

try:
    # Patch a Job
    api_response = api_instance.patch_job(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->patch_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Patch**](Patch.md)|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_job_action**
> object post_job_action(uuid, cmd, body, plugin=plugin)

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
uuid = 'uuid_example'  # str | 
cmd = 'cmd_example'  # str | 
body = NULL  # object | 
plugin = 'plugin_example'  # str |  (optional)

try:
    # Call an action on the node.
    api_response = api_instance.post_job_action(uuid, cmd, body, plugin=plugin)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->post_job_action: %s\n" % e)
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

# **put_job**
> Job put_job(body, uuid)

Put a Job

Update a Job specified by {uuid} using a JSON Job

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
body = drppy_client.Job()  # Job | 
uuid = 'uuid_example'  # str | 

try:
    # Put a Job
    api_response = api_instance.put_job(body, uuid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->put_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Job**](Job.md)|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_job_log**
> put_job_log(body, uuid)

Append the string to the end of the job's log.

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
api_instance = drppy_client.JobsApi(drppy_client.ApiClient(configuration))
body = NULL  # object | 
uuid = 'uuid_example'  # str | 

try:
    # Append the string to the end of the job's log.
    api_instance.put_job_log(body, uuid)
except ApiException as e:
    print("Exception when calling JobsApi->put_job_log: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | 
 **uuid** | [**str**](.md)|  | 

### Return type

void (empty response body)

### Authorization

[Bearer](../README.md#Bearer), [basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

