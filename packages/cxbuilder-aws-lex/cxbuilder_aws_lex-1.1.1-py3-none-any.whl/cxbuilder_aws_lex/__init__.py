r'''
# @cxbuilder/aws-lex

[![CI/CD Pipeline](https://github.com/cxbuilder/aws-lex/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/cxbuilder/aws-lex/actions/workflows/ci-cd.yml)
[![npm version](https://badge.fury.io/js/@cxbuilder%2Faws-lex.svg)](https://badge.fury.io/js/@cxbuilder%2Faws-lex)
[![PyPI version](https://badge.fury.io/py/cxbuilder-aws-lex.svg)](https://badge.fury.io/py/cxbuilder-aws-lex)
[![View on Construct Hub](https://constructs.dev/badge?package=%40cxbuilder%2Faws-lex)](https://constructs.dev/packages/@cxbuilder/aws-lex)

## Overview

The `@cxbuilder/aws-lex` package provides higher-level (L2) constructs for AWS LexV2 bot creation using the AWS CDK. It significantly simplifies the process of building conversational interfaces with Amazon Lex by abstracting away the complexity of the AWS LexV2 L1 constructs.

## Why Use This Library?

AWS LexV2 L1 constructs are notoriously difficult to understand and use correctly. They require deep knowledge of the underlying CloudFormation resources and complex property structures. This library addresses these challenges by:

* **Simplifying the API**: Providing an intuitive, object-oriented interface for defining bots, intents, slots, and locales
* **Automating best practices**: Handling versioning and alias management automatically
* **Reducing boilerplate**: Eliminating repetitive code for common bot configurations
* **Improving maintainability**: Using classes with encapsulated transformation logic instead of complex nested objects

## Key Features

* **Automatic versioning**: Creates a bot version and associates it with the `live` alias when input changes
* **Simplified intent creation**: Define intents with utterances and slots using a clean, declarative syntax
* **Multi-locale support**: Easily create bots that support multiple languages
* **Lambda integration**: Streamlined setup for dialog and fulfillment Lambda hooks
* **Extensible design**: For complex use cases, you can always drop down to L1 constructs or fork the repository

## Installation

### Node.js

```bash
npm install @cxbuilder/aws-lex
```

### Python

```bash
pip install cxbuilder-aws-lex
```

## Quick Start

Create a simple yes/no bot with multi-language support:

### TypeScript

```python
import { App, Stack } from 'aws-cdk-lib';
import { Bot, Intent, Locale } from '@cxbuilder/aws-lex';

const app = new App();
const stack = new Stack(app, 'MyLexStack');

new Bot(stack, 'YesNoBot', {
  name: 'my-yes-no-bot',
  locales: [
    new Locale({
      localeId: 'en_US',
      voiceId: 'Joanna',
      intents: [
        new Intent({
          name: 'Yes',
          utterances: ['yes', 'yeah', 'yep', 'absolutely', 'of course'],
        }),
        new Intent({
          name: 'No',
          utterances: ['no', 'nope', 'never', 'absolutely not', 'no way'],
        }),
      ],
    }),
    new Locale({
      localeId: 'es_US',
      voiceId: 'Lupe',
      intents: [
        new Intent({
          name: 'Yes',
          utterances: ['sí', 'claro', 'por supuesto', 'correcto', 'exacto'],
        }),
        new Intent({
          name: 'No',
          utterances: ['no', 'para nada', 'negativo', 'jamás', 'en absoluto'],
        }),
      ],
    }),
  ],
});
```

## Advanced Example: Bot with Slots and Lambda Integration

```python
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Bot, Intent, Locale, Slot } from '@cxbuilder/aws-lex';

const fulfillmentLambda = new NodejsFunction(stack, 'Handler', {
  entry: './src/bot-handler.ts',
});

new Bot(stack, 'BookingBot', {
  name: 'hotel-booking-bot',
  locales: [
    new Locale({
      localeId: 'en_US',
      voiceId: 'Joanna',
      codeHook: {
        fn: fulfillmentLambda,
        fulfillment: true,
      },
      intents: [
        new Intent({
          name: 'BookHotel',
          utterances: [
            'I want to book a room',
            'Book a hotel for {checkInDate}',
            'I need a room in {city}',
          ],
          slots: [
            new Slot({
              name: 'city',
              slotTypeName: 'AMAZON.City',
              elicitationMessages: ['Which city would you like to visit?'],
              required: true,
            }),
            new Slot({
              name: 'checkInDate',
              slotTypeName: 'AMAZON.Date',
              elicitationMessages: ['What date would you like to check in?'],
              required: true,
            }),
          ],
        }),
      ],
    }),
  ],
});
```

## Architecture

The library uses a class-based approach with the following main components:

* **Bot**: The main construct that creates the Lex bot resource
* **Locale**: Configures language-specific settings and resources
* **Intent**: Defines conversational intents with utterances and slots
* **Slot**: Defines input parameters for intents
* **SlotType**: Defines custom slot types with enumeration values

## Advanced Usage

While this library simplifies common use cases, you can still leverage the full power of AWS LexV2 for complex scenarios:

* **Rich responses**: For bots that use cards and complex response types
* **Custom dialog management**: For sophisticated conversation flows
* **Advanced slot validation**: For complex input validation requirements

In these cases, you can either extend the library classes or drop down to the L1 constructs as needed.

## License

MIT
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

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_lex as _aws_cdk_aws_lex_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class Bot(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cxbuilder/aws-lex.Bot",
):
    '''Defines a simplified interface for creating an Amazon Lex Bot.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        locales: typing.Sequence["Locale"],
        name: builtins.str,
        audio_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        description: typing.Optional[builtins.str] = None,
        idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
        replica_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param locales: 
        :param name: Bot name.
        :param audio_bucket: If provided, bot will record audio.
        :param description: Bot description.
        :param idle_session_ttl_in_seconds: Default: 300
        :param log_group: If provided, bot will send lex logs.
        :param nlu_confidence_threshold: Default: 0.4
        :param replica_regions: 
        :param role: Allows you to create a role externally. Use this if all your bots use the same permissions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b66b7aa3df3511d03e4ecb5245512928461adf3646bc373ac69add43fad8786)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BotProps(
            locales=locales,
            name=name,
            audio_bucket=audio_bucket,
            description=description,
            idle_session_ttl_in_seconds=idle_session_ttl_in_seconds,
            log_group=log_group,
            nlu_confidence_threshold=nlu_confidence_threshold,
            replica_regions=replica_regions,
            role=role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="conversationLogSettings")
    def conversation_log_settings(
        self,
        alias_name: builtins.str,
    ) -> typing.Optional[_aws_cdk_aws_lex_ceddda9d.CfnBotAlias.ConversationLogSettingsProperty]:
        '''
        :param alias_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eb46d0eb5aab6caec43e68297a9bb2c3784a63d5777ca280caf770eaa5b4462)
            check_type(argname="argument alias_name", value=alias_name, expected_type=type_hints["alias_name"])
        return typing.cast(typing.Optional[_aws_cdk_aws_lex_ceddda9d.CfnBotAlias.ConversationLogSettingsProperty], jsii.invoke(self, "conversationLogSettings", [alias_name]))

    @builtins.property
    @jsii.member(jsii_name="cfnBot")
    def cfn_bot(self) -> _aws_cdk_aws_lex_ceddda9d.CfnBot:
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBot, jsii.get(self, "cfnBot"))

    @builtins.property
    @jsii.member(jsii_name="cfnBotAlias")
    def cfn_bot_alias(self) -> _aws_cdk_aws_lex_ceddda9d.CfnBotAlias:
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBotAlias, jsii.get(self, "cfnBotAlias"))

    @builtins.property
    @jsii.member(jsii_name="cfnBotVersion")
    def cfn_bot_version(self) -> _aws_cdk_aws_lex_ceddda9d.CfnBotVersion:
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBotVersion, jsii.get(self, "cfnBotVersion"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.BotProps",
    jsii_struct_bases=[],
    name_mapping={
        "locales": "locales",
        "name": "name",
        "audio_bucket": "audioBucket",
        "description": "description",
        "idle_session_ttl_in_seconds": "idleSessionTtlInSeconds",
        "log_group": "logGroup",
        "nlu_confidence_threshold": "nluConfidenceThreshold",
        "replica_regions": "replicaRegions",
        "role": "role",
    },
)
class BotProps:
    def __init__(
        self,
        *,
        locales: typing.Sequence["Locale"],
        name: builtins.str,
        audio_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        description: typing.Optional[builtins.str] = None,
        idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
        replica_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param locales: 
        :param name: Bot name.
        :param audio_bucket: If provided, bot will record audio.
        :param description: Bot description.
        :param idle_session_ttl_in_seconds: Default: 300
        :param log_group: If provided, bot will send lex logs.
        :param nlu_confidence_threshold: Default: 0.4
        :param replica_regions: 
        :param role: Allows you to create a role externally. Use this if all your bots use the same permissions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__939189742fb16d1bb58391e5f36bacc14ec9852222433072a4f83673d3873d17)
            check_type(argname="argument locales", value=locales, expected_type=type_hints["locales"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument audio_bucket", value=audio_bucket, expected_type=type_hints["audio_bucket"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument idle_session_ttl_in_seconds", value=idle_session_ttl_in_seconds, expected_type=type_hints["idle_session_ttl_in_seconds"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument nlu_confidence_threshold", value=nlu_confidence_threshold, expected_type=type_hints["nlu_confidence_threshold"])
            check_type(argname="argument replica_regions", value=replica_regions, expected_type=type_hints["replica_regions"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "locales": locales,
            "name": name,
        }
        if audio_bucket is not None:
            self._values["audio_bucket"] = audio_bucket
        if description is not None:
            self._values["description"] = description
        if idle_session_ttl_in_seconds is not None:
            self._values["idle_session_ttl_in_seconds"] = idle_session_ttl_in_seconds
        if log_group is not None:
            self._values["log_group"] = log_group
        if nlu_confidence_threshold is not None:
            self._values["nlu_confidence_threshold"] = nlu_confidence_threshold
        if replica_regions is not None:
            self._values["replica_regions"] = replica_regions
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def locales(self) -> typing.List["Locale"]:
        result = self._values.get("locales")
        assert result is not None, "Required property 'locales' is missing"
        return typing.cast(typing.List["Locale"], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Bot name.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audio_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''If provided, bot will record audio.'''
        result = self._values.get("audio_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Bot description.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idle_session_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 300
        '''
        result = self._values.get("idle_session_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''If provided, bot will send lex logs.'''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def nlu_confidence_threshold(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 0.4
        '''
        result = self._values.get("nlu_confidence_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replica_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("replica_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Allows you to create a role externally.

        Use this if all your bots use the same permissions
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Intent(metaclass=jsii.JSIIMeta, jsii_type="@cxbuilder/aws-lex.Intent"):
    def __init__(
        self,
        *,
        name: builtins.str,
        utterances: typing.Sequence[builtins.str],
        confirmation_failure_prompt: typing.Optional[builtins.str] = None,
        confirmation_prompt: typing.Optional[builtins.str] = None,
        fulfillment_failure_prompt: typing.Optional[builtins.str] = None,
        fulfillment_prompt: typing.Optional[builtins.str] = None,
        slots: typing.Optional[typing.Sequence["Slot"]] = None,
    ) -> None:
        '''
        :param name: 
        :param utterances: 
        :param confirmation_failure_prompt: 
        :param confirmation_prompt: 
        :param fulfillment_failure_prompt: 
        :param fulfillment_prompt: 
        :param slots: 
        '''
        props = IntentProps(
            name=name,
            utterances=utterances,
            confirmation_failure_prompt=confirmation_failure_prompt,
            confirmation_prompt=confirmation_prompt,
            fulfillment_failure_prompt=fulfillment_failure_prompt,
            fulfillment_prompt=fulfillment_prompt,
            slots=slots,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toCdk")
    def to_cdk(
        self,
        dialog_code_hook: builtins.bool,
        fulfillment_code_hook: builtins.bool,
    ) -> _aws_cdk_aws_lex_ceddda9d.CfnBot.IntentProperty:
        '''
        :param dialog_code_hook: -
        :param fulfillment_code_hook: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bcd0a568f6b8bc4d8c416357cfa51eb6f8d1d9a641b03cdd0109df437e31735)
            check_type(argname="argument dialog_code_hook", value=dialog_code_hook, expected_type=type_hints["dialog_code_hook"])
            check_type(argname="argument fulfillment_code_hook", value=fulfillment_code_hook, expected_type=type_hints["fulfillment_code_hook"])
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBot.IntentProperty, jsii.invoke(self, "toCdk", [dialog_code_hook, fulfillment_code_hook]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73cf94b90f74dd79ff237e474f47ccf073c1a0c1769c1bf8ffc57611e0494d9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="utterances")
    def utterances(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "utterances"))

    @utterances.setter
    def utterances(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6a18eb1a04c23378fcf29add9b897f7edc8eabdb2e8ba6804be274d4051eb68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utterances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confirmationDeclinedPrompt")
    def confirmation_declined_prompt(self) -> typing.Optional[builtins.str]:
        '''If provided, lex will speak this when confirmation is declined.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confirmationDeclinedPrompt"))

    @confirmation_declined_prompt.setter
    def confirmation_declined_prompt(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76554220bf1b2ba17174528b01493cd9d84337e43d2f621f7071c8f5d801db74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confirmationDeclinedPrompt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confirmationPrompt")
    def confirmation_prompt(self) -> typing.Optional[builtins.str]:
        '''If provided, lex will confirm the intent.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confirmationPrompt"))

    @confirmation_prompt.setter
    def confirmation_prompt(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf6337be4d210afd62b619f0aa30cc23c58df2a44a616e1c1a1408add9547649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confirmationPrompt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fulfillmentFailurePrompt")
    def fulfillment_failure_prompt(self) -> typing.Optional[builtins.str]:
        '''If provided, lex will speak this when the intent fulfillment fails.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fulfillmentFailurePrompt"))

    @fulfillment_failure_prompt.setter
    def fulfillment_failure_prompt(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f00c03d711854d1087a305d1c7cd8a456ebe74ddce78b68e2e7753ec9d9b56f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fulfillmentFailurePrompt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fulfillmentPrompt")
    def fulfillment_prompt(self) -> typing.Optional[builtins.str]:
        '''If provided, lex will speak this when the intent is fullfilled.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fulfillmentPrompt"))

    @fulfillment_prompt.setter
    def fulfillment_prompt(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f18e8d7d573b1cc97bb981511c178096f3c90432095f9ffe79546eaf92cc671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fulfillmentPrompt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slots")
    def slots(self) -> typing.Optional[typing.List["Slot"]]:
        '''Slots in priority order.'''
        return typing.cast(typing.Optional[typing.List["Slot"]], jsii.get(self, "slots"))

    @slots.setter
    def slots(self, value: typing.Optional[typing.List["Slot"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__380d6014ea80ab2b039337e5559c86efcd28f2eb836d16dc2ef55a060b64da8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slots", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.IntentProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "utterances": "utterances",
        "confirmation_failure_prompt": "confirmationFailurePrompt",
        "confirmation_prompt": "confirmationPrompt",
        "fulfillment_failure_prompt": "fulfillmentFailurePrompt",
        "fulfillment_prompt": "fulfillmentPrompt",
        "slots": "slots",
    },
)
class IntentProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        utterances: typing.Sequence[builtins.str],
        confirmation_failure_prompt: typing.Optional[builtins.str] = None,
        confirmation_prompt: typing.Optional[builtins.str] = None,
        fulfillment_failure_prompt: typing.Optional[builtins.str] = None,
        fulfillment_prompt: typing.Optional[builtins.str] = None,
        slots: typing.Optional[typing.Sequence["Slot"]] = None,
    ) -> None:
        '''
        :param name: 
        :param utterances: 
        :param confirmation_failure_prompt: 
        :param confirmation_prompt: 
        :param fulfillment_failure_prompt: 
        :param fulfillment_prompt: 
        :param slots: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64854e6efff0b4de5c2cf7bd3aa17a62e6ab3665b43b707caf51a6804cae93a3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument utterances", value=utterances, expected_type=type_hints["utterances"])
            check_type(argname="argument confirmation_failure_prompt", value=confirmation_failure_prompt, expected_type=type_hints["confirmation_failure_prompt"])
            check_type(argname="argument confirmation_prompt", value=confirmation_prompt, expected_type=type_hints["confirmation_prompt"])
            check_type(argname="argument fulfillment_failure_prompt", value=fulfillment_failure_prompt, expected_type=type_hints["fulfillment_failure_prompt"])
            check_type(argname="argument fulfillment_prompt", value=fulfillment_prompt, expected_type=type_hints["fulfillment_prompt"])
            check_type(argname="argument slots", value=slots, expected_type=type_hints["slots"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "utterances": utterances,
        }
        if confirmation_failure_prompt is not None:
            self._values["confirmation_failure_prompt"] = confirmation_failure_prompt
        if confirmation_prompt is not None:
            self._values["confirmation_prompt"] = confirmation_prompt
        if fulfillment_failure_prompt is not None:
            self._values["fulfillment_failure_prompt"] = fulfillment_failure_prompt
        if fulfillment_prompt is not None:
            self._values["fulfillment_prompt"] = fulfillment_prompt
        if slots is not None:
            self._values["slots"] = slots

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def utterances(self) -> typing.List[builtins.str]:
        result = self._values.get("utterances")
        assert result is not None, "Required property 'utterances' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def confirmation_failure_prompt(self) -> typing.Optional[builtins.str]:
        result = self._values.get("confirmation_failure_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def confirmation_prompt(self) -> typing.Optional[builtins.str]:
        result = self._values.get("confirmation_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fulfillment_failure_prompt(self) -> typing.Optional[builtins.str]:
        result = self._values.get("fulfillment_failure_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fulfillment_prompt(self) -> typing.Optional[builtins.str]:
        result = self._values.get("fulfillment_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def slots(self) -> typing.Optional[typing.List["Slot"]]:
        result = self._values.get("slots")
        return typing.cast(typing.Optional[typing.List["Slot"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IntentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexRole(
    _aws_cdk_aws_iam_ceddda9d.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cxbuilder/aws-lex.LexRole",
):
    '''Standard lex role configuration.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        lex_log_group_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lex_log_group_name: Limits permission to write to a single log group.
        :param role_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e0cc8abcaee00884442792c97ff10a6e07b056c02158c3451fbf064aa72b740)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LexRoleProps(
            lex_log_group_name=lex_log_group_name, role_name=role_name
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.LexRoleProps",
    jsii_struct_bases=[],
    name_mapping={"lex_log_group_name": "lexLogGroupName", "role_name": "roleName"},
)
class LexRoleProps:
    def __init__(
        self,
        *,
        lex_log_group_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param lex_log_group_name: Limits permission to write to a single log group.
        :param role_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1679559836a043b576bd52e350f92fc71fe12dec0b52396d92bf696cf6985888)
            check_type(argname="argument lex_log_group_name", value=lex_log_group_name, expected_type=type_hints["lex_log_group_name"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if lex_log_group_name is not None:
            self._values["lex_log_group_name"] = lex_log_group_name
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def lex_log_group_name(self) -> typing.Optional[builtins.str]:
        '''Limits permission to write to a single log group.'''
        result = self._values.get("lex_log_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Locale(metaclass=jsii.JSIIMeta, jsii_type="@cxbuilder/aws-lex.Locale"):
    def __init__(
        self,
        *,
        locale_id: builtins.str,
        voice_id: builtins.str,
        code_hook: typing.Optional[typing.Union["LocaleCodeHook", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        intents: typing.Optional[typing.Sequence[Intent]] = None,
        nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
        slot_types: typing.Optional[typing.Sequence["SlotType"]] = None,
    ) -> None:
        '''
        :param locale_id: 
        :param voice_id: 
        :param code_hook: 
        :param description: 
        :param engine: 
        :param intents: 
        :param nlu_confidence_threshold: 
        :param slot_types: 
        '''
        props = LocaleProps(
            locale_id=locale_id,
            voice_id=voice_id,
            code_hook=code_hook,
            description=description,
            engine=engine,
            intents=intents,
            nlu_confidence_threshold=nlu_confidence_threshold,
            slot_types=slot_types,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addPermission")
    def add_permission(
        self,
        scope: _constructs_77d1e7e8.Construct,
        bot_id: builtins.str,
    ) -> None:
        '''Allows all bot aliases to invoke the code hook lambda.

        :param scope: -
        :param bot_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc2b68f597684a49df6926de4c8ea80bead4d305ef999b28f386df7f4f8f914b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument bot_id", value=bot_id, expected_type=type_hints["bot_id"])
        return typing.cast(None, jsii.invoke(self, "addPermission", [scope, bot_id]))

    @jsii.member(jsii_name="toCdk")
    def to_cdk(
        self,
        bot_nlu_confidence_threshold: jsii.Number,
    ) -> _aws_cdk_aws_lex_ceddda9d.CfnBot.BotLocaleProperty:
        '''
        :param bot_nlu_confidence_threshold: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__561f5fe43edfde7cf7d4294cd30258789aa4d74e68317c1545e088643999b57b)
            check_type(argname="argument bot_nlu_confidence_threshold", value=bot_nlu_confidence_threshold, expected_type=type_hints["bot_nlu_confidence_threshold"])
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBot.BotLocaleProperty, jsii.invoke(self, "toCdk", [bot_nlu_confidence_threshold]))

    @builtins.property
    @jsii.member(jsii_name="localeId")
    def locale_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localeId"))

    @locale_id.setter
    def locale_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29c20e16645ac3ac6f7cbbde8f06709388ce36ab861b559d72f8cad3000becb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="voiceId")
    def voice_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "voiceId"))

    @voice_id.setter
    def voice_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__592d701f4912a266c2a7df9905c500b7129f0ee010353213ba6d92eb05459fc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "voiceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="codeHook")
    def code_hook(self) -> typing.Optional["LocaleCodeHook"]:
        '''Optional dialog and fulfillment hooks.'''
        return typing.cast(typing.Optional["LocaleCodeHook"], jsii.get(self, "codeHook"))

    @code_hook.setter
    def code_hook(self, value: typing.Optional["LocaleCodeHook"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a6aa2b999f90a6df971c09d5064139c5ad49ecc6e310921ecd37d5d105d0de7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "codeHook", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d32971dd3020db7c868bdaf41ce5c84dbec22b9c94de0f1c739cf9b565de6d28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="engine")
    def engine(self) -> typing.Optional[builtins.str]:
        '''
        :default: LexDefaults.engine
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cea14d93c26e0e452be95b0194bdb3ca9629131645b5609acb6c9804615a5855)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "engine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intents")
    def intents(self) -> typing.Optional[typing.List[Intent]]:
        '''Defines an intent and its associated utterances.'''
        return typing.cast(typing.Optional[typing.List[Intent]], jsii.get(self, "intents"))

    @intents.setter
    def intents(self, value: typing.Optional[typing.List[Intent]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c4e750755a4d983f75260e83741bb3dc57d199c5b26f2099a6736daeb1a3d37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nluConfidenceThreshold")
    def nlu_confidence_threshold(self) -> typing.Optional[jsii.Number]:
        '''If not provided, will default to bot default value.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nluConfidenceThreshold"))

    @nlu_confidence_threshold.setter
    def nlu_confidence_threshold(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa06977e88d791a2f236817e61af6f93f1a8238a0ba4ac3387266d3e80610574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nluConfidenceThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slotTypes")
    def slot_types(self) -> typing.Optional[typing.List["SlotType"]]:
        '''Any non-standard slot types required.'''
        return typing.cast(typing.Optional[typing.List["SlotType"]], jsii.get(self, "slotTypes"))

    @slot_types.setter
    def slot_types(self, value: typing.Optional[typing.List["SlotType"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6f7cb1e95d56064b66922fbc5a3aedf6acde865555c9c28c58e558197129061)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slotTypes", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.LocaleCodeHook",
    jsii_struct_bases=[],
    name_mapping={"fn": "fn", "dialog": "dialog", "fulfillment": "fulfillment"},
)
class LocaleCodeHook:
    def __init__(
        self,
        *,
        fn: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        dialog: typing.Optional[builtins.bool] = None,
        fulfillment: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param fn: The lambda function that will be invoked.
        :param dialog: Whether to invoke the lambda for each dialog turn.
        :param fulfillment: Whether to invoke the lambda for each intent fulfillment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a35bd79dda028f06b08ef09dcedeaf0cf0a69e8e7d7a4bc09c70355cdebf839)
            check_type(argname="argument fn", value=fn, expected_type=type_hints["fn"])
            check_type(argname="argument dialog", value=dialog, expected_type=type_hints["dialog"])
            check_type(argname="argument fulfillment", value=fulfillment, expected_type=type_hints["fulfillment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fn": fn,
        }
        if dialog is not None:
            self._values["dialog"] = dialog
        if fulfillment is not None:
            self._values["fulfillment"] = fulfillment

    @builtins.property
    def fn(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The lambda function that will be invoked.'''
        result = self._values.get("fn")
        assert result is not None, "Required property 'fn' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def dialog(self) -> typing.Optional[builtins.bool]:
        '''Whether to invoke the lambda for each dialog turn.'''
        result = self._values.get("dialog")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def fulfillment(self) -> typing.Optional[builtins.bool]:
        '''Whether to invoke the lambda for each intent fulfillment.'''
        result = self._values.get("fulfillment")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LocaleCodeHook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.LocaleProps",
    jsii_struct_bases=[],
    name_mapping={
        "locale_id": "localeId",
        "voice_id": "voiceId",
        "code_hook": "codeHook",
        "description": "description",
        "engine": "engine",
        "intents": "intents",
        "nlu_confidence_threshold": "nluConfidenceThreshold",
        "slot_types": "slotTypes",
    },
)
class LocaleProps:
    def __init__(
        self,
        *,
        locale_id: builtins.str,
        voice_id: builtins.str,
        code_hook: typing.Optional[typing.Union[LocaleCodeHook, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        intents: typing.Optional[typing.Sequence[Intent]] = None,
        nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
        slot_types: typing.Optional[typing.Sequence["SlotType"]] = None,
    ) -> None:
        '''
        :param locale_id: 
        :param voice_id: 
        :param code_hook: 
        :param description: 
        :param engine: 
        :param intents: 
        :param nlu_confidence_threshold: 
        :param slot_types: 
        '''
        if isinstance(code_hook, dict):
            code_hook = LocaleCodeHook(**code_hook)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9be63ab9108ceac68241166834aefa079f65bee5b69d86ef9f8e5666e8e79dcf)
            check_type(argname="argument locale_id", value=locale_id, expected_type=type_hints["locale_id"])
            check_type(argname="argument voice_id", value=voice_id, expected_type=type_hints["voice_id"])
            check_type(argname="argument code_hook", value=code_hook, expected_type=type_hints["code_hook"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument intents", value=intents, expected_type=type_hints["intents"])
            check_type(argname="argument nlu_confidence_threshold", value=nlu_confidence_threshold, expected_type=type_hints["nlu_confidence_threshold"])
            check_type(argname="argument slot_types", value=slot_types, expected_type=type_hints["slot_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "locale_id": locale_id,
            "voice_id": voice_id,
        }
        if code_hook is not None:
            self._values["code_hook"] = code_hook
        if description is not None:
            self._values["description"] = description
        if engine is not None:
            self._values["engine"] = engine
        if intents is not None:
            self._values["intents"] = intents
        if nlu_confidence_threshold is not None:
            self._values["nlu_confidence_threshold"] = nlu_confidence_threshold
        if slot_types is not None:
            self._values["slot_types"] = slot_types

    @builtins.property
    def locale_id(self) -> builtins.str:
        result = self._values.get("locale_id")
        assert result is not None, "Required property 'locale_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def voice_id(self) -> builtins.str:
        result = self._values.get("voice_id")
        assert result is not None, "Required property 'voice_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_hook(self) -> typing.Optional[LocaleCodeHook]:
        result = self._values.get("code_hook")
        return typing.cast(typing.Optional[LocaleCodeHook], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def intents(self) -> typing.Optional[typing.List[Intent]]:
        result = self._values.get("intents")
        return typing.cast(typing.Optional[typing.List[Intent]], result)

    @builtins.property
    def nlu_confidence_threshold(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("nlu_confidence_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def slot_types(self) -> typing.Optional[typing.List["SlotType"]]:
        result = self._values.get("slot_types")
        return typing.cast(typing.Optional[typing.List["SlotType"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LocaleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Slot(metaclass=jsii.JSIIMeta, jsii_type="@cxbuilder/aws-lex.Slot"):
    def __init__(
        self,
        *,
        elicitation_messages: typing.Sequence[builtins.str],
        name: builtins.str,
        slot_type_name: builtins.str,
        allow_interrupt: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        required: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param elicitation_messages: 
        :param name: 
        :param slot_type_name: 
        :param allow_interrupt: 
        :param description: 
        :param max_retries: 
        :param required: 
        '''
        props = SlotProps(
            elicitation_messages=elicitation_messages,
            name=name,
            slot_type_name=slot_type_name,
            allow_interrupt=allow_interrupt,
            description=description,
            max_retries=max_retries,
            required=required,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toCdk")
    def to_cdk(self) -> _aws_cdk_aws_lex_ceddda9d.CfnBot.SlotProperty:
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBot.SlotProperty, jsii.invoke(self, "toCdk", []))

    @builtins.property
    @jsii.member(jsii_name="elicitationMessages")
    def elicitation_messages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "elicitationMessages"))

    @elicitation_messages.setter
    def elicitation_messages(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7928b529b6a8303c97668b6db64e10276dc6621ac2860abe78a73b7276775fdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elicitationMessages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35444ed72450cd6e6a2c86eddbd7e00c3983fefe05f6b7153c26bb0995c9049d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slotTypeName")
    def slot_type_name(self) -> builtins.str:
        '''
        :todo: is there a way to restrict to possible values?
        '''
        return typing.cast(builtins.str, jsii.get(self, "slotTypeName"))

    @slot_type_name.setter
    def slot_type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9330402ad825d9f2d1b90d3226fcfd7be197a3c0b156a3a22a2e6a969ed75bc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slotTypeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowInterrupt")
    def allow_interrupt(self) -> typing.Optional[builtins.bool]:
        '''
        :default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowInterrupt"))

    @allow_interrupt.setter
    def allow_interrupt(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e30e2781ea8a2c629313b6db236caff371f4ed391bbd097c136a59d7eef7cb1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowInterrupt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f19bdbfe13639fca3bbd64e92cbde6170a2c18d43fb7c62aadc9c90f126bf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 3
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f2d10fcbabfb8c3e5b8108bf7646545f7353c61be7dd8eb03c2d5edae8ecc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRetries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "required"))

    @required.setter
    def required(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6af2dd54df09de5646c77bc2507b59f28fee358bc30454d6b0d980474967caec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.SlotProps",
    jsii_struct_bases=[],
    name_mapping={
        "elicitation_messages": "elicitationMessages",
        "name": "name",
        "slot_type_name": "slotTypeName",
        "allow_interrupt": "allowInterrupt",
        "description": "description",
        "max_retries": "maxRetries",
        "required": "required",
    },
)
class SlotProps:
    def __init__(
        self,
        *,
        elicitation_messages: typing.Sequence[builtins.str],
        name: builtins.str,
        slot_type_name: builtins.str,
        allow_interrupt: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        required: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param elicitation_messages: 
        :param name: 
        :param slot_type_name: 
        :param allow_interrupt: 
        :param description: 
        :param max_retries: 
        :param required: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4ed9cbc26de475c985e4fe6e89e521833dbb673741cdcd9a289089637dc63db)
            check_type(argname="argument elicitation_messages", value=elicitation_messages, expected_type=type_hints["elicitation_messages"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument slot_type_name", value=slot_type_name, expected_type=type_hints["slot_type_name"])
            check_type(argname="argument allow_interrupt", value=allow_interrupt, expected_type=type_hints["allow_interrupt"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument max_retries", value=max_retries, expected_type=type_hints["max_retries"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "elicitation_messages": elicitation_messages,
            "name": name,
            "slot_type_name": slot_type_name,
        }
        if allow_interrupt is not None:
            self._values["allow_interrupt"] = allow_interrupt
        if description is not None:
            self._values["description"] = description
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def elicitation_messages(self) -> typing.List[builtins.str]:
        result = self._values.get("elicitation_messages")
        assert result is not None, "Required property 'elicitation_messages' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def slot_type_name(self) -> builtins.str:
        result = self._values.get("slot_type_name")
        assert result is not None, "Required property 'slot_type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_interrupt(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("allow_interrupt")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def required(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("required")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlotType(metaclass=jsii.JSIIMeta, jsii_type="@cxbuilder/aws-lex.SlotType"):
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[typing.Union["SlotTypeValue", typing.Dict[builtins.str, typing.Any]]],
        description: typing.Optional[builtins.str] = None,
        resolution_strategy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param values: 
        :param description: 
        :param resolution_strategy: 
        '''
        props = SlotTypeProps(
            name=name,
            values=values,
            description=description,
            resolution_strategy=resolution_strategy,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toCdk")
    def to_cdk(self) -> _aws_cdk_aws_lex_ceddda9d.CfnBot.SlotTypeProperty:
        return typing.cast(_aws_cdk_aws_lex_ceddda9d.CfnBot.SlotTypeProperty, jsii.invoke(self, "toCdk", []))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29f30581d1d7ae0f1824357392222e6a10f65138af5860492b08c3d4a82d95a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List["SlotTypeValue"]:
        return typing.cast(typing.List["SlotTypeValue"], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List["SlotTypeValue"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d429564bf4a3e2c7577f3e9c388d2f4212459646173002348ba5226fca3c39f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568c0aacb37af2fcb7f2e3718ec12c5ed05eea54389b3674b8a73764a8887cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resolutionStrategy")
    def resolution_strategy(self) -> typing.Optional[builtins.str]:
        ''''ORIGINAL_VALUE' (the default) will resolve to what the caller said, provided it is close to one the provided sample values.

        'TOP_RESOLUTION' will always resolve to a sample value, or not at all. Use this if you need to branch on slot values
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resolutionStrategy"))

    @resolution_strategy.setter
    def resolution_strategy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31fd7dd5b02fda358d377e1d2c56d9962143a08a6b46416b4ea091d017fad962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resolutionStrategy", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.SlotTypeProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "values": "values",
        "description": "description",
        "resolution_strategy": "resolutionStrategy",
    },
)
class SlotTypeProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[typing.Union["SlotTypeValue", typing.Dict[builtins.str, typing.Any]]],
        description: typing.Optional[builtins.str] = None,
        resolution_strategy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param values: 
        :param description: 
        :param resolution_strategy: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2548b2959c37966b77ce2182092be2c1a71a69bfa7393ece5f1404a3cfc8dca6)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument resolution_strategy", value=resolution_strategy, expected_type=type_hints["resolution_strategy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "values": values,
        }
        if description is not None:
            self._values["description"] = description
        if resolution_strategy is not None:
            self._values["resolution_strategy"] = resolution_strategy

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List["SlotTypeValue"]:
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List["SlotTypeValue"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resolution_strategy(self) -> typing.Optional[builtins.str]:
        result = self._values.get("resolution_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlotTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cxbuilder/aws-lex.SlotTypeValue",
    jsii_struct_bases=[],
    name_mapping={"sample_value": "sampleValue", "synonyms": "synonyms"},
)
class SlotTypeValue:
    def __init__(
        self,
        *,
        sample_value: builtins.str,
        synonyms: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param sample_value: If 'resolutionStrategy' is set to 'TOP_RESOLUTION', this will be the resolved slot value if the slot is successfully filled.
        :param synonyms: a list of phrases that you want the bot to resolve to the sample value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c01c0f6887c67e764eb50e5b234ca8d07a26d1190e2ef256dae3ea20cc074dc)
            check_type(argname="argument sample_value", value=sample_value, expected_type=type_hints["sample_value"])
            check_type(argname="argument synonyms", value=synonyms, expected_type=type_hints["synonyms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sample_value": sample_value,
        }
        if synonyms is not None:
            self._values["synonyms"] = synonyms

    @builtins.property
    def sample_value(self) -> builtins.str:
        '''If 'resolutionStrategy' is set to 'TOP_RESOLUTION', this will be the resolved slot value if the slot is successfully filled.'''
        result = self._values.get("sample_value")
        assert result is not None, "Required property 'sample_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def synonyms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''a list of phrases that you want the bot to resolve to the sample value.'''
        result = self._values.get("synonyms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlotTypeValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Bot",
    "BotProps",
    "Intent",
    "IntentProps",
    "LexRole",
    "LexRoleProps",
    "Locale",
    "LocaleCodeHook",
    "LocaleProps",
    "Slot",
    "SlotProps",
    "SlotType",
    "SlotTypeProps",
    "SlotTypeValue",
]

publication.publish()

def _typecheckingstub__0b66b7aa3df3511d03e4ecb5245512928461adf3646bc373ac69add43fad8786(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    locales: typing.Sequence[Locale],
    name: builtins.str,
    audio_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    description: typing.Optional[builtins.str] = None,
    idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
    replica_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eb46d0eb5aab6caec43e68297a9bb2c3784a63d5777ca280caf770eaa5b4462(
    alias_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__939189742fb16d1bb58391e5f36bacc14ec9852222433072a4f83673d3873d17(
    *,
    locales: typing.Sequence[Locale],
    name: builtins.str,
    audio_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    description: typing.Optional[builtins.str] = None,
    idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
    replica_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bcd0a568f6b8bc4d8c416357cfa51eb6f8d1d9a641b03cdd0109df437e31735(
    dialog_code_hook: builtins.bool,
    fulfillment_code_hook: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73cf94b90f74dd79ff237e474f47ccf073c1a0c1769c1bf8ffc57611e0494d9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6a18eb1a04c23378fcf29add9b897f7edc8eabdb2e8ba6804be274d4051eb68(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76554220bf1b2ba17174528b01493cd9d84337e43d2f621f7071c8f5d801db74(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf6337be4d210afd62b619f0aa30cc23c58df2a44a616e1c1a1408add9547649(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00c03d711854d1087a305d1c7cd8a456ebe74ddce78b68e2e7753ec9d9b56f5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f18e8d7d573b1cc97bb981511c178096f3c90432095f9ffe79546eaf92cc671(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__380d6014ea80ab2b039337e5559c86efcd28f2eb836d16dc2ef55a060b64da8a(
    value: typing.Optional[typing.List[Slot]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64854e6efff0b4de5c2cf7bd3aa17a62e6ab3665b43b707caf51a6804cae93a3(
    *,
    name: builtins.str,
    utterances: typing.Sequence[builtins.str],
    confirmation_failure_prompt: typing.Optional[builtins.str] = None,
    confirmation_prompt: typing.Optional[builtins.str] = None,
    fulfillment_failure_prompt: typing.Optional[builtins.str] = None,
    fulfillment_prompt: typing.Optional[builtins.str] = None,
    slots: typing.Optional[typing.Sequence[Slot]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e0cc8abcaee00884442792c97ff10a6e07b056c02158c3451fbf064aa72b740(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    lex_log_group_name: typing.Optional[builtins.str] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1679559836a043b576bd52e350f92fc71fe12dec0b52396d92bf696cf6985888(
    *,
    lex_log_group_name: typing.Optional[builtins.str] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc2b68f597684a49df6926de4c8ea80bead4d305ef999b28f386df7f4f8f914b(
    scope: _constructs_77d1e7e8.Construct,
    bot_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__561f5fe43edfde7cf7d4294cd30258789aa4d74e68317c1545e088643999b57b(
    bot_nlu_confidence_threshold: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29c20e16645ac3ac6f7cbbde8f06709388ce36ab861b559d72f8cad3000becb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__592d701f4912a266c2a7df9905c500b7129f0ee010353213ba6d92eb05459fc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a6aa2b999f90a6df971c09d5064139c5ad49ecc6e310921ecd37d5d105d0de7(
    value: typing.Optional[LocaleCodeHook],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d32971dd3020db7c868bdaf41ce5c84dbec22b9c94de0f1c739cf9b565de6d28(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cea14d93c26e0e452be95b0194bdb3ca9629131645b5609acb6c9804615a5855(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c4e750755a4d983f75260e83741bb3dc57d199c5b26f2099a6736daeb1a3d37(
    value: typing.Optional[typing.List[Intent]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa06977e88d791a2f236817e61af6f93f1a8238a0ba4ac3387266d3e80610574(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6f7cb1e95d56064b66922fbc5a3aedf6acde865555c9c28c58e558197129061(
    value: typing.Optional[typing.List[SlotType]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a35bd79dda028f06b08ef09dcedeaf0cf0a69e8e7d7a4bc09c70355cdebf839(
    *,
    fn: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    dialog: typing.Optional[builtins.bool] = None,
    fulfillment: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9be63ab9108ceac68241166834aefa079f65bee5b69d86ef9f8e5666e8e79dcf(
    *,
    locale_id: builtins.str,
    voice_id: builtins.str,
    code_hook: typing.Optional[typing.Union[LocaleCodeHook, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    engine: typing.Optional[builtins.str] = None,
    intents: typing.Optional[typing.Sequence[Intent]] = None,
    nlu_confidence_threshold: typing.Optional[jsii.Number] = None,
    slot_types: typing.Optional[typing.Sequence[SlotType]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7928b529b6a8303c97668b6db64e10276dc6621ac2860abe78a73b7276775fdb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35444ed72450cd6e6a2c86eddbd7e00c3983fefe05f6b7153c26bb0995c9049d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9330402ad825d9f2d1b90d3226fcfd7be197a3c0b156a3a22a2e6a969ed75bc5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e30e2781ea8a2c629313b6db236caff371f4ed391bbd097c136a59d7eef7cb1b(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f19bdbfe13639fca3bbd64e92cbde6170a2c18d43fb7c62aadc9c90f126bf9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f2d10fcbabfb8c3e5b8108bf7646545f7353c61be7dd8eb03c2d5edae8ecc6(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6af2dd54df09de5646c77bc2507b59f28fee358bc30454d6b0d980474967caec(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ed9cbc26de475c985e4fe6e89e521833dbb673741cdcd9a289089637dc63db(
    *,
    elicitation_messages: typing.Sequence[builtins.str],
    name: builtins.str,
    slot_type_name: builtins.str,
    allow_interrupt: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    required: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29f30581d1d7ae0f1824357392222e6a10f65138af5860492b08c3d4a82d95a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d429564bf4a3e2c7577f3e9c388d2f4212459646173002348ba5226fca3c39f(
    value: typing.List[SlotTypeValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568c0aacb37af2fcb7f2e3718ec12c5ed05eea54389b3674b8a73764a8887cde(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31fd7dd5b02fda358d377e1d2c56d9962143a08a6b46416b4ea091d017fad962(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2548b2959c37966b77ce2182092be2c1a71a69bfa7393ece5f1404a3cfc8dca6(
    *,
    name: builtins.str,
    values: typing.Sequence[typing.Union[SlotTypeValue, typing.Dict[builtins.str, typing.Any]]],
    description: typing.Optional[builtins.str] = None,
    resolution_strategy: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c01c0f6887c67e764eb50e5b234ca8d07a26d1190e2ef256dae3ea20cc074dc(
    *,
    sample_value: builtins.str,
    synonyms: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
