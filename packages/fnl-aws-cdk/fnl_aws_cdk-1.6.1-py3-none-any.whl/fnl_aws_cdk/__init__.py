r'''
# Will be replacing this with project documentation
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
import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_codeguruprofiler as _aws_cdk_aws_codeguruprofiler_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import constructs as _constructs_77d1e7e8


class FnlApplicationLoadBalancer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlApplicationLoadBalancer",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        log_bucket_name: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
        client_keep_alive: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        desync_mitigation_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.DesyncMitigationMode] = None,
        drop_invalid_header_fields: typing.Optional[builtins.bool] = None,
        http2_enabled: typing.Optional[builtins.bool] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        preserve_host_header: typing.Optional[builtins.bool] = None,
        preserve_xff_client_port: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        waf_fail_open: typing.Optional[builtins.bool] = None,
        x_amzn_tls_version_and_cipher_suite_headers: typing.Optional[builtins.bool] = None,
        xff_header_processing_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.XffHeaderProcessingMode] = None,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cross_zone_enabled: typing.Optional[builtins.bool] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        deny_all_igw_traffic: typing.Optional[builtins.bool] = None,
        internet_facing: typing.Optional[builtins.bool] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        minimum_capacity_unit: typing.Optional[jsii.Number] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param log_bucket_name: 
        :param program: 
        :param project: 
        :param tier: 
        :param client_keep_alive: The client keep alive duration. The valid range is 60 to 604800 seconds (1 minute to 7 days). Default: - Duration.seconds(3600)
        :param desync_mitigation_mode: Determines how the load balancer handles requests that might pose a security risk to your application. Default: DesyncMitigationMode.DEFENSIVE
        :param drop_invalid_header_fields: Indicates whether HTTP headers with invalid header fields are removed by the load balancer (true) or routed to targets (false). Default: false
        :param http2_enabled: Indicates whether HTTP/2 is enabled. Default: true
        :param idle_timeout: The load balancer idle timeout, in seconds. Default: 60
        :param ip_address_type: The type of IP addresses to use. Default: IpAddressType.IPV4
        :param preserve_host_header: Indicates whether the Application Load Balancer should preserve the host header in the HTTP request and send it to the target without any change. Default: false
        :param preserve_xff_client_port: Indicates whether the X-Forwarded-For header should preserve the source port that the client used to connect to the load balancer. Default: false
        :param security_group: Security group to associate with this load balancer. Default: A security group is created
        :param waf_fail_open: Indicates whether to allow a WAF-enabled load balancer to route requests to targets if it is unable to forward the request to AWS WAF. Default: false
        :param x_amzn_tls_version_and_cipher_suite_headers: Indicates whether the two headers (x-amzn-tls-version and x-amzn-tls-cipher-suite), which contain information about the negotiated TLS version and cipher suite, are added to the client request before sending it to the target. The x-amzn-tls-version header has information about the TLS protocol version negotiated with the client, and the x-amzn-tls-cipher-suite header has information about the cipher suite negotiated with the client. Both headers are in OpenSSL format. Default: false
        :param xff_header_processing_mode: Enables you to modify, preserve, or remove the X-Forwarded-For header in the HTTP request before the Application Load Balancer sends the request to the target. Default: XffHeaderProcessingMode.APPEND
        :param vpc: The VPC network to place the load balancer in.
        :param cross_zone_enabled: Indicates whether cross-zone load balancing is enabled. Default: - false for Network Load Balancers and true for Application Load Balancers. This can not be ``false`` for Application Load Balancers.
        :param deletion_protection: Indicates whether deletion protection is enabled. Default: false
        :param deny_all_igw_traffic: Indicates whether the load balancer blocks traffic through the Internet Gateway (IGW). Default: - false for internet-facing load balancers and true for internal load balancers
        :param internet_facing: Whether the load balancer has an internet-routable address. Default: false
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param minimum_capacity_unit: The minimum capacity (LCU) for a load balancer. Default: undefined - ELB default is 0 LCU
        :param vpc_subnets: Which subnets place the load balancer in. Default: - the Vpc default strategy.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13150ce831166ee97725a053aacabfb0d1c7c9fefa771701160d406b6b11a7e4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FnlApplicationLoadBalancerProps(
            log_bucket_name=log_bucket_name,
            program=program,
            project=project,
            tier=tier,
            client_keep_alive=client_keep_alive,
            desync_mitigation_mode=desync_mitigation_mode,
            drop_invalid_header_fields=drop_invalid_header_fields,
            http2_enabled=http2_enabled,
            idle_timeout=idle_timeout,
            ip_address_type=ip_address_type,
            preserve_host_header=preserve_host_header,
            preserve_xff_client_port=preserve_xff_client_port,
            security_group=security_group,
            waf_fail_open=waf_fail_open,
            x_amzn_tls_version_and_cipher_suite_headers=x_amzn_tls_version_and_cipher_suite_headers,
            xff_header_processing_mode=xff_header_processing_mode,
            vpc=vpc,
            cross_zone_enabled=cross_zone_enabled,
            deletion_protection=deletion_protection,
            deny_all_igw_traffic=deny_all_igw_traffic,
            internet_facing=internet_facing,
            load_balancer_name=load_balancer_name,
            minimum_capacity_unit=minimum_capacity_unit,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="fnl-aws-cdk.FnlApplicationLoadBalancerProps",
    jsii_struct_bases=[
        _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancerProps
    ],
    name_mapping={
        "vpc": "vpc",
        "cross_zone_enabled": "crossZoneEnabled",
        "deletion_protection": "deletionProtection",
        "deny_all_igw_traffic": "denyAllIgwTraffic",
        "internet_facing": "internetFacing",
        "load_balancer_name": "loadBalancerName",
        "minimum_capacity_unit": "minimumCapacityUnit",
        "vpc_subnets": "vpcSubnets",
        "client_keep_alive": "clientKeepAlive",
        "desync_mitigation_mode": "desyncMitigationMode",
        "drop_invalid_header_fields": "dropInvalidHeaderFields",
        "http2_enabled": "http2Enabled",
        "idle_timeout": "idleTimeout",
        "ip_address_type": "ipAddressType",
        "preserve_host_header": "preserveHostHeader",
        "preserve_xff_client_port": "preserveXffClientPort",
        "security_group": "securityGroup",
        "waf_fail_open": "wafFailOpen",
        "x_amzn_tls_version_and_cipher_suite_headers": "xAmznTlsVersionAndCipherSuiteHeaders",
        "xff_header_processing_mode": "xffHeaderProcessingMode",
        "log_bucket_name": "logBucketName",
        "program": "program",
        "project": "project",
        "tier": "tier",
    },
)
class FnlApplicationLoadBalancerProps(
    _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancerProps,
):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cross_zone_enabled: typing.Optional[builtins.bool] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        deny_all_igw_traffic: typing.Optional[builtins.bool] = None,
        internet_facing: typing.Optional[builtins.bool] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        minimum_capacity_unit: typing.Optional[jsii.Number] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        client_keep_alive: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        desync_mitigation_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.DesyncMitigationMode] = None,
        drop_invalid_header_fields: typing.Optional[builtins.bool] = None,
        http2_enabled: typing.Optional[builtins.bool] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        preserve_host_header: typing.Optional[builtins.bool] = None,
        preserve_xff_client_port: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        waf_fail_open: typing.Optional[builtins.bool] = None,
        x_amzn_tls_version_and_cipher_suite_headers: typing.Optional[builtins.bool] = None,
        xff_header_processing_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.XffHeaderProcessingMode] = None,
        log_bucket_name: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
    ) -> None:
        '''
        :param vpc: The VPC network to place the load balancer in.
        :param cross_zone_enabled: Indicates whether cross-zone load balancing is enabled. Default: - false for Network Load Balancers and true for Application Load Balancers. This can not be ``false`` for Application Load Balancers.
        :param deletion_protection: Indicates whether deletion protection is enabled. Default: false
        :param deny_all_igw_traffic: Indicates whether the load balancer blocks traffic through the Internet Gateway (IGW). Default: - false for internet-facing load balancers and true for internal load balancers
        :param internet_facing: Whether the load balancer has an internet-routable address. Default: false
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param minimum_capacity_unit: The minimum capacity (LCU) for a load balancer. Default: undefined - ELB default is 0 LCU
        :param vpc_subnets: Which subnets place the load balancer in. Default: - the Vpc default strategy.
        :param client_keep_alive: The client keep alive duration. The valid range is 60 to 604800 seconds (1 minute to 7 days). Default: - Duration.seconds(3600)
        :param desync_mitigation_mode: Determines how the load balancer handles requests that might pose a security risk to your application. Default: DesyncMitigationMode.DEFENSIVE
        :param drop_invalid_header_fields: Indicates whether HTTP headers with invalid header fields are removed by the load balancer (true) or routed to targets (false). Default: false
        :param http2_enabled: Indicates whether HTTP/2 is enabled. Default: true
        :param idle_timeout: The load balancer idle timeout, in seconds. Default: 60
        :param ip_address_type: The type of IP addresses to use. Default: IpAddressType.IPV4
        :param preserve_host_header: Indicates whether the Application Load Balancer should preserve the host header in the HTTP request and send it to the target without any change. Default: false
        :param preserve_xff_client_port: Indicates whether the X-Forwarded-For header should preserve the source port that the client used to connect to the load balancer. Default: false
        :param security_group: Security group to associate with this load balancer. Default: A security group is created
        :param waf_fail_open: Indicates whether to allow a WAF-enabled load balancer to route requests to targets if it is unable to forward the request to AWS WAF. Default: false
        :param x_amzn_tls_version_and_cipher_suite_headers: Indicates whether the two headers (x-amzn-tls-version and x-amzn-tls-cipher-suite), which contain information about the negotiated TLS version and cipher suite, are added to the client request before sending it to the target. The x-amzn-tls-version header has information about the TLS protocol version negotiated with the client, and the x-amzn-tls-cipher-suite header has information about the cipher suite negotiated with the client. Both headers are in OpenSSL format. Default: false
        :param xff_header_processing_mode: Enables you to modify, preserve, or remove the X-Forwarded-For header in the HTTP request before the Application Load Balancer sends the request to the target. Default: XffHeaderProcessingMode.APPEND
        :param log_bucket_name: 
        :param program: 
        :param project: 
        :param tier: 
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9382dfd5cf2bf47c34d25a6822f705db560b63e011a772ea5ced0e684577823e)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cross_zone_enabled", value=cross_zone_enabled, expected_type=type_hints["cross_zone_enabled"])
            check_type(argname="argument deletion_protection", value=deletion_protection, expected_type=type_hints["deletion_protection"])
            check_type(argname="argument deny_all_igw_traffic", value=deny_all_igw_traffic, expected_type=type_hints["deny_all_igw_traffic"])
            check_type(argname="argument internet_facing", value=internet_facing, expected_type=type_hints["internet_facing"])
            check_type(argname="argument load_balancer_name", value=load_balancer_name, expected_type=type_hints["load_balancer_name"])
            check_type(argname="argument minimum_capacity_unit", value=minimum_capacity_unit, expected_type=type_hints["minimum_capacity_unit"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument client_keep_alive", value=client_keep_alive, expected_type=type_hints["client_keep_alive"])
            check_type(argname="argument desync_mitigation_mode", value=desync_mitigation_mode, expected_type=type_hints["desync_mitigation_mode"])
            check_type(argname="argument drop_invalid_header_fields", value=drop_invalid_header_fields, expected_type=type_hints["drop_invalid_header_fields"])
            check_type(argname="argument http2_enabled", value=http2_enabled, expected_type=type_hints["http2_enabled"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument preserve_host_header", value=preserve_host_header, expected_type=type_hints["preserve_host_header"])
            check_type(argname="argument preserve_xff_client_port", value=preserve_xff_client_port, expected_type=type_hints["preserve_xff_client_port"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument waf_fail_open", value=waf_fail_open, expected_type=type_hints["waf_fail_open"])
            check_type(argname="argument x_amzn_tls_version_and_cipher_suite_headers", value=x_amzn_tls_version_and_cipher_suite_headers, expected_type=type_hints["x_amzn_tls_version_and_cipher_suite_headers"])
            check_type(argname="argument xff_header_processing_mode", value=xff_header_processing_mode, expected_type=type_hints["xff_header_processing_mode"])
            check_type(argname="argument log_bucket_name", value=log_bucket_name, expected_type=type_hints["log_bucket_name"])
            check_type(argname="argument program", value=program, expected_type=type_hints["program"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
            "log_bucket_name": log_bucket_name,
            "program": program,
            "project": project,
            "tier": tier,
        }
        if cross_zone_enabled is not None:
            self._values["cross_zone_enabled"] = cross_zone_enabled
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if deny_all_igw_traffic is not None:
            self._values["deny_all_igw_traffic"] = deny_all_igw_traffic
        if internet_facing is not None:
            self._values["internet_facing"] = internet_facing
        if load_balancer_name is not None:
            self._values["load_balancer_name"] = load_balancer_name
        if minimum_capacity_unit is not None:
            self._values["minimum_capacity_unit"] = minimum_capacity_unit
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if client_keep_alive is not None:
            self._values["client_keep_alive"] = client_keep_alive
        if desync_mitigation_mode is not None:
            self._values["desync_mitigation_mode"] = desync_mitigation_mode
        if drop_invalid_header_fields is not None:
            self._values["drop_invalid_header_fields"] = drop_invalid_header_fields
        if http2_enabled is not None:
            self._values["http2_enabled"] = http2_enabled
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if preserve_host_header is not None:
            self._values["preserve_host_header"] = preserve_host_header
        if preserve_xff_client_port is not None:
            self._values["preserve_xff_client_port"] = preserve_xff_client_port
        if security_group is not None:
            self._values["security_group"] = security_group
        if waf_fail_open is not None:
            self._values["waf_fail_open"] = waf_fail_open
        if x_amzn_tls_version_and_cipher_suite_headers is not None:
            self._values["x_amzn_tls_version_and_cipher_suite_headers"] = x_amzn_tls_version_and_cipher_suite_headers
        if xff_header_processing_mode is not None:
            self._values["xff_header_processing_mode"] = xff_header_processing_mode

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC network to place the load balancer in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cross_zone_enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether cross-zone load balancing is enabled.

        :default:

        - false for Network Load Balancers and true for Application Load Balancers.
        This can not be ``false`` for Application Load Balancers.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-loadbalancer-loadbalancerattribute.html
        '''
        result = self._values.get("cross_zone_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether deletion protection is enabled.

        :default: false
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deny_all_igw_traffic(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the load balancer blocks traffic through the Internet Gateway (IGW).

        :default: - false for internet-facing load balancers and true for internal load balancers
        '''
        result = self._values.get("deny_all_igw_traffic")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def internet_facing(self) -> typing.Optional[builtins.bool]:
        '''Whether the load balancer has an internet-routable address.

        :default: false
        '''
        result = self._values.get("internet_facing")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def load_balancer_name(self) -> typing.Optional[builtins.str]:
        '''Name of the load balancer.

        :default: - Automatically generated name.
        '''
        result = self._values.get("load_balancer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum_capacity_unit(self) -> typing.Optional[jsii.Number]:
        '''The minimum capacity (LCU) for a load balancer.

        :default: undefined - ELB default is 0 LCU

        :see: https://exampleloadbalancer.com/ondemand_capacity_reservation_calculator.html
        '''
        result = self._values.get("minimum_capacity_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Which subnets place the load balancer in.

        :default: - the Vpc default strategy.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def client_keep_alive(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The client keep alive duration.

        The valid range is 60 to 604800 seconds (1 minute to 7 days).

        :default: - Duration.seconds(3600)
        '''
        result = self._values.get("client_keep_alive")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def desync_mitigation_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.DesyncMitigationMode]:
        '''Determines how the load balancer handles requests that might pose a security risk to your application.

        :default: DesyncMitigationMode.DEFENSIVE
        '''
        result = self._values.get("desync_mitigation_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.DesyncMitigationMode], result)

    @builtins.property
    def drop_invalid_header_fields(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether HTTP headers with invalid header fields are removed by the load balancer (true) or routed to targets (false).

        :default: false
        '''
        result = self._values.get("drop_invalid_header_fields")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def http2_enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether HTTP/2 is enabled.

        :default: true
        '''
        result = self._values.get("http2_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        :default: 60
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType]:
        '''The type of IP addresses to use.

        :default: IpAddressType.IPV4
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType], result)

    @builtins.property
    def preserve_host_header(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the Application Load Balancer should preserve the host header in the HTTP request and send it to the target without any change.

        :default: false
        '''
        result = self._values.get("preserve_host_header")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def preserve_xff_client_port(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the X-Forwarded-For header should preserve the source port that the client used to connect to the load balancer.

        :default: false
        '''
        result = self._values.get("preserve_xff_client_port")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security group to associate with this load balancer.

        :default: A security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def waf_fail_open(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to allow a WAF-enabled load balancer to route requests to targets if it is unable to forward the request to AWS WAF.

        :default: false
        '''
        result = self._values.get("waf_fail_open")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def x_amzn_tls_version_and_cipher_suite_headers(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Indicates whether the two headers (x-amzn-tls-version and x-amzn-tls-cipher-suite), which contain information about the negotiated TLS version and cipher suite, are added to the client request before sending it to the target.

        The x-amzn-tls-version header has information about the TLS protocol version negotiated with the client,
        and the x-amzn-tls-cipher-suite header has information about the cipher suite negotiated with the client.

        Both headers are in OpenSSL format.

        :default: false
        '''
        result = self._values.get("x_amzn_tls_version_and_cipher_suite_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def xff_header_processing_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.XffHeaderProcessingMode]:
        '''Enables you to modify, preserve, or remove the X-Forwarded-For header in the HTTP request before the Application Load Balancer sends the request to the target.

        :default: XffHeaderProcessingMode.APPEND
        '''
        result = self._values.get("xff_header_processing_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.XffHeaderProcessingMode], result)

    @builtins.property
    def log_bucket_name(self) -> builtins.str:
        result = self._values.get("log_bucket_name")
        assert result is not None, "Required property 'log_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def program(self) -> builtins.str:
        result = self._values.get("program")
        assert result is not None, "Required property 'program' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tier(self) -> builtins.str:
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FnlApplicationLoadBalancerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FnlDatabaseCluster(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlDatabaseCluster",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        master_user: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
        days_after_password_rotation: typing.Optional[jsii.Number] = None,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
        backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
        cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
        copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
        iam_authentication: typing.Optional[builtins.bool] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        instances: typing.Optional[jsii.Number] = None,
        instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
        monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_v2_auto_pause_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
        serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
        subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param master_user: The master username for accessing the database cluster.
        :param program: 
        :param project: 
        :param tier: 
        :param days_after_password_rotation: The number of days after which the password will be rotated. Default: 180
        :param engine: What kind of database to start.
        :param auto_minor_version_upgrade: Specifies whether minor engine upgrades are applied automatically to the DB cluster during the maintenance window. Default: true
        :param backtrack_window: The number of seconds to set a cluster's target backtrack window to. This feature is only supported by the Aurora MySQL database engine and cannot be enabled on existing clusters. Default: 0 seconds (no backtrack)
        :param backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - no log exports
        :param cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - logs never expire
        :param cloudwatch_logs_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - a new role is created.
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param cluster_scailability_type: (deprecated) [Misspelled] Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScailabilityType.STANDARD
        :param cluster_scalability_type: Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScalabilityType.STANDARD
        :param copy_tags_to_snapshot: Whether to copy tags to the snapshot when a snapshot is created. Default: - true
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        :param database_insights_mode: The database insights mode. Default: - DatabaseInsightsMode.STANDARD when performance insights are enabled and Amazon Aurora engine is used, otherwise not set.
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection. To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        :param domain: Directory ID for associating the DB cluster with a specific Active Directory. Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication. If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled. Default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        :param domain_role: The IAM role to be used when making API calls to the Directory Service. The role needs the AWS-managed policy ``AmazonRDSDirectoryServiceAccess`` or equivalent. Default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        :param enable_cluster_level_enhanced_monitoring: Whether to enable enhanced monitoring at the cluster level. If set to true, ``monitoringInterval`` and ``monitoringRole`` are applied to not the instances, but the cluster. ``monitoringInterval`` is required to be set if ``enableClusterLevelEnhancedMonitoring`` is set to true. Default: - When the ``monitoringInterval`` is set, enhanced monitoring is enabled for each instance.
        :param enable_data_api: Whether to enable the Data API for the cluster. Default: - false
        :param enable_local_write_forwarding: Whether read replicas can forward write operations to the writer DB instance in the DB cluster. This setting can only be enabled for Aurora MySQL 3.04 or higher, and for Aurora PostgreSQL 16.4 or higher (for version 16), 15.8 or higher (for version 15), and 14.13 or higher (for version 14). Default: false
        :param enable_performance_insights: Whether to enable Performance Insights for the DB cluster. Default: - false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set, or ``databaseInsightsMode`` is set to ``DatabaseInsightsMode.ADVANCED``.
        :param engine_lifecycle_support: The life cycle type for this DB cluster. Default: undefined - AWS RDS default setting is ``EngineLifecycleSupport.OPEN_SOURCE_RDS_EXTENDED_SUPPORT``
        :param iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
        :param instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
        :param instance_props: (deprecated) Settings for the individual instances that are launched.
        :param instances: (deprecated) How many replicas/instances to create. Has to be at least 1. Default: 2
        :param instance_update_behaviour: The ordering of updates for instances. Default: InstanceUpdateBehaviour.BULK
        :param monitoring_interval: The interval between points when Amazon RDS collects enhanced monitoring metrics. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - no enhanced monitoring
        :param monitoring_role: Role that will be used to manage DB monitoring. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - A role is automatically created for you
        :param network_type: The network type of the DB instance. Default: - IPV4
        :param parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
        :param parameters: The parameters in the DBClusterParameterGroup to create automatically. You can only specify parameterGroup or parameters but not both. You need to use a versioned engine to auto-generate a DBClusterParameterGroup. Default: - None
        :param performance_insight_encryption_key: The AWS KMS key for encryption of Performance Insights data. Default: - default master key
        :param performance_insight_retention: The amount of time, in days, to retain Performance Insights data. If you set ``databaseInsightsMode`` to ``DatabaseInsightsMode.ADVANCED``, you must set this property to ``PerformanceInsightRetention.MONTHS_15``. Default: - 7
        :param port: What port to listen on. Default: - The default for the engine is used.
        :param preferred_maintenance_window: A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: 'Sun:23:45-Mon:00:15' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param readers: A list of instances to create as cluster reader instances. Default: - no readers are created. The cluster will have a single writer/reader
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param replication_source_identifier: The Amazon Resource Name (ARN) of the source DB instance or DB cluster if this DB cluster is created as a read replica. Cannot be used with credentials. Default: - This DB Cluster is not a read replica
        :param s3_export_buckets: S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportRole`` is used. For MySQL: Default: - None
        :param s3_export_role: Role that will be associated with this DB cluster to enable S3 export. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 export feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise
        :param s3_import_buckets: S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportRole`` is used. For MySQL: Default: - None
        :param s3_import_role: Role that will be associated with this DB cluster to enable S3 import. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 import feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise
        :param security_groups: Security group. Default: - a new security group is created.
        :param serverless_v2_auto_pause_duration: Specifies the duration an Aurora Serverless v2 DB instance must be idle before Aurora attempts to automatically pause it. The duration must be between 300 seconds (5 minutes) and 86,400 seconds (24 hours). Default: - The default is 300 seconds (5 minutes).
        :param serverless_v2_max_capacity: The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on. The largest value that you can use is 256. The maximum capacity must be higher than 0.5 ACUs. Default: 2
        :param serverless_v2_min_capacity: The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on. The smallest value that you can use is 0. For Aurora versions that support the Aurora Serverless v2 auto-pause feature, the smallest value that you can use is 0. For versions that don't support Aurora Serverless v2 auto-pause, the smallest value that you can use is 0.5. Default: 0.5
        :param storage_encrypted: Whether to enable storage encryption. Default: - true if storageEncryptionKey is provided, false otherwise
        :param storage_encryption_key: The KMS key for storage encryption. If specified, ``storageEncrypted`` will be set to ``true``. Default: - if storageEncrypted is true then the default master key, no key otherwise
        :param storage_type: The storage type to be associated with the DB cluster. Default: - DBClusterStorageType.AURORA
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc: What subnets to run the RDS instances in. Must be at least 2 subnets in two different AZs.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the Vpc default strategy if not specified.
        :param writer: The instance to use for the cluster writer. Default: - required if instanceProps is not provided
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80663bd98e0c4795537932bc105df8fb18eb5e00b2365adc3fb9a61f4dbf85fe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FnlDatabaseClusterProps(
            master_user=master_user,
            program=program,
            project=project,
            tier=tier,
            days_after_password_rotation=days_after_password_rotation,
            engine=engine,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            backtrack_window=backtrack_window,
            backup=backup,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            cloudwatch_logs_retention_role=cloudwatch_logs_retention_role,
            cluster_identifier=cluster_identifier,
            cluster_scailability_type=cluster_scailability_type,
            cluster_scalability_type=cluster_scalability_type,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            credentials=credentials,
            database_insights_mode=database_insights_mode,
            default_database_name=default_database_name,
            deletion_protection=deletion_protection,
            domain=domain,
            domain_role=domain_role,
            enable_cluster_level_enhanced_monitoring=enable_cluster_level_enhanced_monitoring,
            enable_data_api=enable_data_api,
            enable_local_write_forwarding=enable_local_write_forwarding,
            enable_performance_insights=enable_performance_insights,
            engine_lifecycle_support=engine_lifecycle_support,
            iam_authentication=iam_authentication,
            instance_identifier_base=instance_identifier_base,
            instance_props=instance_props,
            instances=instances,
            instance_update_behaviour=instance_update_behaviour,
            monitoring_interval=monitoring_interval,
            monitoring_role=monitoring_role,
            network_type=network_type,
            parameter_group=parameter_group,
            parameters=parameters,
            performance_insight_encryption_key=performance_insight_encryption_key,
            performance_insight_retention=performance_insight_retention,
            port=port,
            preferred_maintenance_window=preferred_maintenance_window,
            readers=readers,
            removal_policy=removal_policy,
            replication_source_identifier=replication_source_identifier,
            s3_export_buckets=s3_export_buckets,
            s3_export_role=s3_export_role,
            s3_import_buckets=s3_import_buckets,
            s3_import_role=s3_import_role,
            security_groups=security_groups,
            serverless_v2_auto_pause_duration=serverless_v2_auto_pause_duration,
            serverless_v2_max_capacity=serverless_v2_max_capacity,
            serverless_v2_min_capacity=serverless_v2_min_capacity,
            storage_encrypted=storage_encrypted,
            storage_encryption_key=storage_encryption_key,
            storage_type=storage_type,
            subnet_group=subnet_group,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            writer=writer,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_rds_ceddda9d.DatabaseCluster:
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.DatabaseCluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="parameterGroup")
    def parameter_group(self) -> _aws_cdk_aws_rds_ceddda9d.ParameterGroup:
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.ParameterGroup, jsii.get(self, "parameterGroup"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetGroup")
    def subnet_group(self) -> _aws_cdk_aws_rds_ceddda9d.SubnetGroup:
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.SubnetGroup, jsii.get(self, "subnetGroup"))


@jsii.data_type(
    jsii_type="fnl-aws-cdk.FnlDatabaseClusterProps",
    jsii_struct_bases=[_aws_cdk_aws_rds_ceddda9d.DatabaseClusterProps],
    name_mapping={
        "engine": "engine",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "backtrack_window": "backtrackWindow",
        "backup": "backup",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "cloudwatch_logs_retention_role": "cloudwatchLogsRetentionRole",
        "cluster_identifier": "clusterIdentifier",
        "cluster_scailability_type": "clusterScailabilityType",
        "cluster_scalability_type": "clusterScalabilityType",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "credentials": "credentials",
        "database_insights_mode": "databaseInsightsMode",
        "default_database_name": "defaultDatabaseName",
        "deletion_protection": "deletionProtection",
        "domain": "domain",
        "domain_role": "domainRole",
        "enable_cluster_level_enhanced_monitoring": "enableClusterLevelEnhancedMonitoring",
        "enable_data_api": "enableDataApi",
        "enable_local_write_forwarding": "enableLocalWriteForwarding",
        "enable_performance_insights": "enablePerformanceInsights",
        "engine_lifecycle_support": "engineLifecycleSupport",
        "iam_authentication": "iamAuthentication",
        "instance_identifier_base": "instanceIdentifierBase",
        "instance_props": "instanceProps",
        "instances": "instances",
        "instance_update_behaviour": "instanceUpdateBehaviour",
        "monitoring_interval": "monitoringInterval",
        "monitoring_role": "monitoringRole",
        "network_type": "networkType",
        "parameter_group": "parameterGroup",
        "parameters": "parameters",
        "performance_insight_encryption_key": "performanceInsightEncryptionKey",
        "performance_insight_retention": "performanceInsightRetention",
        "port": "port",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "readers": "readers",
        "removal_policy": "removalPolicy",
        "replication_source_identifier": "replicationSourceIdentifier",
        "s3_export_buckets": "s3ExportBuckets",
        "s3_export_role": "s3ExportRole",
        "s3_import_buckets": "s3ImportBuckets",
        "s3_import_role": "s3ImportRole",
        "security_groups": "securityGroups",
        "serverless_v2_auto_pause_duration": "serverlessV2AutoPauseDuration",
        "serverless_v2_max_capacity": "serverlessV2MaxCapacity",
        "serverless_v2_min_capacity": "serverlessV2MinCapacity",
        "storage_encrypted": "storageEncrypted",
        "storage_encryption_key": "storageEncryptionKey",
        "storage_type": "storageType",
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "writer": "writer",
        "master_user": "masterUser",
        "program": "program",
        "project": "project",
        "tier": "tier",
        "days_after_password_rotation": "daysAfterPasswordRotation",
    },
)
class FnlDatabaseClusterProps(_aws_cdk_aws_rds_ceddda9d.DatabaseClusterProps):
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
        backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
        cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
        copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
        iam_authentication: typing.Optional[builtins.bool] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        instances: typing.Optional[jsii.Number] = None,
        instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
        monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_v2_auto_pause_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
        serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
        subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
        master_user: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
        days_after_password_rotation: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param engine: What kind of database to start.
        :param auto_minor_version_upgrade: Specifies whether minor engine upgrades are applied automatically to the DB cluster during the maintenance window. Default: true
        :param backtrack_window: The number of seconds to set a cluster's target backtrack window to. This feature is only supported by the Aurora MySQL database engine and cannot be enabled on existing clusters. Default: 0 seconds (no backtrack)
        :param backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - no log exports
        :param cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - logs never expire
        :param cloudwatch_logs_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - a new role is created.
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param cluster_scailability_type: (deprecated) [Misspelled] Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScailabilityType.STANDARD
        :param cluster_scalability_type: Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScalabilityType.STANDARD
        :param copy_tags_to_snapshot: Whether to copy tags to the snapshot when a snapshot is created. Default: - true
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        :param database_insights_mode: The database insights mode. Default: - DatabaseInsightsMode.STANDARD when performance insights are enabled and Amazon Aurora engine is used, otherwise not set.
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection. To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        :param domain: Directory ID for associating the DB cluster with a specific Active Directory. Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication. If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled. Default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        :param domain_role: The IAM role to be used when making API calls to the Directory Service. The role needs the AWS-managed policy ``AmazonRDSDirectoryServiceAccess`` or equivalent. Default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        :param enable_cluster_level_enhanced_monitoring: Whether to enable enhanced monitoring at the cluster level. If set to true, ``monitoringInterval`` and ``monitoringRole`` are applied to not the instances, but the cluster. ``monitoringInterval`` is required to be set if ``enableClusterLevelEnhancedMonitoring`` is set to true. Default: - When the ``monitoringInterval`` is set, enhanced monitoring is enabled for each instance.
        :param enable_data_api: Whether to enable the Data API for the cluster. Default: - false
        :param enable_local_write_forwarding: Whether read replicas can forward write operations to the writer DB instance in the DB cluster. This setting can only be enabled for Aurora MySQL 3.04 or higher, and for Aurora PostgreSQL 16.4 or higher (for version 16), 15.8 or higher (for version 15), and 14.13 or higher (for version 14). Default: false
        :param enable_performance_insights: Whether to enable Performance Insights for the DB cluster. Default: - false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set, or ``databaseInsightsMode`` is set to ``DatabaseInsightsMode.ADVANCED``.
        :param engine_lifecycle_support: The life cycle type for this DB cluster. Default: undefined - AWS RDS default setting is ``EngineLifecycleSupport.OPEN_SOURCE_RDS_EXTENDED_SUPPORT``
        :param iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
        :param instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
        :param instance_props: (deprecated) Settings for the individual instances that are launched.
        :param instances: (deprecated) How many replicas/instances to create. Has to be at least 1. Default: 2
        :param instance_update_behaviour: The ordering of updates for instances. Default: InstanceUpdateBehaviour.BULK
        :param monitoring_interval: The interval between points when Amazon RDS collects enhanced monitoring metrics. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - no enhanced monitoring
        :param monitoring_role: Role that will be used to manage DB monitoring. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - A role is automatically created for you
        :param network_type: The network type of the DB instance. Default: - IPV4
        :param parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
        :param parameters: The parameters in the DBClusterParameterGroup to create automatically. You can only specify parameterGroup or parameters but not both. You need to use a versioned engine to auto-generate a DBClusterParameterGroup. Default: - None
        :param performance_insight_encryption_key: The AWS KMS key for encryption of Performance Insights data. Default: - default master key
        :param performance_insight_retention: The amount of time, in days, to retain Performance Insights data. If you set ``databaseInsightsMode`` to ``DatabaseInsightsMode.ADVANCED``, you must set this property to ``PerformanceInsightRetention.MONTHS_15``. Default: - 7
        :param port: What port to listen on. Default: - The default for the engine is used.
        :param preferred_maintenance_window: A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: 'Sun:23:45-Mon:00:15' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param readers: A list of instances to create as cluster reader instances. Default: - no readers are created. The cluster will have a single writer/reader
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param replication_source_identifier: The Amazon Resource Name (ARN) of the source DB instance or DB cluster if this DB cluster is created as a read replica. Cannot be used with credentials. Default: - This DB Cluster is not a read replica
        :param s3_export_buckets: S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportRole`` is used. For MySQL: Default: - None
        :param s3_export_role: Role that will be associated with this DB cluster to enable S3 export. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 export feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise
        :param s3_import_buckets: S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportRole`` is used. For MySQL: Default: - None
        :param s3_import_role: Role that will be associated with this DB cluster to enable S3 import. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 import feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise
        :param security_groups: Security group. Default: - a new security group is created.
        :param serverless_v2_auto_pause_duration: Specifies the duration an Aurora Serverless v2 DB instance must be idle before Aurora attempts to automatically pause it. The duration must be between 300 seconds (5 minutes) and 86,400 seconds (24 hours). Default: - The default is 300 seconds (5 minutes).
        :param serverless_v2_max_capacity: The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on. The largest value that you can use is 256. The maximum capacity must be higher than 0.5 ACUs. Default: 2
        :param serverless_v2_min_capacity: The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on. The smallest value that you can use is 0. For Aurora versions that support the Aurora Serverless v2 auto-pause feature, the smallest value that you can use is 0. For versions that don't support Aurora Serverless v2 auto-pause, the smallest value that you can use is 0.5. Default: 0.5
        :param storage_encrypted: Whether to enable storage encryption. Default: - true if storageEncryptionKey is provided, false otherwise
        :param storage_encryption_key: The KMS key for storage encryption. If specified, ``storageEncrypted`` will be set to ``true``. Default: - if storageEncrypted is true then the default master key, no key otherwise
        :param storage_type: The storage type to be associated with the DB cluster. Default: - DBClusterStorageType.AURORA
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc: What subnets to run the RDS instances in. Must be at least 2 subnets in two different AZs.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the Vpc default strategy if not specified.
        :param writer: The instance to use for the cluster writer. Default: - required if instanceProps is not provided
        :param master_user: The master username for accessing the database cluster.
        :param program: 
        :param project: 
        :param tier: 
        :param days_after_password_rotation: The number of days after which the password will be rotated. Default: 180
        '''
        if isinstance(backup, dict):
            backup = _aws_cdk_aws_rds_ceddda9d.BackupProps(**backup)
        if isinstance(instance_props, dict):
            instance_props = _aws_cdk_aws_rds_ceddda9d.InstanceProps(**instance_props)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__902bd453cb25d04eae50c39a5bba0022bed12f9f4be93b8c8640b424f416c92e)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument auto_minor_version_upgrade", value=auto_minor_version_upgrade, expected_type=type_hints["auto_minor_version_upgrade"])
            check_type(argname="argument backtrack_window", value=backtrack_window, expected_type=type_hints["backtrack_window"])
            check_type(argname="argument backup", value=backup, expected_type=type_hints["backup"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument cloudwatch_logs_retention_role", value=cloudwatch_logs_retention_role, expected_type=type_hints["cloudwatch_logs_retention_role"])
            check_type(argname="argument cluster_identifier", value=cluster_identifier, expected_type=type_hints["cluster_identifier"])
            check_type(argname="argument cluster_scailability_type", value=cluster_scailability_type, expected_type=type_hints["cluster_scailability_type"])
            check_type(argname="argument cluster_scalability_type", value=cluster_scalability_type, expected_type=type_hints["cluster_scalability_type"])
            check_type(argname="argument copy_tags_to_snapshot", value=copy_tags_to_snapshot, expected_type=type_hints["copy_tags_to_snapshot"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument database_insights_mode", value=database_insights_mode, expected_type=type_hints["database_insights_mode"])
            check_type(argname="argument default_database_name", value=default_database_name, expected_type=type_hints["default_database_name"])
            check_type(argname="argument deletion_protection", value=deletion_protection, expected_type=type_hints["deletion_protection"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument domain_role", value=domain_role, expected_type=type_hints["domain_role"])
            check_type(argname="argument enable_cluster_level_enhanced_monitoring", value=enable_cluster_level_enhanced_monitoring, expected_type=type_hints["enable_cluster_level_enhanced_monitoring"])
            check_type(argname="argument enable_data_api", value=enable_data_api, expected_type=type_hints["enable_data_api"])
            check_type(argname="argument enable_local_write_forwarding", value=enable_local_write_forwarding, expected_type=type_hints["enable_local_write_forwarding"])
            check_type(argname="argument enable_performance_insights", value=enable_performance_insights, expected_type=type_hints["enable_performance_insights"])
            check_type(argname="argument engine_lifecycle_support", value=engine_lifecycle_support, expected_type=type_hints["engine_lifecycle_support"])
            check_type(argname="argument iam_authentication", value=iam_authentication, expected_type=type_hints["iam_authentication"])
            check_type(argname="argument instance_identifier_base", value=instance_identifier_base, expected_type=type_hints["instance_identifier_base"])
            check_type(argname="argument instance_props", value=instance_props, expected_type=type_hints["instance_props"])
            check_type(argname="argument instances", value=instances, expected_type=type_hints["instances"])
            check_type(argname="argument instance_update_behaviour", value=instance_update_behaviour, expected_type=type_hints["instance_update_behaviour"])
            check_type(argname="argument monitoring_interval", value=monitoring_interval, expected_type=type_hints["monitoring_interval"])
            check_type(argname="argument monitoring_role", value=monitoring_role, expected_type=type_hints["monitoring_role"])
            check_type(argname="argument network_type", value=network_type, expected_type=type_hints["network_type"])
            check_type(argname="argument parameter_group", value=parameter_group, expected_type=type_hints["parameter_group"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument performance_insight_encryption_key", value=performance_insight_encryption_key, expected_type=type_hints["performance_insight_encryption_key"])
            check_type(argname="argument performance_insight_retention", value=performance_insight_retention, expected_type=type_hints["performance_insight_retention"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument preferred_maintenance_window", value=preferred_maintenance_window, expected_type=type_hints["preferred_maintenance_window"])
            check_type(argname="argument readers", value=readers, expected_type=type_hints["readers"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_source_identifier", value=replication_source_identifier, expected_type=type_hints["replication_source_identifier"])
            check_type(argname="argument s3_export_buckets", value=s3_export_buckets, expected_type=type_hints["s3_export_buckets"])
            check_type(argname="argument s3_export_role", value=s3_export_role, expected_type=type_hints["s3_export_role"])
            check_type(argname="argument s3_import_buckets", value=s3_import_buckets, expected_type=type_hints["s3_import_buckets"])
            check_type(argname="argument s3_import_role", value=s3_import_role, expected_type=type_hints["s3_import_role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument serverless_v2_auto_pause_duration", value=serverless_v2_auto_pause_duration, expected_type=type_hints["serverless_v2_auto_pause_duration"])
            check_type(argname="argument serverless_v2_max_capacity", value=serverless_v2_max_capacity, expected_type=type_hints["serverless_v2_max_capacity"])
            check_type(argname="argument serverless_v2_min_capacity", value=serverless_v2_min_capacity, expected_type=type_hints["serverless_v2_min_capacity"])
            check_type(argname="argument storage_encrypted", value=storage_encrypted, expected_type=type_hints["storage_encrypted"])
            check_type(argname="argument storage_encryption_key", value=storage_encryption_key, expected_type=type_hints["storage_encryption_key"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
            check_type(argname="argument master_user", value=master_user, expected_type=type_hints["master_user"])
            check_type(argname="argument program", value=program, expected_type=type_hints["program"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
            check_type(argname="argument days_after_password_rotation", value=days_after_password_rotation, expected_type=type_hints["days_after_password_rotation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
            "master_user": master_user,
            "program": program,
            "project": project,
            "tier": tier,
        }
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if backtrack_window is not None:
            self._values["backtrack_window"] = backtrack_window
        if backup is not None:
            self._values["backup"] = backup
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if cloudwatch_logs_retention_role is not None:
            self._values["cloudwatch_logs_retention_role"] = cloudwatch_logs_retention_role
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_scailability_type is not None:
            self._values["cluster_scailability_type"] = cluster_scailability_type
        if cluster_scalability_type is not None:
            self._values["cluster_scalability_type"] = cluster_scalability_type
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if credentials is not None:
            self._values["credentials"] = credentials
        if database_insights_mode is not None:
            self._values["database_insights_mode"] = database_insights_mode
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if domain is not None:
            self._values["domain"] = domain
        if domain_role is not None:
            self._values["domain_role"] = domain_role
        if enable_cluster_level_enhanced_monitoring is not None:
            self._values["enable_cluster_level_enhanced_monitoring"] = enable_cluster_level_enhanced_monitoring
        if enable_data_api is not None:
            self._values["enable_data_api"] = enable_data_api
        if enable_local_write_forwarding is not None:
            self._values["enable_local_write_forwarding"] = enable_local_write_forwarding
        if enable_performance_insights is not None:
            self._values["enable_performance_insights"] = enable_performance_insights
        if engine_lifecycle_support is not None:
            self._values["engine_lifecycle_support"] = engine_lifecycle_support
        if iam_authentication is not None:
            self._values["iam_authentication"] = iam_authentication
        if instance_identifier_base is not None:
            self._values["instance_identifier_base"] = instance_identifier_base
        if instance_props is not None:
            self._values["instance_props"] = instance_props
        if instances is not None:
            self._values["instances"] = instances
        if instance_update_behaviour is not None:
            self._values["instance_update_behaviour"] = instance_update_behaviour
        if monitoring_interval is not None:
            self._values["monitoring_interval"] = monitoring_interval
        if monitoring_role is not None:
            self._values["monitoring_role"] = monitoring_role
        if network_type is not None:
            self._values["network_type"] = network_type
        if parameter_group is not None:
            self._values["parameter_group"] = parameter_group
        if parameters is not None:
            self._values["parameters"] = parameters
        if performance_insight_encryption_key is not None:
            self._values["performance_insight_encryption_key"] = performance_insight_encryption_key
        if performance_insight_retention is not None:
            self._values["performance_insight_retention"] = performance_insight_retention
        if port is not None:
            self._values["port"] = port
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if readers is not None:
            self._values["readers"] = readers
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_source_identifier is not None:
            self._values["replication_source_identifier"] = replication_source_identifier
        if s3_export_buckets is not None:
            self._values["s3_export_buckets"] = s3_export_buckets
        if s3_export_role is not None:
            self._values["s3_export_role"] = s3_export_role
        if s3_import_buckets is not None:
            self._values["s3_import_buckets"] = s3_import_buckets
        if s3_import_role is not None:
            self._values["s3_import_role"] = s3_import_role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if serverless_v2_auto_pause_duration is not None:
            self._values["serverless_v2_auto_pause_duration"] = serverless_v2_auto_pause_duration
        if serverless_v2_max_capacity is not None:
            self._values["serverless_v2_max_capacity"] = serverless_v2_max_capacity
        if serverless_v2_min_capacity is not None:
            self._values["serverless_v2_min_capacity"] = serverless_v2_min_capacity
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if storage_encryption_key is not None:
            self._values["storage_encryption_key"] = storage_encryption_key
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if subnet_group is not None:
            self._values["subnet_group"] = subnet_group
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if writer is not None:
            self._values["writer"] = writer
        if days_after_password_rotation is not None:
            self._values["days_after_password_rotation"] = days_after_password_rotation

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IClusterEngine:
        '''What kind of database to start.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IClusterEngine, result)

    @builtins.property
    def auto_minor_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether minor engine upgrades are applied automatically to the DB cluster during the maintenance window.

        :default: true
        '''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backtrack_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The number of seconds to set a cluster's target backtrack window to.

        This feature is only supported by the Aurora MySQL database engine and
        cannot be enabled on existing clusters.

        :default: 0 seconds (no backtrack)

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html
        '''
        result = self._values.get("backtrack_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def backup(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps]:
        '''Backup settings.

        :default:

        - Backup retention period for automated backups is 1 day.
        Backup preferred window is set to a 30-minute window selected at random from an
        8-hour block of time for each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html#USER_WorkingWithAutomatedBackups.BackupWindow
        '''
        result = self._values.get("backup")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - no log exports
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``Infinity``.

        :default: - logs never expire
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def cloudwatch_logs_retention_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        :default: - a new role is created.
        '''
        result = self._values.get("cloudwatch_logs_retention_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''An optional identifier for the cluster.

        :default: - A name is automatically generated.
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_scailability_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType]:
        '''(deprecated) [Misspelled] Specifies the scalability mode of the Aurora DB cluster.

        Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD.

        :default: ClusterScailabilityType.STANDARD

        :deprecated: Use clusterScalabilityType instead. This will be removed in the next major version.

        :stability: deprecated
        '''
        result = self._values.get("cluster_scailability_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType], result)

    @builtins.property
    def cluster_scalability_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType]:
        '''Specifies the scalability mode of the Aurora DB cluster.

        Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD.

        :default: ClusterScalabilityType.STANDARD
        '''
        result = self._values.get("cluster_scalability_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType], result)

    @builtins.property
    def copy_tags_to_snapshot(self) -> typing.Optional[builtins.bool]:
        '''Whether to copy tags to the snapshot when a snapshot is created.

        :default: - true
        '''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def credentials(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials]:
        '''Credentials for the administrative user.

        :default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials], result)

    @builtins.property
    def database_insights_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode]:
        '''The database insights mode.

        :default: - DatabaseInsightsMode.STANDARD when performance insights are enabled and Amazon Aurora engine is used, otherwise not set.
        '''
        result = self._values.get("database_insights_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''Name of a database which is automatically created inside the cluster.

        :default: - Database is not created in cluster.
        '''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DB cluster should have deletion protection enabled.

        :default:

        - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection.
        To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Directory ID for associating the DB cluster with a specific Active Directory.

        Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication.
        If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled.

        :default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role to be used when making API calls to the Directory Service.

        The role needs the AWS-managed policy
        ``AmazonRDSDirectoryServiceAccess`` or equivalent.

        :default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        '''
        result = self._values.get("domain_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def enable_cluster_level_enhanced_monitoring(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether to enable enhanced monitoring at the cluster level.

        If set to true, ``monitoringInterval`` and ``monitoringRole`` are applied to not the instances, but the cluster.
        ``monitoringInterval`` is required to be set if ``enableClusterLevelEnhancedMonitoring`` is set to true.

        :default: - When the ``monitoringInterval`` is set, enhanced monitoring is enabled for each instance.
        '''
        result = self._values.get("enable_cluster_level_enhanced_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_data_api(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable the Data API for the cluster.

        :default: - false
        '''
        result = self._values.get("enable_data_api")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_local_write_forwarding(self) -> typing.Optional[builtins.bool]:
        '''Whether read replicas can forward write operations to the writer DB instance in the DB cluster.

        This setting can only be enabled for Aurora MySQL 3.04 or higher, and for Aurora PostgreSQL 16.4
        or higher (for version 16), 15.8 or higher (for version 15), and 14.13 or higher (for version 14).

        :default: false

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-postgresql-write-forwarding.html
        '''
        result = self._values.get("enable_local_write_forwarding")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_performance_insights(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable Performance Insights for the DB cluster.

        :default:

        - false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set,
        or ``databaseInsightsMode`` is set to ``DatabaseInsightsMode.ADVANCED``.
        '''
        result = self._values.get("enable_performance_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def engine_lifecycle_support(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport]:
        '''The life cycle type for this DB cluster.

        :default: undefined - AWS RDS default setting is ``EngineLifecycleSupport.OPEN_SOURCE_RDS_EXTENDED_SUPPORT``

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/extended-support.html
        '''
        result = self._values.get("engine_lifecycle_support")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport], result)

    @builtins.property
    def iam_authentication(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

        :default: false
        '''
        result = self._values.get("iam_authentication")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_identifier_base(self) -> typing.Optional[builtins.str]:
        '''Base identifier for instances.

        Every replica is named by appending the replica number to this string, 1-based.

        :default:

        - clusterIdentifier is used with the word "Instance" appended.
        If clusterIdentifier is not provided, the identifier is automatically generated.
        '''
        result = self._values.get("instance_identifier_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceProps]:
        '''(deprecated) Settings for the individual instances that are launched.

        :deprecated: - use writer and readers instead

        :stability: deprecated
        '''
        result = self._values.get("instance_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceProps], result)

    @builtins.property
    def instances(self) -> typing.Optional[jsii.Number]:
        '''(deprecated) How many replicas/instances to create.

        Has to be at least 1.

        :default: 2

        :deprecated: - use writer and readers instead

        :stability: deprecated
        '''
        result = self._values.get("instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_update_behaviour(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour]:
        '''The ordering of updates for instances.

        :default: InstanceUpdateBehaviour.BULK
        '''
        result = self._values.get("instance_update_behaviour")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour], result)

    @builtins.property
    def monitoring_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The interval between points when Amazon RDS collects enhanced monitoring metrics.

        If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster,
        otherwise it is applied to the instances.

        :default: - no enhanced monitoring
        '''
        result = self._values.get("monitoring_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def monitoring_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be used to manage DB monitoring.

        If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster,
        otherwise it is applied to the instances.

        :default: - A role is automatically created for you
        '''
        result = self._values.get("monitoring_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def network_type(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType]:
        '''The network type of the DB instance.

        :default: - IPV4
        '''
        result = self._values.get("network_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType], result)

    @builtins.property
    def parameter_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup]:
        '''Additional parameters to pass to the database engine.

        :default: - No parameter group.
        '''
        result = self._values.get("parameter_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The parameters in the DBClusterParameterGroup to create automatically.

        You can only specify parameterGroup or parameters but not both.
        You need to use a versioned engine to auto-generate a DBClusterParameterGroup.

        :default: - None
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def performance_insight_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key for encryption of Performance Insights data.

        :default: - default master key
        '''
        result = self._values.get("performance_insight_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def performance_insight_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention]:
        '''The amount of time, in days, to retain Performance Insights data.

        If you set ``databaseInsightsMode`` to ``DatabaseInsightsMode.ADVANCED``, you must set this property to ``PerformanceInsightRetention.MONTHS_15``.

        :default: - 7
        '''
        result = self._values.get("performance_insight_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''What port to listen on.

        :default: - The default for the engine is used.
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC).

        Example: 'Sun:23:45-Mon:00:15'

        :default:

        - 30-minute window selected at random from an 8-hour block of time for
        each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Maintenance.html#Concepts.DBMaintenance
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]]:
        '''A list of instances to create as cluster reader instances.

        :default: - no readers are created. The cluster will have a single writer/reader
        '''
        result = self._values.get("readers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update.

        :default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_source_identifier(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the source DB instance or DB cluster if this DB cluster is created as a read replica.

        Cannot be used with credentials.

        :default: - This DB Cluster is not a read replica
        '''
        result = self._values.get("replication_source_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_export_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ExportRole`` is used.

        For MySQL:

        :default: - None

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/postgresql-s3-export.html
        '''
        result = self._values.get("s3_export_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def s3_export_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be associated with this DB cluster to enable S3 export.

        This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ExportBuckets`` is used.
        To use this property with Aurora PostgreSQL, it must be configured with the S3 export feature enabled when creating the DatabaseClusterEngine
        For MySQL:

        :default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/postgresql-s3-export.html
        '''
        result = self._values.get("s3_export_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def s3_import_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ImportRole`` is used.

        For MySQL:

        :default: - None

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Migrating.html
        '''
        result = self._values.get("s3_import_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def s3_import_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be associated with this DB cluster to enable S3 import.

        This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ImportBuckets`` is used.
        To use this property with Aurora PostgreSQL, it must be configured with the S3 import feature enabled when creating the DatabaseClusterEngine
        For MySQL:

        :default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Migrating.html
        '''
        result = self._values.get("s3_import_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security group.

        :default: - a new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def serverless_v2_auto_pause_duration(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Specifies the duration an Aurora Serverless v2 DB instance must be idle before Aurora attempts to automatically pause it.

        The duration must be between 300 seconds (5 minutes) and 86,400 seconds (24 hours).

        :default: - The default is 300 seconds (5 minutes).

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2-auto-pause.html
        '''
        result = self._values.get("serverless_v2_auto_pause_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def serverless_v2_max_capacity(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster.

        You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on.
        The largest value that you can use is 256.

        The maximum capacity must be higher than 0.5 ACUs.

        :default: 2

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html#aurora-serverless-v2.max_capacity_considerations
        '''
        result = self._values.get("serverless_v2_max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def serverless_v2_min_capacity(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster.

        You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on.
        The smallest value that you can use is 0.

        For Aurora versions that support the Aurora Serverless v2 auto-pause feature, the smallest value that you can use is 0.
        For versions that don't support Aurora Serverless v2 auto-pause, the smallest value that you can use is 0.5.

        :default: 0.5

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html#aurora-serverless-v2.min_capacity_considerations
        '''
        result = self._values.get("serverless_v2_min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable storage encryption.

        :default: - true if storageEncryptionKey is provided, false otherwise
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def storage_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key for storage encryption.

        If specified, ``storageEncrypted`` will be set to ``true``.

        :default: - if storageEncrypted is true then the default master key, no key otherwise
        '''
        result = self._values.get("storage_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def storage_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType]:
        '''The storage type to be associated with the DB cluster.

        :default: - DBClusterStorageType.AURORA
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType], result)

    @builtins.property
    def subnet_group(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup]:
        '''Existing subnet group for the cluster.

        :default: - a new subnet group will be created.
        '''
        result = self._values.get("subnet_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''What subnets to run the RDS instances in.

        Must be at least 2 subnets in two different AZs.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the instances within the VPC.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def writer(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]:
        '''The instance to use for the cluster writer.

        :default: - required if instanceProps is not provided
        '''
        result = self._values.get("writer")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance], result)

    @builtins.property
    def master_user(self) -> builtins.str:
        '''The master username for accessing the database cluster.'''
        result = self._values.get("master_user")
        assert result is not None, "Required property 'master_user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def program(self) -> builtins.str:
        result = self._values.get("program")
        assert result is not None, "Required property 'program' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tier(self) -> builtins.str:
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def days_after_password_rotation(self) -> typing.Optional[jsii.Number]:
        '''The number of days after which the password will be rotated.

        :default: 180
        '''
        result = self._values.get("days_after_password_rotation")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FnlDatabaseClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FnlDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlDomain",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        masteruser: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
        version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
        access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
        capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cold_storage_enabled: typing.Optional[builtins.bool] = None,
        custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_auto_software_update: typing.Optional[builtins.bool] = None,
        enable_version_upgrade: typing.Optional[builtins.bool] = None,
        encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enforce_https: typing.Optional[builtins.bool] = None,
        fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        node_to_node_encryption: typing.Optional[builtins.bool] = None,
        off_peak_window_enabled: typing.Optional[builtins.bool] = None,
        off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
        tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
        use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param masteruser: 
        :param program: 
        :param project: 
        :param tier: 
        :param version: The Elasticsearch/OpenSearch version that your domain will leverage.
        :param access_policies: Domain access policies. Default: - No access policies.
        :param advanced_options: Additional options to specify for the Amazon OpenSearch Service domain. Default: - no advanced options are specified
        :param automated_snapshot_start_hour: The hour in UTC during which the service takes an automated daily snapshot of the indices in the Amazon OpenSearch Service domain. Only applies for Elasticsearch versions below 5.3. Default: - Hourly automated snapshots not used
        :param capacity: The cluster capacity configuration for the Amazon OpenSearch Service domain. Default: - 1 r5.large.search data node; no dedicated master nodes.
        :param cognito_dashboards_auth: Configures Amazon OpenSearch Service to use Amazon Cognito authentication for OpenSearch Dashboards. Default: - Cognito not used for authentication to OpenSearch Dashboards.
        :param cold_storage_enabled: Whether to enable or disable cold storage on the domain. You must enable UltraWarm storage to enable cold storage. Default: - undefined
        :param custom_endpoint: To configure a custom domain configure these options. If you specify a Route53 hosted zone it will create a CNAME record and use DNS validation for the certificate Default: - no custom domain endpoint will be configured
        :param domain_name: Enforces a particular physical domain name. Default: - A name will be auto-generated.
        :param ebs: The configurations of Amazon Elastic Block Store (Amazon EBS) volumes that are attached to data nodes in the Amazon OpenSearch Service domain. Default: - 10 GiB General Purpose (SSD) volumes per node.
        :param enable_auto_software_update: Specifies whether automatic service software updates are enabled for the domain. Default: - false
        :param enable_version_upgrade: To upgrade an Amazon OpenSearch Service domain to a new version, rather than replacing the entire domain resource, use the EnableVersionUpgrade update policy. Default: - false
        :param encryption_at_rest: Encryption at rest options for the cluster. Default: - No encryption at rest
        :param enforce_https: True to require that all traffic to the domain arrive over HTTPS. Default: - false
        :param fine_grained_access_control: Specifies options for fine-grained access control. Requires Elasticsearch version 6.7 or later or OpenSearch version 1.0 or later. Enabling fine-grained access control also requires encryption of data at rest and node-to-node encryption, along with enforced HTTPS. Default: - fine-grained access control is disabled
        :param ip_address_type: Specify either dual stack or IPv4 as your IP address type. Dual stack allows you to share domain resources across IPv4 and IPv6 address types, and is the recommended option. If you set your IP address type to dual stack, you can't change your address type later. Default: - IpAddressType.IPV4
        :param logging: Configuration log publishing configuration options. Default: - No logs are published
        :param node_to_node_encryption: Specify true to enable node to node encryption. Requires Elasticsearch version 6.0 or later or OpenSearch version 1.0 or later. Default: - Node to node encryption is not enabled.
        :param off_peak_window_enabled: Options for enabling a domain's off-peak window, during which OpenSearch Service can perform mandatory configuration changes on the domain. Off-peak windows were introduced on February 16, 2023. All domains created before this date have the off-peak window disabled by default. You must manually enable and configure the off-peak window for these domains. All domains created after this date will have the off-peak window enabled by default. You can't disable the off-peak window for a domain after it's enabled. Default: - Disabled for domains created before February 16, 2023. Enabled for domains created after. Enabled if ``offPeakWindowStart`` is set.
        :param off_peak_window_start: Start time for the off-peak window, in Coordinated Universal Time (UTC). The window length will always be 10 hours, so you can't specify an end time. For example, if you specify 11:00 P.M. UTC as a start time, the end time will automatically be set to 9:00 A.M. Default: - 10:00 P.M. local time
        :param removal_policy: Policy to apply when the domain is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_groups: The list of security groups that are associated with the VPC endpoints for the domain. Only used if ``vpc`` is specified. Default: - One new security group is created.
        :param suppress_logs_resource_policy: Specify whether to create a CloudWatch Logs resource policy or not. When logging is enabled for the domain, a CloudWatch Logs resource policy is created by default. However, CloudWatch Logs supports only 10 resource policies per region. If you enable logging for several domains, it may hit the quota and cause an error. By setting this property to true, creating a resource policy is suppressed, allowing you to avoid this problem. If you set this option to true, you must create a resource policy before deployment. Default: - false
        :param tls_security_policy: The minimum TLS version required for traffic to the domain. Default: - TLSSecurityPolicy.TLS_1_2
        :param use_unsigned_basic_auth: Configures the domain so that unsigned basic auth is enabled. If no master user is provided a default master user with username ``admin`` and a dynamically generated password stored in KMS is created. The password can be retrieved by getting ``masterUserPassword`` from the domain instance. Setting this to true will also add an access policy that allows unsigned access, enable node to node encryption, encryption at rest. If conflicting settings are encountered (like disabling encryption at rest) enabling this setting will cause a failure. Default: - false
        :param vpc: Place the domain inside this VPC. Default: - Domain is not placed in a VPC.
        :param vpc_subnets: The specific vpc subnets the domain will be placed in. You must provide one subnet for each Availability Zone that your domain uses. For example, you must specify three subnet IDs for a three Availability Zone domain. Only used if ``vpc`` is specified. Default: - All private subnets.
        :param zone_awareness: The cluster zone awareness configuration for the Amazon OpenSearch Service domain. Default: - no zone awareness (1 AZ)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1774551a478936302e0e03196bb20bdab223251d49cf6559d37ce058b9840fed)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FnlOpensearchProps(
            masteruser=masteruser,
            program=program,
            project=project,
            tier=tier,
            version=version,
            access_policies=access_policies,
            advanced_options=advanced_options,
            automated_snapshot_start_hour=automated_snapshot_start_hour,
            capacity=capacity,
            cognito_dashboards_auth=cognito_dashboards_auth,
            cold_storage_enabled=cold_storage_enabled,
            custom_endpoint=custom_endpoint,
            domain_name=domain_name,
            ebs=ebs,
            enable_auto_software_update=enable_auto_software_update,
            enable_version_upgrade=enable_version_upgrade,
            encryption_at_rest=encryption_at_rest,
            enforce_https=enforce_https,
            fine_grained_access_control=fine_grained_access_control,
            ip_address_type=ip_address_type,
            logging=logging,
            node_to_node_encryption=node_to_node_encryption,
            off_peak_window_enabled=off_peak_window_enabled,
            off_peak_window_start=off_peak_window_start,
            removal_policy=removal_policy,
            security_groups=security_groups,
            suppress_logs_resource_policy=suppress_logs_resource_policy,
            tls_security_policy=tls_security_policy,
            use_unsigned_basic_auth=use_unsigned_basic_auth,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            zone_awareness=zone_awareness,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class FnlFunction(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlFunction",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        code: _aws_cdk_aws_lambda_ceddda9d.Code,
        handler: builtins.str,
        runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
        adot_instrumentation: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        application_log_level: typing.Optional[builtins.str] = None,
        application_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel] = None,
        architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        code_signing_config: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.VersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        dead_letter_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        events: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
        filesystem: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        insights_version: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion] = None,
        ipv6_allowed_for_dual_stack: typing.Optional[builtins.bool] = None,
        layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
        log_format: typing.Optional[builtins.str] = None,
        logging_format: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        log_removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        log_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        params_and_secrets: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup] = None,
        recursive_loop: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        runtime_management_mode: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        snap_start: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf] = None,
        system_log_level: typing.Optional[builtins.str] = None,
        system_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        on_failure: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
        on_success: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when defining a function from a Docker image.
        :param adot_instrumentation: Specify the configuration of AWS Distro for OpenTelemetry (ADOT) instrumentation. Default: - No ADOT instrumentation
        :param allow_all_ipv6_outbound: Whether to allow the Lambda to send all ipv6 network traffic. If set to true, there will only be a single egress rule which allows all outbound ipv6 traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets using ipv6. Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set. Instead, configure ``allowAllIpv6Outbound`` directly on the security group. Default: false
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param application_log_level: (deprecated) Sets the application log level for the function. Default: "INFO"
        :param application_log_level_v2: Sets the application log level for the function. Default: ApplicationLogLevel.INFO
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. If SNS topic is desired, specify ``deadLetterTopic`` property instead. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param dead_letter_topic: The SNS topic to use as a DLQ. Note that if ``deadLetterQueueEnabled`` is set to ``true``, an SQS queue will be created rather than an SNS topic. Using an SNS topic as a DLQ requires this property to be set explicitly. Default: - no SNS topic
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param ephemeral_storage_size: The size of the function’s /tmp directory in MiB. Default: 512 MiB
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param ipv6_allowed_for_dual_stack: Allows outbound IPv6 traffic on VPC functions that are connected to dual-stack subnets. Only used if 'vpc' is supplied. Default: false
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_format: (deprecated) Sets the logFormat for the function. Default: "Text"
        :param logging_format: Sets the loggingFormat for the function. Default: LoggingFormat.TEXT
        :param log_group: The log group the function sends logs to. By default, Lambda functions send logs to an automatically created default log group named /aws/lambda/<function name>. However you cannot change the properties of this auto-created log group using the AWS CDK, e.g. you cannot set a different log retention. Use the ``logGroup`` property to create a fully customizable LogGroup ahead of time, and instruct the Lambda function to send logs to it. Providing a user-controlled log group was rolled out to commercial regions on 2023-11-16. If you are deploying to another type of region, please check regional availability first. Default: ``/aws/lambda/${this.functionName}`` - default log group created by Lambda
        :param log_removal_policy: (deprecated) Determine the removal policy of the log group that is auto-created by this construct. Normally you want to retain the log group so you can diagnose issues from logs even after a deployment that no longer includes the log group. In that case, use the normal date-based retention policy to age out your logs. Default: RemovalPolicy.Retain
        :param log_retention: (deprecated) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. This is a legacy API and we strongly recommend you move away from it if you can. Instead create a fully customizable log group with ``logs.LogGroup`` and use the ``logGroup`` property to instruct the Lambda function to send logs to it. Migrating from ``logRetention`` to ``logGroup`` will cause the name of the log group to change. Users and code and referencing the name verbatim will have to adjust. In AWS CDK code, you can access the log group name directly from the LogGroup construct:: import * as logs from 'aws-cdk-lib/aws-logs'; declare const myLogGroup: logs.LogGroup; myLogGroup.logGroupName; Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can. ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can. ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param params_and_secrets: Specify the configuration of Parameters and Secrets Extension. Default: - No Parameters and Secrets Extension
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param recursive_loop: Sets the Recursive Loop Protection for Lambda Function. It lets Lambda detect and terminate unintended recursive loops. Default: RecursiveLoop.Terminate
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param runtime_management_mode: Sets the runtime management configuration for a function's version. Default: Auto
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param snap_start: Enable SnapStart for Lambda Function. SnapStart is currently supported for Java 11, Java 17, Python 3.12, Python 3.13, and .NET 8 runtime Default: - No snapstart
        :param system_log_level: (deprecated) Sets the system log level for the function. Default: "INFO"
        :param system_log_level_v2: Sets the system log level for the function. Default: SystemLogLevel.INFO
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. This is required when ``vpcSubnets`` is specified. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Note: Internet access for Lambda Functions requires a NAT Gateway, so picking public subnets is not allowed (unless ``allowPublicSubnet`` is set to ``true``). Default: - the Vpc default strategy if not specified
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acc9182e49dbeda08843e3f91358010a394f53520d65c6ec34ac3d5aab936357)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FnlFunctionProps(
            code=code,
            handler=handler,
            runtime=runtime,
            adot_instrumentation=adot_instrumentation,
            allow_all_ipv6_outbound=allow_all_ipv6_outbound,
            allow_all_outbound=allow_all_outbound,
            allow_public_subnet=allow_public_subnet,
            application_log_level=application_log_level,
            application_log_level_v2=application_log_level_v2,
            architecture=architecture,
            code_signing_config=code_signing_config,
            current_version_options=current_version_options,
            dead_letter_queue=dead_letter_queue,
            dead_letter_queue_enabled=dead_letter_queue_enabled,
            dead_letter_topic=dead_letter_topic,
            description=description,
            environment=environment,
            environment_encryption=environment_encryption,
            ephemeral_storage_size=ephemeral_storage_size,
            events=events,
            filesystem=filesystem,
            function_name=function_name,
            initial_policy=initial_policy,
            insights_version=insights_version,
            ipv6_allowed_for_dual_stack=ipv6_allowed_for_dual_stack,
            layers=layers,
            log_format=log_format,
            logging_format=logging_format,
            log_group=log_group,
            log_removal_policy=log_removal_policy,
            log_retention=log_retention,
            log_retention_retry_options=log_retention_retry_options,
            log_retention_role=log_retention_role,
            memory_size=memory_size,
            params_and_secrets=params_and_secrets,
            profiling=profiling,
            profiling_group=profiling_group,
            recursive_loop=recursive_loop,
            reserved_concurrent_executions=reserved_concurrent_executions,
            role=role,
            runtime_management_mode=runtime_management_mode,
            security_groups=security_groups,
            snap_start=snap_start,
            system_log_level=system_log_level,
            system_log_level_v2=system_log_level_v2,
            timeout=timeout,
            tracing=tracing,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            max_event_age=max_event_age,
            on_failure=on_failure,
            on_success=on_success,
            retry_attempts=retry_attempts,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "function"))


@jsii.data_type(
    jsii_type="fnl-aws-cdk.FnlFunctionProps",
    jsii_struct_bases=[_aws_cdk_aws_lambda_ceddda9d.FunctionProps],
    name_mapping={
        "max_event_age": "maxEventAge",
        "on_failure": "onFailure",
        "on_success": "onSuccess",
        "retry_attempts": "retryAttempts",
        "adot_instrumentation": "adotInstrumentation",
        "allow_all_ipv6_outbound": "allowAllIpv6Outbound",
        "allow_all_outbound": "allowAllOutbound",
        "allow_public_subnet": "allowPublicSubnet",
        "application_log_level": "applicationLogLevel",
        "application_log_level_v2": "applicationLogLevelV2",
        "architecture": "architecture",
        "code_signing_config": "codeSigningConfig",
        "current_version_options": "currentVersionOptions",
        "dead_letter_queue": "deadLetterQueue",
        "dead_letter_queue_enabled": "deadLetterQueueEnabled",
        "dead_letter_topic": "deadLetterTopic",
        "description": "description",
        "environment": "environment",
        "environment_encryption": "environmentEncryption",
        "ephemeral_storage_size": "ephemeralStorageSize",
        "events": "events",
        "filesystem": "filesystem",
        "function_name": "functionName",
        "initial_policy": "initialPolicy",
        "insights_version": "insightsVersion",
        "ipv6_allowed_for_dual_stack": "ipv6AllowedForDualStack",
        "layers": "layers",
        "log_format": "logFormat",
        "logging_format": "loggingFormat",
        "log_group": "logGroup",
        "log_removal_policy": "logRemovalPolicy",
        "log_retention": "logRetention",
        "log_retention_retry_options": "logRetentionRetryOptions",
        "log_retention_role": "logRetentionRole",
        "memory_size": "memorySize",
        "params_and_secrets": "paramsAndSecrets",
        "profiling": "profiling",
        "profiling_group": "profilingGroup",
        "recursive_loop": "recursiveLoop",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "role": "role",
        "runtime_management_mode": "runtimeManagementMode",
        "security_groups": "securityGroups",
        "snap_start": "snapStart",
        "system_log_level": "systemLogLevel",
        "system_log_level_v2": "systemLogLevelV2",
        "timeout": "timeout",
        "tracing": "tracing",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "code": "code",
        "handler": "handler",
        "runtime": "runtime",
    },
)
class FnlFunctionProps(_aws_cdk_aws_lambda_ceddda9d.FunctionProps):
    def __init__(
        self,
        *,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        on_failure: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
        on_success: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        adot_instrumentation: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        application_log_level: typing.Optional[builtins.str] = None,
        application_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel] = None,
        architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        code_signing_config: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.VersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        dead_letter_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        events: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
        filesystem: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        insights_version: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion] = None,
        ipv6_allowed_for_dual_stack: typing.Optional[builtins.bool] = None,
        layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
        log_format: typing.Optional[builtins.str] = None,
        logging_format: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        log_removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        log_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        params_and_secrets: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup] = None,
        recursive_loop: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        runtime_management_mode: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        snap_start: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf] = None,
        system_log_level: typing.Optional[builtins.str] = None,
        system_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        code: _aws_cdk_aws_lambda_ceddda9d.Code,
        handler: builtins.str,
        runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
    ) -> None:
        '''Properties for the LambdaFunction construct.

        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        :param adot_instrumentation: Specify the configuration of AWS Distro for OpenTelemetry (ADOT) instrumentation. Default: - No ADOT instrumentation
        :param allow_all_ipv6_outbound: Whether to allow the Lambda to send all ipv6 network traffic. If set to true, there will only be a single egress rule which allows all outbound ipv6 traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets using ipv6. Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set. Instead, configure ``allowAllIpv6Outbound`` directly on the security group. Default: false
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param application_log_level: (deprecated) Sets the application log level for the function. Default: "INFO"
        :param application_log_level_v2: Sets the application log level for the function. Default: ApplicationLogLevel.INFO
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. If SNS topic is desired, specify ``deadLetterTopic`` property instead. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param dead_letter_topic: The SNS topic to use as a DLQ. Note that if ``deadLetterQueueEnabled`` is set to ``true``, an SQS queue will be created rather than an SNS topic. Using an SNS topic as a DLQ requires this property to be set explicitly. Default: - no SNS topic
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param ephemeral_storage_size: The size of the function’s /tmp directory in MiB. Default: 512 MiB
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param ipv6_allowed_for_dual_stack: Allows outbound IPv6 traffic on VPC functions that are connected to dual-stack subnets. Only used if 'vpc' is supplied. Default: false
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_format: (deprecated) Sets the logFormat for the function. Default: "Text"
        :param logging_format: Sets the loggingFormat for the function. Default: LoggingFormat.TEXT
        :param log_group: The log group the function sends logs to. By default, Lambda functions send logs to an automatically created default log group named /aws/lambda/<function name>. However you cannot change the properties of this auto-created log group using the AWS CDK, e.g. you cannot set a different log retention. Use the ``logGroup`` property to create a fully customizable LogGroup ahead of time, and instruct the Lambda function to send logs to it. Providing a user-controlled log group was rolled out to commercial regions on 2023-11-16. If you are deploying to another type of region, please check regional availability first. Default: ``/aws/lambda/${this.functionName}`` - default log group created by Lambda
        :param log_removal_policy: (deprecated) Determine the removal policy of the log group that is auto-created by this construct. Normally you want to retain the log group so you can diagnose issues from logs even after a deployment that no longer includes the log group. In that case, use the normal date-based retention policy to age out your logs. Default: RemovalPolicy.Retain
        :param log_retention: (deprecated) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. This is a legacy API and we strongly recommend you move away from it if you can. Instead create a fully customizable log group with ``logs.LogGroup`` and use the ``logGroup`` property to instruct the Lambda function to send logs to it. Migrating from ``logRetention`` to ``logGroup`` will cause the name of the log group to change. Users and code and referencing the name verbatim will have to adjust. In AWS CDK code, you can access the log group name directly from the LogGroup construct:: import * as logs from 'aws-cdk-lib/aws-logs'; declare const myLogGroup: logs.LogGroup; myLogGroup.logGroupName; Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can. ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can. ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param params_and_secrets: Specify the configuration of Parameters and Secrets Extension. Default: - No Parameters and Secrets Extension
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param recursive_loop: Sets the Recursive Loop Protection for Lambda Function. It lets Lambda detect and terminate unintended recursive loops. Default: RecursiveLoop.Terminate
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param runtime_management_mode: Sets the runtime management configuration for a function's version. Default: Auto
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param snap_start: Enable SnapStart for Lambda Function. SnapStart is currently supported for Java 11, Java 17, Python 3.12, Python 3.13, and .NET 8 runtime Default: - No snapstart
        :param system_log_level: (deprecated) Sets the system log level for the function. Default: "INFO"
        :param system_log_level_v2: Sets the system log level for the function. Default: SystemLogLevel.INFO
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. This is required when ``vpcSubnets`` is specified. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Note: Internet access for Lambda Functions requires a NAT Gateway, so picking public subnets is not allowed (unless ``allowPublicSubnet`` is set to ``true``). Default: - the Vpc default strategy if not specified
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when defining a function from a Docker image.
        '''
        if isinstance(adot_instrumentation, dict):
            adot_instrumentation = _aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig(**adot_instrumentation)
        if isinstance(current_version_options, dict):
            current_version_options = _aws_cdk_aws_lambda_ceddda9d.VersionOptions(**current_version_options)
        if isinstance(log_retention_retry_options, dict):
            log_retention_retry_options = _aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions(**log_retention_retry_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d2d45ddfe1fafd9faa95821aef8b21e5eb0f1615bfdd44d99b07408a0563f56)
            check_type(argname="argument max_event_age", value=max_event_age, expected_type=type_hints["max_event_age"])
            check_type(argname="argument on_failure", value=on_failure, expected_type=type_hints["on_failure"])
            check_type(argname="argument on_success", value=on_success, expected_type=type_hints["on_success"])
            check_type(argname="argument retry_attempts", value=retry_attempts, expected_type=type_hints["retry_attempts"])
            check_type(argname="argument adot_instrumentation", value=adot_instrumentation, expected_type=type_hints["adot_instrumentation"])
            check_type(argname="argument allow_all_ipv6_outbound", value=allow_all_ipv6_outbound, expected_type=type_hints["allow_all_ipv6_outbound"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument allow_public_subnet", value=allow_public_subnet, expected_type=type_hints["allow_public_subnet"])
            check_type(argname="argument application_log_level", value=application_log_level, expected_type=type_hints["application_log_level"])
            check_type(argname="argument application_log_level_v2", value=application_log_level_v2, expected_type=type_hints["application_log_level_v2"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument code_signing_config", value=code_signing_config, expected_type=type_hints["code_signing_config"])
            check_type(argname="argument current_version_options", value=current_version_options, expected_type=type_hints["current_version_options"])
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument dead_letter_queue_enabled", value=dead_letter_queue_enabled, expected_type=type_hints["dead_letter_queue_enabled"])
            check_type(argname="argument dead_letter_topic", value=dead_letter_topic, expected_type=type_hints["dead_letter_topic"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument environment_encryption", value=environment_encryption, expected_type=type_hints["environment_encryption"])
            check_type(argname="argument ephemeral_storage_size", value=ephemeral_storage_size, expected_type=type_hints["ephemeral_storage_size"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument filesystem", value=filesystem, expected_type=type_hints["filesystem"])
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument initial_policy", value=initial_policy, expected_type=type_hints["initial_policy"])
            check_type(argname="argument insights_version", value=insights_version, expected_type=type_hints["insights_version"])
            check_type(argname="argument ipv6_allowed_for_dual_stack", value=ipv6_allowed_for_dual_stack, expected_type=type_hints["ipv6_allowed_for_dual_stack"])
            check_type(argname="argument layers", value=layers, expected_type=type_hints["layers"])
            check_type(argname="argument log_format", value=log_format, expected_type=type_hints["log_format"])
            check_type(argname="argument logging_format", value=logging_format, expected_type=type_hints["logging_format"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument log_removal_policy", value=log_removal_policy, expected_type=type_hints["log_removal_policy"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument log_retention_retry_options", value=log_retention_retry_options, expected_type=type_hints["log_retention_retry_options"])
            check_type(argname="argument log_retention_role", value=log_retention_role, expected_type=type_hints["log_retention_role"])
            check_type(argname="argument memory_size", value=memory_size, expected_type=type_hints["memory_size"])
            check_type(argname="argument params_and_secrets", value=params_and_secrets, expected_type=type_hints["params_and_secrets"])
            check_type(argname="argument profiling", value=profiling, expected_type=type_hints["profiling"])
            check_type(argname="argument profiling_group", value=profiling_group, expected_type=type_hints["profiling_group"])
            check_type(argname="argument recursive_loop", value=recursive_loop, expected_type=type_hints["recursive_loop"])
            check_type(argname="argument reserved_concurrent_executions", value=reserved_concurrent_executions, expected_type=type_hints["reserved_concurrent_executions"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument runtime_management_mode", value=runtime_management_mode, expected_type=type_hints["runtime_management_mode"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument snap_start", value=snap_start, expected_type=type_hints["snap_start"])
            check_type(argname="argument system_log_level", value=system_log_level, expected_type=type_hints["system_log_level"])
            check_type(argname="argument system_log_level_v2", value=system_log_level_v2, expected_type=type_hints["system_log_level_v2"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument tracing", value=tracing, expected_type=type_hints["tracing"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code": code,
            "handler": handler,
            "runtime": runtime,
        }
        if max_event_age is not None:
            self._values["max_event_age"] = max_event_age
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if adot_instrumentation is not None:
            self._values["adot_instrumentation"] = adot_instrumentation
        if allow_all_ipv6_outbound is not None:
            self._values["allow_all_ipv6_outbound"] = allow_all_ipv6_outbound
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if allow_public_subnet is not None:
            self._values["allow_public_subnet"] = allow_public_subnet
        if application_log_level is not None:
            self._values["application_log_level"] = application_log_level
        if application_log_level_v2 is not None:
            self._values["application_log_level_v2"] = application_log_level_v2
        if architecture is not None:
            self._values["architecture"] = architecture
        if code_signing_config is not None:
            self._values["code_signing_config"] = code_signing_config
        if current_version_options is not None:
            self._values["current_version_options"] = current_version_options
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if dead_letter_queue_enabled is not None:
            self._values["dead_letter_queue_enabled"] = dead_letter_queue_enabled
        if dead_letter_topic is not None:
            self._values["dead_letter_topic"] = dead_letter_topic
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if ephemeral_storage_size is not None:
            self._values["ephemeral_storage_size"] = ephemeral_storage_size
        if events is not None:
            self._values["events"] = events
        if filesystem is not None:
            self._values["filesystem"] = filesystem
        if function_name is not None:
            self._values["function_name"] = function_name
        if initial_policy is not None:
            self._values["initial_policy"] = initial_policy
        if insights_version is not None:
            self._values["insights_version"] = insights_version
        if ipv6_allowed_for_dual_stack is not None:
            self._values["ipv6_allowed_for_dual_stack"] = ipv6_allowed_for_dual_stack
        if layers is not None:
            self._values["layers"] = layers
        if log_format is not None:
            self._values["log_format"] = log_format
        if logging_format is not None:
            self._values["logging_format"] = logging_format
        if log_group is not None:
            self._values["log_group"] = log_group
        if log_removal_policy is not None:
            self._values["log_removal_policy"] = log_removal_policy
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if log_retention_retry_options is not None:
            self._values["log_retention_retry_options"] = log_retention_retry_options
        if log_retention_role is not None:
            self._values["log_retention_role"] = log_retention_role
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if params_and_secrets is not None:
            self._values["params_and_secrets"] = params_and_secrets
        if profiling is not None:
            self._values["profiling"] = profiling
        if profiling_group is not None:
            self._values["profiling_group"] = profiling_group
        if recursive_loop is not None:
            self._values["recursive_loop"] = recursive_loop
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if role is not None:
            self._values["role"] = role
        if runtime_management_mode is not None:
            self._values["runtime_management_mode"] = runtime_management_mode
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if snap_start is not None:
            self._values["snap_start"] = snap_start
        if system_log_level is not None:
            self._values["system_log_level"] = system_log_level
        if system_log_level_v2 is not None:
            self._values["system_log_level_v2"] = system_log_level_v2
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing is not None:
            self._values["tracing"] = tracing
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def max_event_age(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum age of a request that Lambda sends to a function for processing.

        Minimum: 60 seconds
        Maximum: 6 hours

        :default: Duration.hours(6)
        '''
        result = self._values.get("max_event_age")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def on_failure(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination]:
        '''The destination for failed invocations.

        :default: - no destination
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination], result)

    @builtins.property
    def on_success(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination]:
        '''The destination for successful invocations.

        :default: - no destination
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry when the function returns an error.

        Minimum: 0
        Maximum: 2

        :default: 2
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def adot_instrumentation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig]:
        '''Specify the configuration of AWS Distro for OpenTelemetry (ADOT) instrumentation.

        :default: - No ADOT instrumentation

        :see: https://aws-otel.github.io/docs/getting-started/lambda
        '''
        result = self._values.get("adot_instrumentation")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig], result)

    @builtins.property
    def allow_all_ipv6_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all ipv6 network traffic.

        If set to true, there will only be a single egress rule which allows all
        outbound ipv6 traffic. If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets using ipv6.

        Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set.
        Instead, configure ``allowAllIpv6Outbound`` directly on the security group.

        :default: false
        '''
        result = self._values.get("allow_all_ipv6_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all network traffic (except ipv6).

        If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets.

        Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set.
        Instead, configure ``allowAllOutbound`` directly on the security group.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_public_subnet(self) -> typing.Optional[builtins.bool]:
        '''Lambda Functions in a public subnet can NOT access the internet.

        Use this property to acknowledge this limitation and still place the function in a public subnet.

        :default: false

        :see: https://stackoverflow.com/questions/52992085/why-cant-an-aws-lambda-function-inside-a-public-subnet-in-a-vpc-connect-to-the/52994841#52994841
        '''
        result = self._values.get("allow_public_subnet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def application_log_level(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Sets the application log level for the function.

        :default: "INFO"

        :deprecated: Use ``applicationLogLevelV2`` as a property instead.

        :stability: deprecated
        '''
        result = self._values.get("application_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_log_level_v2(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel]:
        '''Sets the application log level for the function.

        :default: ApplicationLogLevel.INFO
        '''
        result = self._values.get("application_log_level_v2")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel], result)

    @builtins.property
    def architecture(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture]:
        '''The system architectures compatible with this lambda function.

        :default: Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture], result)

    @builtins.property
    def code_signing_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig]:
        '''Code signing config associated with this function.

        :default: - Not Sign the Code
        '''
        result = self._values.get("code_signing_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig], result)

    @builtins.property
    def current_version_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.VersionOptions]:
        '''Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method.

        :default: - default options as described in ``VersionOptions``
        '''
        result = self._values.get("current_version_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.VersionOptions], result)

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''The SQS queue to use if DLQ is enabled.

        If SNS topic is desired, specify ``deadLetterTopic`` property instead.

        :default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], result)

    @builtins.property
    def dead_letter_queue_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enabled DLQ.

        If ``deadLetterQueue`` is undefined,
        an SQS queue with default options will be defined for your Function.

        :default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        '''
        result = self._values.get("dead_letter_queue_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dead_letter_topic(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''The SNS topic to use as a DLQ.

        Note that if ``deadLetterQueueEnabled`` is set to ``true``, an SQS queue will be created
        rather than an SNS topic. Using an SNS topic as a DLQ requires this property to be set explicitly.

        :default: - no SNS topic
        '''
        result = self._values.get("dead_letter_topic")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the function.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key-value pairs that Lambda caches and makes available for your Lambda functions.

        Use environment variables to apply configuration changes, such
        as test and production environment configurations, without changing your
        Lambda function source code.

        :default: - No environment variables.
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key that's used to encrypt your function's environment variables.

        :default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        '''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def ephemeral_storage_size(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''The size of the function’s /tmp directory in MiB.

        :default: 512 MiB
        '''
        result = self._values.get("ephemeral_storage_size")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def events(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.IEventSource]]:
        '''Event sources for this function.

        You can also add event sources using ``addEventSource``.

        :default: - No event sources.
        '''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.IEventSource]], result)

    @builtins.property
    def filesystem(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem]:
        '''The filesystem configuration for the lambda function.

        :default: - will not mount any filesystem
        '''
        result = self._values.get("filesystem")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''A name for the function.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that
        ID for the function's name. For more information, see Name Type.
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initial_policy(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Initial policy statements to add to the created Lambda Role.

        You can call ``addToRolePolicy`` to the created lambda to add statements post creation.

        :default: - No policy statements are added to the created Lambda role.
        '''
        result = self._values.get("initial_policy")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def insights_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion]:
        '''Specify the version of CloudWatch Lambda insights to use for monitoring.

        :default: - No Lambda Insights

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights-Getting-Started-docker.html
        '''
        result = self._values.get("insights_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion], result)

    @builtins.property
    def ipv6_allowed_for_dual_stack(self) -> typing.Optional[builtins.bool]:
        '''Allows outbound IPv6 traffic on VPC functions that are connected to dual-stack subnets.

        Only used if 'vpc' is supplied.

        :default: false
        '''
        result = self._values.get("ipv6_allowed_for_dual_stack")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def layers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]]:
        '''A list of layers to add to the function's execution environment.

        You can configure your Lambda function to pull in
        additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies
        that can be used by multiple functions.

        :default: - No layers.
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]], result)

    @builtins.property
    def log_format(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Sets the logFormat for the function.

        :default: "Text"

        :deprecated: Use ``loggingFormat`` as a property instead.

        :stability: deprecated
        '''
        result = self._values.get("log_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_format(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat]:
        '''Sets the loggingFormat for the function.

        :default: LoggingFormat.TEXT
        '''
        result = self._values.get("logging_format")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The log group the function sends logs to.

        By default, Lambda functions send logs to an automatically created default log group named /aws/lambda/.
        However you cannot change the properties of this auto-created log group using the AWS CDK, e.g. you cannot set a different log retention.

        Use the ``logGroup`` property to create a fully customizable LogGroup ahead of time, and instruct the Lambda function to send logs to it.

        Providing a user-controlled log group was rolled out to commercial regions on 2023-11-16.
        If you are deploying to another type of region, please check regional availability first.

        :default: ``/aws/lambda/${this.functionName}`` - default log group created by Lambda
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def log_removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(deprecated) Determine the removal policy of the log group that is auto-created by this construct.

        Normally you want to retain the log group so you can diagnose issues
        from logs even after a deployment that no longer includes the log group.
        In that case, use the normal date-based retention policy to age out your
        logs.

        :default: RemovalPolicy.Retain

        :deprecated: use ``logGroup`` instead

        :stability: deprecated
        '''
        result = self._values.get("log_removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(deprecated) The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        This is a legacy API and we strongly recommend you move away from it if you can.
        Instead create a fully customizable log group with ``logs.LogGroup`` and use the ``logGroup`` property
        to instruct the Lambda function to send logs to it.
        Migrating from ``logRetention`` to ``logGroup`` will cause the name of the log group to change.
        Users and code and referencing the name verbatim will have to adjust.

        In AWS CDK code, you can access the log group name directly from the LogGroup construct::

           import * as logs from 'aws-cdk-lib/aws-logs';

           declare const myLogGroup: logs.LogGroup;
           myLogGroup.logGroupName;

        :default: logs.RetentionDays.INFINITE

        :deprecated: use ``logGroup`` instead

        :stability: deprecated
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def log_retention_retry_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions]:
        '''When log retention is specified, a custom resource attempts to create the CloudWatch log group.

        These options control the retry policy when interacting with CloudWatch APIs.

        This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can.
        ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it.

        :default: - Default AWS SDK retry options.
        '''
        result = self._values.get("log_retention_retry_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions], result)

    @builtins.property
    def log_retention_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can.
        ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it.

        :default: - A new role is created.
        '''
        result = self._values.get("log_retention_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU
        power. For more information, see Resource Model in the AWS Lambda
        Developer Guide.

        :default: 128
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def params_and_secrets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion]:
        '''Specify the configuration of Parameters and Secrets Extension.

        :default: - No Parameters and Secrets Extension

        :see: https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
        '''
        result = self._values.get("params_and_secrets")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion], result)

    @builtins.property
    def profiling(self) -> typing.Optional[builtins.bool]:
        '''Enable profiling.

        :default: - No profiling.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profiling_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup]:
        '''Profiling Group.

        :default: - A new profiling group will be created if ``profiling`` is set.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup], result)

    @builtins.property
    def recursive_loop(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop]:
        '''Sets the Recursive Loop Protection for Lambda Function.

        It lets Lambda detect and terminate unintended recursive loops.

        :default: RecursiveLoop.Terminate
        '''
        result = self._values.get("recursive_loop")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''The maximum of concurrent executions you want to reserve for the function.

        :default: - No specific limit - account limit.

        :see: https://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html
        '''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Lambda execution role.

        This is the role that will be assumed by the function upon execution.
        It controls the permissions that the function will have. The Role must
        be assumable by the 'lambda.amazonaws.com' service principal.

        The default Role automatically has permissions granted for Lambda execution. If you
        provide a Role, you must add the relevant AWS managed policies yourself.

        The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and
        "service-role/AWSLambdaVPCAccessExecutionRole".

        :default:

        - A unique role will be generated for this lambda function.
        Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def runtime_management_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode]:
        '''Sets the runtime management configuration for a function's version.

        :default: Auto
        '''
        result = self._values.get("runtime_management_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of security groups to associate with the Lambda's network interfaces.

        Only used if 'vpc' is supplied.

        :default:

        - If the function is placed within a VPC and a security group is
        not specified, either by this or securityGroup prop, a dedicated security
        group will be created for this function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def snap_start(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf]:
        '''Enable SnapStart for Lambda Function.

        SnapStart is currently supported for Java 11, Java 17, Python 3.12, Python 3.13, and .NET 8 runtime

        :default: - No snapstart
        '''
        result = self._values.get("snap_start")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf], result)

    @builtins.property
    def system_log_level(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Sets the system log level for the function.

        :default: "INFO"

        :deprecated: Use ``systemLogLevelV2`` as a property instead.

        :stability: deprecated
        '''
        result = self._values.get("system_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_log_level_v2(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel]:
        '''Sets the system log level for the function.

        :default: SystemLogLevel.INFO
        '''
        result = self._values.get("system_log_level_v2")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.seconds(3)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def tracing(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing]:
        '''Enable AWS X-Ray Tracing for Lambda Function.

        :default: Tracing.Disabled
        '''
        result = self._values.get("tracing")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC network to place Lambda network interfaces.

        Specify this if the Lambda function needs to access resources in a VPC.
        This is required when ``vpcSubnets`` is specified.

        :default: - Function is not placed within a VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        This requires ``vpc`` to be specified in order for interfaces to actually be
        placed in the subnets. If ``vpc`` is not specify, this will raise an error.

        Note: Internet access for Lambda Functions requires a NAT Gateway, so picking
        public subnets is not allowed (unless ``allowPublicSubnet`` is set to ``true``).

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def code(self) -> _aws_cdk_aws_lambda_ceddda9d.Code:
        '''The source code of your Lambda function.

        You can point to a file in an
        Amazon Simple Storage Service (Amazon S3) bucket or specify your source
        code as inline text.
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Code, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''The name of the method within your code that Lambda calls to execute your function.

        The format includes the file name. It can also include
        namespaces and other qualifiers, depending on the runtime.
        For more information, see https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html.

        Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image.

        NOTE: If you specify your source code as inline text by specifying the
        ZipFile property within the Code property, specify index.function_name as
        the handler.
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime(self) -> _aws_cdk_aws_lambda_ceddda9d.Runtime:
        '''The runtime environment for the Lambda function that you are uploading.

        For valid values, see the Runtime property in the AWS Lambda Developer
        Guide.

        Use ``Runtime.FROM_IMAGE`` when defining a function from a Docker image.
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Runtime, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FnlFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FnlLogGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlLogGroup",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        data_protection_policy: typing.Optional[_aws_cdk_aws_logs_ceddda9d.DataProtectionPolicy] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        field_index_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.FieldIndexPolicy]] = None,
        log_group_class: typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupClass] = None,
        log_group_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param data_protection_policy: Data Protection Policy for this log group. Default: - no data protection policy
        :param encryption_key: The KMS customer managed key to encrypt the log group with. Default: Server-side encryption managed by the CloudWatch Logs service
        :param field_index_policies: Field Index Policies for this log group. Default: - no field index policies for this log group.
        :param log_group_class: The class of the log group. Possible values are: STANDARD and INFREQUENT_ACCESS. INFREQUENT_ACCESS class provides customers a cost-effective way to consolidate logs which supports querying using Logs Insights. The logGroupClass property cannot be changed once the log group is created. Default: LogGroupClass.STANDARD
        :param log_group_name: Name of the log group. Default: Automatically generated
        :param removal_policy: Determine the removal policy of this log group. Normally you want to retain the log group so you can diagnose issues from logs even after a deployment that no longer includes the log group. In that case, use the normal date-based retention policy to age out your logs. Default: RemovalPolicy.Retain
        :param retention: How long, in days, the log contents will be retained. To retain all logs, set this value to RetentionDays.INFINITE. Default: RetentionDays.TWO_YEARS
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37ca06dbea84aa08fca36e59e2f74d21679f3ecced9bc33f1ac1b90c78d5a77a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FnlLogGroupProps(
            data_protection_policy=data_protection_policy,
            encryption_key=encryption_key,
            field_index_policies=field_index_policies,
            log_group_class=log_group_class,
            log_group_name=log_group_name,
            removal_policy=removal_policy,
            retention=retention,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "logGroup"))


@jsii.data_type(
    jsii_type="fnl-aws-cdk.FnlLogGroupProps",
    jsii_struct_bases=[_aws_cdk_aws_logs_ceddda9d.LogGroupProps],
    name_mapping={
        "data_protection_policy": "dataProtectionPolicy",
        "encryption_key": "encryptionKey",
        "field_index_policies": "fieldIndexPolicies",
        "log_group_class": "logGroupClass",
        "log_group_name": "logGroupName",
        "removal_policy": "removalPolicy",
        "retention": "retention",
    },
)
class FnlLogGroupProps(_aws_cdk_aws_logs_ceddda9d.LogGroupProps):
    def __init__(
        self,
        *,
        data_protection_policy: typing.Optional[_aws_cdk_aws_logs_ceddda9d.DataProtectionPolicy] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        field_index_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.FieldIndexPolicy]] = None,
        log_group_class: typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupClass] = None,
        log_group_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param data_protection_policy: Data Protection Policy for this log group. Default: - no data protection policy
        :param encryption_key: The KMS customer managed key to encrypt the log group with. Default: Server-side encryption managed by the CloudWatch Logs service
        :param field_index_policies: Field Index Policies for this log group. Default: - no field index policies for this log group.
        :param log_group_class: The class of the log group. Possible values are: STANDARD and INFREQUENT_ACCESS. INFREQUENT_ACCESS class provides customers a cost-effective way to consolidate logs which supports querying using Logs Insights. The logGroupClass property cannot be changed once the log group is created. Default: LogGroupClass.STANDARD
        :param log_group_name: Name of the log group. Default: Automatically generated
        :param removal_policy: Determine the removal policy of this log group. Normally you want to retain the log group so you can diagnose issues from logs even after a deployment that no longer includes the log group. In that case, use the normal date-based retention policy to age out your logs. Default: RemovalPolicy.Retain
        :param retention: How long, in days, the log contents will be retained. To retain all logs, set this value to RetentionDays.INFINITE. Default: RetentionDays.TWO_YEARS
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__172d9afbfa9f9cb58059d2150f802150d6554e803098d03773c0a48586061702)
            check_type(argname="argument data_protection_policy", value=data_protection_policy, expected_type=type_hints["data_protection_policy"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument field_index_policies", value=field_index_policies, expected_type=type_hints["field_index_policies"])
            check_type(argname="argument log_group_class", value=log_group_class, expected_type=type_hints["log_group_class"])
            check_type(argname="argument log_group_name", value=log_group_name, expected_type=type_hints["log_group_name"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument retention", value=retention, expected_type=type_hints["retention"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if data_protection_policy is not None:
            self._values["data_protection_policy"] = data_protection_policy
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if field_index_policies is not None:
            self._values["field_index_policies"] = field_index_policies
        if log_group_class is not None:
            self._values["log_group_class"] = log_group_class
        if log_group_name is not None:
            self._values["log_group_name"] = log_group_name
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if retention is not None:
            self._values["retention"] = retention

    @builtins.property
    def data_protection_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.DataProtectionPolicy]:
        '''Data Protection Policy for this log group.

        :default: - no data protection policy
        '''
        result = self._values.get("data_protection_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.DataProtectionPolicy], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS customer managed key to encrypt the log group with.

        :default: Server-side encryption managed by the CloudWatch Logs service
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def field_index_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_logs_ceddda9d.FieldIndexPolicy]]:
        '''Field Index Policies for this log group.

        :default: - no field index policies for this log group.
        '''
        result = self._values.get("field_index_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_logs_ceddda9d.FieldIndexPolicy]], result)

    @builtins.property
    def log_group_class(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupClass]:
        '''The class of the log group. Possible values are: STANDARD and INFREQUENT_ACCESS.

        INFREQUENT_ACCESS class provides customers a cost-effective way to consolidate
        logs which supports querying using Logs Insights. The logGroupClass property cannot
        be changed once the log group is created.

        :default: LogGroupClass.STANDARD
        '''
        result = self._values.get("log_group_class")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupClass], result)

    @builtins.property
    def log_group_name(self) -> typing.Optional[builtins.str]:
        '''Name of the log group.

        :default: Automatically generated
        '''
        result = self._values.get("log_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Determine the removal policy of this log group.

        Normally you want to retain the log group so you can diagnose issues
        from logs even after a deployment that no longer includes the log group.
        In that case, use the normal date-based retention policy to age out your
        logs.

        :default: RemovalPolicy.Retain
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def retention(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''How long, in days, the log contents will be retained.

        To retain all logs, set this value to RetentionDays.INFINITE.

        :default: RetentionDays.TWO_YEARS
        '''
        result = self._values.get("retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FnlLogGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="fnl-aws-cdk.FnlOpensearchProps",
    jsii_struct_bases=[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps],
    name_mapping={
        "version": "version",
        "access_policies": "accessPolicies",
        "advanced_options": "advancedOptions",
        "automated_snapshot_start_hour": "automatedSnapshotStartHour",
        "capacity": "capacity",
        "cognito_dashboards_auth": "cognitoDashboardsAuth",
        "cold_storage_enabled": "coldStorageEnabled",
        "custom_endpoint": "customEndpoint",
        "domain_name": "domainName",
        "ebs": "ebs",
        "enable_auto_software_update": "enableAutoSoftwareUpdate",
        "enable_version_upgrade": "enableVersionUpgrade",
        "encryption_at_rest": "encryptionAtRest",
        "enforce_https": "enforceHttps",
        "fine_grained_access_control": "fineGrainedAccessControl",
        "ip_address_type": "ipAddressType",
        "logging": "logging",
        "node_to_node_encryption": "nodeToNodeEncryption",
        "off_peak_window_enabled": "offPeakWindowEnabled",
        "off_peak_window_start": "offPeakWindowStart",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "suppress_logs_resource_policy": "suppressLogsResourcePolicy",
        "tls_security_policy": "tlsSecurityPolicy",
        "use_unsigned_basic_auth": "useUnsignedBasicAuth",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "zone_awareness": "zoneAwareness",
        "masteruser": "masteruser",
        "program": "program",
        "project": "project",
        "tier": "tier",
    },
)
class FnlOpensearchProps(_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps):
    def __init__(
        self,
        *,
        version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
        access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
        capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cold_storage_enabled: typing.Optional[builtins.bool] = None,
        custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_auto_software_update: typing.Optional[builtins.bool] = None,
        enable_version_upgrade: typing.Optional[builtins.bool] = None,
        encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enforce_https: typing.Optional[builtins.bool] = None,
        fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        node_to_node_encryption: typing.Optional[builtins.bool] = None,
        off_peak_window_enabled: typing.Optional[builtins.bool] = None,
        off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
        tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
        use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        masteruser: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
    ) -> None:
        '''
        :param version: The Elasticsearch/OpenSearch version that your domain will leverage.
        :param access_policies: Domain access policies. Default: - No access policies.
        :param advanced_options: Additional options to specify for the Amazon OpenSearch Service domain. Default: - no advanced options are specified
        :param automated_snapshot_start_hour: The hour in UTC during which the service takes an automated daily snapshot of the indices in the Amazon OpenSearch Service domain. Only applies for Elasticsearch versions below 5.3. Default: - Hourly automated snapshots not used
        :param capacity: The cluster capacity configuration for the Amazon OpenSearch Service domain. Default: - 1 r5.large.search data node; no dedicated master nodes.
        :param cognito_dashboards_auth: Configures Amazon OpenSearch Service to use Amazon Cognito authentication for OpenSearch Dashboards. Default: - Cognito not used for authentication to OpenSearch Dashboards.
        :param cold_storage_enabled: Whether to enable or disable cold storage on the domain. You must enable UltraWarm storage to enable cold storage. Default: - undefined
        :param custom_endpoint: To configure a custom domain configure these options. If you specify a Route53 hosted zone it will create a CNAME record and use DNS validation for the certificate Default: - no custom domain endpoint will be configured
        :param domain_name: Enforces a particular physical domain name. Default: - A name will be auto-generated.
        :param ebs: The configurations of Amazon Elastic Block Store (Amazon EBS) volumes that are attached to data nodes in the Amazon OpenSearch Service domain. Default: - 10 GiB General Purpose (SSD) volumes per node.
        :param enable_auto_software_update: Specifies whether automatic service software updates are enabled for the domain. Default: - false
        :param enable_version_upgrade: To upgrade an Amazon OpenSearch Service domain to a new version, rather than replacing the entire domain resource, use the EnableVersionUpgrade update policy. Default: - false
        :param encryption_at_rest: Encryption at rest options for the cluster. Default: - No encryption at rest
        :param enforce_https: True to require that all traffic to the domain arrive over HTTPS. Default: - false
        :param fine_grained_access_control: Specifies options for fine-grained access control. Requires Elasticsearch version 6.7 or later or OpenSearch version 1.0 or later. Enabling fine-grained access control also requires encryption of data at rest and node-to-node encryption, along with enforced HTTPS. Default: - fine-grained access control is disabled
        :param ip_address_type: Specify either dual stack or IPv4 as your IP address type. Dual stack allows you to share domain resources across IPv4 and IPv6 address types, and is the recommended option. If you set your IP address type to dual stack, you can't change your address type later. Default: - IpAddressType.IPV4
        :param logging: Configuration log publishing configuration options. Default: - No logs are published
        :param node_to_node_encryption: Specify true to enable node to node encryption. Requires Elasticsearch version 6.0 or later or OpenSearch version 1.0 or later. Default: - Node to node encryption is not enabled.
        :param off_peak_window_enabled: Options for enabling a domain's off-peak window, during which OpenSearch Service can perform mandatory configuration changes on the domain. Off-peak windows were introduced on February 16, 2023. All domains created before this date have the off-peak window disabled by default. You must manually enable and configure the off-peak window for these domains. All domains created after this date will have the off-peak window enabled by default. You can't disable the off-peak window for a domain after it's enabled. Default: - Disabled for domains created before February 16, 2023. Enabled for domains created after. Enabled if ``offPeakWindowStart`` is set.
        :param off_peak_window_start: Start time for the off-peak window, in Coordinated Universal Time (UTC). The window length will always be 10 hours, so you can't specify an end time. For example, if you specify 11:00 P.M. UTC as a start time, the end time will automatically be set to 9:00 A.M. Default: - 10:00 P.M. local time
        :param removal_policy: Policy to apply when the domain is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_groups: The list of security groups that are associated with the VPC endpoints for the domain. Only used if ``vpc`` is specified. Default: - One new security group is created.
        :param suppress_logs_resource_policy: Specify whether to create a CloudWatch Logs resource policy or not. When logging is enabled for the domain, a CloudWatch Logs resource policy is created by default. However, CloudWatch Logs supports only 10 resource policies per region. If you enable logging for several domains, it may hit the quota and cause an error. By setting this property to true, creating a resource policy is suppressed, allowing you to avoid this problem. If you set this option to true, you must create a resource policy before deployment. Default: - false
        :param tls_security_policy: The minimum TLS version required for traffic to the domain. Default: - TLSSecurityPolicy.TLS_1_2
        :param use_unsigned_basic_auth: Configures the domain so that unsigned basic auth is enabled. If no master user is provided a default master user with username ``admin`` and a dynamically generated password stored in KMS is created. The password can be retrieved by getting ``masterUserPassword`` from the domain instance. Setting this to true will also add an access policy that allows unsigned access, enable node to node encryption, encryption at rest. If conflicting settings are encountered (like disabling encryption at rest) enabling this setting will cause a failure. Default: - false
        :param vpc: Place the domain inside this VPC. Default: - Domain is not placed in a VPC.
        :param vpc_subnets: The specific vpc subnets the domain will be placed in. You must provide one subnet for each Availability Zone that your domain uses. For example, you must specify three subnet IDs for a three Availability Zone domain. Only used if ``vpc`` is specified. Default: - All private subnets.
        :param zone_awareness: The cluster zone awareness configuration for the Amazon OpenSearch Service domain. Default: - no zone awareness (1 AZ)
        :param masteruser: 
        :param program: 
        :param project: 
        :param tier: 
        '''
        if isinstance(capacity, dict):
            capacity = _aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig(**capacity)
        if isinstance(cognito_dashboards_auth, dict):
            cognito_dashboards_auth = _aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions(**cognito_dashboards_auth)
        if isinstance(custom_endpoint, dict):
            custom_endpoint = _aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions(**custom_endpoint)
        if isinstance(ebs, dict):
            ebs = _aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions(**ebs)
        if isinstance(encryption_at_rest, dict):
            encryption_at_rest = _aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions(**encryption_at_rest)
        if isinstance(fine_grained_access_control, dict):
            fine_grained_access_control = _aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions(**fine_grained_access_control)
        if isinstance(logging, dict):
            logging = _aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions(**logging)
        if isinstance(off_peak_window_start, dict):
            off_peak_window_start = _aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime(**off_peak_window_start)
        if isinstance(zone_awareness, dict):
            zone_awareness = _aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig(**zone_awareness)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b98a65b43d9cbd67c6c0c9178b7e8e1cf232aa09bcdd5767936652f1dc6370)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument access_policies", value=access_policies, expected_type=type_hints["access_policies"])
            check_type(argname="argument advanced_options", value=advanced_options, expected_type=type_hints["advanced_options"])
            check_type(argname="argument automated_snapshot_start_hour", value=automated_snapshot_start_hour, expected_type=type_hints["automated_snapshot_start_hour"])
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument cognito_dashboards_auth", value=cognito_dashboards_auth, expected_type=type_hints["cognito_dashboards_auth"])
            check_type(argname="argument cold_storage_enabled", value=cold_storage_enabled, expected_type=type_hints["cold_storage_enabled"])
            check_type(argname="argument custom_endpoint", value=custom_endpoint, expected_type=type_hints["custom_endpoint"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument ebs", value=ebs, expected_type=type_hints["ebs"])
            check_type(argname="argument enable_auto_software_update", value=enable_auto_software_update, expected_type=type_hints["enable_auto_software_update"])
            check_type(argname="argument enable_version_upgrade", value=enable_version_upgrade, expected_type=type_hints["enable_version_upgrade"])
            check_type(argname="argument encryption_at_rest", value=encryption_at_rest, expected_type=type_hints["encryption_at_rest"])
            check_type(argname="argument enforce_https", value=enforce_https, expected_type=type_hints["enforce_https"])
            check_type(argname="argument fine_grained_access_control", value=fine_grained_access_control, expected_type=type_hints["fine_grained_access_control"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument node_to_node_encryption", value=node_to_node_encryption, expected_type=type_hints["node_to_node_encryption"])
            check_type(argname="argument off_peak_window_enabled", value=off_peak_window_enabled, expected_type=type_hints["off_peak_window_enabled"])
            check_type(argname="argument off_peak_window_start", value=off_peak_window_start, expected_type=type_hints["off_peak_window_start"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument suppress_logs_resource_policy", value=suppress_logs_resource_policy, expected_type=type_hints["suppress_logs_resource_policy"])
            check_type(argname="argument tls_security_policy", value=tls_security_policy, expected_type=type_hints["tls_security_policy"])
            check_type(argname="argument use_unsigned_basic_auth", value=use_unsigned_basic_auth, expected_type=type_hints["use_unsigned_basic_auth"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument zone_awareness", value=zone_awareness, expected_type=type_hints["zone_awareness"])
            check_type(argname="argument masteruser", value=masteruser, expected_type=type_hints["masteruser"])
            check_type(argname="argument program", value=program, expected_type=type_hints["program"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
            "masteruser": masteruser,
            "program": program,
            "project": project,
            "tier": tier,
        }
        if access_policies is not None:
            self._values["access_policies"] = access_policies
        if advanced_options is not None:
            self._values["advanced_options"] = advanced_options
        if automated_snapshot_start_hour is not None:
            self._values["automated_snapshot_start_hour"] = automated_snapshot_start_hour
        if capacity is not None:
            self._values["capacity"] = capacity
        if cognito_dashboards_auth is not None:
            self._values["cognito_dashboards_auth"] = cognito_dashboards_auth
        if cold_storage_enabled is not None:
            self._values["cold_storage_enabled"] = cold_storage_enabled
        if custom_endpoint is not None:
            self._values["custom_endpoint"] = custom_endpoint
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if ebs is not None:
            self._values["ebs"] = ebs
        if enable_auto_software_update is not None:
            self._values["enable_auto_software_update"] = enable_auto_software_update
        if enable_version_upgrade is not None:
            self._values["enable_version_upgrade"] = enable_version_upgrade
        if encryption_at_rest is not None:
            self._values["encryption_at_rest"] = encryption_at_rest
        if enforce_https is not None:
            self._values["enforce_https"] = enforce_https
        if fine_grained_access_control is not None:
            self._values["fine_grained_access_control"] = fine_grained_access_control
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if logging is not None:
            self._values["logging"] = logging
        if node_to_node_encryption is not None:
            self._values["node_to_node_encryption"] = node_to_node_encryption
        if off_peak_window_enabled is not None:
            self._values["off_peak_window_enabled"] = off_peak_window_enabled
        if off_peak_window_start is not None:
            self._values["off_peak_window_start"] = off_peak_window_start
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if suppress_logs_resource_policy is not None:
            self._values["suppress_logs_resource_policy"] = suppress_logs_resource_policy
        if tls_security_policy is not None:
            self._values["tls_security_policy"] = tls_security_policy
        if use_unsigned_basic_auth is not None:
            self._values["use_unsigned_basic_auth"] = use_unsigned_basic_auth
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if zone_awareness is not None:
            self._values["zone_awareness"] = zone_awareness

    @builtins.property
    def version(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion:
        '''The Elasticsearch/OpenSearch version that your domain will leverage.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion, result)

    @builtins.property
    def access_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Domain access policies.

        :default: - No access policies.
        '''
        result = self._values.get("access_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def advanced_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional options to specify for the Amazon OpenSearch Service domain.

        :default: - no advanced options are specified

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html#createdomain-configure-advanced-options
        '''
        result = self._values.get("advanced_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def automated_snapshot_start_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour in UTC during which the service takes an automated daily snapshot of the indices in the Amazon OpenSearch Service domain.

        Only applies for Elasticsearch versions
        below 5.3.

        :default: - Hourly automated snapshots not used
        '''
        result = self._values.get("automated_snapshot_start_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def capacity(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig]:
        '''The cluster capacity configuration for the Amazon OpenSearch Service domain.

        :default: - 1 r5.large.search data node; no dedicated master nodes.
        '''
        result = self._values.get("capacity")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig], result)

    @builtins.property
    def cognito_dashboards_auth(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions]:
        '''Configures Amazon OpenSearch Service to use Amazon Cognito authentication for OpenSearch Dashboards.

        :default: - Cognito not used for authentication to OpenSearch Dashboards.
        '''
        result = self._values.get("cognito_dashboards_auth")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions], result)

    @builtins.property
    def cold_storage_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable or disable cold storage on the domain.

        You must enable UltraWarm storage to enable cold storage.

        :default: - undefined

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cold-storage.html
        '''
        result = self._values.get("cold_storage_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions]:
        '''To configure a custom domain configure these options.

        If you specify a Route53 hosted zone it will create a CNAME record and use DNS validation for the certificate

        :default: - no custom domain endpoint will be configured
        '''
        result = self._values.get("custom_endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''Enforces a particular physical domain name.

        :default: - A name will be auto-generated.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions]:
        '''The configurations of Amazon Elastic Block Store (Amazon EBS) volumes that are attached to data nodes in the Amazon OpenSearch Service domain.

        :default: - 10 GiB General Purpose (SSD) volumes per node.
        '''
        result = self._values.get("ebs")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions], result)

    @builtins.property
    def enable_auto_software_update(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether automatic service software updates are enabled for the domain.

        :default: - false

        :see: https://docs.aws.amazon.com/it_it/AWSCloudFormation/latest/UserGuide/aws-properties-opensearchservice-domain-softwareupdateoptions.html
        '''
        result = self._values.get("enable_auto_software_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''To upgrade an Amazon OpenSearch Service domain to a new version, rather than replacing the entire domain resource, use the EnableVersionUpgrade update policy.

        :default: - false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html#cfn-attributes-updatepolicy-upgradeopensearchdomain
        '''
        result = self._values.get("enable_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_at_rest(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions]:
        '''Encryption at rest options for the cluster.

        :default: - No encryption at rest
        '''
        result = self._values.get("encryption_at_rest")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions], result)

    @builtins.property
    def enforce_https(self) -> typing.Optional[builtins.bool]:
        '''True to require that all traffic to the domain arrive over HTTPS.

        :default: - false
        '''
        result = self._values.get("enforce_https")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def fine_grained_access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions]:
        '''Specifies options for fine-grained access control.

        Requires Elasticsearch version 6.7 or later or OpenSearch version 1.0 or later. Enabling fine-grained access control
        also requires encryption of data at rest and node-to-node encryption, along with
        enforced HTTPS.

        :default: - fine-grained access control is disabled
        '''
        result = self._values.get("fine_grained_access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType]:
        '''Specify either dual stack or IPv4 as your IP address type.

        Dual stack allows you to share domain resources across IPv4 and IPv6 address types, and is the recommended option.

        If you set your IP address type to dual stack, you can't change your address type later.

        :default: - IpAddressType.IPV4
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType], result)

    @builtins.property
    def logging(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions]:
        '''Configuration log publishing configuration options.

        :default: - No logs are published
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions], result)

    @builtins.property
    def node_to_node_encryption(self) -> typing.Optional[builtins.bool]:
        '''Specify true to enable node to node encryption.

        Requires Elasticsearch version 6.0 or later or OpenSearch version 1.0 or later.

        :default: - Node to node encryption is not enabled.
        '''
        result = self._values.get("node_to_node_encryption")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def off_peak_window_enabled(self) -> typing.Optional[builtins.bool]:
        '''Options for enabling a domain's off-peak window, during which OpenSearch Service can perform mandatory configuration changes on the domain.

        Off-peak windows were introduced on February 16, 2023.
        All domains created before this date have the off-peak window disabled by default.
        You must manually enable and configure the off-peak window for these domains.
        All domains created after this date will have the off-peak window enabled by default.
        You can't disable the off-peak window for a domain after it's enabled.

        :default: - Disabled for domains created before February 16, 2023. Enabled for domains created after. Enabled if ``offPeakWindowStart`` is set.

        :see: https://docs.aws.amazon.com/it_it/AWSCloudFormation/latest/UserGuide/aws-properties-opensearchservice-domain-offpeakwindow.html
        '''
        result = self._values.get("off_peak_window_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def off_peak_window_start(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime]:
        '''Start time for the off-peak window, in Coordinated Universal Time (UTC).

        The window length will always be 10 hours, so you can't specify an end time.
        For example, if you specify 11:00 P.M. UTC as a start time, the end time will automatically be set to 9:00 A.M.

        :default: - 10:00 P.M. local time
        '''
        result = self._values.get("off_peak_window_start")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the domain is removed from the stack.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of security groups that are associated with the VPC endpoints for the domain.

        Only used if ``vpc`` is specified.

        :default: - One new security group is created.

        :see: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def suppress_logs_resource_policy(self) -> typing.Optional[builtins.bool]:
        '''Specify whether to create a CloudWatch Logs resource policy or not.

        When logging is enabled for the domain, a CloudWatch Logs resource policy is created by default.
        However, CloudWatch Logs supports only 10 resource policies per region.
        If you enable logging for several domains, it may hit the quota and cause an error.
        By setting this property to true, creating a resource policy is suppressed, allowing you to avoid this problem.

        If you set this option to true, you must create a resource policy before deployment.

        :default: - false

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createdomain-configure-slow-logs.html
        '''
        result = self._values.get("suppress_logs_resource_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tls_security_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy]:
        '''The minimum TLS version required for traffic to the domain.

        :default: - TLSSecurityPolicy.TLS_1_2
        '''
        result = self._values.get("tls_security_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy], result)

    @builtins.property
    def use_unsigned_basic_auth(self) -> typing.Optional[builtins.bool]:
        '''Configures the domain so that unsigned basic auth is enabled.

        If no master user is provided a default master user
        with username ``admin`` and a dynamically generated password stored in KMS is created. The password can be retrieved
        by getting ``masterUserPassword`` from the domain instance.

        Setting this to true will also add an access policy that allows unsigned
        access, enable node to node encryption, encryption at rest. If conflicting
        settings are encountered (like disabling encryption at rest) enabling this
        setting will cause a failure.

        :default: - false
        '''
        result = self._values.get("use_unsigned_basic_auth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''Place the domain inside this VPC.

        :default: - Domain is not placed in a VPC.

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vpc.html
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''The specific vpc subnets the domain will be placed in.

        You must provide one subnet for each Availability Zone
        that your domain uses. For example, you must specify three subnet IDs for a three Availability Zone
        domain.

        Only used if ``vpc`` is specified.

        :default: - All private subnets.

        :see: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def zone_awareness(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig]:
        '''The cluster zone awareness configuration for the Amazon OpenSearch Service domain.

        :default: - no zone awareness (1 AZ)
        '''
        result = self._values.get("zone_awareness")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig], result)

    @builtins.property
    def masteruser(self) -> builtins.str:
        result = self._values.get("masteruser")
        assert result is not None, "Required property 'masteruser' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def program(self) -> builtins.str:
        result = self._values.get("program")
        assert result is not None, "Required property 'program' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tier(self) -> builtins.str:
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FnlOpensearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FnlSpecRestApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlSpecRestApi",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        template_file_path: builtins.str,
        template_variables: typing.Mapping[builtins.str, builtins.str],
        api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
        match_pattern: typing.Optional[builtins.str] = None,
        stage_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageProps, typing.Dict[builtins.str, typing.Any]]] = None,
        validate_substitutions: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param template_file_path: Path to OpenAPI specification template file. This file should contain placeholders for template variables. Example: 'path/to/template.yaml'
        :param template_variables: Template variables to be substituted in the OpenAPI specification. Example: { "variableName": "value", "anotherVariable": "anotherValue" }
        :param api_props: Additional properties to pass to the underlying SpecRestApi construct. Note: apiDefinition will be ignored as it's generated from the template.
        :param match_pattern: Regular expression pattern to match template variables in the OpenAPI specification. By default, it will match any string enclosed in double curly braces with a dollar sign, e.g., ${{variable}} Default: '\\$\\{\\{([^}]+)\\}\\'
        :param stage_props: Optional properties for the API Gateway stage. If provided, a stage will be created with these properties.
        :param validate_substitutions: Whether to validate the substitutions in the OpenAPI specification. If true, it will throw an error if any template variable is not provided. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d53943d8525e3843ccf056273de7e1fa13ddec2fd7ff9ef649f6af2519e297a2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FnlSpecRestApiProps(
            template_file_path=template_file_path,
            template_variables=template_variables,
            api_props=api_props,
            match_pattern=match_pattern,
            stage_props=stage_props,
            validate_substitutions=validate_substitutions,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDomainName")
    def add_domain_name(
        self,
        id: builtins.str,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        domain_name: builtins.str,
        base_path: typing.Optional[builtins.str] = None,
        endpoint_type: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.EndpointType] = None,
        mtls: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MTLSConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        security_policy: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy] = None,
    ) -> _aws_cdk_aws_apigateway_ceddda9d.DomainName:
        '''Adds a custom domain name to the API Gateway.

        :param id: The ID for the domain name.
        :param certificate: The reference to an AWS-managed certificate for use by the edge-optimized endpoint for the domain name. For "EDGE" domain names, the certificate needs to be in the US East (N. Virginia) region.
        :param domain_name: The custom domain name for your API. Uppercase letters are not supported.
        :param base_path: The base path name that callers of the API must provide in the URL after the domain name (e.g. ``example.com/base-path``). If you specify this property, it can't be an empty string. Default: - map requests from the domain root (e.g. ``example.com``).
        :param endpoint_type: The type of endpoint for this DomainName. Default: REGIONAL
        :param mtls: The mutual TLS authentication configuration for a custom domain name. Default: - mTLS is not configured.
        :param security_policy: The Transport Layer Security (TLS) version + cipher suite for this domain name. Default: SecurityPolicy.TLS_1_2

        :return: The created domain name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__644ea4809e7189ff664581a8d8c3725a55606f3c2e84e039ec194fff19a2a47d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions(
            certificate=certificate,
            domain_name=domain_name,
            base_path=base_path,
            endpoint_type=endpoint_type,
            mtls=mtls,
            security_policy=security_policy,
        )

        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.DomainName, jsii.invoke(self, "addDomainName", [id, options]))

    @jsii.member(jsii_name="addUsagePlan")
    def add_usage_plan(
        self,
        id: builtins.str,
        *,
        api_stages: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.UsagePlanPerApiStage, typing.Dict[builtins.str, typing.Any]]]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        quota: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.QuotaSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> _aws_cdk_aws_apigateway_ceddda9d.UsagePlan:
        '''Adds a usage plan to the API Gateway.

        :param id: The ID for the usage plan.
        :param api_stages: API Stages to be associated with the usage plan. Default: none
        :param description: Represents usage plan purpose. Default: none
        :param name: Name for this usage plan. Default: none
        :param quota: Number of requests clients can make in a given time period. Default: none
        :param throttle: Overall throttle settings for the API. Default: none

        :return: The created usage plan.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0798befcbf026271ee5b671de87e53e744e873aabe55edce05e6aae3f18395ad)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_apigateway_ceddda9d.UsagePlanProps(
            api_stages=api_stages,
            description=description,
            name=name,
            quota=quota,
            throttle=throttle,
        )

        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.UsagePlan, jsii.invoke(self, "addUsagePlan", [id, props]))

    @jsii.member(jsii_name="applyRemovalPolicy")
    def apply_removal_policy(self, policy: _aws_cdk_ceddda9d.RemovalPolicy) -> None:
        '''Applies a removal policy to the API Gateway.

        :param policy: The removal policy to apply to the API Gateway.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5dd7a3adb02a66eaf2ae7fcb73aa12dd017247d3f0d41023af9f707ca9f9959)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        return typing.cast(None, jsii.invoke(self, "applyRemovalPolicy", [policy]))

    @jsii.member(jsii_name="arnForExecuteApi")
    def arn_for_execute_api(
        self,
        method: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''Returns the ARN for the API Gateway's execute API.

        :param method: The HTTP method (e.g., 'GET', 'POST').
        :param path: The resource path (e.g., '/users').
        :param stage: The API Gateway stage (e.g., 'dev').

        :return: The ARN for the execute API.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__426f02f5528cb7a416889a32e3c9fca2d65fed1bf727c0870f292a2479c45ece)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        return typing.cast(builtins.str, jsii.invoke(self, "arnForExecuteApi", [method, path, stage]))

    @jsii.member(jsii_name="urlForPath")
    def url_for_path(self, path: builtins.str) -> builtins.str:
        '''Returns the URL for a specific path in the API Gateway.

        :param path: The resource path (e.g., '/users').

        :return: The URL for the specified path.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e94a5dd72319f653a3c48b65be222c9c2d4844dd208d6f050f7cdfbcb7601a6d)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.invoke(self, "urlForPath", [path]))

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.SpecRestApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> _aws_cdk_aws_apigateway_ceddda9d.Deployment:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.Deployment, jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "logGroup"))

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "FnlStage":
        return typing.cast("FnlStage", jsii.get(self, "stage"))


@jsii.data_type(
    jsii_type="fnl-aws-cdk.FnlSpecRestApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "template_file_path": "templateFilePath",
        "template_variables": "templateVariables",
        "api_props": "apiProps",
        "match_pattern": "matchPattern",
        "stage_props": "stageProps",
        "validate_substitutions": "validateSubstitutions",
    },
)
class FnlSpecRestApiProps:
    def __init__(
        self,
        *,
        template_file_path: builtins.str,
        template_variables: typing.Mapping[builtins.str, builtins.str],
        api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
        match_pattern: typing.Optional[builtins.str] = None,
        stage_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageProps, typing.Dict[builtins.str, typing.Any]]] = None,
        validate_substitutions: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Template-specific properties for FnlSpecRestApi construct.

        :param template_file_path: Path to OpenAPI specification template file. This file should contain placeholders for template variables. Example: 'path/to/template.yaml'
        :param template_variables: Template variables to be substituted in the OpenAPI specification. Example: { "variableName": "value", "anotherVariable": "anotherValue" }
        :param api_props: Additional properties to pass to the underlying SpecRestApi construct. Note: apiDefinition will be ignored as it's generated from the template.
        :param match_pattern: Regular expression pattern to match template variables in the OpenAPI specification. By default, it will match any string enclosed in double curly braces with a dollar sign, e.g., ${{variable}} Default: '\\$\\{\\{([^}]+)\\}\\'
        :param stage_props: Optional properties for the API Gateway stage. If provided, a stage will be created with these properties.
        :param validate_substitutions: Whether to validate the substitutions in the OpenAPI specification. If true, it will throw an error if any template variable is not provided. Default: true
        '''
        if isinstance(api_props, dict):
            api_props = _aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps(**api_props)
        if isinstance(stage_props, dict):
            stage_props = _aws_cdk_aws_apigateway_ceddda9d.StageProps(**stage_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad4096376fc7f43c85dae1bd827497ead46d36357bd0fcc6fc8a57272348a13a)
            check_type(argname="argument template_file_path", value=template_file_path, expected_type=type_hints["template_file_path"])
            check_type(argname="argument template_variables", value=template_variables, expected_type=type_hints["template_variables"])
            check_type(argname="argument api_props", value=api_props, expected_type=type_hints["api_props"])
            check_type(argname="argument match_pattern", value=match_pattern, expected_type=type_hints["match_pattern"])
            check_type(argname="argument stage_props", value=stage_props, expected_type=type_hints["stage_props"])
            check_type(argname="argument validate_substitutions", value=validate_substitutions, expected_type=type_hints["validate_substitutions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "template_file_path": template_file_path,
            "template_variables": template_variables,
        }
        if api_props is not None:
            self._values["api_props"] = api_props
        if match_pattern is not None:
            self._values["match_pattern"] = match_pattern
        if stage_props is not None:
            self._values["stage_props"] = stage_props
        if validate_substitutions is not None:
            self._values["validate_substitutions"] = validate_substitutions

    @builtins.property
    def template_file_path(self) -> builtins.str:
        '''Path to OpenAPI specification template file.

        This file should contain placeholders for template variables.
        Example: 'path/to/template.yaml'
        '''
        result = self._values.get("template_file_path")
        assert result is not None, "Required property 'template_file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_variables(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Template variables to be substituted in the OpenAPI specification.

        Example: { "variableName": "value", "anotherVariable": "anotherValue" }
        '''
        result = self._values.get("template_variables")
        assert result is not None, "Required property 'template_variables' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def api_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps]:
        '''Additional properties to pass to the underlying SpecRestApi construct.

        Note: apiDefinition will be ignored as it's generated from the template.
        '''
        result = self._values.get("api_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps], result)

    @builtins.property
    def match_pattern(self) -> typing.Optional[builtins.str]:
        '''Regular expression pattern to match template variables in the OpenAPI specification.

        By default, it will match any string enclosed in double curly braces with a dollar sign, e.g., ${{variable}}

        :default: '\\$\\{\\{([^}]+)\\}\\'
        '''
        result = self._values.get("match_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.StageProps]:
        '''Optional properties for the API Gateway stage.

        If provided, a stage will be created with these properties.
        '''
        result = self._values.get("stage_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.StageProps], result)

    @builtins.property
    def validate_substitutions(self) -> typing.Optional[builtins.bool]:
        '''Whether to validate the substitutions in the OpenAPI specification.

        If true, it will throw an error if any template variable is not provided.

        :default: true
        '''
        result = self._values.get("validate_substitutions")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FnlSpecRestApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FnlStage(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.FnlStage",
):
    '''Custom Stage for API Gateway that allows for additional properties or methods to be added in the future.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        deployment: _aws_cdk_aws_apigateway_ceddda9d.Deployment,
        access_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
        access_log_format: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AccessLogFormat] = None,
        cache_cluster_enabled: typing.Optional[builtins.bool] = None,
        cache_cluster_size: typing.Optional[builtins.str] = None,
        client_certificate_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        documentation_version: typing.Optional[builtins.str] = None,
        method_options: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodDeploymentOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        stage_name: typing.Optional[builtins.str] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        cache_data_encrypted: typing.Optional[builtins.bool] = None,
        cache_ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        caching_enabled: typing.Optional[builtins.bool] = None,
        data_trace_enabled: typing.Optional[builtins.bool] = None,
        logging_level: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodLoggingLevel] = None,
        metrics_enabled: typing.Optional[builtins.bool] = None,
        throttling_burst_limit: typing.Optional[jsii.Number] = None,
        throttling_rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param deployment: The deployment that this stage points to [disable-awslint:ref-via-interface].
        :param access_log_destination: The CloudWatch Logs log group or Firehose delivery stream where to write access logs. Default: - No destination
        :param access_log_format: A single line format of access logs of data, as specified by selected $content variables. The format must include either ``AccessLogFormat.contextRequestId()`` or ``AccessLogFormat.contextExtendedRequestId()``. Default: - Common Log Format
        :param cache_cluster_enabled: Indicates whether cache clustering is enabled for the stage. Default: - Disabled for the stage.
        :param cache_cluster_size: The stage's cache cluster size. Default: 0.5
        :param client_certificate_id: The identifier of the client certificate that API Gateway uses to call your integration endpoints in the stage. Default: - None.
        :param description: A description of the purpose of the stage. Default: - No description.
        :param documentation_version: The version identifier of the API documentation snapshot. Default: - No documentation version.
        :param method_options: Method deployment options for specific resources/methods. These will override common options defined in ``StageOptions#methodOptions``. Default: - Common options will be used.
        :param stage_name: The name of the stage, which API Gateway uses as the first path segment in the invoked Uniform Resource Identifier (URI). Default: - "prod"
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this method. Default: false
        :param variables: A map that defines the stage variables. Variable names must consist of alphanumeric characters, and the values must match the following regular expression: [A-Za-z0-9-._~:/?#&=,]+. Default: - No stage variables.
        :param cache_data_encrypted: Indicates whether the cached responses are encrypted. Default: false
        :param cache_ttl: Specifies the time to live (TTL), in seconds, for cached responses. The higher the TTL, the longer the response will be cached. Default: Duration.minutes(5)
        :param caching_enabled: Specifies whether responses should be cached and returned for requests. A cache cluster must be enabled on the stage for responses to be cached. Default: - Caching is Disabled.
        :param data_trace_enabled: Specifies whether data trace logging is enabled for this method. When enabled, API gateway will log the full API requests and responses. This can be useful to troubleshoot APIs, but can result in logging sensitive data. We recommend that you don't enable this feature for production APIs. Default: false
        :param logging_level: Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs. Default: - Off
        :param metrics_enabled: Specifies whether Amazon CloudWatch metrics are enabled for this method. Default: false
        :param throttling_burst_limit: Specifies the throttling burst limit. The total rate of all requests in your AWS account is limited to 5,000 requests. Default: - No additional restriction.
        :param throttling_rate_limit: Specifies the throttling rate limit. The total rate of all requests in your AWS account is limited to 10,000 requests per second (rps). Default: - No additional restriction.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f035d03428591c7bdd7b9e3b87e37dc394141cc16cb05b6a51c24f4dc39a7674)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_apigateway_ceddda9d.StageProps(
            deployment=deployment,
            access_log_destination=access_log_destination,
            access_log_format=access_log_format,
            cache_cluster_enabled=cache_cluster_enabled,
            cache_cluster_size=cache_cluster_size,
            client_certificate_id=client_certificate_id,
            description=description,
            documentation_version=documentation_version,
            method_options=method_options,
            stage_name=stage_name,
            tracing_enabled=tracing_enabled,
            variables=variables,
            cache_data_encrypted=cache_data_encrypted,
            cache_ttl=cache_ttl,
            caching_enabled=caching_enabled,
            data_trace_enabled=data_trace_enabled,
            logging_level=logging_level,
            metrics_enabled=metrics_enabled,
            throttling_burst_limit=throttling_burst_limit,
            throttling_rate_limit=throttling_rate_limit,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> _aws_cdk_aws_apigateway_ceddda9d.Stage:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.Stage, jsii.get(self, "stage"))


__all__ = [
    "FnlApplicationLoadBalancer",
    "FnlApplicationLoadBalancerProps",
    "FnlDatabaseCluster",
    "FnlDatabaseClusterProps",
    "FnlDomain",
    "FnlFunction",
    "FnlFunctionProps",
    "FnlLogGroup",
    "FnlLogGroupProps",
    "FnlOpensearchProps",
    "FnlSpecRestApi",
    "FnlSpecRestApiProps",
    "FnlStage",
]

publication.publish()

def _typecheckingstub__13150ce831166ee97725a053aacabfb0d1c7c9fefa771701160d406b6b11a7e4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    log_bucket_name: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
    client_keep_alive: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    desync_mitigation_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.DesyncMitigationMode] = None,
    drop_invalid_header_fields: typing.Optional[builtins.bool] = None,
    http2_enabled: typing.Optional[builtins.bool] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    preserve_host_header: typing.Optional[builtins.bool] = None,
    preserve_xff_client_port: typing.Optional[builtins.bool] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    waf_fail_open: typing.Optional[builtins.bool] = None,
    x_amzn_tls_version_and_cipher_suite_headers: typing.Optional[builtins.bool] = None,
    xff_header_processing_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.XffHeaderProcessingMode] = None,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cross_zone_enabled: typing.Optional[builtins.bool] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    deny_all_igw_traffic: typing.Optional[builtins.bool] = None,
    internet_facing: typing.Optional[builtins.bool] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    minimum_capacity_unit: typing.Optional[jsii.Number] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9382dfd5cf2bf47c34d25a6822f705db560b63e011a772ea5ced0e684577823e(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cross_zone_enabled: typing.Optional[builtins.bool] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    deny_all_igw_traffic: typing.Optional[builtins.bool] = None,
    internet_facing: typing.Optional[builtins.bool] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    minimum_capacity_unit: typing.Optional[jsii.Number] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    client_keep_alive: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    desync_mitigation_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.DesyncMitigationMode] = None,
    drop_invalid_header_fields: typing.Optional[builtins.bool] = None,
    http2_enabled: typing.Optional[builtins.bool] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    preserve_host_header: typing.Optional[builtins.bool] = None,
    preserve_xff_client_port: typing.Optional[builtins.bool] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    waf_fail_open: typing.Optional[builtins.bool] = None,
    x_amzn_tls_version_and_cipher_suite_headers: typing.Optional[builtins.bool] = None,
    xff_header_processing_mode: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.XffHeaderProcessingMode] = None,
    log_bucket_name: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80663bd98e0c4795537932bc105df8fb18eb5e00b2365adc3fb9a61f4dbf85fe(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    master_user: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
    days_after_password_rotation: typing.Optional[jsii.Number] = None,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
    backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
    cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
    copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
    default_database_name: typing.Optional[builtins.str] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    domain: typing.Optional[builtins.str] = None,
    domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
    enable_data_api: typing.Optional[builtins.bool] = None,
    enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
    iam_authentication: typing.Optional[builtins.bool] = None,
    instance_identifier_base: typing.Optional[builtins.str] = None,
    instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    instances: typing.Optional[jsii.Number] = None,
    instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
    monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
    port: typing.Optional[jsii.Number] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_source_identifier: typing.Optional[builtins.str] = None,
    s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_v2_auto_pause_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
    serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
    storage_encrypted: typing.Optional[builtins.bool] = None,
    storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
    subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__902bd453cb25d04eae50c39a5bba0022bed12f9f4be93b8c8640b424f416c92e(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
    backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
    cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
    copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
    default_database_name: typing.Optional[builtins.str] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    domain: typing.Optional[builtins.str] = None,
    domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
    enable_data_api: typing.Optional[builtins.bool] = None,
    enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
    iam_authentication: typing.Optional[builtins.bool] = None,
    instance_identifier_base: typing.Optional[builtins.str] = None,
    instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    instances: typing.Optional[jsii.Number] = None,
    instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
    monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
    port: typing.Optional[jsii.Number] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_source_identifier: typing.Optional[builtins.str] = None,
    s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_v2_auto_pause_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
    serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
    storage_encrypted: typing.Optional[builtins.bool] = None,
    storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
    subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    master_user: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
    days_after_password_rotation: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1774551a478936302e0e03196bb20bdab223251d49cf6559d37ce058b9840fed(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    masteruser: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
    version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
    access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
    capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cold_storage_enabled: typing.Optional[builtins.bool] = None,
    custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    domain_name: typing.Optional[builtins.str] = None,
    ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_auto_software_update: typing.Optional[builtins.bool] = None,
    enable_version_upgrade: typing.Optional[builtins.bool] = None,
    encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enforce_https: typing.Optional[builtins.bool] = None,
    fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
    logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    node_to_node_encryption: typing.Optional[builtins.bool] = None,
    off_peak_window_enabled: typing.Optional[builtins.bool] = None,
    off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
    tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
    use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acc9182e49dbeda08843e3f91358010a394f53520d65c6ec34ac3d5aab936357(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    code: _aws_cdk_aws_lambda_ceddda9d.Code,
    handler: builtins.str,
    runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
    adot_instrumentation: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    allow_public_subnet: typing.Optional[builtins.bool] = None,
    application_log_level: typing.Optional[builtins.str] = None,
    application_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel] = None,
    architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    code_signing_config: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig] = None,
    current_version_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.VersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
    dead_letter_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    events: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
    filesystem: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem] = None,
    function_name: typing.Optional[builtins.str] = None,
    initial_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    insights_version: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion] = None,
    ipv6_allowed_for_dual_stack: typing.Optional[builtins.bool] = None,
    layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
    log_format: typing.Optional[builtins.str] = None,
    logging_format: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    log_removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    log_retention_retry_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    log_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    params_and_secrets: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion] = None,
    profiling: typing.Optional[builtins.bool] = None,
    profiling_group: typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup] = None,
    recursive_loop: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop] = None,
    reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    runtime_management_mode: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    snap_start: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf] = None,
    system_log_level: typing.Optional[builtins.str] = None,
    system_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    tracing: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    on_failure: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
    on_success: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
    retry_attempts: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d2d45ddfe1fafd9faa95821aef8b21e5eb0f1615bfdd44d99b07408a0563f56(
    *,
    max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    on_failure: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
    on_success: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
    retry_attempts: typing.Optional[jsii.Number] = None,
    adot_instrumentation: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    allow_public_subnet: typing.Optional[builtins.bool] = None,
    application_log_level: typing.Optional[builtins.str] = None,
    application_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel] = None,
    architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    code_signing_config: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig] = None,
    current_version_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.VersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
    dead_letter_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    events: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
    filesystem: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem] = None,
    function_name: typing.Optional[builtins.str] = None,
    initial_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    insights_version: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion] = None,
    ipv6_allowed_for_dual_stack: typing.Optional[builtins.bool] = None,
    layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
    log_format: typing.Optional[builtins.str] = None,
    logging_format: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    log_removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    log_retention_retry_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    log_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    params_and_secrets: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion] = None,
    profiling: typing.Optional[builtins.bool] = None,
    profiling_group: typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup] = None,
    recursive_loop: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop] = None,
    reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    runtime_management_mode: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    snap_start: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf] = None,
    system_log_level: typing.Optional[builtins.str] = None,
    system_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    tracing: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    code: _aws_cdk_aws_lambda_ceddda9d.Code,
    handler: builtins.str,
    runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37ca06dbea84aa08fca36e59e2f74d21679f3ecced9bc33f1ac1b90c78d5a77a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    data_protection_policy: typing.Optional[_aws_cdk_aws_logs_ceddda9d.DataProtectionPolicy] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    field_index_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.FieldIndexPolicy]] = None,
    log_group_class: typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupClass] = None,
    log_group_name: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__172d9afbfa9f9cb58059d2150f802150d6554e803098d03773c0a48586061702(
    *,
    data_protection_policy: typing.Optional[_aws_cdk_aws_logs_ceddda9d.DataProtectionPolicy] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    field_index_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.FieldIndexPolicy]] = None,
    log_group_class: typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupClass] = None,
    log_group_name: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b98a65b43d9cbd67c6c0c9178b7e8e1cf232aa09bcdd5767936652f1dc6370(
    *,
    version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
    access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
    capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cold_storage_enabled: typing.Optional[builtins.bool] = None,
    custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    domain_name: typing.Optional[builtins.str] = None,
    ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_auto_software_update: typing.Optional[builtins.bool] = None,
    enable_version_upgrade: typing.Optional[builtins.bool] = None,
    encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enforce_https: typing.Optional[builtins.bool] = None,
    fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
    logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    node_to_node_encryption: typing.Optional[builtins.bool] = None,
    off_peak_window_enabled: typing.Optional[builtins.bool] = None,
    off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
    tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
    use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    masteruser: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d53943d8525e3843ccf056273de7e1fa13ddec2fd7ff9ef649f6af2519e297a2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    template_file_path: builtins.str,
    template_variables: typing.Mapping[builtins.str, builtins.str],
    api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    match_pattern: typing.Optional[builtins.str] = None,
    stage_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageProps, typing.Dict[builtins.str, typing.Any]]] = None,
    validate_substitutions: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__644ea4809e7189ff664581a8d8c3725a55606f3c2e84e039ec194fff19a2a47d(
    id: builtins.str,
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    domain_name: builtins.str,
    base_path: typing.Optional[builtins.str] = None,
    endpoint_type: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.EndpointType] = None,
    mtls: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MTLSConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    security_policy: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0798befcbf026271ee5b671de87e53e744e873aabe55edce05e6aae3f18395ad(
    id: builtins.str,
    *,
    api_stages: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.UsagePlanPerApiStage, typing.Dict[builtins.str, typing.Any]]]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    quota: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.QuotaSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5dd7a3adb02a66eaf2ae7fcb73aa12dd017247d3f0d41023af9f707ca9f9959(
    policy: _aws_cdk_ceddda9d.RemovalPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__426f02f5528cb7a416889a32e3c9fca2d65fed1bf727c0870f292a2479c45ece(
    method: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    stage: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e94a5dd72319f653a3c48b65be222c9c2d4844dd208d6f050f7cdfbcb7601a6d(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4096376fc7f43c85dae1bd827497ead46d36357bd0fcc6fc8a57272348a13a(
    *,
    template_file_path: builtins.str,
    template_variables: typing.Mapping[builtins.str, builtins.str],
    api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.SpecRestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    match_pattern: typing.Optional[builtins.str] = None,
    stage_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageProps, typing.Dict[builtins.str, typing.Any]]] = None,
    validate_substitutions: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f035d03428591c7bdd7b9e3b87e37dc394141cc16cb05b6a51c24f4dc39a7674(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    deployment: _aws_cdk_aws_apigateway_ceddda9d.Deployment,
    access_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
    access_log_format: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AccessLogFormat] = None,
    cache_cluster_enabled: typing.Optional[builtins.bool] = None,
    cache_cluster_size: typing.Optional[builtins.str] = None,
    client_certificate_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    documentation_version: typing.Optional[builtins.str] = None,
    method_options: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodDeploymentOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    stage_name: typing.Optional[builtins.str] = None,
    tracing_enabled: typing.Optional[builtins.bool] = None,
    variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    cache_data_encrypted: typing.Optional[builtins.bool] = None,
    cache_ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    caching_enabled: typing.Optional[builtins.bool] = None,
    data_trace_enabled: typing.Optional[builtins.bool] = None,
    logging_level: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodLoggingLevel] = None,
    metrics_enabled: typing.Optional[builtins.bool] = None,
    throttling_burst_limit: typing.Optional[jsii.Number] = None,
    throttling_rate_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
