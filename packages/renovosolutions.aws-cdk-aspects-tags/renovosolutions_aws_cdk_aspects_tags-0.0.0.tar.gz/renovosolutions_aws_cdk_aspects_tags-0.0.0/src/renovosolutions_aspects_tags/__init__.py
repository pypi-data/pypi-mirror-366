r'''
# CDK Aspects Library - Tags

A library of [AWS CDK Aspects](https://docs.aws.amazon.com/cdk/v2/guide/aspects.html) for applying consistent tagging to AWS resources.

## Features

This library provides two main aspects for tagging AWS resources:

### ApplyTags

An aspect that applies a set of custom tags to all taggable resources in the given scope. This is useful for:

* Cost allocation and tracking
* Resource management and organization
* Compliance and governance requirements
* Environment identification

### ApplyKmsTags

An aspect that applies CloudFormation-specific tags to KMS keys, including:

* `cfn:stack-name` - The name of the CloudFormation stack
* `cfn:logical-id` - The logical ID of the KMS key resource

This is particularly useful because KMS keys are not automatically tagged by CloudFormation, making them difficult to track and manage in large deployments.

It's not possible to use the same tags that CloudFormation applies to other resources, because those names are reserved for CloudFormation's internal use. As a best approximation, it uses the similar tag names listed above.

## Examples

### TypeScript

```python
import { Aspects, App, Stack } from 'aws-cdk-lib';
import { aws_s3 as s3, aws_kms as kms } from 'aws-cdk-lib';
import { ApplyTags, ApplyKmsTags } from '@renovosolutions/cdk-aspects-library-tags';

const app = new App();
const stack = new Stack(app, 'MyStack');

// Create some resources
new s3.Bucket(stack, 'MyBucket');
new kms.Key(stack, 'MyKey');

// Apply custom tags to all taggable resources
const tags = {
  'Environment': 'Production',
  'Project': 'MyProject',
  'Owner': 'TeamName'
};
Aspects.of(stack).add(new ApplyTags(tags));

// Apply CloudFormation tags specifically to KMS keys
Aspects.of(stack).add(new ApplyKmsTags());
```

### Python

```python
from aws_cdk import (
  Aspects,
  App,
  Stack,
  aws_s3 as s3,
  aws_kms as kms,
)
from renovosolutions_aspects_tags import (
  ApplyTags,
  ApplyKmsTags,
)

app = App()
stack = Stack(app, "MyStack")

# Create some resources
s3.Bucket(stack, "MyBucket")
kms.Key(stack, "MyKey")

# Apply custom tags to all taggable resources
tags = {
    "Environment": "Production",
    "Project": "MyProject",
    "Owner": "TeamName"
}
Aspects.of(stack).add(ApplyTags(tags))

# Apply CloudFormation tags specifically to KMS keys
Aspects.of(stack).add(ApplyKmsTags())
```

### C Sharp

```csharp
using Amazon.CDK;
using Amazon.CDK.AWS.S3;
using Amazon.CDK.AWS.KMS;
using System.Collections.Generic;
using renovosolutions;

var app = new App();
var stack = new Stack(app, "MyStack");

// Create some resources
new Bucket(stack, "MyBucket");
new Key(stack, "MyKey");

// Apply custom tags to all taggable resources
var tags = new Dictionary<string, string>
{
    ["Environment"] = "Production",
    ["Project"] = "MyProject",
    ["Owner"] = "TeamName"
};
Aspects.Of(stack).Add(new ApplyTags(tags));

// Apply CloudFormation tags specifically to KMS keys
Aspects.Of(stack).Add(new ApplyKmsTags());
```

## Scope of Application

The aspects in this library work at different scopes:

* **ApplyTags**: Applies to all resources that implement the `ITaggable` interface (most AWS resources)
* **ApplyKmsTags**: Applies specifically to `AWS::KMS::Key` resources

You can apply these aspects at any level in your CDK hierarchy:

* **App level**: Tags all resources across all stacks
* **Stack level**: Tags all resources within a specific stack
* **Construct level**: Tags resources within a specific construct

## API Reference

For detailed API documentation, see [API.md](./API.md).

## Contributing

Contributions are welcome! Please see our [contributing guidelines](https://github.com/RenovoSolutions/cdk-aspects-library-tags/blob/main/CONTRIBUTING.md) for more details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
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


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class ApplyKmsTags(
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-tags.ApplyKmsTags",
):
    '''An aspect that applies CloudFormation tags to all KMS keys in the given scope.

    This is useful because KMS keys are not automatically tagged by CloudFormation,
    which makes them hard to track and manage.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''Visits each construct in the scope and applies the tags if the construct is a KMS key.

        :param node: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__275c380e3d99fa139f05c53361df13d2179a3d4c9dee529fc3a5e1824e87580a)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class ApplyTags(
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-tags.ApplyTags",
):
    '''An aspect that applies a set of tags to all taggable resources in the given scope.

    This aspect can be used to enforce consistent tagging across resources,
    which is useful for cost allocation, resource management, and compliance purposes.
    '''

    def __init__(self, tags: typing.Mapping[builtins.str, builtins.str]) -> None:
        '''Creates an instance of the ApplyTags aspect.

        :param tags: - a record of key-value pairs to apply as tags to taggable resources in the CDK app.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f41e675e56b38054a3fb8a2ba58bc735df0a1ac922844a0259f8398a3eb4ba1a)
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        jsii.create(self.__class__, self, [tags])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''Visits each construct in the scope and applies the tags if the construct is taggable.

        :param node: - the construct to visit.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acf26c08009305034f9a0aafbb05e7998e375ba748de9c4ce0c4d6c965c209e1)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''A record of key-value pairs to apply as tags to taggable resources in the CDK app.'''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fef6736c3eb0e9fcc6a55339d0f19b8be11b7f836ab8261c807b86c1e70ce148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ApplyKmsTags",
    "ApplyTags",
]

publication.publish()

def _typecheckingstub__275c380e3d99fa139f05c53361df13d2179a3d4c9dee529fc3a5e1824e87580a(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f41e675e56b38054a3fb8a2ba58bc735df0a1ac922844a0259f8398a3eb4ba1a(
    tags: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acf26c08009305034f9a0aafbb05e7998e375ba748de9c4ce0c4d6c965c209e1(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fef6736c3eb0e9fcc6a55339d0f19b8be11b7f836ab8261c807b86c1e70ce148(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass
