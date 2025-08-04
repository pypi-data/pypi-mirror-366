r'''
# CDK Express Pipeline

[![npm version](https://badge.fury.io/js/cdk-express-pipeline.svg)](https://badge.fury.io/js/cdk-express-pipeline)
[![PyPI version](https://badge.fury.io/py/cdk-express-pipeline.svg)](https://badge.fury.io/py/cdk-express-pipeline)

> [!IMPORTANT]
> Full documentation is available at [https://rehanvdm.github.io/cdk-express-pipeline/](https://rehanvdm.github.io/cdk-express-pipeline/).

## What is CDK Express Pipeline?

[CDK Express Pipeline](https://github.com/rehanvdm/cdk-express-pipeline/tree/main) is a library built on the AWS CDK,
allowing you to define pipelines in a CDK-native method. It leverages the CDK CLI to compute and deploy the correct
dependency graph between Waves, Stages, and Stacks using the <code>.addDependency</code> method, making it build-system
agnostic and an alternative to AWS CDK Pipelines.

## Key Features

* **Build System Agnostic**: Works on any system for example your local machine, GitHub, GitLab, etc.
* **Waves and Stages**: Define your pipeline structure using Waves and Stages
* **Uses CDK CLI**: Uses the `cdk deploy` command to deploy your stacks
* **Multi Account and Multi Region**: Supports deployments across multiple accounts and regions mad possible by `cdk bootstrap`
* **Fast Deployments**: Make use of concurrent/parallel Stack deployments
* **Multi-Language Support**: Supports **TS and Python** CDK
* **Generated Mermaid Diagrams**: Generates diagrams for your pipeline structure
* **Generated CI Workflows**: Generates CI workflows for your pipeline (only GitHub Actions supported for now, others welcome)

## Quick Start

```bash
npm install cdk-express-pipeline
```

Let's illustrate a common patten, deploying infra stacks before application stacks. The `IamStack` is only in the
`us-east-1` region, while the `NetworkingStack` is in both `us-east-1` and `eu-west-1`.

The application stacks `AppAStack` and `AppBStack` depend on the networking stack and are deployed in both regions.
The `AppBStack` also depends on the `AppAStack`.

```python
//bin/your-app.ts
const app = new App();
const expressPipeline = new CdkExpressPipeline();

const regions = ['us-east-1', 'eu-west-1'];

const infraWave = expressPipeline.addWave('Infra');
const infraWaveUsEast1Stage = infraWave.addStage('us-east-1');
const infraWaveEuWest1Stage = infraWave.addStage('eu-west-1');
new IamStack(app, 'Iam', infraWaveUsEast1Stage);
new NetworkingStack(app, 'Networking', infraWaveUsEast1Stage);
new NetworkingStack(app, 'Networking', infraWaveEuWest1Stage);

const appWave = expressPipeline.addWave('Application');
for (const region of regions) {
  const appWaveStage = appWave.addStage(region);
  const appA = new AppAStack(app, 'AppA', appWaveStage);
  const appB = new AppBStack(app, 'AppB', appWaveStage);
  appB.addExpressDependency(appA);
}

expressPipeline.synth([
  infraWave,
  appWave,
], true, {});
```

Running `cdk deploy '**' --concurrency 10` will deploy all stacks in the correct order based on their dependencies. This
is indicated on the CLI output:

```plaintext
ORDER OF DEPLOYMENT
🌊 Waves  - Deployed sequentially.
🏗 Stages - Deployed in parallel by default, unless the wave is marked `[Seq 🏗]` for sequential stage execution.
📦 Stacks - Deployed after their dependent stacks within the stage (dependencies shown below them with ↳).
           - Lines prefixed with a pipe (|) indicate stacks matching the CDK pattern.
           - Stack deployment order within the stage is shown in square brackets (ex: [1])

| 🌊 Infra
|   🏗 us-east-1
|     📦 Iam (Infra_us-east-1_Iam) [1]
|     📦 Networking (Infra_us-east-1_Networking) [1]
|   🏗 eu-west-1
|     📦 Networking (Infra_eu-west-1_Networking) [1]
| 🌊 Application
|   🏗 us-east-1
|     📦 AppA (Application_us-east-1_AppA) [1]
|     📦 AppB (Application_us-east-1_AppB) [2]
|        ↳ AppA
|   🏗 eu-west-1
|     📦 AppA (Application_eu-west-1_AppA) [1]
|     📦 AppB (Application_eu-west-1_AppB) [2]
|        ↳ AppA
```

A Mermaid diagram of the pipeline is saved to `./pipeline-deployment-order.md` automatically:

```mermaid
graph TD
    subgraph Wave0["🌊 Infra"]
        subgraph Wave0Stage0["🏗 us-east-1"]
            StackInfra_us_east_1_Iam["📦 Iam [1]"]
            StackInfra_us_east_1_Networking["📦 Networking [1]"]
        end
        subgraph Wave0Stage1["🏗 eu-west-1"]
            StackInfra_eu_west_1_Networking["📦 Networking [1]"]
        end
    end
    subgraph Wave1["🌊 Application"]
        subgraph Wave1Stage0["🏗 us-east-1"]
            StackApplication_us_east_1_AppA["📦 AppA [1]"]
            StackApplication_us_east_1_AppB["📦 AppB [2]"]
        end
        subgraph Wave1Stage1["🏗 eu-west-1"]
            StackApplication_eu_west_1_AppA["📦 AppA [1]"]
            StackApplication_eu_west_1_AppB["📦 AppB [2]"]
        end
    end
    StackApplication_us_east_1_AppA --> StackApplication_us_east_1_AppB
    StackApplication_eu_west_1_AppA --> StackApplication_eu_west_1_AppB
    Wave0 --> Wave1
```

CDK Express Pipeline is build system agnostic, meaning you can run the `cdk deploy` command from any environment,
such as your local machine, GitHub Actions, GitLab CI, etc. It includes a function to generate GitHub Actions workflow,
more build systems can be added as needed.

## Next Steps

> [!IMPORTANT]
> Full documentation is available at [https://rehanvdm.github.io/cdk-express-pipeline/](https://rehanvdm.github.io/cdk-express-pipeline/).
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


@jsii.data_type(
    jsii_type="cdk-express-pipeline.BuildConfig",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "workflow": "workflow"},
)
class BuildConfig:
    def __init__(
        self,
        *,
        type: builtins.str,
        workflow: typing.Optional[typing.Union["WorkflowLocation", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param type: The type of workflow to use.
        :param workflow: Only required if type is 'workflow'. Specify the workflow or reusable action to use for building
        '''
        if isinstance(workflow, dict):
            workflow = WorkflowLocation(**workflow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__176a33dbfec3fbf84c7f09cd7d5fa47dc7938b65faf1fefd2a2e277c8b10b538)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument workflow", value=workflow, expected_type=type_hints["workflow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if workflow is not None:
            self._values["workflow"] = workflow

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of workflow to use.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workflow(self) -> typing.Optional["WorkflowLocation"]:
        '''Only required if type is 'workflow'.

        Specify the workflow or reusable action to use for building
        '''
        result = self._values.get("workflow")
        return typing.cast(typing.Optional["WorkflowLocation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdkExpressPipeline(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.CdkExpressPipeline",
):
    '''A CDK Express Pipeline that defines the order in which the stacks are deployed.'''

    def __init__(
        self,
        *,
        separator: typing.Optional[builtins.str] = None,
        waves: typing.Optional[typing.Sequence["ExpressWave"]] = None,
    ) -> None:
        '''
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: _
        :param waves: The waves in the pipeline.
        '''
        props = CdkExpressPipelineProps(separator=separator, waves=waves)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addWave")
    def add_wave(
        self,
        id: builtins.str,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> "IExpressWave":
        '''Add a wave to the pipeline.

        :param id: The wave identifier.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d5a812c29abca46e9446db3e0acfaedb3fb0f70a5ccbc26b8b26b62c731b30)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        return typing.cast("IExpressWave", jsii.invoke(self, "addWave", [id, sequential_stages]))

    @jsii.member(jsii_name="generateGitHubWorkflows")
    def generate_git_hub_workflows(
        self,
        git_hub_workflow_config: typing.Union["GitHubWorkflowConfig", typing.Dict[builtins.str, typing.Any]],
        save_to_files: typing.Optional[builtins.bool] = None,
    ) -> typing.List["GithubWorkflowFile"]:
        '''
        :param git_hub_workflow_config: -
        :param save_to_files: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e284e6bc2289754ab5a16d412952ff0c2b3c0f4ae78655914206f911311579c0)
            check_type(argname="argument git_hub_workflow_config", value=git_hub_workflow_config, expected_type=type_hints["git_hub_workflow_config"])
            check_type(argname="argument save_to_files", value=save_to_files, expected_type=type_hints["save_to_files"])
        return typing.cast(typing.List["GithubWorkflowFile"], jsii.invoke(self, "generateGitHubWorkflows", [git_hub_workflow_config, save_to_files]))

    @jsii.member(jsii_name="generateMermaidDiagram")
    def generate_mermaid_diagram(
        self,
        waves: typing.Sequence["IExpressWave"],
    ) -> builtins.str:
        '''Generate a Mermaid diagram showing the deployment order.

        :param waves: The waves to include in the diagram.

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48596730e21a3fe0e78a5e73d024ad054e1679fbe0d63f873eb81c728a6fc0d6)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(builtins.str, jsii.invoke(self, "generateMermaidDiagram", [waves]))

    @jsii.member(jsii_name="printWaves")
    def print_waves(self, waves: typing.Sequence["IExpressWave"]) -> None:
        '''Print the order of deployment to the console.

        :param waves: -

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18d77fb9496cb5fdeabb0fe5a14c3dcd08b7a4747694ac0a799b01dfa105a34)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(None, jsii.invoke(self, "printWaves", [waves]))

    @jsii.member(jsii_name="saveGitHubWorkflows")
    def save_git_hub_workflows(
        self,
        workflows: typing.Sequence[typing.Union["GithubWorkflowFile", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param workflows: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a545be0c7f0244a8cedbc9796c6c38f57f873c3c1ba9bb23a76f5d8f63bfafa)
            check_type(argname="argument workflows", value=workflows, expected_type=type_hints["workflows"])
        return typing.cast(None, jsii.invoke(self, "saveGitHubWorkflows", [workflows]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        waves: typing.Optional[typing.Sequence["IExpressWave"]] = None,
        print: typing.Optional[builtins.bool] = None,
        *,
        file_name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Synthesize the pipeline which creates the dependencies between the stacks in the correct order.

        :param waves: The waves to synthesize.
        :param print: Whether to print the order of deployment to the console.
        :param file_name: Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.
        :param path: The path where the Mermaid diagram will be saved. If not provided defaults to root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddf3f54429b9cebdd63080df8e42a8f0bee80ea5889f7848d8110f99befcf433)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
            check_type(argname="argument print", value=print, expected_type=type_hints["print"])
        save_mermaid_diagram = MermaidDiagramOutput(file_name=file_name, path=path)

        return typing.cast(None, jsii.invoke(self, "synth", [waves, print, save_mermaid_diagram]))

    @builtins.property
    @jsii.member(jsii_name="waves")
    def waves(self) -> typing.List["IExpressWave"]:
        return typing.cast(typing.List["IExpressWave"], jsii.get(self, "waves"))


@jsii.data_type(
    jsii_type="cdk-express-pipeline.CdkExpressPipelineAssembly",
    jsii_struct_bases=[],
    name_mapping={"waves": "waves"},
)
class CdkExpressPipelineAssembly:
    def __init__(
        self,
        *,
        waves: typing.Sequence[typing.Union["CdkExpressPipelineAssemblyWave", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param waves: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__973836022e8419d6996db18e9376d9e9f363b6b8746e80a5208b60649e5e0548)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "waves": waves,
        }

    @builtins.property
    def waves(self) -> typing.List["CdkExpressPipelineAssemblyWave"]:
        result = self._values.get("waves")
        assert result is not None, "Required property 'waves' is missing"
        return typing.cast(typing.List["CdkExpressPipelineAssemblyWave"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkExpressPipelineAssembly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.CdkExpressPipelineAssemblyStack",
    jsii_struct_bases=[],
    name_mapping={"stack_id": "stackId", "stack_name": "stackName"},
)
class CdkExpressPipelineAssemblyStack:
    def __init__(self, *, stack_id: builtins.str, stack_name: builtins.str) -> None:
        '''
        :param stack_id: 
        :param stack_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8cc27cce2b3b402590f9ed6714e538ea3ce9457c7f64fd4299544f1e4ca45e6)
            check_type(argname="argument stack_id", value=stack_id, expected_type=type_hints["stack_id"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stack_id": stack_id,
            "stack_name": stack_name,
        }

    @builtins.property
    def stack_id(self) -> builtins.str:
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_name(self) -> builtins.str:
        result = self._values.get("stack_name")
        assert result is not None, "Required property 'stack_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkExpressPipelineAssemblyStack(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.CdkExpressPipelineAssemblyStage",
    jsii_struct_bases=[],
    name_mapping={"stacks": "stacks", "stage_id": "stageId"},
)
class CdkExpressPipelineAssemblyStage:
    def __init__(
        self,
        *,
        stacks: typing.Sequence[typing.Union[CdkExpressPipelineAssemblyStack, typing.Dict[builtins.str, typing.Any]]],
        stage_id: builtins.str,
    ) -> None:
        '''
        :param stacks: 
        :param stage_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07fd5e056e014f371264dd85f08c120ecdf36ed4b5347f07bbc10a6c63ce1294)
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument stage_id", value=stage_id, expected_type=type_hints["stage_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stacks": stacks,
            "stage_id": stage_id,
        }

    @builtins.property
    def stacks(self) -> typing.List[CdkExpressPipelineAssemblyStack]:
        result = self._values.get("stacks")
        assert result is not None, "Required property 'stacks' is missing"
        return typing.cast(typing.List[CdkExpressPipelineAssemblyStack], result)

    @builtins.property
    def stage_id(self) -> builtins.str:
        result = self._values.get("stage_id")
        assert result is not None, "Required property 'stage_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkExpressPipelineAssemblyStage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.CdkExpressPipelineAssemblyWave",
    jsii_struct_bases=[],
    name_mapping={"stages": "stages", "wave_id": "waveId"},
)
class CdkExpressPipelineAssemblyWave:
    def __init__(
        self,
        *,
        stages: typing.Sequence[typing.Union[CdkExpressPipelineAssemblyStage, typing.Dict[builtins.str, typing.Any]]],
        wave_id: builtins.str,
    ) -> None:
        '''
        :param stages: 
        :param wave_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d56a7bedc197325c6dc7f8604d76dded58fc174561a83fba34b02d40e8ba18c0)
            check_type(argname="argument stages", value=stages, expected_type=type_hints["stages"])
            check_type(argname="argument wave_id", value=wave_id, expected_type=type_hints["wave_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stages": stages,
            "wave_id": wave_id,
        }

    @builtins.property
    def stages(self) -> typing.List[CdkExpressPipelineAssemblyStage]:
        result = self._values.get("stages")
        assert result is not None, "Required property 'stages' is missing"
        return typing.cast(typing.List[CdkExpressPipelineAssemblyStage], result)

    @builtins.property
    def wave_id(self) -> builtins.str:
        result = self._values.get("wave_id")
        assert result is not None, "Required property 'wave_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkExpressPipelineAssemblyWave(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdkExpressPipelineLegacy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.CdkExpressPipelineLegacy",
):
    '''A CDK Express Pipeline that defines the order in which the stacks are deployed.

    This is the legacy version of the pipeline that uses the ``Stack`` class, for plug and play compatibility with existing CDK projects that can not
    use the ``ExpressStack`` class. For new projects, use the ``CdkExpressPipeline`` class.
    '''

    def __init__(
        self,
        waves: typing.Optional[typing.Sequence["IExpressWaveLegacy"]] = None,
    ) -> None:
        '''
        :param waves: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e78d8fa8554a29ac59173413b98062741ae83aeb4754f02a80c85c27e16d8ce)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        jsii.create(self.__class__, self, [waves])

    @jsii.member(jsii_name="addWave")
    def add_wave(
        self,
        id: builtins.str,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> "ExpressWaveLegacy":
        '''Add a wave to the pipeline.

        :param id: The wave identifier.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58733341409ff8a6c60fbf06de891a31f81f41cf55e7503aaa0238ee46ff5166)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        return typing.cast("ExpressWaveLegacy", jsii.invoke(self, "addWave", [id, sequential_stages]))

    @jsii.member(jsii_name="generateMermaidDiagram")
    def generate_mermaid_diagram(
        self,
        waves: typing.Sequence["IExpressWaveLegacy"],
    ) -> builtins.str:
        '''Generate a Mermaid diagram showing the deployment order.

        :param waves: The waves to include in the diagram.

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1ef4d18ff1ca1a7788d1801361a996c26480f2387d3a28be69812108f489380)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(builtins.str, jsii.invoke(self, "generateMermaidDiagram", [waves]))

    @jsii.member(jsii_name="printWaves")
    def print_waves(self, waves: typing.Sequence["IExpressWaveLegacy"]) -> None:
        '''Print the order of deployment to the console.

        :param waves: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d22fe922729d650ca61abf0f4568bb8cbafe791434481f3e0cce74d098f785e)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(None, jsii.invoke(self, "printWaves", [waves]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        waves: typing.Optional[typing.Sequence["IExpressWaveLegacy"]] = None,
        print: typing.Optional[builtins.bool] = None,
        *,
        file_name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Synthesize the pipeline which creates the dependencies between the stacks in the correct order.

        :param waves: The waves to synthesize.
        :param print: Whether to print the order of deployment to the console.
        :param file_name: Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.
        :param path: The path where the Mermaid diagram will be saved. If not provided defaults to root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7d8bd5a65c1437ed17046edfb50f14e1f2b8f73c9db08927132a10f37d409d)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
            check_type(argname="argument print", value=print, expected_type=type_hints["print"])
        save_mermaid_diagram = MermaidDiagramOutput(file_name=file_name, path=path)

        return typing.cast(None, jsii.invoke(self, "synth", [waves, print, save_mermaid_diagram]))

    @builtins.property
    @jsii.member(jsii_name="waves")
    def waves(self) -> typing.List["IExpressWaveLegacy"]:
        return typing.cast(typing.List["IExpressWaveLegacy"], jsii.get(self, "waves"))

    @waves.setter
    def waves(self, value: typing.List["IExpressWaveLegacy"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54082bd27a8ceffd74f1b6a0cb05b3bbcf4ffa9ada94c72e52e645687ad4ad5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waves", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="cdk-express-pipeline.CdkExpressPipelineProps",
    jsii_struct_bases=[],
    name_mapping={"separator": "separator", "waves": "waves"},
)
class CdkExpressPipelineProps:
    def __init__(
        self,
        *,
        separator: typing.Optional[builtins.str] = None,
        waves: typing.Optional[typing.Sequence["ExpressWave"]] = None,
    ) -> None:
        '''
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: _
        :param waves: The waves in the pipeline.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc99a79d5da23f439f19b4717a315983fa455ec2ae7d0300ac3d7381d5892205)
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if separator is not None:
            self._values["separator"] = separator
        if waves is not None:
            self._values["waves"] = waves

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Separator between the wave, stage and stack ids that are concatenated to form the stack id.

        :default: _
        '''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def waves(self) -> typing.Optional[typing.List["ExpressWave"]]:
        '''The waves in the pipeline.'''
        result = self._values.get("waves")
        return typing.cast(typing.Optional[typing.List["ExpressWave"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkExpressPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.DeployWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={
        "assume_region": "assumeRegion",
        "assume_role_arn": "assumeRoleArn",
        "commands": "commands",
        "on": "on",
        "stack_selector": "stackSelector",
        "id": "id",
    },
)
class DeployWorkflowConfig:
    def __init__(
        self,
        *,
        assume_region: builtins.str,
        assume_role_arn: builtins.str,
        commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
        on: typing.Union["WorkflowTriggers", typing.Dict[builtins.str, typing.Any]],
        stack_selector: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param assume_region: AWS region to assume for the diff operation.
        :param assume_role_arn: ARN of the role to assume for the diff operation.
        :param commands: Commands to run for synthesis.
        :param on: Conditions that trigger the deploy workflow.
        :param stack_selector: Selector for the stack type.
        :param id: Unique identifier, postfixed to the generated workflow name. Can be omitted if only one workflow is specified.
        '''
        if isinstance(on, dict):
            on = WorkflowTriggers(**on)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__064ff6a399a517de1d9d8831492460b92378a4013ef6125878a1c1553dab6e74)
            check_type(argname="argument assume_region", value=assume_region, expected_type=type_hints["assume_region"])
            check_type(argname="argument assume_role_arn", value=assume_role_arn, expected_type=type_hints["assume_role_arn"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
            check_type(argname="argument stack_selector", value=stack_selector, expected_type=type_hints["stack_selector"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assume_region": assume_region,
            "assume_role_arn": assume_role_arn,
            "commands": commands,
            "on": on,
            "stack_selector": stack_selector,
        }
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def assume_region(self) -> builtins.str:
        '''AWS region to assume for the diff operation.'''
        result = self._values.get("assume_region")
        assert result is not None, "Required property 'assume_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> builtins.str:
        '''ARN of the role to assume for the diff operation.'''
        result = self._values.get("assume_role_arn")
        assert result is not None, "Required property 'assume_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commands(self) -> typing.List[typing.Mapping[builtins.str, builtins.str]]:
        '''Commands to run for synthesis.'''
        result = self._values.get("commands")
        assert result is not None, "Required property 'commands' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def on(self) -> "WorkflowTriggers":
        '''Conditions that trigger the deploy workflow.'''
        result = self._values.get("on")
        assert result is not None, "Required property 'on' is missing"
        return typing.cast("WorkflowTriggers", result)

    @builtins.property
    def stack_selector(self) -> builtins.str:
        '''Selector for the stack type.'''
        result = self._values.get("stack_selector")
        assert result is not None, "Required property 'stack_selector' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier, postfixed to the generated workflow name.

        Can be omitted if only one workflow is specified.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeployWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.DiffWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={
        "assume_region": "assumeRegion",
        "assume_role_arn": "assumeRoleArn",
        "commands": "commands",
        "on": "on",
        "stack_selector": "stackSelector",
        "id": "id",
        "write_as_comment": "writeAsComment",
    },
)
class DiffWorkflowConfig:
    def __init__(
        self,
        *,
        assume_region: builtins.str,
        assume_role_arn: builtins.str,
        commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
        on: typing.Union["WorkflowTriggers", typing.Dict[builtins.str, typing.Any]],
        stack_selector: builtins.str,
        id: typing.Optional[builtins.str] = None,
        write_as_comment: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param assume_region: AWS region to assume for the diff operation.
        :param assume_role_arn: ARN of the role to assume for the diff operation.
        :param commands: Commands to run for synthesis.
        :param on: Conditions that trigger the diff workflow.
        :param stack_selector: Selector for the stack type.
        :param id: Unique identifier, postfixed to the generated workflow name. Can be omitted if only one workflow is specified.
        :param write_as_comment: Whether to write the diff as a comment. Default: true
        '''
        if isinstance(on, dict):
            on = WorkflowTriggers(**on)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd8d22f0c989f84b5e91067c258f24562fc4d3b5c471e9302c3fd36c7c66492)
            check_type(argname="argument assume_region", value=assume_region, expected_type=type_hints["assume_region"])
            check_type(argname="argument assume_role_arn", value=assume_role_arn, expected_type=type_hints["assume_role_arn"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
            check_type(argname="argument stack_selector", value=stack_selector, expected_type=type_hints["stack_selector"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument write_as_comment", value=write_as_comment, expected_type=type_hints["write_as_comment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assume_region": assume_region,
            "assume_role_arn": assume_role_arn,
            "commands": commands,
            "on": on,
            "stack_selector": stack_selector,
        }
        if id is not None:
            self._values["id"] = id
        if write_as_comment is not None:
            self._values["write_as_comment"] = write_as_comment

    @builtins.property
    def assume_region(self) -> builtins.str:
        '''AWS region to assume for the diff operation.'''
        result = self._values.get("assume_region")
        assert result is not None, "Required property 'assume_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> builtins.str:
        '''ARN of the role to assume for the diff operation.'''
        result = self._values.get("assume_role_arn")
        assert result is not None, "Required property 'assume_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commands(self) -> typing.List[typing.Mapping[builtins.str, builtins.str]]:
        '''Commands to run for synthesis.'''
        result = self._values.get("commands")
        assert result is not None, "Required property 'commands' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def on(self) -> "WorkflowTriggers":
        '''Conditions that trigger the diff workflow.'''
        result = self._values.get("on")
        assert result is not None, "Required property 'on' is missing"
        return typing.cast("WorkflowTriggers", result)

    @builtins.property
    def stack_selector(self) -> builtins.str:
        '''Selector for the stack type.'''
        result = self._values.get("stack_selector")
        assert result is not None, "Required property 'stack_selector' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier, postfixed to the generated workflow name.

        Can be omitted if only one workflow is specified.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def write_as_comment(self) -> typing.Optional[builtins.bool]:
        '''Whether to write the diff as a comment.

        :default: true
        '''
        result = self._values.get("write_as_comment")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DiffWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.ExpressWaveProps",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "separator": "separator"},
)
class ExpressWaveProps:
    def __init__(
        self,
        *,
        id: builtins.str,
        separator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: 
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: ``_``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d91dc79595e990d6da1a185afde4e65465da1f5dc12abd5220e16803db5481a2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if separator is not None:
            self._values["separator"] = separator

    @builtins.property
    def id(self) -> builtins.str:
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Separator between the wave, stage and stack ids that are concatenated to form the stack id.

        :default: ``_``
        '''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExpressWaveProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.GitHubWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={"deploy": "deploy", "diff": "diff", "synth": "synth"},
)
class GitHubWorkflowConfig:
    def __init__(
        self,
        *,
        deploy: typing.Sequence[typing.Union[DeployWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
        diff: typing.Sequence[typing.Union[DiffWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
        synth: typing.Union["SynthWorkflowConfig", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param deploy: Configuration for the deploy workflow.
        :param diff: Configuration for the diff workflow.
        :param synth: Configuration for the synth workflow.
        '''
        if isinstance(synth, dict):
            synth = SynthWorkflowConfig(**synth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a08064d282d091b65891b01b014a0a8a260163ad7f73ec21450a321e2a8b285)
            check_type(argname="argument deploy", value=deploy, expected_type=type_hints["deploy"])
            check_type(argname="argument diff", value=diff, expected_type=type_hints["diff"])
            check_type(argname="argument synth", value=synth, expected_type=type_hints["synth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "deploy": deploy,
            "diff": diff,
            "synth": synth,
        }

    @builtins.property
    def deploy(self) -> typing.List[DeployWorkflowConfig]:
        '''Configuration for the deploy workflow.'''
        result = self._values.get("deploy")
        assert result is not None, "Required property 'deploy' is missing"
        return typing.cast(typing.List[DeployWorkflowConfig], result)

    @builtins.property
    def diff(self) -> typing.List[DiffWorkflowConfig]:
        '''Configuration for the diff workflow.'''
        result = self._values.get("diff")
        assert result is not None, "Required property 'diff' is missing"
        return typing.cast(typing.List[DiffWorkflowConfig], result)

    @builtins.property
    def synth(self) -> "SynthWorkflowConfig":
        '''Configuration for the synth workflow.'''
        result = self._values.get("synth")
        assert result is not None, "Required property 'synth' is missing"
        return typing.cast("SynthWorkflowConfig", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GithubWorkflow(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.GithubWorkflow",
):
    def __init__(self, json: typing.Mapping[typing.Any, typing.Any]) -> None:
        '''
        :param json: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3923cfcb617f1c1f17d022bb3436263a7c98cdcb87f419363015fb8520b511d6)
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
        jsii.create(self.__class__, self, [json])

    @jsii.member(jsii_name="patch")
    def patch(self, *ops: "Patch") -> "GithubWorkflow":
        '''Applies a set of JSON-Patch (RFC-6902) operations to this object and returns the result.

        :param ops: The operations to apply.

        :return: The result object
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49ff91c791fec0d9e19de3f5d1c58b5d0e0e2045aeed51944132881cecfefa62)
            check_type(argname="argument ops", value=ops, expected_type=typing.Tuple[type_hints["ops"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("GithubWorkflow", jsii.invoke(self, "patch", [*ops]))

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "json"))

    @json.setter
    def json(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22f05ed853a2e74dee0193a62770b3ae51bb4f3b85b9efbd5d32135798819a32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "json", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="cdk-express-pipeline.GithubWorkflowFile",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "file_name": "fileName"},
)
class GithubWorkflowFile:
    def __init__(self, *, content: GithubWorkflow, file_name: builtins.str) -> None:
        '''
        :param content: 
        :param file_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__038bf0270c6ca55596a013a4a31894e79899942811087d804768f4ed4ba3d4e2)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "file_name": file_name,
        }

    @builtins.property
    def content(self) -> GithubWorkflow:
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(GithubWorkflow, result)

    @builtins.property
    def file_name(self) -> builtins.str:
        result = self._values.get("file_name")
        assert result is not None, "Required property 'file_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubWorkflowFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressStack")
class IExpressStack(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stack identifier which is a combination of the wave, stage and stack id.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "ExpressStage":
        '''The stage that the stack belongs to.'''
        ...

    @stage.setter
    def stage(self, value: "ExpressStage") -> None:
        ...

    @jsii.member(jsii_name="addExpressDependency")
    def add_express_dependency(
        self,
        target: "ExpressStack",
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Add a dependency between this stack and another ExpressStack.

        This can be used to define dependencies between any two stacks within an

        :param target: The ``ExpressStack`` to depend on.
        :param reason: The reason for the dependency.
        '''
        ...

    @jsii.member(jsii_name="expressDependencies")
    def express_dependencies(self) -> typing.List["ExpressStack"]:
        '''The ExpressStack dependencies of the stack.'''
        ...


class _IExpressStackProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressStack"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stack identifier which is a combination of the wave, stage and stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76bd73c874b49b4683b044d917cc6800ed471f2b41d3164b902c206407432cbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "ExpressStage":
        '''The stage that the stack belongs to.'''
        return typing.cast("ExpressStage", jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: "ExpressStage") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61a812768afc62205a9db0f1f9d01095658800d0cc43087913d4c1645cde7bdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stage", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="addExpressDependency")
    def add_express_dependency(
        self,
        target: "ExpressStack",
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Add a dependency between this stack and another ExpressStack.

        This can be used to define dependencies between any two stacks within an

        :param target: The ``ExpressStack`` to depend on.
        :param reason: The reason for the dependency.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a14719acbf68f0fd518f950b2dd5d2922f8e4c9c9273c2f85d05589af97f191)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "addExpressDependency", [target, reason]))

    @jsii.member(jsii_name="expressDependencies")
    def express_dependencies(self) -> typing.List["ExpressStack"]:
        '''The ExpressStack dependencies of the stack.'''
        return typing.cast(typing.List["ExpressStack"], jsii.invoke(self, "expressDependencies", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressStack).__jsii_proxy_class__ = lambda : _IExpressStackProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressStage")
class IExpressStage(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List["ExpressStack"]:
        '''The stacks in the stage.'''
        ...

    @stacks.setter
    def stacks(self, value: typing.List["ExpressStack"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="wave")
    def wave(self) -> "ExpressWave":
        '''The wave that the stage belongs to.'''
        ...

    @wave.setter
    def wave(self, value: "ExpressWave") -> None:
        ...


class _IExpressStageProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressStage"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbca333d17cf67f3ebc52a25d3e08fdc38766f46ae2bcaeff4c01e2edbbd5dce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List["ExpressStack"]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List["ExpressStack"], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List["ExpressStack"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28e54cfe0e98d05cd17fa7ea13e156a82d091df55640c4094698ec7e78ed884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wave")
    def wave(self) -> "ExpressWave":
        '''The wave that the stage belongs to.'''
        return typing.cast("ExpressWave", jsii.get(self, "wave"))

    @wave.setter
    def wave(self, value: "ExpressWave") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce620906fddfafba1ff8377098c5f9c35ada5694e2e5c6f9d15368e7d1d4c517)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wave", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressStage).__jsii_proxy_class__ = lambda : _IExpressStageProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressStageLegacy")
class IExpressStageLegacy(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''The stacks in the stage.'''
        ...

    @stacks.setter
    def stacks(self, value: typing.List[_aws_cdk_ceddda9d.Stack]) -> None:
        ...


class _IExpressStageLegacyProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressStageLegacy"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fdf2493af932e5d33d989d572f161b8c998d0298e6a848f0a7af5edeca7b052)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List[_aws_cdk_ceddda9d.Stack], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List[_aws_cdk_ceddda9d.Stack]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fffd047542b1ad122d53335fcab6ee350d782b3038d2efbf3f05152a18e8559c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressStageLegacy).__jsii_proxy_class__ = lambda : _IExpressStageLegacyProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressWave")
class IExpressWave(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        '''Separator between the wave, stage and stack ids that are concatenated to form the final stack id.'''
        ...

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List["ExpressStage"]:
        '''The ExpressStages in the wave.'''
        ...

    @stages.setter
    def stages(self, value: typing.List["ExpressStage"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        ...

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> "ExpressStage":
        '''Add an ExpressStage to the wave.

        :param id: The ExpressStage identifier.
        '''
        ...


class _IExpressWaveProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressWave"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8030e0d36f67ca6d88248c3aebc00cb88a9491700acbd6c7d3e4f5f06dcff718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        '''Separator between the wave, stage and stack ids that are concatenated to form the final stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2deeb751aa022d2277fc1af871b8a9419aaef6e789a22f82063f21230a6d03fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List["ExpressStage"]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List["ExpressStage"], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List["ExpressStage"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c33defa4497d6fd82c65487c1c51107af3c835ae4d7e1216f929dd314edaca26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae1159ae328148533b46258d902359880ce2c3976c0b7e6fc201ec69c017e429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> "ExpressStage":
        '''Add an ExpressStage to the wave.

        :param id: The ExpressStage identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0c0680f13cf234d76dc5ad77fd9b99005e303ff37a88d475016ab8e65495bbf)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast("ExpressStage", jsii.invoke(self, "addStage", [id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressWave).__jsii_proxy_class__ = lambda : _IExpressWaveProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressWaveLegacy")
class IExpressWaveLegacy(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IExpressStageLegacy]:
        '''The ExpressStages in the wave.'''
        ...

    @stages.setter
    def stages(self, value: typing.List[IExpressStageLegacy]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        ...

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IExpressWaveLegacyProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressWaveLegacy"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebcd93f3691046bc34c345a2d0c5fd123d149d6852a73f251c4a5caeef0b161a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IExpressStageLegacy]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List[IExpressStageLegacy], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List[IExpressStageLegacy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8bc3fea3bdc86a865ca6e2fcf12e74fb6190d42fb2b51e85f0be6ed539336b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__344bf89503483c6b8c5fcb2f9805b54198866f417be91cb3b67b3d568e301831)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressWaveLegacy).__jsii_proxy_class__ = lambda : _IExpressWaveLegacyProxy


class JsonPatch(metaclass=jsii.JSIIMeta, jsii_type="cdk-express-pipeline.JsonPatch"):
    '''Utility for applying RFC-6902 JSON-Patch to a document.

    Use the the ``JsonPatch.apply(doc, ...ops)`` function to apply a set of
    operations to a JSON document and return the result.

    Operations can be created using the factory methods ``JsonPatch.add()``,
    ``JsonPatch.remove()``, etc.

    const output = JsonPatch.apply(input,
    JsonPatch.replace('/world/hi/there', 'goodbye'),
    JsonPatch.add('/world/foo/', 'boom'),
    JsonPatch.remove('/hello'),
    );
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="add")
    @builtins.classmethod
    def add(cls, path: builtins.str, value: typing.Any) -> "Patch":
        '''Adds a value to an object or inserts it into an array.

        In the case of an
        array, the value is inserted before the given index. The - character can be
        used instead of an index to insert at the end of an array.

        :param path: -
        :param value: -

        Example::

            JsonPatch.add('/biscuits/1', { "name": "Ginger Nut" })
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e889f82d734296a9f0fc5b80c758f87482441af97e2f6881b76116f0713750d9)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Patch", jsii.sinvoke(cls, "add", [path, value]))

    @jsii.member(jsii_name="copy")
    @builtins.classmethod
    def copy(cls, from_: builtins.str, path: builtins.str) -> "Patch":
        '''Copies a value from one location to another within the JSON document.

        Both
        from and path are JSON Pointers.

        :param from_: -
        :param path: -

        Example::

            JsonPatch.copy('/biscuits/0', '/best_biscuit')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__813b3a258d86b3573be493d4a4f1937b1dce819225438e9c68f4aa38f4c2096e)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("Patch", jsii.sinvoke(cls, "copy", [from_, path]))

    @jsii.member(jsii_name="move")
    @builtins.classmethod
    def move(cls, from_: builtins.str, path: builtins.str) -> "Patch":
        '''Moves a value from one location to the other.

        Both from and path are JSON Pointers.

        :param from_: -
        :param path: -

        Example::

            JsonPatch.move('/biscuits', '/cookies')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34fb68007ee11bfe467e5b1f06ca9be4c08cea9c900d9ac6d607578c852e6e6f)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("Patch", jsii.sinvoke(cls, "move", [from_, path]))

    @jsii.member(jsii_name="remove")
    @builtins.classmethod
    def remove(cls, path: builtins.str) -> "Patch":
        '''Removes a value from an object or array.

        :param path: -

        Example::

            JsonPatch.remove('/biscuits/0')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc2803e74056c4dfba071084f24ac7dd182da2d46c8b000b79ce5f02cee5705)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("Patch", jsii.sinvoke(cls, "remove", [path]))

    @jsii.member(jsii_name="replace")
    @builtins.classmethod
    def replace(cls, path: builtins.str, value: typing.Any) -> "Patch":
        '''Replaces a value.

        Equivalent to a “remove” followed by an “add”.

        :param path: -
        :param value: -

        Example::

            JsonPatch.replace('/biscuits/0/name', 'Chocolate Digestive')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ed71656eb191c64ead4dc6b43291a424f80bceabb5b77fcb37d4c4b8c97936)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Patch", jsii.sinvoke(cls, "replace", [path, value]))

    @jsii.member(jsii_name="test")
    @builtins.classmethod
    def test(cls, path: builtins.str, value: typing.Any) -> "Patch":
        '''Tests that the specified value is set in the document.

        If the test fails,
        then the patch as a whole should not apply.

        :param path: -
        :param value: -

        Example::

            JsonPatch.test('/best_biscuit/name', 'Choco Leibniz')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c17fdce4c05352755c8a52f7d062025f2bb0826dbd449a0d8992c92ca5e51b)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Patch", jsii.sinvoke(cls, "test", [path, value]))

    @jsii.member(jsii_name="patch")
    def patch(self, document: typing.Any, *ops: "Patch") -> typing.Any:
        '''Applies a set of JSON-Patch (RFC-6902) operations to ``document`` and returns the result.

        :param document: The document to patch.
        :param ops: The operations to apply.

        :return: The result document
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebb90fc798a7a245a98f9531a4a6f7ca5fe9f20211bc9558257b92b2ea04b634)
            check_type(argname="argument document", value=document, expected_type=type_hints["document"])
            check_type(argname="argument ops", value=ops, expected_type=typing.Tuple[type_hints["ops"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(typing.Any, jsii.invoke(self, "patch", [document, *ops]))


@jsii.data_type(
    jsii_type="cdk-express-pipeline.MermaidDiagramOutput",
    jsii_struct_bases=[],
    name_mapping={"file_name": "fileName", "path": "path"},
)
class MermaidDiagramOutput:
    def __init__(
        self,
        *,
        file_name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_name: Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.
        :param path: The path where the Mermaid diagram will be saved. If not provided defaults to root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caca80227433ac13947de383baf8167a009b64337177ebceb2f23878fe124840)
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if file_name is not None:
            self._values["file_name"] = file_name
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def file_name(self) -> typing.Optional[builtins.str]:
        '''Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.'''
        result = self._values.get("file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path where the Mermaid diagram will be saved.

        If not provided defaults to root
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MermaidDiagramOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.Patch",
    jsii_struct_bases=[],
    name_mapping={"op": "op", "path": "path", "from_": "from", "value": "value"},
)
class Patch:
    def __init__(
        self,
        *,
        op: builtins.str,
        path: builtins.str,
        from_: typing.Optional[builtins.str] = None,
        value: typing.Any = None,
    ) -> None:
        '''
        :param op: 
        :param path: 
        :param from_: 
        :param value: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe7f0ac4df8801b436758db5c210377cc3da157971ec27286e0f9c78ea316ab)
            check_type(argname="argument op", value=op, expected_type=type_hints["op"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "op": op,
            "path": path,
        }
        if from_ is not None:
            self._values["from_"] = from_
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def op(self) -> builtins.str:
        result = self._values.get("op")
        assert result is not None, "Required property 'op' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Any:
        result = self._values.get("value")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Patch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.SynthWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={"build_config": "buildConfig", "commands": "commands"},
)
class SynthWorkflowConfig:
    def __init__(
        self,
        *,
        build_config: typing.Union[BuildConfig, typing.Dict[builtins.str, typing.Any]],
        commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''
        :param build_config: Configuration for the build workflow.
        :param commands: Commands to run for synthesis.
        '''
        if isinstance(build_config, dict):
            build_config = BuildConfig(**build_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04546b59d0caef85d626030a6e0a441f23d5fb05cabb5e49cfda6fbf80c226ad)
            check_type(argname="argument build_config", value=build_config, expected_type=type_hints["build_config"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "build_config": build_config,
            "commands": commands,
        }

    @builtins.property
    def build_config(self) -> BuildConfig:
        '''Configuration for the build workflow.'''
        result = self._values.get("build_config")
        assert result is not None, "Required property 'build_config' is missing"
        return typing.cast(BuildConfig, result)

    @builtins.property
    def commands(self) -> typing.List[typing.Mapping[builtins.str, builtins.str]]:
        '''Commands to run for synthesis.'''
        result = self._values.get("commands")
        assert result is not None, "Required property 'commands' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SynthWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowLocation",
    jsii_struct_bases=[],
    name_mapping={"path": "path"},
)
class WorkflowLocation:
    def __init__(self, *, path: builtins.str) -> None:
        '''
        :param path: The path of the workflow to call before synthesis.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__201aead098a7134c6fd7dcb35cef32abfc1e2be9abfbca91e28a062d7541627e)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }

    @builtins.property
    def path(self) -> builtins.str:
        '''The path of the workflow to call before synthesis.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowTriggers",
    jsii_struct_bases=[],
    name_mapping={"pull_request": "pullRequest", "push": "push"},
)
class WorkflowTriggers:
    def __init__(
        self,
        *,
        pull_request: typing.Optional[typing.Union["WorkflowTriggersPullRequests", typing.Dict[builtins.str, typing.Any]]] = None,
        push: typing.Optional[typing.Union["WorkflowTriggersPush", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param pull_request: 
        :param push: 
        '''
        if isinstance(pull_request, dict):
            pull_request = WorkflowTriggersPullRequests(**pull_request)
        if isinstance(push, dict):
            push = WorkflowTriggersPush(**push)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a79785af7f44c5c832451175f3341cd5538fd42ec6de66f4f5750cdc30e4bc80)
            check_type(argname="argument pull_request", value=pull_request, expected_type=type_hints["pull_request"])
            check_type(argname="argument push", value=push, expected_type=type_hints["push"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pull_request is not None:
            self._values["pull_request"] = pull_request
        if push is not None:
            self._values["push"] = push

    @builtins.property
    def pull_request(self) -> typing.Optional["WorkflowTriggersPullRequests"]:
        result = self._values.get("pull_request")
        return typing.cast(typing.Optional["WorkflowTriggersPullRequests"], result)

    @builtins.property
    def push(self) -> typing.Optional["WorkflowTriggersPush"]:
        result = self._values.get("push")
        return typing.cast(typing.Optional["WorkflowTriggersPush"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowTriggers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowTriggersPullRequests",
    jsii_struct_bases=[],
    name_mapping={"branches": "branches"},
)
class WorkflowTriggersPullRequests:
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param branches: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26b6341660e3e70454386c5ce9a951fa0c7e59e59ade150cb48489e1eb584a4a)
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowTriggersPullRequests(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowTriggersPush",
    jsii_struct_bases=[],
    name_mapping={"branches": "branches"},
)
class WorkflowTriggersPush:
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param branches: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcbae0f217bbe05c16c45d14f261a43d5190abbe7a105bc981ed007bdc9774e8)
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowTriggersPush(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IExpressStack)
class ExpressStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressStack",
):
    '''A CDK Express Pipeline Stack that belongs to an ExpressStage.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        stage: "ExpressStage",
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressStack class.

        :param scope: The parent of this stack, usually an ``App`` but could be any construct.
        :param id: The stack identifier which will be used to construct the final id as a combination of the wave, stage and stack id.
        :param stage: The stage that the stack belongs to.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15a9a33311b5aa41f122528e87925d8662e0815e5f09d7988e374cfdea050a91)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        stack_props = _aws_cdk_ceddda9d.StackProps(
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, stage, stack_props])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(
        self,
        target: _aws_cdk_ceddda9d.Stack,
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Use ``addDependency`` for dependencies between stacks in an ExpressStage.

        Otherwise, use ``addExpressDependency``
        to construct the Pipeline of stacks between Waves and Stages.

        :param target: -
        :param reason: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc587ab6bc13caffa524be9c0320a53ca9f80c4fc7c757ceffb0008ac347573)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "addDependency", [target, reason]))

    @jsii.member(jsii_name="addExpressDependency")
    def add_express_dependency(
        self,
        target: "ExpressStack",
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Only use to create dependencies between Stacks in Waves and Stages for building the Pipeline, where having cyclic dependencies is not possible.

        If the ``addExpressDependency`` is used outside the Pipeline construction,
        it will not be safe. Use ``addDependency`` to create stack dependency within the same Stage.

        :param target: -
        :param reason: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__879d590ae5362b889422ff44e98e8fdc081b30ab75c3f73bb791f1e59cffa2be)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "addExpressDependency", [target, reason]))

    @jsii.member(jsii_name="expressDependencies")
    def express_dependencies(self) -> typing.List["ExpressStack"]:
        '''The ExpressStack dependencies of the stack.'''
        return typing.cast(typing.List["ExpressStack"], jsii.invoke(self, "expressDependencies", []))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stack identifier which is a combination of the wave, stage and stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a767759dfa5395be6ecc01266961a9c2cc361036411cc35372ee6e11029546c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "ExpressStage":
        '''The stage that the stack belongs to.'''
        return typing.cast("ExpressStage", jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: "ExpressStage") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e958c9ef72a2d0c3aaf0f9f1a60e0b6201b1633c81a640e71ca2bbe7f16654f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stage", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressStage)
class ExpressStage(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressStage",
):
    '''A CDK Express Pipeline Stage that belongs to an ExpressWave.'''

    def __init__(
        self,
        id: builtins.str,
        wave: "ExpressWave",
        stacks: typing.Optional[typing.Sequence[ExpressStack]] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressStage class.

        :param id: The stage identifier.
        :param wave: The wave that the stage belongs to.
        :param stacks: The ExpressStacks in the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__245ca2826c9b997f2790635ddcfbef04762bc8a2022332e01afc13b949cf70a4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument wave", value=wave, expected_type=type_hints["wave"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
        jsii.create(self.__class__, self, [id, wave, stacks])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85b05051a77c643d3ed8a27735fdb1c5115fb33b71da08b5137bf934b65ebe1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[ExpressStack]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List[ExpressStack], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List[ExpressStack]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e05ff1a3d72f333ec26c5d8730168d1024b024fab396ec5decbb16ef55ecdd68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wave")
    def wave(self) -> "ExpressWave":
        '''The wave that the stage belongs to.'''
        return typing.cast("ExpressWave", jsii.get(self, "wave"))

    @wave.setter
    def wave(self, value: "ExpressWave") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7663ce522608a1a19b5783485ae032e41251aa3bcaf50c25d7f5601587b2c86d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wave", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressStageLegacy)
class ExpressStageLegacy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressStageLegacy",
):
    '''A stage that holds stacks.'''

    def __init__(
        self,
        id: builtins.str,
        stacks: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Stack]] = None,
    ) -> None:
        '''
        :param id: The stage identifier.
        :param stacks: The stacks in the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6fafe372848c826b5095466be599af161c0ef85262c4461c5b15946d416d8a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
        jsii.create(self.__class__, self, [id, stacks])

    @jsii.member(jsii_name="addStack")
    def add_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> _aws_cdk_ceddda9d.Stack:
        '''Add a stack to the stage.

        :param stack: The stack to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c894af91effb498dcc85f4ce0d7c1ea7cc88b0e9ce46cd0afbe5faba127dcd9a)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.invoke(self, "addStack", [stack]))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf3eb70b31883db55c7481c3af5635274ea0b531152ffc77fbe240d4cf471109)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List[_aws_cdk_ceddda9d.Stack], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List[_aws_cdk_ceddda9d.Stack]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4560b751b8175d35b73d56b09336c93f3b65806421e5136ac4b9479b20d4fded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressWave)
class ExpressWave(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressWave",
):
    '''A CDK Express Pipeline Wave that contains ExpressStages.'''

    def __init__(
        self,
        id: builtins.str,
        separator: typing.Optional[builtins.str] = None,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressWave class.

        :param id: The wave identifier.
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: '_'.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2d5f3923a6b2ec80e7126dcf3fee4db4c4302e23528b8f1a6b804dbcd52b1bd)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        jsii.create(self.__class__, self, [id, separator, sequential_stages])

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> ExpressStage:
        '''Add an ExpressStage to the wave.

        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2483221f4b80a77d7fb5425bb01e862bb0faa20975c01571285867e7ebac289a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(ExpressStage, jsii.invoke(self, "addStage", [id]))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26db5d9a6d2445284b7c8d5a9e1f799dd10cda56d628bfa4a2a86e736e5b5f5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        '''Separator between the wave, stage and stack ids that are concatenated to form the final stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d5854ca09bf38f246ea0ad1547c742b4d85ac21de4ecdd25f7fde0b74cee485)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[ExpressStage]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List[ExpressStage], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List[ExpressStage]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__397c6edf3478bfddcdbbc65faf7cf101e55552e8c9866bcc82db7287aa7e3727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.'''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faca2817a2891ad9c62ca6c4294f0d2c4e09a89632dd03f8a2770e04ce81559d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressWaveLegacy)
