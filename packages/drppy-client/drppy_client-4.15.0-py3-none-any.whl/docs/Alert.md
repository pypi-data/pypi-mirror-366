# Alert

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**acknowledge_time** | **datetime** | AcknowledgeTime - time of acknowledgement | [optional] 
**acknowledge_user** | **str** | AcknowledgeUser - user who acknowledged | [optional] 
**acknowledged** | **bool** | Acknowledged - has the alert been acknowledged | [optional] 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**contents** | **str** | Contents is the full information about the alert | [optional] 
**count** | **int** | Count is the number of times this Name has been called uniquely beyond the initial create. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**level** | **str** | Level of the alert Range of values: Error, Warn, Info, Debug | [optional] 
**name** | **str** | Name is a short name for this alert.  This can contain any reference information for humans you want associated with the alert. | [optional] 
**note** | **str** | Notes - field for additional information about the Alert Use this field for notes about what is done with the alert. | [optional] 
**params** | **dict(str, object)** | Params - structure of data elements - filterable | [optional] 
**principal** | **str** | Principal is the creator of the alert. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**time** | **datetime** | Time of the alert. | [optional] 
**uuid** | **str** | The UUID of the alert. This is auto-created at Create time, and cannot change afterwards. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


