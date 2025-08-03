"""
This module defines simplified data models tailored for use in the MCP Server.

These models are derived from the SDK models but include only the essential fields.
The purpose of this is to reduce the amount of data being sent to the LLM's,
which helps prevent unnecessary context noise and reduces the chances of hallucinations,
especially when working with large payloads.

By stripping down the models to their most relevant attributes, we ensure
leaner communication with the LLM and improve the quality and reliability
of its responses.
"""

from typing import List, Optional, cast

from devopness.base import DevopnessBaseModel
from devopness.models import (
    Action,
    ActionDeploymentData,
    ActionRelation,
    ActionRelationShallow,
    ActionStatus,
    ActionStep,
    ActionTarget,
    ActionTargetCredentialData,
    ActionTargetNetworkData,
    Application,
    ApplicationRelation,
    CredentialRelation,
    Daemon,
    DaemonRelation,
    EnvironmentRelation,
    Pipeline,
    PipelineRelation,
    PipelineStepRunnerName,
    ProjectRelation,
    Server,
    ServerRelation,
    ServerStatus,
    Service,
    ServiceRelation,
    SshKey,
    SshKeyRelation,
    SslCertificate,
    SslCertificateRelation,
    Step,
    Variable,
    VariableRelation,
    VirtualHost,
    VirtualHostRelation,
)

from .types import TypeExtraData


class ProjectSummary(DevopnessBaseModel):
    id: int
    name: str
    url_web_permalink: str

    @classmethod
    def from_sdk_model(
        cls,
        data: ProjectRelation,
    ) -> "ProjectSummary":
        return cls(
            id=data.id,
            name=data.name,
            url_web_permalink=f"https://app.devopness.com/projects/{data.id}",
        )


