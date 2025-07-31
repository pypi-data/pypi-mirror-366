# UxSetting

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description is a short string description of the object | [optional] 
**documentation** | **str** | Documentation is an RST string defining the object | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**id** | **str** | Id is the Name of the object | [optional] 
**option** | **str** | Option is the refrence to the UxOption | [optional] 
**params** | **dict(str, object)** | Params is an unused residual of the object from previous releases | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**target** | **str** | Target is the entity that this applies to user, role, or global user is specified as user++&lt;user name&gt; role is specified as role++&lt;role name&gt; | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 
**value** | **str** | Value is the value of the option | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