class ExpressWaveLegacy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressWaveLegacy",
):
    '''A CDK Express Pipeline Legacy Wave that contains Legacy Stages.'''

    def __init__(
        self,
        id: builtins.str,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressWaveLegacy class.

        :param id: The wave identifier.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0081ffdae64cce4db9c69087d8b66bb2d1dadbd8afbb7316e0b3bf8c9efbb03)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        jsii.create(self.__class__, self, [id, sequential_stages])

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> ExpressStageLegacy:
        '''Add a stage to the wave.

        :param id: The stage identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a5c818dec4565e93efada7052a99392254569073240c5aa57b5dd41234ce08a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(ExpressStageLegacy, jsii.invoke(self, "addStage", [id]))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77354438e2a204945817e7e42750078579440a11efd1bc3059037d1a389dbf4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IExpressStageLegacy]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List[IExpressStageLegacy], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List[IExpressStageLegacy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e46f4bd7d8ca47367b9b065564e04c58819d2f62dc94c8e21d96cab827ad27cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.'''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfb40afb352b1f780efc7514fb88ca08543b06d925f6ba10e33a7afa07d236db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "BuildConfig",
    "CdkExpressPipeline",
    "CdkExpressPipelineAssembly",
    "CdkExpressPipelineAssemblyStack",
    "CdkExpressPipelineAssemblyStage",
    "CdkExpressPipelineAssemblyWave",
    "CdkExpressPipelineLegacy",
    "CdkExpressPipelineProps",
    "DeployWorkflowConfig",
    "DiffWorkflowConfig",
    "ExpressStack",
    "ExpressStage",
    "ExpressStageLegacy",
    "ExpressWave",
    "ExpressWaveLegacy",
    "ExpressWaveProps",
    "GitHubWorkflowConfig",
    "GithubWorkflow",
    "GithubWorkflowFile",
    "IExpressStack",
    "IExpressStage",
    "IExpressStageLegacy",
    "IExpressWave",
    "IExpressWaveLegacy",
    "JsonPatch",
    "MermaidDiagramOutput",
    "Patch",
    "SynthWorkflowConfig",
    "WorkflowLocation",
    "WorkflowTriggers",
    "WorkflowTriggersPullRequests",
    "WorkflowTriggersPush",
]