class EnvironmentSummary(DevopnessBaseModel):
    id: int
    name: str
    description: Optional[str]
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: EnvironmentRelation,
        extra_data: TypeExtraData = None,
    ) -> "EnvironmentSummary":
        return cls(
            id=data.id,
            name=data.name,
            description=data.description,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class ActionStepSummary(DevopnessBaseModel):
    id: int
    name: Optional[str]
    status: ActionStatus
    action_id: int
    action_target_id: int
    action_target_step_order: int

    @classmethod
    def from_sdk_model(
        cls,
        data: ActionStep,
    ) -> "ActionStepSummary | None":
        return cls(
            id=data.id,
            name=data.name,
            status=data.status,
            action_id=data.action_id,
            action_target_id=data.action_target_id,
            action_target_step_order=data.order,
        )


class ActionTargetSummary(DevopnessBaseModel):
    id: int
    target_id: int
    target_type: str
    target_name: Optional[str]
    steps: Optional[List[Optional[ActionStepSummary]]]
    steps_count: Optional[int]

    @classmethod
    def from_sdk_model(
        cls,
        data: ActionTarget,
    ) -> "ActionTargetSummary":
        return cls(
            id=data.id,
            target_id=data.resource_id,
            target_type=data.resource_type,
            target_name=(
                None
                if data.resource_data is None
                else data.resource_data.name
                if isinstance(
                    data.resource_data,
                    (ActionTargetCredentialData, ActionTargetNetworkData),
                )
                else data.resource_data.hostname
            ),
            steps=[
                ActionStepSummary.from_sdk_model(step)  #
                if step is not None
                else None
                for step in data.steps or []
            ],
            steps_count=data.total_steps,
        )


class ActionSummary(DevopnessBaseModel):
    id: int
    type: str
    status: str
    status_reason_code: str
    data: Optional[ActionDeploymentData]
    resource_id: Optional[int]
    resource_type: Optional[str]
    resource_name: Optional[str]
    resource_pipeline_id: Optional[int]
    targets: List[ActionTargetSummary]
    environment_id: Optional[int]
    project_id: Optional[int]
    url_web_permalink: str

    @classmethod
    def from_sdk_model(
        cls,
        data: Action | ActionRelation | ActionRelationShallow,
    ) -> "ActionSummary":
        return cls(
            id=data.id,
            type=data.type_human_readable,
            status=data.status_human_readable,
            status_reason_code=data.status_reason_human_readable,
            data=(
                data.action_data  # ActionRelation(Shallow) does not include action_data
                if isinstance(data, (Action))
                else None
            ),
            resource_id=(
                data.resource.id  # ActionRelationShallow does not include `resource`
                if isinstance(data, (Action, ActionRelation))
                else None
            ),
            resource_type=(
                data.resource.type
                # ActionRelationShallow does not include `resource`
                if isinstance(data, (Action, ActionRelation))
                else None
            ),
            resource_name=(
                getattr(data.resource.data, "name", None)
                # ActionRelationShallow does not include `resource`
                if isinstance(data, (Action, ActionRelation))
                else None
            ),
            resource_pipeline_id=(
                data.pipeline_id
                # ActionRelation(Shallow) does not include pipeline_id
                if isinstance(data, (Action))
                else None
            ),
            targets=[
                ActionTargetSummary.from_sdk_model(target)
                for target in data.targets or []
            ],
            environment_id=(
                data.environment.id
                # ActionRelation(Shallow) does not include `environment`
                if isinstance(data, (Action)) and data.environment is not None
                else None
            ),
            project_id=(
                data.project.id
                # ActionRelation(Shallow) does not include `project`
                if isinstance(data, (Action)) and data.project is not None
                else None
            ),
            url_web_permalink=data.url_web_permalink,
        )


class PipelineStepSummary(DevopnessBaseModel):
    id: int
    name: Optional[str]
    command: str
    runner: PipelineStepRunnerName
    trigger_order: int
    is_auto_generated: bool
    url_web_permalink: Optional[str]

    @classmethod
    def from_sdk_model(
        cls,
        data: Step,
        extra_data: TypeExtraData = None,
    ) -> "PipelineStepSummary":
        return cls(
            id=data.id,
            name=data.name,
            command=data.command,
            runner=data.runner,
            trigger_order=data.trigger_order,
            is_auto_generated=data.is_auto_generated,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class PipelineSummary(DevopnessBaseModel):
    id: int
    name: str
    operation: str
    steps: Optional[list[PipelineStepSummary]] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: Pipeline | PipelineRelation,
        extra_data: TypeExtraData = None,
    ) -> "PipelineSummary":
        return cls(
            id=data.id,
            name=data.name,
            operation=data.operation,
            steps=[
                PipelineStepSummary.from_sdk_model(step)
                for step in getattr(data, "steps", [])
            ],
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class SSHKeySummary(DevopnessBaseModel):
    id: int
    name: str
    fingerprint: str
    last_action: Optional[ActionSummary] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: SshKey | SshKeyRelation,
        extra_data: TypeExtraData = None,
    ) -> "SSHKeySummary":
        return cls(
            id=data.id,
            name=data.name,
            fingerprint=data.fingerprint,
            last_action=(
                ActionSummary.from_sdk_model(data.last_action)
                if data.last_action is not None
                else None
            ),
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class CredentialSummary(DevopnessBaseModel):
    id: int
    name: str
    provider: str
    provider_type: str
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: CredentialRelation,
        extra_data: TypeExtraData = None,
    ) -> "CredentialSummary":
        return cls(
            id=data.id,
            name=data.name,
            provider=data.provider.code_human_readable,
            provider_type=data.provider_type_human_readable,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class ServiceSummary(DevopnessBaseModel):
    id: int
    name: str
    type: str
    version: str
    last_action: Optional[ActionSummary] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: Service | ServiceRelation,
        extra_data: TypeExtraData = None,
    ) -> "ServiceSummary":
        return cls(
            id=data.id,
            name=data.name,
            type=data.type,
            version=cast(str, data.version),
            last_action=(
                ActionSummary.from_sdk_model(data.last_action)
                if data.last_action is not None
                else None
            ),
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class ApplicationSummary(DevopnessBaseModel):
    id: int
    name: str
    repository: str
    programming_language: str
    programming_language_version: str
    programming_language_framework: str
    root_directory: Optional[str] = None
    install_dependencies_command: Optional[str] = None
    build_command: Optional[str] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: Application | ApplicationRelation,
        extra_data: TypeExtraData = None,
    ) -> "ApplicationSummary":
        return cls(
            id=data.id,
            name=data.name,
            repository=data.repository,
            programming_language=data.programming_language,
            programming_language_version=data.engine_version,
            programming_language_framework=data.framework,
            root_directory=data.root_directory,
            install_dependencies_command=data.install_dependencies_command,
            build_command=data.build_command,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class ServerSummary(DevopnessBaseModel):
    id: int
    name: str
    status: ServerStatus
    ip_address: Optional[str] = None
    ssh_port: int
    provider_code: str
    provider_region: Optional[str] = None
    instance_type: Optional[str] = None
    last_action: Optional[ActionSummary] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: Server | ServerRelation,
        extra_data: TypeExtraData = None,
    ) -> "ServerSummary":
        return cls(
            id=data.id,
            name=data.name,
            status=data.status,
            ip_address=data.ip_address,
            ssh_port=data.ssh_port,
            provider_code=data.provider_name,
            provider_region=(
                data.region
                if isinstance(data, ServerRelation)
                else getattr(
                    data.provision_input.settings,
                    "region",
                    None,
                )
            ),
            instance_type=extra_data.server_instance_type if extra_data else None,
            last_action=(
                ActionSummary.from_sdk_model(data.last_action)
                if data.last_action is not None
                else None
            ),
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class DaemonSummary(DevopnessBaseModel):
    id: int
    name: str
    command: str
    run_as_user: str
    process_count: int
    working_directory: Optional[str]
    application_id: Optional[int] = None
    application_name: Optional[str] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: Daemon | DaemonRelation,
        extra_data: TypeExtraData = None,
    ) -> "DaemonSummary":
        return cls(
            id=data.id,
            name=data.name,
            command=data.command,
            run_as_user=data.run_as_user,
            process_count=data.process_count,
            working_directory=data.working_directory,
            application_id=data.application.id
            if data.application is not None
            else None,
            application_name=data.application.name
            if data.application is not None
            else None,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class SSLCertificateSummary(DevopnessBaseModel):
    id: int
    name: str
    active: bool
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: SslCertificate | SslCertificateRelation,
        extra_data: TypeExtraData = None,
    ) -> "SSLCertificateSummary":
        return cls(
            id=data.id,
            name=data.name,
            active=data.active,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class VirtualHostSummary(DevopnessBaseModel):
    id: int
    name: str
    root_directory: Optional[str]
    ssl_certificate_id: Optional[int] = None
    application_id: Optional[int] = None
    application_name: Optional[str] = None
    application_listen_address: Optional[str] = None
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: VirtualHost | VirtualHostRelation,
        extra_data: TypeExtraData = None,
    ) -> "VirtualHostSummary":
        return cls(
            id=data.id,
            name=data.name,
            ssl_certificate_id=data.ssl_certificate.id
            if data.ssl_certificate is not None
            else None,
            root_directory=data.root_directory or "",
            application_id=data.application.id
            if data.application is not None
            else None,
            application_name=data.application.name
            if data.application is not None
            else None,
            application_listen_address=data.application_listen_address,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )


class VariableSummary(DevopnessBaseModel):
    id: int
    key: str
    value: str
    target: str
    is_secret: bool
    description: Optional[str]
    url_web_permalink: Optional[str] = None

    @classmethod
    def from_sdk_model(
        cls,
        data: Variable | VariableRelation,
        extra_data: TypeExtraData = None,
    ) -> "VariableSummary":
        value = data.value or ""
        if extra_data and extra_data.application_hide_config_file_content:
            value = ""

        return cls(
            id=data.id,
            key=data.key,
            value=value,
            target=data.target,
            is_secret=data.hidden,
            description=data.description,
            url_web_permalink=extra_data.url_web_permalink if extra_data else None,
        )
