"""
This module is responsible for discovering and registering Devopness tools
from service classes into the MCP Server.

Each tool is defined as a static method starting with the prefix 'tool_'
and is extracted automatically. These tools are renamed with a final prefix
'devopness_' and added to the FastMCP server, making them available for use
by the LLM.

Call `register_tools(mcp_server)` to make all tools available.
"""

from typing import Any, TypedDict, override

from fastmcp.tools.tool import Tool as FastMCPTool
from fastmcp.utilities.json_schema import compress_schema
from fastmcp.utilities.types import find_kwarg_by_type, get_cached_typeadapter
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from pydantic_core.core_schema import IntSchema

from .services.action_service import ActionService
from .services.application_service import ApplicationService
from .services.credential_service import CredentialService
from .services.daemon_service import DaemonService
from .services.environment_service import EnvironmentService
from .services.pipeline_service import PipelineService
from .services.project_service import ProjectService
from .services.server_service import ServerService
from .services.service_service import ServiceService
from .services.ssh_key_service import SSHKeyService
from .services.ssl_certificate import SSLCertificateService
from .services.user_service import UserService
from .services.virtual_host_service import VirtualHostService
from .services.webhook_service import WebHookService
from .types import Server, ServerContext


class Tool(TypedDict):
    name: str
    func: Any


MCP_TOOL_PREFIX = "tool_"
MCP_TOOL_PREFIX_LEN = len(MCP_TOOL_PREFIX)
MCP_TOOL_FINAL_PREFIX = "devopness_"


def is_mcp_tool(name: str, member: Any) -> bool:  # noqa: ANN401
    return name.startswith(MCP_TOOL_PREFIX) and isinstance(member, staticmethod)


def extract_tools_from_service(service: type) -> list[Tool]:
    tools: list[Tool] = []

    for name, member in service.__dict__.items():
        if not is_mcp_tool(name, member):
            continue

        tool_name: str = MCP_TOOL_FINAL_PREFIX + name[MCP_TOOL_PREFIX_LEN:]
        tool_func: Any = member.__func__

        tool = Tool(
            name=tool_name,
            func=tool_func,
        )

        tools.append(tool)

    return tools


class CustomIntegerNumberJsonSchema(GenerateJsonSchema):
    """
    Custom JSON Schema generator that overrides the default type mapping for
    integers to always use `"type": "number"`.

    See: https://forum.cursor.com/t/mcp-server-tool-calls-fail-with-invalid-type-for-parameter-in-tool/70831

    This also adds `"type": "string"` to `anyOf` when a field allows `"number"`
    and `"null"`, as a workaround for a bug in Cursor (macOS version 1.2.4).

    In this version, Cursor incorrectly sends integer values (40) as strings ("40"),
    causing tool calls to fail if the schema does not allow strings.

    Allowing `"string"` is safe: Pydantic will still enforce that the actual Python type
    (`int`) is respected, and will raise a clear validation error if the input string
    cannot be parsed as an integer.
    """

    @override
    def get_flattened_anyof(self, schemas: list[JsonSchemaValue]) -> JsonSchemaValue:
        anyof = super().get_flattened_anyof(schemas)
        members: list[dict[str, Any]] = anyof.get("anyOf", [])

        has_null = False
        has_number = False
        has_string = False

        for member in members:
            if member.get("type") == "number":
                has_number = True
            elif member.get("type") == "null":
                has_null = True
            elif member.get("type") == "string":
                has_string = True

        # Add "string" to allow int-as-string workaround (e.g., "40" instead of 40)
        if has_number and has_null and not has_string:
            members.append({"type": "string"})

        return {"anyOf": members}

    @override
    def int_schema(self, schema: IntSchema) -> dict[str, Any]:
        json_schema = super().int_schema(schema)

        return {**json_schema, "type": "number"}


def register_tools(server: Server) -> None:
    services = [
        ActionService,
        ApplicationService,
        CredentialService,
        DaemonService,
        EnvironmentService,
        PipelineService,
        ProjectService,
        ServerService,
        ServiceService,
        SSHKeyService,
        SSLCertificateService,
        UserService,
        VirtualHostService,
        WebHookService,
    ]

    all_tools: list[Tool] = []

    for service in services:
        server.logger.info(f"Registering tools from {service.__name__}")
        service_tools = extract_tools_from_service(service)
        all_tools.extend(service_tools)

    all_tools.sort(key=lambda tool: tool["name"])

    for tool_config in all_tools:
        tool = FastMCPTool.from_function(
            tool_config["func"],
            tool_config["name"],
        )

        # Use the custom JSON schema generator to ensure `int` types
        # are declared as "number" to prevent issues in Cursor where
        # integers like `69` are incorrectly rejected.
        #
        # Example Error:
        #    Parameter 'application_id' must be one of types [integer, null], got number
        input_type_adapter = get_cached_typeadapter(tool.fn)
        input_schema = input_type_adapter.json_schema(
            schema_generator=CustomIntegerNumberJsonSchema
        )

        # Compress schema and remove the "ctx" parameter (injected by FastMCP)
        # to create the final tool parameter definition.
        # This step effectively overrides `tool.parameters` to ensure proper
        # compatibility with Cursor and expected tool behavior.
        custom_tool_parameters = compress_schema(
            input_schema,
            [
                find_kwarg_by_type(tool.fn, kwarg_type=ServerContext) or "",
            ],
        )

        tool.parameters = custom_tool_parameters
        server.add_tool(tool)
