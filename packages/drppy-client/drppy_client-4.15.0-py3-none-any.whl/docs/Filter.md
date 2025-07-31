# Filter

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aggregate** | **bool** | Aggregate indicates if parameters should be aggregate for search and return | [optional] 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**decode** | **bool** | Decode indicates if the parameters should be decoded before returning the object | [optional] 
**description** | **str** | Description is a short string description of the object | [optional] 
**documentation** | **str** | Documentation is an RST string defining the object | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**exclude_self** | **bool** | ExcludeSelf removes self runners from the list (machines/clusters/resource_brokers) | [optional] 
**group_by** | **list[str]** | GroupBy is a list of Fields or Parameters to generate groups of objects in a return list. | [optional] 
**id** | **str** | Id is the Name of the Filter | [optional] 
**object** | **str** | Object is the name of the set of objects this filter applies to. | [optional] 
**param_set** | **str** | ParamSet defines a comma-separated list of Fields or Parameters to return (can be complex functions) | [optional] 
**params** | **dict(str, object)** | Params is an unused residual of the object from previous releases | [optional] 
**queries** | [**list[Query]**](Query.md) | Queries are the tests to apply to the machine. | [optional] 
**range_only** | **bool** | RangeOnly indicates that counts should be returned of group-bys and no objects. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**reverse** | **bool** | Reverse the returned list | [optional] 
**slim** | **str** | Slim defines if meta, params, or specific parameters should be excluded from the object | [optional] 
**sort** | **list[str]** | Sort is a list of fields / parameters that should scope the list | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


