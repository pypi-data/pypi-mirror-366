# Trigger

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**all_in_filter** | **bool** | AllInFilter if true cause a work_order created for all machines in the filter | [optional] 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**blueprint** | **str** | Blueprint is template to apply | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description is a one-line description of the parameter. | [optional] 
**documentation** | **str** | Documentation details what the parameter does, what values it can take, what it is used for, etc. | [optional] 
**enabled** | **bool** | Enabled is this Trigger enabled | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**filter** | **str** | Filter is a \&quot;list\&quot;-style filter string to find machines to apply the cron too Filter is already assumed to have WorkOrderMode &#x3D;&#x3D; true &amp;&amp; Runnable &#x3D;&#x3D; true | [optional] 
**filter_count** | **int** | FilterCount defines the number of machines to apply the work_order to.  Only one work_order per trigger fire. | [optional] 
**merge_data_into_params** | **bool** | MergeDataIntoParams if true causes the data from the trigger to be merged into the Params of the work_order. | [optional] 
**name** | **str** | Name is the key of this particular Trigger. | 
**params** | **dict(str, object)** | Params parameters to tweak the TriggerProvider | [optional] 
**profiles** | **list[str]** | Profiles to tweak the TriggerProvider | [optional] 
**queue_mode** | **bool** | QueueMode if true causes work_orders to be created without a machine, but with a filter for delayed operation | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**store_data_in_parameter** | **str** | StoreDataInParameter if set tells the triggers data to be stored in the parameter in the Params of the work_order. | [optional] 
**trigger_provider** | **str** | TriggerProvider is the name of the method of this trigger | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 
**work_order_params** | **dict(str, object)** | WorkOrderParams that have been directly set on the Trigger and will be moved to the work order. | [optional] 
**work_order_profiles** | **list[str]** | WorkOrderProfiles to apply to this machine in order when looking for a parameter during rendering. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


