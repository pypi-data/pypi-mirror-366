# UxView

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**airgap** | **bool** | Airgap is not used.  Moved to license. Deprecated | [optional] 
**applicable_roles** | **list[str]** | ApplicableRoles defines the roles that this view shows up for. e.g. superuser means that it will be available for users with the superuser role. | [optional] 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**branding_image** | **str** | BrandingImage defines a files API path that should point to an image file. This replaces the RackN logo. | [optional] 
**bulk_tabs** | **list[str]** |  | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**classifiers** | [**list[Classifier]**](Classifier.md) | Classifiers is deprecated | [optional] 
**columns** | **dict(str, list[str])** | Columns defines the custom colums for a MenuItem Id | [optional] 
**description** | **str** | Description is a short string description of the object | [optional] 
**documentation** | **str** | Documentation is an RST string defining the object | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**hide_edit_objects** | **list[str]** |  | [optional] 
**id** | **str** | Id is the Name of the Filter | [optional] 
**landing_page** | **str** | LandingPage defines the default navigation route None or \&quot;\&quot; will open the system page. if it starts with http, it will navigate to the Overiew page. Otherwise, it will go to the machine&#39;s page. | [optional] 
**machine_fields** | **list[str]** |  | [optional] 
**menu** | [**list[MenuGroup]**](MenuGroup.md) | Menu defines the menu elements. | [optional] 
**params** | **dict(str, object)** | Params is an unused residual of the object from previous releases | [optional] 
**params_restriction** | **list[str]** |  | [optional] 
**profiles_restriction** | **list[str]** |  | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**show_activiation** | **bool** | ShowActiviation is not used.  Moved to license. Deprecated | [optional] 
**stages_restriction** | **list[str]** |  | [optional] 
**tasks_restriction** | **list[str]** |  | [optional] 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 
**workflows_restriction** | **list[str]** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


