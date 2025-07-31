# Plugin

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | A description of this plugin.  This can contain any reference information for humans you want associated with the plugin. | [optional] 
**documentation** | **str** | Documentation of this plugin.  This should tell what the plugin is for, any special considerations that should be taken into account when using it, etc. in rich structured text (rst). | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | The name of the plugin instance.  THis must be unique across all plugins. | 
**params** | **dict(str, object)** | Any additional parameters that may be needed to configure the plugin. | [optional] 
**partial** | **bool** | Partial tracks if the object is not complete when returned. | [optional] 
**plugin_errors** | **list[str]** | Error unrelated to the object validity, but the execution of the plugin. | [optional] 
**provider** | **str** | The plugin provider for this plugin | 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


