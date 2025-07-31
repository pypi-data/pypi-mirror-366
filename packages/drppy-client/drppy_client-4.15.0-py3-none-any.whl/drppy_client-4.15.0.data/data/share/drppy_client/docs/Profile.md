# Profile

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | A description of this profile.  This can contain any reference information for humans you want associated with the profile. | [optional] 
**documentation** | **str** | Documentation of this profile.  This should tell what the profile is for, any special considerations that should be taken into account when using it, etc. in rich structured text (rst). | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | The name of the profile.  This must be unique across all profiles. | 
**params** | **dict(str, object)** | Any additional parameters that may be needed to expand templates for BootEnv, as documented by that boot environment&#39;s RequiredParams and OptionalParams. | [optional] 
**partial** | **bool** | Partial tracks if the object is not complete when returned. | [optional] 
**profiles** | **list[str]** | Additional Profiles that should be considered for parameters | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


