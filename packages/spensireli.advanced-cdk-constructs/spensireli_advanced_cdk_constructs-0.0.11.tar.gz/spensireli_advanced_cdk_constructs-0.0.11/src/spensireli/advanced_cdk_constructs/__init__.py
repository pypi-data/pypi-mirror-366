r'''
# Advanced CDK Constructs

[![codecov](https://codecov.io/gh/spensireli/advanced-cdk-constructs/graph/badge.svg?token=50IITI207T)](https://codecov.io/gh/spensireli/advanced-cdk-constructs)

A collection of advanced AWS CDK constructs to simplify AWS.

## Installation

### From NPM

```bash
npm install advanced-cdk-constructs
```

### From GitHub

```bash
npm install git+https://github.com/spensireli/advanced-cdk-constructs.git
```

## Available Constructs

### GuardDuty Construct

The `GuardDutyConstruct` provides a simplified way to deploy AWS GuardDuty with common security configurations.

#### Import

```python
import { GuardDutyConstruct, GuardDutyConstructProps } from 'advanced-cdk-constructs';
```

#### Basic Usage

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { GuardDutyConstruct } from 'advanced-cdk-constructs';

export class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create GuardDuty with default settings
    const guardDuty = new GuardDutyConstruct(this, 'MyGuardDuty');
  }
}
```

#### Advanced Configuration

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { GuardDutyConstruct, GuardDutyConstructProps } from 'advanced-cdk-constructs';

export class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const guardDutyProps: GuardDutyConstructProps = {
      enableGuardDuty: true,
      kubernetesAuditLogs: true,
      malwareProtection: true,
      s3Logs: true,
    };

    const guardDuty = new GuardDutyConstruct(this, 'MyGuardDuty', guardDutyProps);

    // Access the detector ID for other resources
    console.log('GuardDuty Detector ID:', guardDuty.detectorId);
  }
}
```

#### Configuration Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enableGuardDuty` | `boolean` | `true` | Whether to enable GuardDuty |
| `kubernetesAuditLogs` | `boolean` | `true` | Enable Kubernetes audit logs monitoring |
| `malwareProtection` | `boolean` | `true` | Enable malware protection for EC2 instances |
| `s3Logs` | `boolean` | `true` | Enable S3 logs monitoring |

#### Features

* **Runtime Monitoring**: Automatically enabled for comprehensive threat detection
* **Kubernetes Audit Logs**: Monitors Kubernetes cluster activities
* **Malware Protection**: Scans EC2 instances for malware
* **S3 Logs Monitoring**: Monitors S3 bucket activities for suspicious behavior
* **Detector ID Access**: Public property to reference the detector in other constructs

## Development

### Prerequisites

* Node.js 22.0.0 or higher
* AWS CDK CLI
* TypeScript

### Setup

1. Clone the repository:

```bash
git clone git@github.com:spensireli/advanced-cdk-constructs.git
cd advanced-cdk-constructs
```

1. Install dependencies:

```bash
npm install
```

1. Build the project:

```bash
npx projen build
```

### Testing

Run the test suite:

```bash
npx projen test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/spensireli/advanced-cdk-constructs).
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
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="advanced-cdk-constructs.AllowedImagesState")
class AllowedImagesState(enum.Enum):
    '''(experimental) State for allowed images policy.

    :stability: experimental
    '''

    ENABLED = "ENABLED"
    '''(experimental) Only allow images from specified providers.

    :stability: experimental
    '''
    AUDIT_MODE = "AUDIT_MODE"
    '''(experimental) Audit mode for allowed images.

    :stability: experimental
    '''


class AwsAccount(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.AwsAccount",
):
    '''(experimental) A CDK construct that creates a new AWS Account within an AWS Organization.

    This construct creates a new AWS account and optionally places it within
    specified organizational units. The account can be configured with cross-account
    access roles and organizational tags.

    Example::

       new AwsAccount(this, 'MyAccount', {
         name: 'Development Account',
         email: 'dev-account@example.com',
         parentIds: ['ou-xxxx-xxxxxxxx'],
         roleName: 'OrganizationAccountAccessRole',
         tags: [
           { key: 'Environment', value: 'Development' },
           { key: 'Project', value: 'MyProject' }
         ]
       });

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        name: builtins.str,
        parent_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        role_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Creates a new AWS Account within the organization.

        :param scope: The parent construct.
        :param id: The construct ID.
        :param email: (experimental) The email address associated with the AWS account. This email must be unique and not already associated with another AWS account.
        :param name: (experimental) The name of the AWS account. This will be the display name in the AWS Organizations console.
        :param parent_ids: (experimental) Optional list of parent organizational unit IDs or root IDs. If not provided, the account will be placed in the root of the organization. Default: - Account will be placed in the root
        :param role_name: (experimental) Optional IAM role name to be used for cross-account access. This role will be created in the new account and can be assumed by the master account. Default: - No cross-account role will be created
        :param tags: (experimental) Optional list of tags to apply to the AWS account. These tags will help with organization and cost tracking. Default: - No tags will be applied

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b7dd93e1b3296247f5b7f9f0646e04e44fbfcb67d516c85ce5794f671e01bf0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AwsAccountProps(
            email=email,
            name=name,
            parent_ids=parent_ids,
            role_name=role_name,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="accountArn")
    def account_arn(self) -> builtins.str:
        '''(experimental) The ARN of the created AWS account.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountArn"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''(experimental) The AWS Account ID of the created account.

        This will be available after the account creation is complete.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''(experimental) The name of the AWS account as specified in the props.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property
    @jsii.member(jsii_name="accountStatus")
    def account_status(self) -> builtins.str:
        '''(experimental) The current status of the AWS account (e.g., 'ACTIVE', 'SUSPENDED').

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountStatus"))

    @builtins.property
    @jsii.member(jsii_name="joinedMethod")
    def joined_method(self) -> builtins.str:
        '''(experimental) The method by which the account joined the organization (e.g., 'INVITED').

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "joinedMethod"))

    @builtins.property
    @jsii.member(jsii_name="joinedTimestamp")
    def joined_timestamp(self) -> builtins.str:
        '''(experimental) The timestamp when the account joined the organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "joinedTimestamp"))


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.AwsAccountProps",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "name": "name",
        "parent_ids": "parentIds",
        "role_name": "roleName",
        "tags": "tags",
    },
)
class AwsAccountProps:
    def __init__(
        self,
        *,
        email: builtins.str,
        name: builtins.str,
        parent_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        role_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Properties for creating an AWS Account within an AWS Organization.

        :param email: (experimental) The email address associated with the AWS account. This email must be unique and not already associated with another AWS account.
        :param name: (experimental) The name of the AWS account. This will be the display name in the AWS Organizations console.
        :param parent_ids: (experimental) Optional list of parent organizational unit IDs or root IDs. If not provided, the account will be placed in the root of the organization. Default: - Account will be placed in the root
        :param role_name: (experimental) Optional IAM role name to be used for cross-account access. This role will be created in the new account and can be assumed by the master account. Default: - No cross-account role will be created
        :param tags: (experimental) Optional list of tags to apply to the AWS account. These tags will help with organization and cost tracking. Default: - No tags will be applied

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d151eb0ca9b90ff0364c8a56220f77443733db47131b4befd9ba1449e459df8)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parent_ids", value=parent_ids, expected_type=type_hints["parent_ids"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "name": name,
        }
        if parent_ids is not None:
            self._values["parent_ids"] = parent_ids
        if role_name is not None:
            self._values["role_name"] = role_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def email(self) -> builtins.str:
        '''(experimental) The email address associated with the AWS account.

        This email must be unique and not already associated with another AWS account.

        :stability: experimental
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the AWS account.

        This will be the display name in the AWS Organizations console.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Optional list of parent organizational unit IDs or root IDs.

        If not provided, the account will be placed in the root of the organization.

        :default: - Account will be placed in the root

        :stability: experimental
        '''
        result = self._values.get("parent_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional IAM role name to be used for cross-account access.

        This role will be created in the new account and can be assumed by the master account.

        :default: - No cross-account role will be created

        :stability: experimental
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''(experimental) Optional list of tags to apply to the AWS account.

        These tags will help with organization and cost tracking.

        :default: - No tags will be applied

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsAccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ControlTowerLandingZone(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.ControlTowerLandingZone",
):
    '''(experimental) AWS Control Tower Landing Zone construct.

    This construct provides a comprehensive solution for deploying and managing
    AWS Control Tower landing zones with centralized logging, security auditing,
    and organizational structure management.

    :stability: experimental

    Example::

        const landingZone = new ControlTowerLandingZone(this, 'MyLandingZone', {
          controlTowerStackName: 'my-control-tower',
          governedRegions: ['us-east-1', 'us-west-2'],
          logArchiveAccountEmail: 'log-archive@example.com',
          securityAuditAccountEmail: 'security-audit@example.com',
          logRetentionDays: 90,
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        control_tower_stack_name: builtins.str,
        access_logging_bucket_retention_days: typing.Optional[jsii.Number] = None,
        governed_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_archive_account_email: typing.Optional[builtins.str] = None,
        log_archive_account_id: typing.Optional[builtins.str] = None,
        log_archive_account_role_name: typing.Optional[builtins.str] = None,
        log_archive_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        logging_bucket_kms_key_arn: typing.Optional[builtins.str] = None,
        log_retention_days: typing.Optional[jsii.Number] = None,
        organization_structure: typing.Optional[typing.Mapping[builtins.str, typing.Union["OrganizationalUnit", typing.Dict[builtins.str, typing.Any]]]] = None,
        security_audit_account_email: typing.Optional[builtins.str] = None,
        security_audit_account_id: typing.Optional[builtins.str] = None,
        security_audit_account_role_name: typing.Optional[builtins.str] = None,
        security_audit_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Creates a new Control Tower Landing Zone.

        This constructor sets up the Control Tower landing zone with the specified
        configuration, including centralized logging, security auditing, and
        organizational structure management.

        :param scope: - The scope in which this construct is defined.
        :param id: - The unique identifier for this construct.
        :param control_tower_stack_name: (experimental) The name of the Control Tower stack.
        :param access_logging_bucket_retention_days: (experimental) Number of days to retain access logs in the access logging bucket. Default: - 60 days
        :param governed_regions: (experimental) AWS regions where Control Tower governance will be applied. Default: - Uses the current stack's region
        :param log_archive_account_email: (experimental) Email address for the log archive account. Required when logArchiveAccountId is not provided.
        :param log_archive_account_id: (experimental) AWS account ID for the log archive account. If not provided, a new account will be created using logArchiveAccountEmail.
        :param log_archive_account_role_name: (experimental) IAM role name for the log archive account. Default: - Uses Control Tower default role name
        :param log_archive_account_tags: (experimental) Tags to apply to the log archive account. Default: - Purpose: Log Archive, Environment: Production
        :param logging_bucket_kms_key_arn: (experimental) ARN of the KMS key for encrypting the logging bucket. If not provided, a new KMS key will be created.
        :param log_retention_days: (experimental) Number of days to retain logs in the centralized logging bucket. Default: - 60 days
        :param organization_structure: (experimental) Custom organizational structure. If not provided, defaults to AWS best practices structure. The default structure includes: - Security: Security and compliance accounts - Infrastructure: Shared services and tooling accounts - Workloads: Application workloads and production accounts - Sandbox: Development and testing accounts - Suspended: Isolated accounts requiring investigation Default: - AWS best practices organizational structure
        :param security_audit_account_email: (experimental) Email address for the security audit account. Required when securityAuditAccountId is not provided.
        :param security_audit_account_id: (experimental) AWS account ID for the security audit account. If not provided, a new account will be created using securityAuditAccountEmail.
        :param security_audit_account_role_name: (experimental) IAM role name for the security audit account. Default: - Uses Control Tower default role name
        :param security_audit_account_tags: (experimental) Tags to apply to the security audit account. Default: - Purpose: Security Audit, Environment: Production

        :stability: experimental
        :throws: {Error} When securityAuditAccountEmail is required but not provided
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cb6f81d8d4c2d56fa3847a45be1021aeaa1c2c4c0ff4d34db68af4e54b9c42a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ControlTowerLandingZoneProps(
            control_tower_stack_name=control_tower_stack_name,
            access_logging_bucket_retention_days=access_logging_bucket_retention_days,
            governed_regions=governed_regions,
            log_archive_account_email=log_archive_account_email,
            log_archive_account_id=log_archive_account_id,
            log_archive_account_role_name=log_archive_account_role_name,
            log_archive_account_tags=log_archive_account_tags,
            logging_bucket_kms_key_arn=logging_bucket_kms_key_arn,
            log_retention_days=log_retention_days,
            organization_structure=organization_structure,
            security_audit_account_email=security_audit_account_email,
            security_audit_account_id=security_audit_account_id,
            security_audit_account_role_name=security_audit_account_role_name,
            security_audit_account_tags=security_audit_account_tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="landingZoneArn")
    def landing_zone_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Control Tower landing zone.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "landingZoneArn"))

    @builtins.property
    @jsii.member(jsii_name="landingZoneId")
    def landing_zone_id(self) -> builtins.str:
        '''(experimental) The unique identifier of the Control Tower landing zone.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "landingZoneId"))

    @builtins.property
    @jsii.member(jsii_name="logArchiveAccountId")
    def log_archive_account_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS account ID of the log archive account.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logArchiveAccountId"))

    @builtins.property
    @jsii.member(jsii_name="loggingKmsKeyArn")
    def logging_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the KMS key used for logging bucket encryption.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggingKmsKeyArn"))

    @builtins.property
    @jsii.member(jsii_name="securityAuditAccountId")
    def security_audit_account_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS account ID of the security audit account.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityAuditAccountId"))


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.ControlTowerLandingZoneProps",
    jsii_struct_bases=[],
    name_mapping={
        "control_tower_stack_name": "controlTowerStackName",
        "access_logging_bucket_retention_days": "accessLoggingBucketRetentionDays",
        "governed_regions": "governedRegions",
        "log_archive_account_email": "logArchiveAccountEmail",
        "log_archive_account_id": "logArchiveAccountId",
        "log_archive_account_role_name": "logArchiveAccountRoleName",
        "log_archive_account_tags": "logArchiveAccountTags",
        "logging_bucket_kms_key_arn": "loggingBucketKmsKeyArn",
        "log_retention_days": "logRetentionDays",
        "organization_structure": "organizationStructure",
        "security_audit_account_email": "securityAuditAccountEmail",
        "security_audit_account_id": "securityAuditAccountId",
        "security_audit_account_role_name": "securityAuditAccountRoleName",
        "security_audit_account_tags": "securityAuditAccountTags",
    },
)
class ControlTowerLandingZoneProps:
    def __init__(
        self,
        *,
        control_tower_stack_name: builtins.str,
        access_logging_bucket_retention_days: typing.Optional[jsii.Number] = None,
        governed_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_archive_account_email: typing.Optional[builtins.str] = None,
        log_archive_account_id: typing.Optional[builtins.str] = None,
        log_archive_account_role_name: typing.Optional[builtins.str] = None,
        log_archive_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        logging_bucket_kms_key_arn: typing.Optional[builtins.str] = None,
        log_retention_days: typing.Optional[jsii.Number] = None,
        organization_structure: typing.Optional[typing.Mapping[builtins.str, typing.Union["OrganizationalUnit", typing.Dict[builtins.str, typing.Any]]]] = None,
        security_audit_account_email: typing.Optional[builtins.str] = None,
        security_audit_account_id: typing.Optional[builtins.str] = None,
        security_audit_account_role_name: typing.Optional[builtins.str] = None,
        security_audit_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Properties for configuring AWS Control Tower Landing Zone.

        This interface defines all the configuration options available for setting up
        a Control Tower landing zone with centralized logging, security auditing,
        and organizational structure management.

        :param control_tower_stack_name: (experimental) The name of the Control Tower stack.
        :param access_logging_bucket_retention_days: (experimental) Number of days to retain access logs in the access logging bucket. Default: - 60 days
        :param governed_regions: (experimental) AWS regions where Control Tower governance will be applied. Default: - Uses the current stack's region
        :param log_archive_account_email: (experimental) Email address for the log archive account. Required when logArchiveAccountId is not provided.
        :param log_archive_account_id: (experimental) AWS account ID for the log archive account. If not provided, a new account will be created using logArchiveAccountEmail.
        :param log_archive_account_role_name: (experimental) IAM role name for the log archive account. Default: - Uses Control Tower default role name
        :param log_archive_account_tags: (experimental) Tags to apply to the log archive account. Default: - Purpose: Log Archive, Environment: Production
        :param logging_bucket_kms_key_arn: (experimental) ARN of the KMS key for encrypting the logging bucket. If not provided, a new KMS key will be created.
        :param log_retention_days: (experimental) Number of days to retain logs in the centralized logging bucket. Default: - 60 days
        :param organization_structure: (experimental) Custom organizational structure. If not provided, defaults to AWS best practices structure. The default structure includes: - Security: Security and compliance accounts - Infrastructure: Shared services and tooling accounts - Workloads: Application workloads and production accounts - Sandbox: Development and testing accounts - Suspended: Isolated accounts requiring investigation Default: - AWS best practices organizational structure
        :param security_audit_account_email: (experimental) Email address for the security audit account. Required when securityAuditAccountId is not provided.
        :param security_audit_account_id: (experimental) AWS account ID for the security audit account. If not provided, a new account will be created using securityAuditAccountEmail.
        :param security_audit_account_role_name: (experimental) IAM role name for the security audit account. Default: - Uses Control Tower default role name
        :param security_audit_account_tags: (experimental) Tags to apply to the security audit account. Default: - Purpose: Security Audit, Environment: Production

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b445764c129628d9a04d592edf095a403b52996d6fcdc429cd07e0beb546704b)
            check_type(argname="argument control_tower_stack_name", value=control_tower_stack_name, expected_type=type_hints["control_tower_stack_name"])
            check_type(argname="argument access_logging_bucket_retention_days", value=access_logging_bucket_retention_days, expected_type=type_hints["access_logging_bucket_retention_days"])
            check_type(argname="argument governed_regions", value=governed_regions, expected_type=type_hints["governed_regions"])
            check_type(argname="argument log_archive_account_email", value=log_archive_account_email, expected_type=type_hints["log_archive_account_email"])
            check_type(argname="argument log_archive_account_id", value=log_archive_account_id, expected_type=type_hints["log_archive_account_id"])
            check_type(argname="argument log_archive_account_role_name", value=log_archive_account_role_name, expected_type=type_hints["log_archive_account_role_name"])
            check_type(argname="argument log_archive_account_tags", value=log_archive_account_tags, expected_type=type_hints["log_archive_account_tags"])
            check_type(argname="argument logging_bucket_kms_key_arn", value=logging_bucket_kms_key_arn, expected_type=type_hints["logging_bucket_kms_key_arn"])
            check_type(argname="argument log_retention_days", value=log_retention_days, expected_type=type_hints["log_retention_days"])
            check_type(argname="argument organization_structure", value=organization_structure, expected_type=type_hints["organization_structure"])
            check_type(argname="argument security_audit_account_email", value=security_audit_account_email, expected_type=type_hints["security_audit_account_email"])
            check_type(argname="argument security_audit_account_id", value=security_audit_account_id, expected_type=type_hints["security_audit_account_id"])
            check_type(argname="argument security_audit_account_role_name", value=security_audit_account_role_name, expected_type=type_hints["security_audit_account_role_name"])
            check_type(argname="argument security_audit_account_tags", value=security_audit_account_tags, expected_type=type_hints["security_audit_account_tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "control_tower_stack_name": control_tower_stack_name,
        }
        if access_logging_bucket_retention_days is not None:
            self._values["access_logging_bucket_retention_days"] = access_logging_bucket_retention_days
        if governed_regions is not None:
            self._values["governed_regions"] = governed_regions
        if log_archive_account_email is not None:
            self._values["log_archive_account_email"] = log_archive_account_email
        if log_archive_account_id is not None:
            self._values["log_archive_account_id"] = log_archive_account_id
        if log_archive_account_role_name is not None:
            self._values["log_archive_account_role_name"] = log_archive_account_role_name
        if log_archive_account_tags is not None:
            self._values["log_archive_account_tags"] = log_archive_account_tags
        if logging_bucket_kms_key_arn is not None:
            self._values["logging_bucket_kms_key_arn"] = logging_bucket_kms_key_arn
        if log_retention_days is not None:
            self._values["log_retention_days"] = log_retention_days
        if organization_structure is not None:
            self._values["organization_structure"] = organization_structure
        if security_audit_account_email is not None:
            self._values["security_audit_account_email"] = security_audit_account_email
        if security_audit_account_id is not None:
            self._values["security_audit_account_id"] = security_audit_account_id
        if security_audit_account_role_name is not None:
            self._values["security_audit_account_role_name"] = security_audit_account_role_name
        if security_audit_account_tags is not None:
            self._values["security_audit_account_tags"] = security_audit_account_tags

    @builtins.property
    def control_tower_stack_name(self) -> builtins.str:
        '''(experimental) The name of the Control Tower stack.

        :stability: experimental
        '''
        result = self._values.get("control_tower_stack_name")
        assert result is not None, "Required property 'control_tower_stack_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_logging_bucket_retention_days(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of days to retain access logs in the access logging bucket.

        :default: - 60 days

        :stability: experimental
        '''
        result = self._values.get("access_logging_bucket_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def governed_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) AWS regions where Control Tower governance will be applied.

        :default: - Uses the current stack's region

        :stability: experimental
        '''
        result = self._values.get("governed_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def log_archive_account_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Email address for the log archive account.

        Required when logArchiveAccountId is not provided.

        :stability: experimental
        '''
        result = self._values.get("log_archive_account_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_archive_account_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) AWS account ID for the log archive account.

        If not provided, a new account will be created using logArchiveAccountEmail.

        :stability: experimental
        '''
        result = self._values.get("log_archive_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_archive_account_role_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) IAM role name for the log archive account.

        :default: - Uses Control Tower default role name

        :stability: experimental
        '''
        result = self._values.get("log_archive_account_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_archive_account_tags(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''(experimental) Tags to apply to the log archive account.

        :default: - Purpose: Log Archive, Environment: Production

        :stability: experimental
        '''
        result = self._values.get("log_archive_account_tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    @builtins.property
    def logging_bucket_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) ARN of the KMS key for encrypting the logging bucket.

        If not provided, a new KMS key will be created.

        :stability: experimental
        '''
        result = self._values.get("logging_bucket_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention_days(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of days to retain logs in the centralized logging bucket.

        :default: - 60 days

        :stability: experimental
        '''
        result = self._values.get("log_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def organization_structure(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "OrganizationalUnit"]]:
        '''(experimental) Custom organizational structure. If not provided, defaults to AWS best practices structure.

        The default structure includes:

        - Security: Security and compliance accounts
        - Infrastructure: Shared services and tooling accounts
        - Workloads: Application workloads and production accounts
        - Sandbox: Development and testing accounts
        - Suspended: Isolated accounts requiring investigation

        :default: - AWS best practices organizational structure

        :stability: experimental
        '''
        result = self._values.get("organization_structure")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "OrganizationalUnit"]], result)

    @builtins.property
    def security_audit_account_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Email address for the security audit account.

        Required when securityAuditAccountId is not provided.

        :stability: experimental
        '''
        result = self._values.get("security_audit_account_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_audit_account_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) AWS account ID for the security audit account.

        If not provided, a new account will be created using securityAuditAccountEmail.

        :stability: experimental
        '''
        result = self._values.get("security_audit_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_audit_account_role_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) IAM role name for the security audit account.

        :default: - Uses Control Tower default role name

        :stability: experimental
        '''
        result = self._values.get("security_audit_account_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_audit_account_tags(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''(experimental) Tags to apply to the security audit account.

        :default: - Purpose: Security Audit, Environment: Production

        :stability: experimental
        '''
        result = self._values.get("security_audit_account_tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ControlTowerLandingZoneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DeclarativePolicy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.DeclarativePolicy",
):
    '''(experimental) A CDK construct that creates an AWS Organizations EC2 Declarative Policy.

    This construct allows you to declaratively define and apply EC2-related policies
    such as blocking public access to VPCs, restricting AMI providers, enforcing
    instance metadata service settings, and more.

    Example::

       new DeclarativePolicy(this, 'MyPolicy', {
         targetIds: ['ou-xxxx-xxxxxxxx'],
         vpcBlockPublicAccess: true,
         vpcBlockPublicAccessMode: VpcBlockPublicAccessMode.BLOCK_BIDIRECTIONAL,
       });

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        target_ids: typing.Sequence[builtins.str],
        allowed_image_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_images_state: typing.Optional[AllowedImagesState] = None,
        block_public_snapshots: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_serial_console_access: typing.Optional[builtins.bool] = None,
        http_endpoint: typing.Optional["HttpEndpoint"] = None,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional["HttpTokens"] = None,
        image_block_public_access: typing.Optional[builtins.bool] = None,
        instance_metadata_defaults: typing.Optional[builtins.bool] = None,
        instance_metadata_tags: typing.Optional["InstanceMetadataTags"] = None,
        name: typing.Optional[builtins.str] = None,
        restrict_image_providers: typing.Optional[builtins.bool] = None,
        snapshot_block_public_access_state: typing.Optional["SnapshotBlockPublicAccessState"] = None,
        vpc_block_public_access: typing.Optional[builtins.bool] = None,
        vpc_block_public_access_mode: typing.Optional["VpcBlockPublicAccessMode"] = None,
    ) -> None:
        '''(experimental) Create a new DeclarativePolicy.

        :param scope: The parent construct.
        :param id: The construct ID.
        :param target_ids: (experimental) The target AWS account or organizational unit IDs to which the policy will be attached.
        :param allowed_image_providers: (experimental) The list of allowed image providers or AWS account IDs.
        :param allowed_images_state: (experimental) The state for allowed images policy.
        :param block_public_snapshots: (experimental) Whether to block public sharing of EBS snapshots. Defaults to true.
        :param description: (experimental) The description of the policy.
        :param disable_serial_console_access: (experimental) Whether to disable serial console access. Defaults to true.
        :param http_endpoint: (experimental) The HttpEndpoint setting for instance metadata service.
        :param http_put_response_hop_limit: (experimental) The hop limit for HTTP PUT responses from the instance metadata service.
        :param http_tokens: (experimental) The HttpTokens setting for instance metadata service.
        :param image_block_public_access: (experimental) Whether to block public access to AMIs. Defaults to true.
        :param instance_metadata_defaults: (experimental) Whether to enforce instance metadata service defaults. Defaults to true.
        :param instance_metadata_tags: (experimental) The instance metadata tags setting.
        :param name: (experimental) The name of the policy.
        :param restrict_image_providers: (experimental) Whether to restrict allowed image providers. Defaults to true.
        :param snapshot_block_public_access_state: (experimental) The state for blocking public access to EBS snapshots.
        :param vpc_block_public_access: (experimental) Whether to block public access to VPCs. Defaults to true.
        :param vpc_block_public_access_mode: (experimental) The mode for blocking public access to VPCs.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c322ab6e297ddb8a95e53260366009f5dde082a2b9a13b4479f765e874b83c51)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DeclarativePolicyProps(
            target_ids=target_ids,
            allowed_image_providers=allowed_image_providers,
            allowed_images_state=allowed_images_state,
            block_public_snapshots=block_public_snapshots,
            description=description,
            disable_serial_console_access=disable_serial_console_access,
            http_endpoint=http_endpoint,
            http_put_response_hop_limit=http_put_response_hop_limit,
            http_tokens=http_tokens,
            image_block_public_access=image_block_public_access,
            instance_metadata_defaults=instance_metadata_defaults,
            instance_metadata_tags=instance_metadata_tags,
            name=name,
            restrict_image_providers=restrict_image_providers,
            snapshot_block_public_access_state=snapshot_block_public_access_state,
            vpc_block_public_access=vpc_block_public_access,
            vpc_block_public_access_mode=vpc_block_public_access_mode,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="declarativePolicyArn")
    def declarative_policy_arn(self) -> builtins.str:
        '''(experimental) The ARN of the created declarative policy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "declarativePolicyArn"))


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.DeclarativePolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "target_ids": "targetIds",
        "allowed_image_providers": "allowedImageProviders",
        "allowed_images_state": "allowedImagesState",
        "block_public_snapshots": "blockPublicSnapshots",
        "description": "description",
        "disable_serial_console_access": "disableSerialConsoleAccess",
        "http_endpoint": "httpEndpoint",
        "http_put_response_hop_limit": "httpPutResponseHopLimit",
        "http_tokens": "httpTokens",
        "image_block_public_access": "imageBlockPublicAccess",
        "instance_metadata_defaults": "instanceMetadataDefaults",
        "instance_metadata_tags": "instanceMetadataTags",
        "name": "name",
        "restrict_image_providers": "restrictImageProviders",
        "snapshot_block_public_access_state": "snapshotBlockPublicAccessState",
        "vpc_block_public_access": "vpcBlockPublicAccess",
        "vpc_block_public_access_mode": "vpcBlockPublicAccessMode",
    },
)
class DeclarativePolicyProps:
    def __init__(
        self,
        *,
        target_ids: typing.Sequence[builtins.str],
        allowed_image_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_images_state: typing.Optional[AllowedImagesState] = None,
        block_public_snapshots: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_serial_console_access: typing.Optional[builtins.bool] = None,
        http_endpoint: typing.Optional["HttpEndpoint"] = None,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional["HttpTokens"] = None,
        image_block_public_access: typing.Optional[builtins.bool] = None,
        instance_metadata_defaults: typing.Optional[builtins.bool] = None,
        instance_metadata_tags: typing.Optional["InstanceMetadataTags"] = None,
        name: typing.Optional[builtins.str] = None,
        restrict_image_providers: typing.Optional[builtins.bool] = None,
        snapshot_block_public_access_state: typing.Optional["SnapshotBlockPublicAccessState"] = None,
        vpc_block_public_access: typing.Optional[builtins.bool] = None,
        vpc_block_public_access_mode: typing.Optional["VpcBlockPublicAccessMode"] = None,
    ) -> None:
        '''(experimental) Properties for configuring a DeclarativePolicy.

        :param target_ids: (experimental) The target AWS account or organizational unit IDs to which the policy will be attached.
        :param allowed_image_providers: (experimental) The list of allowed image providers or AWS account IDs.
        :param allowed_images_state: (experimental) The state for allowed images policy.
        :param block_public_snapshots: (experimental) Whether to block public sharing of EBS snapshots. Defaults to true.
        :param description: (experimental) The description of the policy.
        :param disable_serial_console_access: (experimental) Whether to disable serial console access. Defaults to true.
        :param http_endpoint: (experimental) The HttpEndpoint setting for instance metadata service.
        :param http_put_response_hop_limit: (experimental) The hop limit for HTTP PUT responses from the instance metadata service.
        :param http_tokens: (experimental) The HttpTokens setting for instance metadata service.
        :param image_block_public_access: (experimental) Whether to block public access to AMIs. Defaults to true.
        :param instance_metadata_defaults: (experimental) Whether to enforce instance metadata service defaults. Defaults to true.
        :param instance_metadata_tags: (experimental) The instance metadata tags setting.
        :param name: (experimental) The name of the policy.
        :param restrict_image_providers: (experimental) Whether to restrict allowed image providers. Defaults to true.
        :param snapshot_block_public_access_state: (experimental) The state for blocking public access to EBS snapshots.
        :param vpc_block_public_access: (experimental) Whether to block public access to VPCs. Defaults to true.
        :param vpc_block_public_access_mode: (experimental) The mode for blocking public access to VPCs.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f770a9064b96fd38aefde8635ec547a192270fdeddea586f6edb1896b397d2f9)
            check_type(argname="argument target_ids", value=target_ids, expected_type=type_hints["target_ids"])
            check_type(argname="argument allowed_image_providers", value=allowed_image_providers, expected_type=type_hints["allowed_image_providers"])
            check_type(argname="argument allowed_images_state", value=allowed_images_state, expected_type=type_hints["allowed_images_state"])
            check_type(argname="argument block_public_snapshots", value=block_public_snapshots, expected_type=type_hints["block_public_snapshots"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_serial_console_access", value=disable_serial_console_access, expected_type=type_hints["disable_serial_console_access"])
            check_type(argname="argument http_endpoint", value=http_endpoint, expected_type=type_hints["http_endpoint"])
            check_type(argname="argument http_put_response_hop_limit", value=http_put_response_hop_limit, expected_type=type_hints["http_put_response_hop_limit"])
            check_type(argname="argument http_tokens", value=http_tokens, expected_type=type_hints["http_tokens"])
            check_type(argname="argument image_block_public_access", value=image_block_public_access, expected_type=type_hints["image_block_public_access"])
            check_type(argname="argument instance_metadata_defaults", value=instance_metadata_defaults, expected_type=type_hints["instance_metadata_defaults"])
            check_type(argname="argument instance_metadata_tags", value=instance_metadata_tags, expected_type=type_hints["instance_metadata_tags"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument restrict_image_providers", value=restrict_image_providers, expected_type=type_hints["restrict_image_providers"])
            check_type(argname="argument snapshot_block_public_access_state", value=snapshot_block_public_access_state, expected_type=type_hints["snapshot_block_public_access_state"])
            check_type(argname="argument vpc_block_public_access", value=vpc_block_public_access, expected_type=type_hints["vpc_block_public_access"])
            check_type(argname="argument vpc_block_public_access_mode", value=vpc_block_public_access_mode, expected_type=type_hints["vpc_block_public_access_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_ids": target_ids,
        }
        if allowed_image_providers is not None:
            self._values["allowed_image_providers"] = allowed_image_providers
        if allowed_images_state is not None:
            self._values["allowed_images_state"] = allowed_images_state
        if block_public_snapshots is not None:
            self._values["block_public_snapshots"] = block_public_snapshots
        if description is not None:
            self._values["description"] = description
        if disable_serial_console_access is not None:
            self._values["disable_serial_console_access"] = disable_serial_console_access
        if http_endpoint is not None:
            self._values["http_endpoint"] = http_endpoint
        if http_put_response_hop_limit is not None:
            self._values["http_put_response_hop_limit"] = http_put_response_hop_limit
        if http_tokens is not None:
            self._values["http_tokens"] = http_tokens
        if image_block_public_access is not None:
            self._values["image_block_public_access"] = image_block_public_access
        if instance_metadata_defaults is not None:
            self._values["instance_metadata_defaults"] = instance_metadata_defaults
        if instance_metadata_tags is not None:
            self._values["instance_metadata_tags"] = instance_metadata_tags
        if name is not None:
            self._values["name"] = name
        if restrict_image_providers is not None:
            self._values["restrict_image_providers"] = restrict_image_providers
        if snapshot_block_public_access_state is not None:
            self._values["snapshot_block_public_access_state"] = snapshot_block_public_access_state
        if vpc_block_public_access is not None:
            self._values["vpc_block_public_access"] = vpc_block_public_access
        if vpc_block_public_access_mode is not None:
            self._values["vpc_block_public_access_mode"] = vpc_block_public_access_mode

    @builtins.property
    def target_ids(self) -> typing.List[builtins.str]:
        '''(experimental) The target AWS account or organizational unit IDs to which the policy will be attached.

        :stability: experimental
        '''
        result = self._values.get("target_ids")
        assert result is not None, "Required property 'target_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def allowed_image_providers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of allowed image providers or AWS account IDs.

        :stability: experimental
        '''
        result = self._values.get("allowed_image_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_images_state(self) -> typing.Optional[AllowedImagesState]:
        '''(experimental) The state for allowed images policy.

        :stability: experimental
        '''
        result = self._values.get("allowed_images_state")
        return typing.cast(typing.Optional[AllowedImagesState], result)

    @builtins.property
    def block_public_snapshots(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to block public sharing of EBS snapshots.

        Defaults to true.

        :stability: experimental
        '''
        result = self._values.get("block_public_snapshots")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the policy.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_serial_console_access(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to disable serial console access.

        Defaults to true.

        :stability: experimental
        '''
        result = self._values.get("disable_serial_console_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def http_endpoint(self) -> typing.Optional["HttpEndpoint"]:
        '''(experimental) The HttpEndpoint setting for instance metadata service.

        :stability: experimental
        '''
        result = self._values.get("http_endpoint")
        return typing.cast(typing.Optional["HttpEndpoint"], result)

    @builtins.property
    def http_put_response_hop_limit(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The hop limit for HTTP PUT responses from the instance metadata service.

        :stability: experimental
        '''
        result = self._values.get("http_put_response_hop_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_tokens(self) -> typing.Optional["HttpTokens"]:
        '''(experimental) The HttpTokens setting for instance metadata service.

        :stability: experimental
        '''
        result = self._values.get("http_tokens")
        return typing.cast(typing.Optional["HttpTokens"], result)

    @builtins.property
    def image_block_public_access(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to block public access to AMIs.

        Defaults to true.

        :stability: experimental
        '''
        result = self._values.get("image_block_public_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_metadata_defaults(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enforce instance metadata service defaults.

        Defaults to true.

        :stability: experimental
        '''
        result = self._values.get("instance_metadata_defaults")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_metadata_tags(self) -> typing.Optional["InstanceMetadataTags"]:
        '''(experimental) The instance metadata tags setting.

        :stability: experimental
        '''
        result = self._values.get("instance_metadata_tags")
        return typing.cast(typing.Optional["InstanceMetadataTags"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the policy.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restrict_image_providers(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to restrict allowed image providers.

        Defaults to true.

        :stability: experimental
        '''
        result = self._values.get("restrict_image_providers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def snapshot_block_public_access_state(
        self,
    ) -> typing.Optional["SnapshotBlockPublicAccessState"]:
        '''(experimental) The state for blocking public access to EBS snapshots.

        :stability: experimental
        '''
        result = self._values.get("snapshot_block_public_access_state")
        return typing.cast(typing.Optional["SnapshotBlockPublicAccessState"], result)

    @builtins.property
    def vpc_block_public_access(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to block public access to VPCs.

        Defaults to true.

        :stability: experimental
        '''
        result = self._values.get("vpc_block_public_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_block_public_access_mode(
        self,
    ) -> typing.Optional["VpcBlockPublicAccessMode"]:
        '''(experimental) The mode for blocking public access to VPCs.

        :stability: experimental
        '''
        result = self._values.get("vpc_block_public_access_mode")
        return typing.cast(typing.Optional["VpcBlockPublicAccessMode"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeclarativePolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuardDutyConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.GuardDutyConstruct",
):
    '''(experimental) A CDK construct that sets up AWS GuardDuty with configurable data sources and features.

    Example::

       new GuardDutyConstruct(this, 'GuardDuty', {
         enableGuardDuty: true,
         kubernetesAuditLogs: true,
         malwareProtection: true,
         s3Logs: true,
       });

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enable_guard_duty: typing.Optional[builtins.bool] = None,
        kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
        malware_protection: typing.Optional[builtins.bool] = None,
        s3_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Creates a new GuardDutyConstruct.

        :param scope: The parent construct.
        :param id: The construct ID.
        :param enable_guard_duty: (experimental) Whether to enable GuardDuty. Default: true
        :param kubernetes_audit_logs: (experimental) Whether to enable Kubernetes audit logs as a GuardDuty data source. Default: true
        :param malware_protection: (experimental) Whether to enable malware protection (EC2 EBS volume scanning). Default: true
        :param s3_logs: (experimental) Whether to enable S3 logs as a GuardDuty data source. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46f7299fb161d609b36f03ba2aca6e091908d9fb14d778953bdc7011622702eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GuardDutyConstructProps(
            enable_guard_duty=enable_guard_duty,
            kubernetes_audit_logs=kubernetes_audit_logs,
            malware_protection=malware_protection,
            s3_logs=s3_logs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        '''(experimental) The ID of the created GuardDuty detector.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac61776a34cb8e70080be2b8c4962494e39c9264a1ce0012d03a34392a271a0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "detectorId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.GuardDutyConstructProps",
    jsii_struct_bases=[],
    name_mapping={
        "enable_guard_duty": "enableGuardDuty",
        "kubernetes_audit_logs": "kubernetesAuditLogs",
        "malware_protection": "malwareProtection",
        "s3_logs": "s3Logs",
    },
)
class GuardDutyConstructProps:
    def __init__(
        self,
        *,
        enable_guard_duty: typing.Optional[builtins.bool] = None,
        kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
        malware_protection: typing.Optional[builtins.bool] = None,
        s3_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for configuring {@link GuardDutyConstruct}.

        :param enable_guard_duty: (experimental) Whether to enable GuardDuty. Default: true
        :param kubernetes_audit_logs: (experimental) Whether to enable Kubernetes audit logs as a GuardDuty data source. Default: true
        :param malware_protection: (experimental) Whether to enable malware protection (EC2 EBS volume scanning). Default: true
        :param s3_logs: (experimental) Whether to enable S3 logs as a GuardDuty data source. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf89c1357f24b0c602b710cda32441bac689e805673c53a2cd9ceb645e155bc)
            check_type(argname="argument enable_guard_duty", value=enable_guard_duty, expected_type=type_hints["enable_guard_duty"])
            check_type(argname="argument kubernetes_audit_logs", value=kubernetes_audit_logs, expected_type=type_hints["kubernetes_audit_logs"])
            check_type(argname="argument malware_protection", value=malware_protection, expected_type=type_hints["malware_protection"])
            check_type(argname="argument s3_logs", value=s3_logs, expected_type=type_hints["s3_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enable_guard_duty is not None:
            self._values["enable_guard_duty"] = enable_guard_duty
        if kubernetes_audit_logs is not None:
            self._values["kubernetes_audit_logs"] = kubernetes_audit_logs
        if malware_protection is not None:
            self._values["malware_protection"] = malware_protection
        if s3_logs is not None:
            self._values["s3_logs"] = s3_logs

    @builtins.property
    def enable_guard_duty(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable GuardDuty.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enable_guard_duty")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def kubernetes_audit_logs(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable Kubernetes audit logs as a GuardDuty data source.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("kubernetes_audit_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def malware_protection(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable malware protection (EC2 EBS volume scanning).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("malware_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_logs(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable S3 logs as a GuardDuty data source.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("s3_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuardDutyConstructProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="advanced-cdk-constructs.HttpEndpoint")
class HttpEndpoint(enum.Enum):
    '''(experimental) Options for IMDSv2 HttpEndpoint.

    :stability: experimental
    '''

    NO_PREFERENCE = "NO_PREFERENCE"
    '''(experimental) No preference for HttpEndpoint.

    :stability: experimental
    '''
    ENABLED = "ENABLED"
    '''(experimental) Enable HttpEndpoint.

    :stability: experimental
    '''
    DISABLED = "DISABLED"
    '''(experimental) Disable HttpEndpoint.

    :stability: experimental
    '''


@jsii.enum(jsii_type="advanced-cdk-constructs.HttpTokens")
class HttpTokens(enum.Enum):
    '''(experimental) Options for IMDSv2 HttpTokens requirement.

    :stability: experimental
    '''

    NO_PREFERENCE = "NO_PREFERENCE"
    '''(experimental) No preference for HttpTokens.

    :stability: experimental
    '''
    REQUIRED = "REQUIRED"
    '''(experimental) Require HttpTokens.

    :stability: experimental
    '''
    OPTIONAL = "OPTIONAL"
    '''(experimental) HttpTokens are optional.

    :stability: experimental
    '''


@jsii.enum(jsii_type="advanced-cdk-constructs.ImageProvider")
class ImageProvider(enum.Enum):
    '''(experimental) Predefined image providers for allowed images policy.

    :stability: experimental
    '''

    AMAZON = "AMAZON"
    '''(experimental) Amazon-provided images.

    :stability: experimental
    '''
    AWS_MARKETPLACE = "AWS_MARKETPLACE"
    '''(experimental) AWS Marketplace images.

    :stability: experimental
    '''
    AWS_BACKUP_VAULT = "AWS_BACKUP_VAULT"
    '''(experimental) AWS Backup Vault images.

    :stability: experimental
    '''


@jsii.enum(jsii_type="advanced-cdk-constructs.InstanceMetadataTags")
class InstanceMetadataTags(enum.Enum):
    '''(experimental) Options for IMDSv2 Instance Metadata Tags.

    :stability: experimental
    '''

    NO_PREFERENCE = "NO_PREFERENCE"
    '''(experimental) No preference for instance metadata tags.

    :stability: experimental
    '''
    ENABLED = "ENABLED"
    '''(experimental) Enable instance metadata tags.

    :stability: experimental
    '''
    DISABLED = "DISABLED"
    '''(experimental) Disable instance metadata tags.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.OrganizationalUnit",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "description": "description"},
)
class OrganizationalUnit:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Represents an organizational unit within AWS Control Tower.

        Organizational units (OUs) are containers for AWS accounts that help organize
        and manage accounts based on business needs, security requirements, or other criteria.

        :param name: (experimental) The name of the organizational unit.
        :param description: (experimental) Optional description of the organizational unit's purpose.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ad73a6d1752a7abf10a918de714ed9d738c7e92c542540fd95498badfd1734a)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the organizational unit.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description of the organizational unit's purpose.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationalUnit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResourceControlPolicy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.ResourceControlPolicy",
):
    '''(experimental) A CDK construct that creates and attaches an AWS Organizations Resource Control Policy.

    This policy can enforce Confused Deputy Protection and Secure Transport requirements
    across specified AWS accounts, OUs, or roots.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enforce_confused_deputy_protection: builtins.bool,
        enforce_secure_transport: builtins.bool,
        source_org_id: builtins.str,
        target_ids: typing.Sequence[builtins.str],
        name: typing.Optional[builtins.str] = None,
        source_account: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Creates a new {@link ResourceControlPolicy}.

        :param scope: The parent construct.
        :param id: The construct ID.
        :param enforce_confused_deputy_protection: (experimental) Whether to enforce Confused Deputy Protection in the policy.
        :param enforce_secure_transport: (experimental) Whether to enforce Secure Transport in the policy.
        :param source_org_id: (experimental) The AWS Organization ID to enforce as the source organization in the policy.
        :param target_ids: (experimental) The list of target IDs (accounts, OUs, or roots) to which the policy will be attached.
        :param name: (experimental) The name of the resource control policy. If not provided, a default name will be generated. Default: - Automatically generated name based on construct ID.
        :param source_account: (experimental) Optional list of allowed source AWS account IDs. If provided, only these accounts are allowed as source accounts.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__902a49417987a8310171bb7ed475e50f9d10759e5373d419f1b30934c6b7a8fb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ResourceControlPolicyProps(
            enforce_confused_deputy_protection=enforce_confused_deputy_protection,
            enforce_secure_transport=enforce_secure_transport,
            source_org_id=source_org_id,
            target_ids=target_ids,
            name=name,
            source_account=source_account,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="resourceControlPolicyArn")
    def resource_control_policy_arn(self) -> builtins.str:
        '''(experimental) The ARN of the created Resource Control Policy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "resourceControlPolicyArn"))


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.ResourceControlPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "enforce_confused_deputy_protection": "enforceConfusedDeputyProtection",
        "enforce_secure_transport": "enforceSecureTransport",
        "source_org_id": "sourceOrgID",
        "target_ids": "targetIds",
        "name": "name",
        "source_account": "sourceAccount",
    },
)
class ResourceControlPolicyProps:
    def __init__(
        self,
        *,
        enforce_confused_deputy_protection: builtins.bool,
        enforce_secure_transport: builtins.bool,
        source_org_id: builtins.str,
        target_ids: typing.Sequence[builtins.str],
        name: typing.Optional[builtins.str] = None,
        source_account: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for configuring a {@link ResourceControlPolicy}.

        :param enforce_confused_deputy_protection: (experimental) Whether to enforce Confused Deputy Protection in the policy.
        :param enforce_secure_transport: (experimental) Whether to enforce Secure Transport in the policy.
        :param source_org_id: (experimental) The AWS Organization ID to enforce as the source organization in the policy.
        :param target_ids: (experimental) The list of target IDs (accounts, OUs, or roots) to which the policy will be attached.
        :param name: (experimental) The name of the resource control policy. If not provided, a default name will be generated. Default: - Automatically generated name based on construct ID.
        :param source_account: (experimental) Optional list of allowed source AWS account IDs. If provided, only these accounts are allowed as source accounts.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e6388ccce3ae650a4950a69f4d298e21c8e27b29fbedfc2938fb9b173d46a91)
            check_type(argname="argument enforce_confused_deputy_protection", value=enforce_confused_deputy_protection, expected_type=type_hints["enforce_confused_deputy_protection"])
            check_type(argname="argument enforce_secure_transport", value=enforce_secure_transport, expected_type=type_hints["enforce_secure_transport"])
            check_type(argname="argument source_org_id", value=source_org_id, expected_type=type_hints["source_org_id"])
            check_type(argname="argument target_ids", value=target_ids, expected_type=type_hints["target_ids"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_account", value=source_account, expected_type=type_hints["source_account"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enforce_confused_deputy_protection": enforce_confused_deputy_protection,
            "enforce_secure_transport": enforce_secure_transport,
            "source_org_id": source_org_id,
            "target_ids": target_ids,
        }
        if name is not None:
            self._values["name"] = name
        if source_account is not None:
            self._values["source_account"] = source_account

    @builtins.property
    def enforce_confused_deputy_protection(self) -> builtins.bool:
        '''(experimental) Whether to enforce Confused Deputy Protection in the policy.

        :stability: experimental
        '''
        result = self._values.get("enforce_confused_deputy_protection")
        assert result is not None, "Required property 'enforce_confused_deputy_protection' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enforce_secure_transport(self) -> builtins.bool:
        '''(experimental) Whether to enforce Secure Transport in the policy.

        :stability: experimental
        '''
        result = self._values.get("enforce_secure_transport")
        assert result is not None, "Required property 'enforce_secure_transport' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def source_org_id(self) -> builtins.str:
        '''(experimental) The AWS Organization ID to enforce as the source organization in the policy.

        :stability: experimental
        '''
        result = self._values.get("source_org_id")
        assert result is not None, "Required property 'source_org_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_ids(self) -> typing.List[builtins.str]:
        '''(experimental) The list of target IDs (accounts, OUs, or roots) to which the policy will be attached.

        :stability: experimental
        '''
        result = self._values.get("target_ids")
        assert result is not None, "Required property 'target_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the resource control policy.

        If not provided, a default name will be generated.

        :default: - Automatically generated name based on construct ID.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_account(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Optional list of allowed source AWS account IDs.

        If provided, only these accounts are allowed as source accounts.

        :stability: experimental
        '''
        result = self._values.get("source_account")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceControlPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceControlPolicy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.ServiceControlPolicy",
):
    '''(experimental) Defines an AWS Organizations Service Control Policy (SCP) and attaches it to the specified targets.

    Example::

       new ServiceControlPolicy(this, 'MySCP', {
         targetIds: ['ou-xxxx-xxxxxxxx', '123456789012'],
         name: 'DenyEC2',
         statements: [
           {
             Effect: 'Deny',
             Action: 'ec2:*',
             Resource: '*',
           },
         ],
         description: 'Denies all EC2 actions',
       });

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        statements: typing.Sequence[typing.Any],
        target_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new Service Control Policy and attaches it to the specified targets.

        :param scope: The parent construct.
        :param id: The construct ID.
        :param statements: (experimental) The policy statements to include in the Service Control Policy.
        :param target_ids: (experimental) The list of target IDs (accounts or organizational units) to which the policy will be attached.
        :param description: (experimental) The description of the Service Control Policy. Default: - 'Service Control Policy from Advanced CDK Constructs'
        :param name: (experimental) The name of the Service Control Policy. Default: - A name based on the construct ID will be used.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__760e82145d5353cb60ab018950f234e1d937b913c330c411d18025adab7e2647)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ServiceControlPolicyProps(
            statements=statements,
            target_ids=target_ids,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="serviceControlPolicyArn")
    def service_control_policy_arn(self) -> builtins.str:
        '''(experimental) The ARN of the created Service Control Policy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceControlPolicyArn"))


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.ServiceControlPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "statements": "statements",
        "target_ids": "targetIds",
        "description": "description",
        "name": "name",
    },
)
class ServiceControlPolicyProps:
    def __init__(
        self,
        *,
        statements: typing.Sequence[typing.Any],
        target_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for defining a Service Control Policy.

        :param statements: (experimental) The policy statements to include in the Service Control Policy.
        :param target_ids: (experimental) The list of target IDs (accounts or organizational units) to which the policy will be attached.
        :param description: (experimental) The description of the Service Control Policy. Default: - 'Service Control Policy from Advanced CDK Constructs'
        :param name: (experimental) The name of the Service Control Policy. Default: - A name based on the construct ID will be used.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29c5e6c5ce0fa8fb3cc7c9286f3d751662ef7059f2846959035acec36d90c297)
            check_type(argname="argument statements", value=statements, expected_type=type_hints["statements"])
            check_type(argname="argument target_ids", value=target_ids, expected_type=type_hints["target_ids"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "statements": statements,
            "target_ids": target_ids,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def statements(self) -> typing.List[typing.Any]:
        '''(experimental) The policy statements to include in the Service Control Policy.

        :stability: experimental
        '''
        result = self._values.get("statements")
        assert result is not None, "Required property 'statements' is missing"
        return typing.cast(typing.List[typing.Any], result)

    @builtins.property
    def target_ids(self) -> typing.List[builtins.str]:
        '''(experimental) The list of target IDs (accounts or organizational units) to which the policy will be attached.

        :stability: experimental
        '''
        result = self._values.get("target_ids")
        assert result is not None, "Required property 'target_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the Service Control Policy.

        :default: - 'Service Control Policy from Advanced CDK Constructs'

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Service Control Policy.

        :default: - A name based on the construct ID will be used.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceControlPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="advanced-cdk-constructs.SnapshotBlockPublicAccessState")
class SnapshotBlockPublicAccessState(enum.Enum):
    '''(experimental) State for blocking public access to EBS snapshots.

    :stability: experimental
    '''

    BLOCK_NEW_SHARING = "BLOCK_NEW_SHARING"
    '''(experimental) Block new sharing of snapshots.

    :stability: experimental
    '''
    BLOCK_ALL_SHARING = "BLOCK_ALL_SHARING"
    '''(experimental) Block all sharing of snapshots.

    :stability: experimental
    '''


@jsii.enum(jsii_type="advanced-cdk-constructs.VpcBlockPublicAccessMode")
class VpcBlockPublicAccessMode(enum.Enum):
    '''(experimental) Modes for blocking public access to VPCs.

    :stability: experimental
    '''

    OFF = "OFF"
    '''(experimental) No blocking of public access.

    :stability: experimental
    '''
    BLOCK_INGRESS = "BLOCK_INGRESS"
    '''(experimental) Block only ingress (incoming) public access.

    :stability: experimental
    '''
    BLOCK_BIDIRECTIONAL = "BLOCK_BIDIRECTIONAL"
    '''(experimental) Block both ingress and egress (bidirectional) public access.

    :stability: experimental
    '''


__all__ = [
    "AllowedImagesState",
    "AwsAccount",
    "AwsAccountProps",
    "ControlTowerLandingZone",
    "ControlTowerLandingZoneProps",
    "DeclarativePolicy",
    "DeclarativePolicyProps",
    "GuardDutyConstruct",
    "GuardDutyConstructProps",
    "HttpEndpoint",
    "HttpTokens",
    "ImageProvider",
    "InstanceMetadataTags",
    "OrganizationalUnit",
    "ResourceControlPolicy",
    "ResourceControlPolicyProps",
    "ServiceControlPolicy",
    "ServiceControlPolicyProps",
    "SnapshotBlockPublicAccessState",
    "VpcBlockPublicAccessMode",
]

publication.publish()

def _typecheckingstub__1b7dd93e1b3296247f5b7f9f0646e04e44fbfcb67d516c85ce5794f671e01bf0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    email: builtins.str,
    name: builtins.str,
    parent_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    role_name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d151eb0ca9b90ff0364c8a56220f77443733db47131b4befd9ba1449e459df8(
    *,
    email: builtins.str,
    name: builtins.str,
    parent_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    role_name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cb6f81d8d4c2d56fa3847a45be1021aeaa1c2c4c0ff4d34db68af4e54b9c42a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    control_tower_stack_name: builtins.str,
    access_logging_bucket_retention_days: typing.Optional[jsii.Number] = None,
    governed_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    log_archive_account_email: typing.Optional[builtins.str] = None,
    log_archive_account_id: typing.Optional[builtins.str] = None,
    log_archive_account_role_name: typing.Optional[builtins.str] = None,
    log_archive_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    logging_bucket_kms_key_arn: typing.Optional[builtins.str] = None,
    log_retention_days: typing.Optional[jsii.Number] = None,
    organization_structure: typing.Optional[typing.Mapping[builtins.str, typing.Union[OrganizationalUnit, typing.Dict[builtins.str, typing.Any]]]] = None,
    security_audit_account_email: typing.Optional[builtins.str] = None,
    security_audit_account_id: typing.Optional[builtins.str] = None,
    security_audit_account_role_name: typing.Optional[builtins.str] = None,
    security_audit_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b445764c129628d9a04d592edf095a403b52996d6fcdc429cd07e0beb546704b(
    *,
    control_tower_stack_name: builtins.str,
    access_logging_bucket_retention_days: typing.Optional[jsii.Number] = None,
    governed_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    log_archive_account_email: typing.Optional[builtins.str] = None,
    log_archive_account_id: typing.Optional[builtins.str] = None,
    log_archive_account_role_name: typing.Optional[builtins.str] = None,
    log_archive_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    logging_bucket_kms_key_arn: typing.Optional[builtins.str] = None,
    log_retention_days: typing.Optional[jsii.Number] = None,
    organization_structure: typing.Optional[typing.Mapping[builtins.str, typing.Union[OrganizationalUnit, typing.Dict[builtins.str, typing.Any]]]] = None,
    security_audit_account_email: typing.Optional[builtins.str] = None,
    security_audit_account_id: typing.Optional[builtins.str] = None,
    security_audit_account_role_name: typing.Optional[builtins.str] = None,
    security_audit_account_tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c322ab6e297ddb8a95e53260366009f5dde082a2b9a13b4479f765e874b83c51(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    target_ids: typing.Sequence[builtins.str],
    allowed_image_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_images_state: typing.Optional[AllowedImagesState] = None,
    block_public_snapshots: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    disable_serial_console_access: typing.Optional[builtins.bool] = None,
    http_endpoint: typing.Optional[HttpEndpoint] = None,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    http_tokens: typing.Optional[HttpTokens] = None,
    image_block_public_access: typing.Optional[builtins.bool] = None,
    instance_metadata_defaults: typing.Optional[builtins.bool] = None,
    instance_metadata_tags: typing.Optional[InstanceMetadataTags] = None,
    name: typing.Optional[builtins.str] = None,
    restrict_image_providers: typing.Optional[builtins.bool] = None,
    snapshot_block_public_access_state: typing.Optional[SnapshotBlockPublicAccessState] = None,
    vpc_block_public_access: typing.Optional[builtins.bool] = None,
    vpc_block_public_access_mode: typing.Optional[VpcBlockPublicAccessMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f770a9064b96fd38aefde8635ec547a192270fdeddea586f6edb1896b397d2f9(
    *,
    target_ids: typing.Sequence[builtins.str],
    allowed_image_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_images_state: typing.Optional[AllowedImagesState] = None,
    block_public_snapshots: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    disable_serial_console_access: typing.Optional[builtins.bool] = None,
    http_endpoint: typing.Optional[HttpEndpoint] = None,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    http_tokens: typing.Optional[HttpTokens] = None,
    image_block_public_access: typing.Optional[builtins.bool] = None,
    instance_metadata_defaults: typing.Optional[builtins.bool] = None,
    instance_metadata_tags: typing.Optional[InstanceMetadataTags] = None,
    name: typing.Optional[builtins.str] = None,
    restrict_image_providers: typing.Optional[builtins.bool] = None,
    snapshot_block_public_access_state: typing.Optional[SnapshotBlockPublicAccessState] = None,
    vpc_block_public_access: typing.Optional[builtins.bool] = None,
    vpc_block_public_access_mode: typing.Optional[VpcBlockPublicAccessMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46f7299fb161d609b36f03ba2aca6e091908d9fb14d778953bdc7011622702eb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enable_guard_duty: typing.Optional[builtins.bool] = None,
    kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
    malware_protection: typing.Optional[builtins.bool] = None,
    s3_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac61776a34cb8e70080be2b8c4962494e39c9264a1ce0012d03a34392a271a0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf89c1357f24b0c602b710cda32441bac689e805673c53a2cd9ceb645e155bc(
    *,
    enable_guard_duty: typing.Optional[builtins.bool] = None,
    kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
    malware_protection: typing.Optional[builtins.bool] = None,
    s3_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ad73a6d1752a7abf10a918de714ed9d738c7e92c542540fd95498badfd1734a(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__902a49417987a8310171bb7ed475e50f9d10759e5373d419f1b30934c6b7a8fb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enforce_confused_deputy_protection: builtins.bool,
    enforce_secure_transport: builtins.bool,
    source_org_id: builtins.str,
    target_ids: typing.Sequence[builtins.str],
    name: typing.Optional[builtins.str] = None,
    source_account: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e6388ccce3ae650a4950a69f4d298e21c8e27b29fbedfc2938fb9b173d46a91(
    *,
    enforce_confused_deputy_protection: builtins.bool,
    enforce_secure_transport: builtins.bool,
    source_org_id: builtins.str,
    target_ids: typing.Sequence[builtins.str],
    name: typing.Optional[builtins.str] = None,
    source_account: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__760e82145d5353cb60ab018950f234e1d937b913c330c411d18025adab7e2647(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    statements: typing.Sequence[typing.Any],
    target_ids: typing.Sequence[builtins.str],
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29c5e6c5ce0fa8fb3cc7c9286f3d751662ef7059f2846959035acec36d90c297(
    *,
    statements: typing.Sequence[typing.Any],
    target_ids: typing.Sequence[builtins.str],
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
