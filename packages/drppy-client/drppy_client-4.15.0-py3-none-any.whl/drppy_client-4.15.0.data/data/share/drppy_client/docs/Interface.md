# Interface

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active_address** | **str** | ActiveAddress is our best guess at the address that should be used for \&quot;normal\&quot; incoming traffic on this interface. | [optional] 
**addresses** | **list[str]** | Addresses contains the IPv4 and IPv6 addresses bound to this interface in no particular order. | 
**dns_domain** | **str** | DnsDomain is the domain that this system appears to be in on this interface. | [optional] 
**dns_servers** | **list[str]** | DnsServers is a list of DNS server that hsould be used when resolving addresses via this interface. | [optional] 
**gateway** | **str** | Gateway is our best guess about the IP address that traffic forwarded through this interface should be sent to. | [optional] 
**index** | **int** | Index of the interface.  This is OS specific. | [optional] 
**name** | **str** | Name of the interface | 
**read_only** | **bool** | ReadOnly tracks if the store for this object is read-only. This flag is informational, and cannot be changed via the API. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


