# Subnet

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active_end** | **str** | ActiveEnd is the last non-reserved IP address we will hand non-reserved leases from. | 
**active_lease_time** | **int** | ActiveLeaseTime is the default lease duration in seconds we will hand out to leases that do not have a reservation. | 
**active_start** | **str** | ActiveStart is the first non-reserved IP address we will hand non-reserved leases from. | 
**available** | **bool** | Available tracks whether or not the model passed validation. | [optional] 
**bundle** | **str** | Bundle tracks the name of the store containing this object. This field is read-only, and cannot be changed via the API. | [optional] 
**description** | **str** | A description of this Subnet.  This should tell what it is for, any special considerations that should be taken into account when using it, etc. | [optional] 
**documentation** | **str** | Documentation of this subnet.  This should tell what the subnet is for, any special considerations that should be taken into account when using it, etc. in rich structured text (rst). | [optional] 
**enabled** | **bool** | Enabled indicates if the subnet should hand out leases or continue operating leases if already running. | 
**endpoint** | **str** | Endpoint tracks the owner of the object among DRP endpoints | [optional] 
**errors** | **list[str]** | If there are any errors in the validation process, they will be available here. | [optional] 
**name** | **str** | Name is the name of the subnet. Subnet names must be unique | 
**next_server** | **str** | NextServer is the address of the next server in the DHCP/TFTP/PXE chain.  You should only set this if you want to transfer control to a different DHCP or TFTP server. | 
**only_reservations** | **bool** | OnlyReservations indicates that we will only allow leases for which there is a preexisting reservation. | 
**options** | [**list[DhcpOption]**](DhcpOption.md) |  | [optional] 
**pickers** | **list[str]** | Pickers is list of methods that will allocate IP addresses. Each string must refer to a valid address picking strategy.  The current ones are:  \&quot;none\&quot;, which will refuse to hand out an address and refuse to try any remaining strategies.  \&quot;hint\&quot;, which will try to reuse the address that the DHCP packet is requesting, if it has one.  If the request does not have a requested address, \&quot;hint\&quot; will fall through to the next strategy. Otherwise, it will refuse to try any remaining strategies whether or not it can satisfy the request.  This should force the client to fall back to DHCPDISCOVER with no requsted IP address. \&quot;hint\&quot; will reuse expired leases and unexpired leases that match on the requested address, strategy, and token.  \&quot;nextFree\&quot;, which will try to create a Lease with the next free address in the subnet active range.  It will fall through to the next strategy if it cannot find a free IP. \&quot;nextFree\&quot; only considers addresses that do not have a lease, whether or not the lease is expired.  \&quot;mostExpired\&quot; will try to recycle the most expired lease in the subnet&#39;s active range.  All of the address allocation strategies do not consider any addresses that are reserved, as lease creation will be handled by the reservation instead.  We will consider adding more address allocation strategies in the future. | 
**proxy** | **bool** | Proxy indicates if the subnet should act as a proxy DHCP server. If true, the subnet will not manage ip addresses but will send offers to requests.  It is an error for Proxy and Unmanaged to be true. | 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 
**reserved_lease_time** | **int** | ReservedLeasTime is the default lease time we will hand out to leases created from a reservation in our subnet. | 
**strategy** | **str** | Strategy is the leasing strategy that will be used determine what to use from the DHCP packet to handle lease management. | 
**subnet** | **str** | Subnet is the network address in CIDR form that all leases acquired in its range will use for options, lease times, and NextServer settings by default | 
**unmanaged** | **bool** | Unmanaged indicates that dr-provision will never send boot-related options to machines that get leases from this subnet.  If false, dr-provision will send whatever boot-related options it would normally send.  It is an error for Unmanaged and Proxy to both be true. | 
**validated** | **bool** | Validated tracks whether or not the model has been validated. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


