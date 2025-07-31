# VersionSet

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apply** | **bool** |  | [optional] 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**components** | [**list[Element]**](Element.md) |  | [optional] 
**drpux_version** | **str** |  | [optional] 
**drp_version** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**documentation** | **str** |  | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**files** | [**list[FileData]**](FileData.md) |  | [optional] 
**_global** | **dict(str, object)** |  | [optional] 
**id** | **str** |  | [optional] 
**plugins** | [**list[Plugin]**](Plugin.md) |  | [optional] 
**prefs** | **dict(str, str)** |  | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


