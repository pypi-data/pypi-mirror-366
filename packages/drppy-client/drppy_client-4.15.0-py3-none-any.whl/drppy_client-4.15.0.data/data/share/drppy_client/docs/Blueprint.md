# Blueprint

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description is a one-line description of the parameter. | [optional] 
**documentation** | **str** | Documentation details what the parameter does, what values it can take, what it is used for, etc. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | Name is the key of this particular Blueprint. | 
**params** | **dict(str, object)** | Params The Parameters that have been directly set on the Blueprint. | [optional] 
**profiles** | **list[str]** | Profiles An array of profiles to apply to this machine in order when looking for a parameter during rendering. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**tasks** | **list[str]** | Tasks is a list of strings that match the same as the machine&#39;s Task list. Actions, contexts, and stages are allowed, provided that the bootenv does not change. | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


