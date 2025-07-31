# Pool

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allocate_actions** | [**PoolTransitionActions**](PoolTransitionActions.md) |  | [optional] 
**auto_fill** | [**PoolAutoFill**](PoolAutoFill.md) |  | [optional] 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** |  | [optional] 
**documentation** | **str** |  | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**enter_actions** | [**PoolTransitionActions**](PoolTransitionActions.md) |  | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**exit_actions** | [**PoolTransitionActions**](PoolTransitionActions.md) |  | [optional] 
**id** | **str** |  | [optional] 
**parent_pool** | **str** |  | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**release_actions** | [**PoolTransitionActions**](PoolTransitionActions.md) |  | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


