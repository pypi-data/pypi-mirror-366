# Stage

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**boot_env** | **str** | The BootEnv the machine should be in to run this stage. If the machine is not in this bootenv, the bootenv of the machine will be changed. | 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | A description of this stage.  This should tell what it is for, any special considerations that should be taken into account when using it, etc. | [optional] 
**documentation** | **str** | Documentation of this stage.  This should tell what the stage is for, any special considerations that should be taken into account when using it, etc. in rich structured text (rst). | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | The name of the stage. | 
**optional_params** | **list[str]** | The list of extra optional parameters for this stage. They can be present as Machine.Params when the stage is applied to the machine.  These are more other consumers of the stage to know what parameters could additionally be applied to the stage by the renderer based upon the Machine.Params | [optional] 
**output_params** | **list[str]** | OutputParams are that parameters that are possibly set by the Task | [optional] 
**params** | **dict(str, object)** | Params contains parameters for the stage. This allows the machine to access these values while in this stage. | [optional] 
**partial** | **bool** | Partial tracks if the object is not complete when returned. | [optional] 
**profiles** | **list[str]** | The list of profiles a machine should use while in this stage. These are used after machine profiles, but before global. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**reboot** | **bool** | Flag to indicate if a node should be PXE booted on this transition into this Stage.  The nextbootpxe and reboot machine actions will be called if present and Reboot is true | [optional] 
**required_params** | **list[str]** | The list of extra required parameters for this stage. They should be present as Machine.Params when the stage is applied to the machine. | 
**runner_wait** | **bool** | This flag is deprecated and will always be TRUE. | [optional] 
**tasks** | **list[str]** | The list of initial machine tasks that the stage should run | [optional] 
**templates** | [**list[TemplateInfo]**](TemplateInfo.md) | The templates that should be expanded into files for the stage. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


