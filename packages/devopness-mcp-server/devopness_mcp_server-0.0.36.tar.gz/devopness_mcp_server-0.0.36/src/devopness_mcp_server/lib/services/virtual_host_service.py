from typing import Annotated, List, Literal, Optional

from pydantic import Field

from ..models import ActionSummary, VirtualHostSummary
from ..response import MCPResponse
from ..types import MAX_RESOURCES_PER_PAGE, ExtraData, ServerContext
from ..utils import (
    get_instructions_choose_resource,
    get_instructions_format_resource_table,
    get_instructions_format_table,
    get_instructions_how_to_monitor_action,
    get_instructions_next_action_suggestion,
    get_web_link_to_environment_resource,
)


class VirtualHostService:
    @staticmethod
    async def tool_list_virtual_hosts(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        page: int = Field(
            default=1,
            gt=0,
        ),
    ) -> MCPResponse[List[VirtualHostSummary]]:
        response = await ctx.devopness.virtual_hosts.list_environment_virtual_hosts(
            environment_id,
            page,
            per_page=MAX_RESOURCES_PER_PAGE,
        )

        virtual_hosts = [
            VirtualHostSummary.from_sdk_model(
                virtual_host,
                ExtraData(
                    url_web_permalink=get_web_link_to_environment_resource(
                        project_id,
                        environment_id,
                        "virtual-host",
                        virtual_host.id,
                    ),
                ),
            )
            for virtual_host in response.data
        ]

        return MCPResponse.ok(
            virtual_hosts,
            [
                get_instructions_format_table(
                    [
                        (
                            "ID",
                            "{virtual_host.id}",
                        ),
                        (
                            "Name",
                            "[{virtual_host.name}]({virtual_host.url_web_permalink})",
                        ),
                        (
                            "Has active SSL",
                            "IF {virtual_host.ssl_certificate_id}"
                            " THEN `🔒 Yes`"
                            " ELSE `🔓 No`",
                        ),
                        (
                            "Application",
                            "{virtual_host.application_name} OR `-`",
                        ),
                        (
                            "Working directory",
                            "IF {virtual_host.application_name}`"
                            " THEN ~/{virtual_host.application_name}/current/{virtual_host.root_directory}`"  # noqa: E501
                            " ELSE `-`",
                        ),
                        (
                            "Routes to",
                            "{virtual_host.application_listen_address} OR `-`",
                        ),
                    ]
                ),
                get_instructions_choose_resource(
                    "virtual-host",
                ),
                get_instructions_next_action_suggestion("deploy", "virtual-host"),
            ],
        )

    @staticmethod
    async def tool_create_virtual_host(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        vh_name: Annotated[
            str,
            Field(
                examples=[
                    "Domain: example.com",
                    "Subdomain: sub.example.com",
                    "IP address: 127.0.0.1",
                    "IP address with port: 127.0.0.1:3000",
                ]
            ),
        ],
        vh_type: Annotated[
            str,
            Literal["ip-based", "name-based"],
            Field(
                examples=[
                    "IF domain or subdomain: name-based",
                    "IF IP address or IP address with port: ip-based",
                ]
            ),
        ],
        application_id: Optional[int],
        vh_root_directory: Annotated[
            Optional[str],
            Field(
                description="Only applicable if `application_id` is set."
                "Must be a relative path inside the application directory."
            ),
        ] = None,
        vh_routes_to_address: Annotated[
            Optional[str],
            Field(
                description="Only applicable if `application_id` is set."
                "Must be the address where the application is listening to.",
                examples=[
                    "http://localhost:3000",
                    "http://127.0.0.1:8080",
                    "unix:/var/run/example.sock",
                ],
            ),
        ] = None,
    ) -> MCPResponse[VirtualHostSummary]:
        if not application_id:
            vh_root_directory = None
            vh_routes_to_address = None

        response = await ctx.devopness.virtual_hosts.add_environment_virtual_host(
            environment_id,
            {
                "name": vh_name,
                "type": vh_type,
                "application_id": application_id,
                "root_directory": vh_root_directory,
                "application_listen_address": vh_routes_to_address,
            },
        )

        virtual_host = VirtualHostSummary.from_sdk_model(
            response.data,
            ExtraData(
                url_web_permalink=get_web_link_to_environment_resource(
                    project_id,
                    environment_id,
                    "virtual-host",
                    response.data.id,
                ),
            ),
        )

        return MCPResponse.ok(
            virtual_host,
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{virtual_host.id}",
                        ),
                        (
                            "Name",
                            "[{virtual_host.name}]({virtual_host.url_web_permalink})",
                        ),
                        (
                            "Has active SSL",
                            "IF {virtual_host.ssl_certificate_id}"
                            " THEN `🔒 Yes`"
                            " ELSE `🔓 No`",
                        ),
                        (
                            "Application",
                            "{virtual_host.application_name} OR `-`",
                        ),
                        (
                            "Working directory",
                            "IF {virtual_host.application_name}`"
                            " THEN ~/{virtual_host.application_name}/current/{virtual_host.root_directory}`"  # noqa: E501
                            " ELSE `-`",
                        ),
                        (
                            "Routes to",
                            "{virtual_host.application_listen_address} OR `-`",
                        ),
                    ]
                ),
                get_instructions_next_action_suggestion("deploy", "virtual-host"),
            ],
        )

    @staticmethod
    async def tool_deploy_virtual_host(
        ctx: ServerContext,
        pipeline_id: int,
        server_ids: Annotated[
            List[int],
            Field(
                min_length=1,
                description="List of Server IDs to which the action will be targeted.",
            ),
        ],
    ) -> MCPResponse[ActionSummary]:
        response = await ctx.devopness.actions.add_pipeline_action(
            pipeline_id,
            {
                "servers": server_ids,
            },
        )

        action = ActionSummary.from_sdk_model(response.data)

        return MCPResponse.ok(
            action,
            [
                get_instructions_how_to_monitor_action(action.url_web_permalink),
                "Show to the user how to access the virtual host using the URL --> "
                "IF {virtual_host.ssl_certificate_id} is set, 'https://{virtual_host.name}'"
                "otherwise 'http://{virtual_host.name}'.",
            ],
        )

    @staticmethod
    async def tool_edit_virtual_host(
        ctx: ServerContext,
        project_id: int,
        environment_id: int,
        virtual_host_id: int,
        vh_name: Annotated[
            str,
            Field(
                examples=[
                    "Domain: example.com",
                    "Subdomain: sub.example.com",
                    "IP address: 127.0.0.1",
                    "IP address with port: 127.0.0.1:3000",
                ]
            ),
        ],
        application_id: Optional[int],
        vh_root_directory: Annotated[
            Optional[str],
            Field(
                description="Only applicable if `application_id` is set."
                "Must be a relative path inside the application directory.",
                examples=[
                    "'relative/path/in/app/directory' or EMPTY STRING",
                ],
            ),
        ],
        vh_routes_to_address: Annotated[
            Optional[str],
            Field(
                description="Only applicable if `application_id` is set."
                "Must be the address where the application is listening to.",
                examples=[
                    "http://localhost:3000",
                    "http://127.0.0.1:8080",
                    "unix:/var/run/example.sock",
                ],
            ),
        ],
    ) -> MCPResponse[VirtualHostSummary]:
        await ctx.devopness.virtual_hosts.update_virtual_host(
            virtual_host_id,
            {
                "id": virtual_host_id,
                "name": vh_name,
                "application_id": application_id,
                "root_directory": (
                    vh_root_directory if application_id else None  #
                ),
                "application_listen_address": (
                    vh_routes_to_address if application_id else None
                ),
            },
        )

        virtual_host = (
            await ctx.devopness.virtual_hosts.get_virtual_host(virtual_host_id)
        ).data

        return MCPResponse.ok(
            VirtualHostSummary.from_sdk_model(
                virtual_host,
                ExtraData(
                    url_web_permalink=get_web_link_to_environment_resource(
                        project_id,
                        environment_id,
                        "virtual-host",
                        virtual_host.id,
                    ),
                ),
            ),
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{virtual_host.id}",
                        ),
                        (
                            "Name",
                            "[{virtual_host.name}]({virtual_host.url_web_permalink})",
                        ),
                        (
                            "Has active SSL",
                            "IF {virtual_host.ssl_certificate_id}"
                            " THEN `🔒 Yes`"
                            " ELSE `🔓 No`",
                        ),
                        (
                            "Application",
                            "{virtual_host.application_name} OR `-`",
                        ),
                        (
                            "Working directory",
                            "IF {virtual_host.application_name}`"
                            " THEN ~/{virtual_host.application_name}/current/{virtual_host.root_directory}`"  # noqa: E501
                            " ELSE `-`",
                        ),
                        (
                            "Routes to",
                            "{virtual_host.application_listen_address} OR `-`",
                        ),
                    ]
                ),
                get_instructions_next_action_suggestion("deploy", "virtual-host"),
            ],
        )
