# Task

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description is a one-line description of this Task. | [optional] 
**documentation** | **str** | Documentation should describe in detail what this task should do on a machine. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**extra_claims** | [**list[Claim]**](Claim.md) | ExtraClaims is a raw list of Claims that should be added to the default set of allowable Claims when a Job based on this task is running. Any extra claims added here will be added _after_ any added by ExtraRoles | [optional] 
**extra_roles** | **list[str]** | ExtraRoles is a list of Roles whose Claims should be added to the default set of allowable Claims when a Job based on this task is running. | [optional] 
**name** | **str** | Name is the name of this Task.  Task names must be globally unique | 
**optional_params** | **list[str]** | OptionalParams are extra optional parameters that a template rendered for the Task may use. | 
**output_params** | **list[str]** | OutputParams are that parameters that are possibly set by the Task | [optional] 
**prerequisites** | **list[str]** | Prerequisites are tasks that must have been run in the current BootEnv before this task can be run. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**required_params** | **list[str]** | RequiredParams is the list of parameters that are required to be present on Machine.Params or in a profile attached to the machine. | 
**templates** | [**list[TemplateInfo]**](TemplateInfo.md) | Templates lists the templates that need to be rendered for the Task. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


