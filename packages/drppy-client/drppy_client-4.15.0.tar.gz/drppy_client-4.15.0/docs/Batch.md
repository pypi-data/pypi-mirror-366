# Batch

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | A description of this machine.  This can contain any reference information for humans you want associated with the machine. | [optional] 
**end_time** | **datetime** | EndTime is the time the batch failed or finished. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**post_work_order** | **str** | SetupWorkOrder is the scheduling work order that was created at create time. | [optional] 
**post_work_order_template** | [**WorkOrder**](WorkOrder.md) |  | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**setup_work_order** | **str** | SetupWorkOrder is the scheduling work order that was created at create time. | [optional] 
**setup_work_order_template** | [**WorkOrder**](WorkOrder.md) |  | 
**start_time** | **datetime** | StartTime is the time the batch started running. | [optional] 
**state** | **str** | State the batch is in.  Must be one of \&quot;created\&quot;, \&quot;setup\&quot;, \&quot;running\&quot;, \&quot;post\&quot;, \&quot;failed\&quot;, \&quot;finished\&quot;, \&quot;cancelled\&quot; | 
**status** | **str** | Status is the reason for things | [optional] 
**uuid** | **str** | UUID of the batch.  The primary key. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 
**work_order_counts** | **dict(str, int)** | WorkOrderCounts addresses the state of the workorders - this is calculated | [optional] 
**work_order_template** | [**WorkOrder**](WorkOrder.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


