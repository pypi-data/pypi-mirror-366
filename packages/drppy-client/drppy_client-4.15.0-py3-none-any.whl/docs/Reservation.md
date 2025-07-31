# Reservation

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**addr** | **str** | Addr is the IP address permanently assigned to the strategy/token combination. | 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | A description of this Reservation.  This should tell what it is for, any special considerations that should be taken into account when using it, etc. | [optional] 
**documentation** | **str** | Documentation of this reservation.  This should tell what the reservation is for, any special considerations that should be taken into account when using it, etc. in rich structured text (rst). | [optional] 
**duration** | **int** | Duration is the time in seconds for which a lease can be valid. ExpireTime is calculated from Duration. | [optional] 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**next_server** | **str** | NextServer is the address the server should contact next. You should only set this if you want to talk to a DHCP or TFTP server other than the one provided by dr-provision. | [optional] 
**options** | [**list[DhcpOption]**](DhcpOption.md) | Options is the list of DHCP options that apply to this Reservation | [optional] 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**scoped** | **bool** | Scoped indicates that this reservation is tied to a particular Subnet, as determined by the reservation&#39;s Addr. | 
**strategy** | **str** | Strategy is the leasing strategy that will be used determine what to use from the DHCP packet to handle lease management. | 
**subnet** | **str** | Subnet is the name of the Subnet that this Reservation is associated with. This property is read-only. | [optional] 
**token** | **str** | Token is the unique identifier that the strategy for this Reservation should use. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


