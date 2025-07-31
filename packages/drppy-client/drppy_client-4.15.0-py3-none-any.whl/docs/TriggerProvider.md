# TriggerProvider

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description is a one-line description of the parameter. | [optional] 
**documentation** | **str** | Documentation details what the parameter does, what values it can take, what it is used for, etc. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**method** | **str** | Method defines the method used on that URL | [optional] 
**name** | **str** | Name is the key of this particular TriggerProvider. | 
**no_url** | **bool** | NoURL indicates that a URL should NOT be created | [optional] 
**optional_parameters** | **list[str]** | OptionalParameters define the optional values that can be in Params on the Trigger | [optional] 
**params** | **dict(str, object)** | Params that have been directly set on the TriggerProvider. | [optional] 
**profiles** | **list[str]** | Profiles to apply to this machine in order when looking for a parameter during rendering. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**required_parameters** | **list[str]** | RequiredParameters define the values that must be in Params on the Trigger | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


