# Param

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description is a one-line description of the parameter. | [optional] 
**documentation** | **str** | Documentation details what the parameter does, what values it can take, what it is used for, etc. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | Name is the name of the param.  Params must be uniquely named. | 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**schema** | **object** | Schema must be a valid JSONSchema as of draft v4. | 
**secure** | **bool** | Secure implies that any API interactions with this Param will deal with SecureData values. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