publication.publish()

def _typecheckingstub__176a33dbfec3fbf84c7f09cd7d5fa47dc7938b65faf1fefd2a2e277c8b10b538(
    *,
    type: builtins.str,
    workflow: typing.Optional[typing.Union[WorkflowLocation, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d5a812c29abca46e9446db3e0acfaedb3fb0f70a5ccbc26b8b26b62c731b30(
    id: builtins.str,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e284e6bc2289754ab5a16d412952ff0c2b3c0f4ae78655914206f911311579c0(
    git_hub_workflow_config: typing.Union[GitHubWorkflowConfig, typing.Dict[builtins.str, typing.Any]],
    save_to_files: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48596730e21a3fe0e78a5e73d024ad054e1679fbe0d63f873eb81c728a6fc0d6(
    waves: typing.Sequence[IExpressWave],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18d77fb9496cb5fdeabb0fe5a14c3dcd08b7a4747694ac0a799b01dfa105a34(
    waves: typing.Sequence[IExpressWave],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a545be0c7f0244a8cedbc9796c6c38f57f873c3c1ba9bb23a76f5d8f63bfafa(
    workflows: typing.Sequence[typing.Union[GithubWorkflowFile, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddf3f54429b9cebdd63080df8e42a8f0bee80ea5889f7848d8110f99befcf433(
    waves: typing.Optional[typing.Sequence[IExpressWave]] = None,
    print: typing.Optional[builtins.bool] = None,
    *,
    file_name: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__973836022e8419d6996db18e9376d9e9f363b6b8746e80a5208b60649e5e0548(
    *,
    waves: typing.Sequence[typing.Union[CdkExpressPipelineAssemblyWave, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8cc27cce2b3b402590f9ed6714e538ea3ce9457c7f64fd4299544f1e4ca45e6(
    *,
    stack_id: builtins.str,
    stack_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07fd5e056e014f371264dd85f08c120ecdf36ed4b5347f07bbc10a6c63ce1294(
    *,
    stacks: typing.Sequence[typing.Union[CdkExpressPipelineAssemblyStack, typing.Dict[builtins.str, typing.Any]]],
    stage_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d56a7bedc197325c6dc7f8604d76dded58fc174561a83fba34b02d40e8ba18c0(
    *,
    stages: typing.Sequence[typing.Union[CdkExpressPipelineAssemblyStage, typing.Dict[builtins.str, typing.Any]]],
    wave_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e78d8fa8554a29ac59173413b98062741ae83aeb4754f02a80c85c27e16d8ce(
    waves: typing.Optional[typing.Sequence[IExpressWaveLegacy]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58733341409ff8a6c60fbf06de891a31f81f41cf55e7503aaa0238ee46ff5166(
    id: builtins.str,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1ef4d18ff1ca1a7788d1801361a996c26480f2387d3a28be69812108f489380(
    waves: typing.Sequence[IExpressWaveLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d22fe922729d650ca61abf0f4568bb8cbafe791434481f3e0cce74d098f785e(
    waves: typing.Sequence[IExpressWaveLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7d8bd5a65c1437ed17046edfb50f14e1f2b8f73c9db08927132a10f37d409d(
    waves: typing.Optional[typing.Sequence[IExpressWaveLegacy]] = None,
    print: typing.Optional[builtins.bool] = None,
    *,
    file_name: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54082bd27a8ceffd74f1b6a0cb05b3bbcf4ffa9ada94c72e52e645687ad4ad5b(
    value: typing.List[IExpressWaveLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc99a79d5da23f439f19b4717a315983fa455ec2ae7d0300ac3d7381d5892205(
    *,
    separator: typing.Optional[builtins.str] = None,
    waves: typing.Optional[typing.Sequence[ExpressWave]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__064ff6a399a517de1d9d8831492460b92378a4013ef6125878a1c1553dab6e74(
    *,
    assume_region: builtins.str,
    assume_role_arn: builtins.str,
    commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
    on: typing.Union[WorkflowTriggers, typing.Dict[builtins.str, typing.Any]],
    stack_selector: builtins.str,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd8d22f0c989f84b5e91067c258f24562fc4d3b5c471e9302c3fd36c7c66492(
    *,
    assume_region: builtins.str,
    assume_role_arn: builtins.str,
    commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
    on: typing.Union[WorkflowTriggers, typing.Dict[builtins.str, typing.Any]],
    stack_selector: builtins.str,
    id: typing.Optional[builtins.str] = None,
    write_as_comment: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d91dc79595e990d6da1a185afde4e65465da1f5dc12abd5220e16803db5481a2(
    *,
    id: builtins.str,
    separator: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a08064d282d091b65891b01b014a0a8a260163ad7f73ec21450a321e2a8b285(
    *,
    deploy: typing.Sequence[typing.Union[DeployWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
    diff: typing.Sequence[typing.Union[DiffWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
    synth: typing.Union[SynthWorkflowConfig, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3923cfcb617f1c1f17d022bb3436263a7c98cdcb87f419363015fb8520b511d6(
    json: typing.Mapping[typing.Any, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49ff91c791fec0d9e19de3f5d1c58b5d0e0e2045aeed51944132881cecfefa62(
    *ops: Patch,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22f05ed853a2e74dee0193a62770b3ae51bb4f3b85b9efbd5d32135798819a32(
    value: typing.Mapping[typing.Any, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__038bf0270c6ca55596a013a4a31894e79899942811087d804768f4ed4ba3d4e2(
    *,
    content: GithubWorkflow,
    file_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76bd73c874b49b4683b044d917cc6800ed471f2b41d3164b902c206407432cbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61a812768afc62205a9db0f1f9d01095658800d0cc43087913d4c1645cde7bdd(
    value: ExpressStage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a14719acbf68f0fd518f950b2dd5d2922f8e4c9c9273c2f85d05589af97f191(
    target: ExpressStack,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbca333d17cf67f3ebc52a25d3e08fdc38766f46ae2bcaeff4c01e2edbbd5dce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28e54cfe0e98d05cd17fa7ea13e156a82d091df55640c4094698ec7e78ed884(
    value: typing.List[ExpressStack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce620906fddfafba1ff8377098c5f9c35ada5694e2e5c6f9d15368e7d1d4c517(
    value: ExpressWave,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdf2493af932e5d33d989d572f161b8c998d0298e6a848f0a7af5edeca7b052(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffd047542b1ad122d53335fcab6ee350d782b3038d2efbf3f05152a18e8559c(
    value: typing.List[_aws_cdk_ceddda9d.Stack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8030e0d36f67ca6d88248c3aebc00cb88a9491700acbd6c7d3e4f5f06dcff718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2deeb751aa022d2277fc1af871b8a9419aaef6e789a22f82063f21230a6d03fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c33defa4497d6fd82c65487c1c51107af3c835ae4d7e1216f929dd314edaca26(
    value: typing.List[ExpressStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1159ae328148533b46258d902359880ce2c3976c0b7e6fc201ec69c017e429(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0c0680f13cf234d76dc5ad77fd9b99005e303ff37a88d475016ab8e65495bbf(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcd93f3691046bc34c345a2d0c5fd123d149d6852a73f251c4a5caeef0b161a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8bc3fea3bdc86a865ca6e2fcf12e74fb6190d42fb2b51e85f0be6ed539336b3(
    value: typing.List[IExpressStageLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__344bf89503483c6b8c5fcb2f9805b54198866f417be91cb3b67b3d568e301831(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e889f82d734296a9f0fc5b80c758f87482441af97e2f6881b76116f0713750d9(
    path: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__813b3a258d86b3573be493d4a4f1937b1dce819225438e9c68f4aa38f4c2096e(
    from_: builtins.str,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34fb68007ee11bfe467e5b1f06ca9be4c08cea9c900d9ac6d607578c852e6e6f(
    from_: builtins.str,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc2803e74056c4dfba071084f24ac7dd182da2d46c8b000b79ce5f02cee5705(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ed71656eb191c64ead4dc6b43291a424f80bceabb5b77fcb37d4c4b8c97936(
    path: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c17fdce4c05352755c8a52f7d062025f2bb0826dbd449a0d8992c92ca5e51b(
    path: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebb90fc798a7a245a98f9531a4a6f7ca5fe9f20211bc9558257b92b2ea04b634(
    document: typing.Any,
    *ops: Patch,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caca80227433ac13947de383baf8167a009b64337177ebceb2f23878fe124840(
    *,
    file_name: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe7f0ac4df8801b436758db5c210377cc3da157971ec27286e0f9c78ea316ab(
    *,
    op: builtins.str,
    path: builtins.str,
    from_: typing.Optional[builtins.str] = None,
    value: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04546b59d0caef85d626030a6e0a441f23d5fb05cabb5e49cfda6fbf80c226ad(
    *,
    build_config: typing.Union[BuildConfig, typing.Dict[builtins.str, typing.Any]],
    commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__201aead098a7134c6fd7dcb35cef32abfc1e2be9abfbca91e28a062d7541627e(
    *,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a79785af7f44c5c832451175f3341cd5538fd42ec6de66f4f5750cdc30e4bc80(
    *,
    pull_request: typing.Optional[typing.Union[WorkflowTriggersPullRequests, typing.Dict[builtins.str, typing.Any]]] = None,
    push: typing.Optional[typing.Union[WorkflowTriggersPush, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26b6341660e3e70454386c5ce9a951fa0c7e59e59ade150cb48489e1eb584a4a(
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcbae0f217bbe05c16c45d14f261a43d5190abbe7a105bc981ed007bdc9774e8(
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15a9a33311b5aa41f122528e87925d8662e0815e5f09d7988e374cfdea050a91(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    stage: ExpressStage,
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc587ab6bc13caffa524be9c0320a53ca9f80c4fc7c757ceffb0008ac347573(
    target: _aws_cdk_ceddda9d.Stack,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879d590ae5362b889422ff44e98e8fdc081b30ab75c3f73bb791f1e59cffa2be(
    target: ExpressStack,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a767759dfa5395be6ecc01266961a9c2cc361036411cc35372ee6e11029546c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e958c9ef72a2d0c3aaf0f9f1a60e0b6201b1633c81a640e71ca2bbe7f16654f(
    value: ExpressStage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__245ca2826c9b997f2790635ddcfbef04762bc8a2022332e01afc13b949cf70a4(
    id: builtins.str,
    wave: ExpressWave,
    stacks: typing.Optional[typing.Sequence[ExpressStack]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85b05051a77c643d3ed8a27735fdb1c5115fb33b71da08b5137bf934b65ebe1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e05ff1a3d72f333ec26c5d8730168d1024b024fab396ec5decbb16ef55ecdd68(
    value: typing.List[ExpressStack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7663ce522608a1a19b5783485ae032e41251aa3bcaf50c25d7f5601587b2c86d(
    value: ExpressWave,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef6fafe372848c826b5095466be599af161c0ef85262c4461c5b15946d416d8a(
    id: builtins.str,
    stacks: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Stack]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c894af91effb498dcc85f4ce0d7c1ea7cc88b0e9ce46cd0afbe5faba127dcd9a(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3eb70b31883db55c7481c3af5635274ea0b531152ffc77fbe240d4cf471109(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4560b751b8175d35b73d56b09336c93f3b65806421e5136ac4b9479b20d4fded(
    value: typing.List[_aws_cdk_ceddda9d.Stack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2d5f3923a6b2ec80e7126dcf3fee4db4c4302e23528b8f1a6b804dbcd52b1bd(
    id: builtins.str,
    separator: typing.Optional[builtins.str] = None,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2483221f4b80a77d7fb5425bb01e862bb0faa20975c01571285867e7ebac289a(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26db5d9a6d2445284b7c8d5a9e1f799dd10cda56d628bfa4a2a86e736e5b5f5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d5854ca09bf38f246ea0ad1547c742b4d85ac21de4ecdd25f7fde0b74cee485(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__397c6edf3478bfddcdbbc65faf7cf101e55552e8c9866bcc82db7287aa7e3727(
    value: typing.List[ExpressStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faca2817a2891ad9c62ca6c4294f0d2c4e09a89632dd03f8a2770e04ce81559d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0081ffdae64cce4db9c69087d8b66bb2d1dadbd8afbb7316e0b3bf8c9efbb03(
    id: builtins.str,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a5c818dec4565e93efada7052a99392254569073240c5aa57b5dd41234ce08a(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77354438e2a204945817e7e42750078579440a11efd1bc3059037d1a389dbf4b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e46f4bd7d8ca47367b9b065564e04c58819d2f62dc94c8e21d96cab827ad27cc(
    value: typing.List[IExpressStageLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfb40afb352b1f780efc7514fb88ca08543b06d925f6ba10e33a7afa07d236db(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass
