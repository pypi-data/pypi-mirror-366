r'''
# cdk-library-aws-ipam

IP Address allocation management
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import constructs as _constructs_77d1e7e8


class Ipam(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.Ipam",
):
    '''Creates an IPAM.

    IPAM is a VPC feature that you can use to automate your IP address management workflows including
    assigning, tracking, troubleshooting, and auditing IP addresses across AWS Regions and accounts
    throughout your AWS Organization. For more information, see What is IPAM? in the Amazon VPC IPAM
    User Guide.

    :see: https://docs.aws.amazon.com/vpc/latest/ipam/what-is-it-ipam.html
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        operating_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: The description for the IPAM.
        :param operating_regions: The operating Regions for an IPAM. Operating Regions are AWS Regions where the IPAM is allowed to manage IP address CIDRs. IPAM only discovers and monitors resources in the AWS Regions you select as operating Regions. For more information about operating Regions, see Create an IPAM in the Amazon VPC IPAM User Guide. Default: Stack.of(this).region
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8ba2d63f685bbe6575deec58d167d61870546718c07264e1a8a1280b24e07a2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IpamProps(
            description=description, operating_regions=operating_regions, tags=tags
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="cfnIpam")
    def cfn_ipam(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnIPAM:
        '''The underlying IPAM resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnIPAM, jsii.get(self, "cfnIpam"))

    @builtins.property
    @jsii.member(jsii_name="ipamId")
    def ipam_id(self) -> builtins.str:
        '''The ID of the resulting IPAM resource.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamId"))

    @builtins.property
    @jsii.member(jsii_name="privateDefaultScopeId")
    def private_default_scope_id(self) -> builtins.str:
        '''The default private scope ID.'''
        return typing.cast(builtins.str, jsii.get(self, "privateDefaultScopeId"))

    @builtins.property
    @jsii.member(jsii_name="publicDefaultScopeId")
    def public_default_scope_id(self) -> builtins.str:
        '''The default public scope ID.'''
        return typing.cast(builtins.str, jsii.get(self, "publicDefaultScopeId"))

    @builtins.property
    @jsii.member(jsii_name="scopeCount")
    def scope_count(self) -> jsii.Number:
        '''The number of scopes in this IPAM.'''
        return typing.cast(jsii.Number, jsii.get(self, "scopeCount"))


class IpamAllocation(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamAllocation",
):
    '''An IPAM Allocation.

    In IPAM, an allocation is a CIDR assignment from an IPAM pool to another resource or IPAM pool.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ipam_pool: "IpamPool",
        cidr: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        netmask_length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ipam_pool: The IPAM pool from which you would like to allocate a CIDR.
        :param cidr: The CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        :param description: A description of the pool allocation.
        :param netmask_length: The netmask length of the CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fa99ce7cd4be95bf5598a08cb3f338b04a1086c11d147c2fdd7171fed363d00)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IpamAllocationProps(
            ipam_pool=ipam_pool,
            cidr=cidr,
            description=description,
            netmask_length=netmask_length,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="allocation")
    def allocation(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnIPAMAllocation:
        '''The underlying IPAM Allocation resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnIPAMAllocation, jsii.get(self, "allocation"))

    @builtins.property
    @jsii.member(jsii_name="ipamPoolAllocationId")
    def ipam_pool_allocation_id(self) -> builtins.str:
        '''The ID of the allocation.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamPoolAllocationId"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamAllocationProps",
    jsii_struct_bases=[],
    name_mapping={
        "ipam_pool": "ipamPool",
        "cidr": "cidr",
        "description": "description",
        "netmask_length": "netmaskLength",
    },
)
class IpamAllocationProps:
    def __init__(
        self,
        *,
        ipam_pool: "IpamPool",
        cidr: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        netmask_length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties of an IPAM Allocation.

        :param ipam_pool: The IPAM pool from which you would like to allocate a CIDR.
        :param cidr: The CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        :param description: A description of the pool allocation.
        :param netmask_length: The netmask length of the CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff5300dea2f85aaba64388d4569a4be0184ffa203eb25f9b9a6d2748d151b733)
            check_type(argname="argument ipam_pool", value=ipam_pool, expected_type=type_hints["ipam_pool"])
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument netmask_length", value=netmask_length, expected_type=type_hints["netmask_length"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ipam_pool": ipam_pool,
        }
        if cidr is not None:
            self._values["cidr"] = cidr
        if description is not None:
            self._values["description"] = description
        if netmask_length is not None:
            self._values["netmask_length"] = netmask_length

    @builtins.property
    def ipam_pool(self) -> "IpamPool":
        '''The IPAM pool from which you would like to allocate a CIDR.'''
        result = self._values.get("ipam_pool")
        assert result is not None, "Required property 'ipam_pool' is missing"
        return typing.cast("IpamPool", result)

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''The CIDR you would like to allocate from the IPAM pool. Note the following:.

        If there is no DefaultNetmaskLength allocation rule set on the pool, you must
        specify either the NetmaskLength or the CIDR.

        If the DefaultNetmaskLength allocation rule is set on the pool, you can specify
        either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule
        will be ignored.
        '''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the pool allocation.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The netmask length of the CIDR you would like to allocate from the IPAM pool. Note the following:.

        If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the
        NetmaskLength or the CIDR.

        If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the
        NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        '''
        result = self._values.get("netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamAllocationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IpamPool(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamPool",
):
    '''An IPAM Pool.

    In IPAM, a pool is a collection of contiguous IP addresses CIDRs. Pools enable you to organize your IP addresses
    according to your routing and security needs. For example, if you have separate routing and security needs for
    development and production applications, you can create a pool for each.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address_family: "IpamPoolAddressFamily",
        ipam_scope_id: builtins.str,
        allocation_default_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_max_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_min_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_resource_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_import: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        provisioned_cidrs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        source_ipam_pool_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param address_family: The address family of the pool, either IPv4 or IPv6.
        :param ipam_scope_id: The IPAM scope this pool is associated with.
        :param allocation_default_netmask_length: The default netmask length for allocations added to this pool. If, for example, the CIDR assigned to this pool is 10.0.0.0/8 and you enter 16 here, new allocations will default to 10.0.0.0/16.
        :param allocation_max_netmask_length: The maximum netmask length possible for CIDR allocations in this IPAM pool to be compliant. The maximum netmask length must be greater than the minimum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_min_netmask_length: The minimum netmask length required for CIDR allocations in this IPAM pool to be compliant. The minimum netmask length must be less than the maximum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_resource_tags: Tags that are required for resources that use CIDRs from this IPAM pool. Resources that do not have these tags will not be allowed to allocate space from the pool. If the resources have their tags changed after they have allocated space or if the allocation tagging requirements are changed on the pool, the resource may be marked as noncompliant.
        :param auto_import: If selected, IPAM will continuously look for resources within the CIDR range of this pool and automatically import them as allocations into your IPAM. The CIDRs that will be allocated for these resources must not already be allocated to other resources in order for the import to succeed. IPAM will import a CIDR regardless of its compliance with the pool's allocation rules, so a resource might be imported and subsequently marked as noncompliant. If IPAM discovers multiple CIDRs that overlap, IPAM will import the largest CIDR only. If IPAM discovers multiple CIDRs with matching CIDRs, IPAM will randomly import one of them only. A locale must be set on the pool for this feature to work.
        :param description: The description of the pool.
        :param locale: The locale of the IPAM pool. In IPAM, the locale is the AWS Region where you want to make an IPAM pool available for allocations.Only resources in the same Region as the locale of the pool can get IP address allocations from the pool. You can only allocate a CIDR for a VPC, for example, from an IPAM pool that shares a locale with the VPC’s Region. Note that once you choose a Locale for a pool, you cannot modify it. If you choose an AWS Region for locale that has not been configured as an operating Region for the IPAM, you'll get an error.
        :param provisioned_cidrs: The CIDRs provisioned to the IPAM pool. A CIDR is a representation of an IP address and its associated network mask (or netmask) and refers to a range of IP addresses
        :param source_ipam_pool_id: The ID of the source IPAM pool. You can use this option to create an IPAM pool within an existing source pool.
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b7d6bf8a48d79f75e6a4a88a20fec01b65199b09d27630ca3977a265e5a402a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IpamPoolProps(
            address_family=address_family,
            ipam_scope_id=ipam_scope_id,
            allocation_default_netmask_length=allocation_default_netmask_length,
            allocation_max_netmask_length=allocation_max_netmask_length,
            allocation_min_netmask_length=allocation_min_netmask_length,
            allocation_resource_tags=allocation_resource_tags,
            auto_import=auto_import,
            description=description,
            locale=locale,
            provisioned_cidrs=provisioned_cidrs,
            source_ipam_pool_id=source_ipam_pool_id,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="provisionCidr")
    def provision_cidr(self, cidr: builtins.str) -> None:
        '''Adds a CIDR to the pool.

        :param cidr: The CIDR to add to the pool.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1c265e3fd70099c0b143894ffa4de95ea54a64372020a96f92e4838b3b87fcf)
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
        return typing.cast(None, jsii.invoke(self, "provisionCidr", [cidr]))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''The ARN of the resulting IPAM Pool resource.'''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="ipamArn")
    def ipam_arn(self) -> builtins.str:
        '''The ARN of the IPAM this pool belongs to.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamArn"))

    @builtins.property
    @jsii.member(jsii_name="ipamPoolId")
    def ipam_pool_id(self) -> builtins.str:
        '''The ID of the resulting IPAM Pool resource.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamPoolId"))

    @builtins.property
    @jsii.member(jsii_name="ipamScopeArn")
    def ipam_scope_arn(self) -> builtins.str:
        '''The ARN of the scope of the IPAM Pool.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamScopeArn"))

    @builtins.property
    @jsii.member(jsii_name="ipamScopeType")
    def ipam_scope_type(self) -> builtins.str:
        '''The IPAM scope type (public or private) of the scope of the IPAM Pool.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamScopeType"))

    @builtins.property
    @jsii.member(jsii_name="pool")
    def pool(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool:
        '''The underlying IPAM Pool resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool, jsii.get(self, "pool"))

    @builtins.property
    @jsii.member(jsii_name="poolDepth")
    def pool_depth(self) -> jsii.Number:
        '''The depth of pools in your IPAM pool.'''
        return typing.cast(jsii.Number, jsii.get(self, "poolDepth"))

    @builtins.property
    @jsii.member(jsii_name="provisionedCidrs")
    def provisioned_cidrs(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty]:
        '''The provisioned CIDRs for this pool.'''
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty], jsii.get(self, "provisionedCidrs"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        '''The state of the IPAM pool.'''
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="stateMessage")
    def state_message(self) -> builtins.str:
        '''A message related to the failed creation of an IPAM pool.'''
        return typing.cast(builtins.str, jsii.get(self, "stateMessage"))

    @builtins.property
    @jsii.member(jsii_name="allocationDefaultNetmaskLength")
    def allocation_default_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The default netmask length for allocations added to this pool.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocationDefaultNetmaskLength"))


@jsii.enum(jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamPoolAddressFamily")
class IpamPoolAddressFamily(enum.Enum):
    IPV4 = "IPV4"
    IPV6 = "IPV6"


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamPoolProps",
    jsii_struct_bases=[],
    name_mapping={
        "address_family": "addressFamily",
        "ipam_scope_id": "ipamScopeId",
        "allocation_default_netmask_length": "allocationDefaultNetmaskLength",
        "allocation_max_netmask_length": "allocationMaxNetmaskLength",
        "allocation_min_netmask_length": "allocationMinNetmaskLength",
        "allocation_resource_tags": "allocationResourceTags",
        "auto_import": "autoImport",
        "description": "description",
        "locale": "locale",
        "provisioned_cidrs": "provisionedCidrs",
        "source_ipam_pool_id": "sourceIpamPoolId",
        "tags": "tags",
    },
)
class IpamPoolProps:
    def __init__(
        self,
        *,
        address_family: IpamPoolAddressFamily,
        ipam_scope_id: builtins.str,
        allocation_default_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_max_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_min_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_resource_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_import: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        provisioned_cidrs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        source_ipam_pool_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties of an IPAM Pool.

        :param address_family: The address family of the pool, either IPv4 or IPv6.
        :param ipam_scope_id: The IPAM scope this pool is associated with.
        :param allocation_default_netmask_length: The default netmask length for allocations added to this pool. If, for example, the CIDR assigned to this pool is 10.0.0.0/8 and you enter 16 here, new allocations will default to 10.0.0.0/16.
        :param allocation_max_netmask_length: The maximum netmask length possible for CIDR allocations in this IPAM pool to be compliant. The maximum netmask length must be greater than the minimum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_min_netmask_length: The minimum netmask length required for CIDR allocations in this IPAM pool to be compliant. The minimum netmask length must be less than the maximum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_resource_tags: Tags that are required for resources that use CIDRs from this IPAM pool. Resources that do not have these tags will not be allowed to allocate space from the pool. If the resources have their tags changed after they have allocated space or if the allocation tagging requirements are changed on the pool, the resource may be marked as noncompliant.
        :param auto_import: If selected, IPAM will continuously look for resources within the CIDR range of this pool and automatically import them as allocations into your IPAM. The CIDRs that will be allocated for these resources must not already be allocated to other resources in order for the import to succeed. IPAM will import a CIDR regardless of its compliance with the pool's allocation rules, so a resource might be imported and subsequently marked as noncompliant. If IPAM discovers multiple CIDRs that overlap, IPAM will import the largest CIDR only. If IPAM discovers multiple CIDRs with matching CIDRs, IPAM will randomly import one of them only. A locale must be set on the pool for this feature to work.
        :param description: The description of the pool.
        :param locale: The locale of the IPAM pool. In IPAM, the locale is the AWS Region where you want to make an IPAM pool available for allocations.Only resources in the same Region as the locale of the pool can get IP address allocations from the pool. You can only allocate a CIDR for a VPC, for example, from an IPAM pool that shares a locale with the VPC’s Region. Note that once you choose a Locale for a pool, you cannot modify it. If you choose an AWS Region for locale that has not been configured as an operating Region for the IPAM, you'll get an error.
        :param provisioned_cidrs: The CIDRs provisioned to the IPAM pool. A CIDR is a representation of an IP address and its associated network mask (or netmask) and refers to a range of IP addresses
        :param source_ipam_pool_id: The ID of the source IPAM pool. You can use this option to create an IPAM pool within an existing source pool.
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b46a7ccb9fc412b41a87760ab612625cfc3669d44d0e331cd061d741c647c634)
            check_type(argname="argument address_family", value=address_family, expected_type=type_hints["address_family"])
            check_type(argname="argument ipam_scope_id", value=ipam_scope_id, expected_type=type_hints["ipam_scope_id"])
            check_type(argname="argument allocation_default_netmask_length", value=allocation_default_netmask_length, expected_type=type_hints["allocation_default_netmask_length"])
            check_type(argname="argument allocation_max_netmask_length", value=allocation_max_netmask_length, expected_type=type_hints["allocation_max_netmask_length"])
            check_type(argname="argument allocation_min_netmask_length", value=allocation_min_netmask_length, expected_type=type_hints["allocation_min_netmask_length"])
            check_type(argname="argument allocation_resource_tags", value=allocation_resource_tags, expected_type=type_hints["allocation_resource_tags"])
            check_type(argname="argument auto_import", value=auto_import, expected_type=type_hints["auto_import"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument locale", value=locale, expected_type=type_hints["locale"])
            check_type(argname="argument provisioned_cidrs", value=provisioned_cidrs, expected_type=type_hints["provisioned_cidrs"])
            check_type(argname="argument source_ipam_pool_id", value=source_ipam_pool_id, expected_type=type_hints["source_ipam_pool_id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address_family": address_family,
            "ipam_scope_id": ipam_scope_id,
        }
        if allocation_default_netmask_length is not None:
            self._values["allocation_default_netmask_length"] = allocation_default_netmask_length
        if allocation_max_netmask_length is not None:
            self._values["allocation_max_netmask_length"] = allocation_max_netmask_length
        if allocation_min_netmask_length is not None:
            self._values["allocation_min_netmask_length"] = allocation_min_netmask_length
        if allocation_resource_tags is not None:
            self._values["allocation_resource_tags"] = allocation_resource_tags
        if auto_import is not None:
            self._values["auto_import"] = auto_import
        if description is not None:
            self._values["description"] = description
        if locale is not None:
            self._values["locale"] = locale
        if provisioned_cidrs is not None:
            self._values["provisioned_cidrs"] = provisioned_cidrs
        if source_ipam_pool_id is not None:
            self._values["source_ipam_pool_id"] = source_ipam_pool_id
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def address_family(self) -> IpamPoolAddressFamily:
        '''The address family of the pool, either IPv4 or IPv6.'''
        result = self._values.get("address_family")
        assert result is not None, "Required property 'address_family' is missing"
        return typing.cast(IpamPoolAddressFamily, result)

    @builtins.property
    def ipam_scope_id(self) -> builtins.str:
        '''The IPAM scope this pool is associated with.'''
        result = self._values.get("ipam_scope_id")
        assert result is not None, "Required property 'ipam_scope_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocation_default_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The default netmask length for allocations added to this pool.

        If, for example, the CIDR assigned to this pool is 10.0.0.0/8 and you enter 16 here,
        new allocations will default to 10.0.0.0/16.
        '''
        result = self._values.get("allocation_default_netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allocation_max_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The maximum netmask length possible for CIDR allocations in this IPAM pool to be compliant.

        The maximum netmask length must be greater than the minimum netmask length.
        Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        '''
        result = self._values.get("allocation_max_netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allocation_min_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The minimum netmask length required for CIDR allocations in this IPAM pool to be compliant.

        The minimum netmask length must be less than the maximum netmask length.
        Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        '''
        result = self._values.get("allocation_min_netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allocation_resource_tags(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''Tags that are required for resources that use CIDRs from this IPAM pool.

        Resources that do not have these tags will not be allowed to allocate space from the pool.
        If the resources have their tags changed after they have allocated space or if the allocation
        tagging requirements are changed on the pool, the resource may be marked as noncompliant.
        '''
        result = self._values.get("allocation_resource_tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    @builtins.property
    def auto_import(self) -> typing.Optional[builtins.bool]:
        '''If selected, IPAM will continuously look for resources within the CIDR range of this pool and automatically import them as allocations into your IPAM.

        The CIDRs that will be allocated for these resources must not already be allocated
        to other resources in order for the import to succeed. IPAM will import a CIDR regardless of its compliance with the
        pool's allocation rules, so a resource might be imported and subsequently marked as noncompliant. If IPAM discovers
        multiple CIDRs that overlap, IPAM will import the largest CIDR only. If IPAM discovers multiple CIDRs with matching
        CIDRs, IPAM will randomly import one of them only.

        A locale must be set on the pool for this feature to work.
        '''
        result = self._values.get("auto_import")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the pool.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''The locale of the IPAM pool.

        In IPAM, the locale is the AWS Region where you want to make an IPAM pool available
        for allocations.Only resources in the same Region as the locale of the pool can get IP address allocations from the pool.
        You can only allocate a CIDR for a VPC, for example, from an IPAM pool that shares a locale with the VPC’s Region.
        Note that once you choose a Locale for a pool, you cannot modify it. If you choose an AWS Region for locale that has
        not been configured as an operating Region for the IPAM, you'll get an error.
        '''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provisioned_cidrs(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty]]:
        '''The CIDRs provisioned to the IPAM pool.

        A CIDR is a representation of an IP address and its associated network mask
        (or netmask) and refers to a range of IP addresses
        '''
        result = self._values.get("provisioned_cidrs")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty]], result)

    @builtins.property
    def source_ipam_pool_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the source IPAM pool.

        You can use this option to create an IPAM pool within an existing source pool.
        '''
        result = self._values.get("source_ipam_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''The key/value combination of tags to assign to the resource.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamPoolProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "operating_regions": "operatingRegions",
        "tags": "tags",
    },
)
class IpamProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        operating_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties of the IPAM.

        :param description: The description for the IPAM.
        :param operating_regions: The operating Regions for an IPAM. Operating Regions are AWS Regions where the IPAM is allowed to manage IP address CIDRs. IPAM only discovers and monitors resources in the AWS Regions you select as operating Regions. For more information about operating Regions, see Create an IPAM in the Amazon VPC IPAM User Guide. Default: Stack.of(this).region
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7bbda6d6384035af0ea26e2228f9c57777a682864c4b38c2eb52aa580d73662)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument operating_regions", value=operating_regions, expected_type=type_hints["operating_regions"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if operating_regions is not None:
            self._values["operating_regions"] = operating_regions
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for the IPAM.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operating_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The operating Regions for an IPAM.

        Operating Regions are AWS Regions where the IPAM is allowed to manage IP address CIDRs. IPAM only
        discovers and monitors resources in the AWS Regions you select as operating Regions.

        For more information about operating Regions, see Create an IPAM in the Amazon VPC IPAM User Guide.

        :default: Stack.of(this).region

        :see: https://vpc/latest/ipam/create-ipam.html
        '''
        result = self._values.get("operating_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''The key/value combination of tags to assign to the resource.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IpamScope(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamScope",
):
    '''An IPAM Scope.

    In IPAM, a scope is the highest-level container within IPAM. An IPAM contains two default scopes.
    Each scope represents the IP space for a single network. The private scope is intended for all private
    IP address space. The public scope is intended for all public IP address space. Scopes enable you to
    reuse IP addresses across multiple unconnected networks without causing IP address overlap or conflict.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ipam: Ipam,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ipam: The IPAM for which you're creating the scope.
        :param description: The description of the scope.
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e74e1e5f97191ddfd9ded55a792d72a96d2153911a3a3b8ca4627de12b11875)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IpamScopeProps(ipam=ipam, description=description, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''The ARN of the resulting IPAM Scope resource.'''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="ipamArn")
    def ipam_arn(self) -> builtins.str:
        '''The ARN of the IPAM this scope belongs to.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamArn"))

    @builtins.property
    @jsii.member(jsii_name="ipamScopeId")
    def ipam_scope_id(self) -> builtins.str:
        '''The ID of the resulting IPAM Scope resource.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamScopeId"))

    @builtins.property
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> _aws_cdk_ceddda9d.IResolvable:
        '''Indicates whether the scope is the default scope for the IPAM.'''
        return typing.cast(_aws_cdk_ceddda9d.IResolvable, jsii.get(self, "isDefault"))

    @builtins.property
    @jsii.member(jsii_name="poolCount")
    def pool_count(self) -> jsii.Number:
        '''The number of pools in the scope.'''
        return typing.cast(jsii.Number, jsii.get(self, "poolCount"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnIPAMScope:
        '''The underlying IPAM Scope resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnIPAMScope, jsii.get(self, "scope"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamScopeProps",
    jsii_struct_bases=[],
    name_mapping={"ipam": "ipam", "description": "description", "tags": "tags"},
)
class IpamScopeProps:
    def __init__(
        self,
        *,
        ipam: Ipam,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties of an IPAM Scope.

        :param ipam: The IPAM for which you're creating the scope.
        :param description: The description of the scope.
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__860989b1a831232f8ae9f8866098b2fd2676ea9c638158a8e875e1cfbe2b4d7d)
            check_type(argname="argument ipam", value=ipam, expected_type=type_hints["ipam"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ipam": ipam,
        }
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def ipam(self) -> Ipam:
        '''The IPAM for which you're creating the scope.'''
        result = self._values.get("ipam")
        assert result is not None, "Required property 'ipam' is missing"
        return typing.cast(Ipam, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the scope.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''The key/value combination of tags to assign to the resource.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamScopeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Ipam",
    "IpamAllocation",
    "IpamAllocationProps",
    "IpamPool",
    "IpamPoolAddressFamily",
    "IpamPoolProps",
    "IpamProps",
    "IpamScope",
    "IpamScopeProps",
]

publication.publish()

def _typecheckingstub__a8ba2d63f685bbe6575deec58d167d61870546718c07264e1a8a1280b24e07a2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    operating_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fa99ce7cd4be95bf5598a08cb3f338b04a1086c11d147c2fdd7171fed363d00(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ipam_pool: IpamPool,
    cidr: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    netmask_length: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff5300dea2f85aaba64388d4569a4be0184ffa203eb25f9b9a6d2748d151b733(
    *,
    ipam_pool: IpamPool,
    cidr: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    netmask_length: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b7d6bf8a48d79f75e6a4a88a20fec01b65199b09d27630ca3977a265e5a402a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address_family: IpamPoolAddressFamily,
    ipam_scope_id: builtins.str,
    allocation_default_netmask_length: typing.Optional[jsii.Number] = None,
    allocation_max_netmask_length: typing.Optional[jsii.Number] = None,
    allocation_min_netmask_length: typing.Optional[jsii.Number] = None,
    allocation_resource_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    auto_import: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    provisioned_cidrs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    source_ipam_pool_id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1c265e3fd70099c0b143894ffa4de95ea54a64372020a96f92e4838b3b87fcf(
    cidr: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46a7ccb9fc412b41a87760ab612625cfc3669d44d0e331cd061d741c647c634(
    *,
    address_family: IpamPoolAddressFamily,
    ipam_scope_id: builtins.str,
    allocation_default_netmask_length: typing.Optional[jsii.Number] = None,
    allocation_max_netmask_length: typing.Optional[jsii.Number] = None,
    allocation_min_netmask_length: typing.Optional[jsii.Number] = None,
    allocation_resource_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    auto_import: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    provisioned_cidrs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool.ProvisionedCidrProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    source_ipam_pool_id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7bbda6d6384035af0ea26e2228f9c57777a682864c4b38c2eb52aa580d73662(
    *,
    description: typing.Optional[builtins.str] = None,
    operating_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e74e1e5f97191ddfd9ded55a792d72a96d2153911a3a3b8ca4627de12b11875(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ipam: Ipam,
    description: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__860989b1a831232f8ae9f8866098b2fd2676ea9c638158a8e875e1cfbe2b4d7d(
    *,
    ipam: Ipam,
    description: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
