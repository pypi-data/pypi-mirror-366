# User

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | Description of user | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | Name is the name of the user | 
**password_hash** | **list[int]** | PasswordHash is the scrypt-hashed version of the user&#39;s Password. | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**roles** | **list[str]** | Roles is a list of Roles this User has. | [optional] 
**secret** | **str** | Token secret - this is used when generating user token&#39;s to allow for revocation by the grantor or the grantee.  Changing this will invalidate all existing tokens that have this user as a user or a grantor. | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


