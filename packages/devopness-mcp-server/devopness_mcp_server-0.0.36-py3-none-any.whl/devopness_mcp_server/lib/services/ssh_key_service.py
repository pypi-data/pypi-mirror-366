from typing import Annotated, List

from pydantic import Field

from ..models import ActionSummary, SSHKeySummary
from ..response import MCPResponse
from ..types import ServerContext
from ..utils import (
    get_instructions_format_resource_table,
    get_instructions_how_to_monitor_action,
    get_instructions_next_action_suggestion,
)


class SSHKeyService:
    @staticmethod
    async def tool_create_ssh_key(
        ctx: ServerContext,
        environment_id: int,
        name: str,
        public_key: str,
    ) -> MCPResponse[SSHKeySummary]:
        """
        Rules:
        - If the user does not provide a public key, you MUST ask them to provide one.
        - You MUST offer to find the public key for the user.
        - You MUST offer to generate a new ssh key pair for the user.
        """
        response = await ctx.devopness.ssh_keys.add_environment_ssh_key(
            environment_id,
            {
                "name": name,
                "public_key": public_key,
            },
        )

        ssh_key = SSHKeySummary.from_sdk_model(response.data)

        return MCPResponse.ok(
            ssh_key,
            [
                get_instructions_format_resource_table(
                    [
                        (
                            "ID",
                            "{ssh_key.id}",
                        ),
                        (
                            "Name",
                            "[{ssh_key.name}]({ssh_key.url_web_permalink})",
                        ),
                    ]
                ),
                get_instructions_next_action_suggestion("deploy", "ssh-key"),
            ],
        )

    @staticmethod
    async def tool_deploy_ssh_key(
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
                "Show the user the command to remote connect"
                "the server(s) using the SSH Key.",
            ],
        )
