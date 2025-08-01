import contextlib
from _typeshed import Incomplete
from bosa_core import Plugin as Plugin
from bosa_server_plugins.common.remote.plugin import RemoteServerPlugin as RemoteServerPlugin
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, HttpHandler as HttpHandler
from bosa_server_plugins.handler.auth import AuthenticationSchema as AuthenticationSchema
from bosa_server_plugins.handler.fastapi_schema import FastApiSchemaExtractor as FastApiSchemaExtractor
from bosa_server_plugins.handler.response import ApiResponse as ApiResponse
from bosa_server_plugins.handler.router import Router as Router
from bosa_server_plugins.handler.schema import SchemaExtractor as SchemaExtractor
from fastapi import FastAPI as FastAPI
from mcp.server.fastmcp import FastMCP

def is_pydantic_model(cls) -> bool:
    """Check if a class is a Pydantic model.

    Args:
        cls: The class to check

    Returns:
        True if the class is a Pydantic model, False otherwise
    """

class MockRequest:
    """Mock implementation of starlette.requests.Request for use in MCP tools."""
    query_params: Incomplete
    headers: Incomplete
    cookies: Incomplete
    client: Incomplete
    def __init__(self, query_params=None) -> None:
        """Initialize the mock request.

        Args:
            query_params: The query parameters to initialize the mock request with
        """

class MockResponse:
    """Mock implementation of starlette.responses.Response for use in MCP tools."""
    status_code: int
    headers: Incomplete
    body: Incomplete
    def __init__(self) -> None:
        """Initialize the mock response."""

class McpGenerator:
    """MCP Generator for FastAPI.

    This class is responsible for generating FastMCP instances for the given plugin classes.

    Attributes:
        mcps: Dictionary mapping plugin names to FastMCP instances
    """
    mcps: Incomplete
    def __init__(self) -> None:
        """Initialize the MCP Generator."""
    def generate_fastmcp(self, plugin_classes: list, mcp_name: str = 'bosa'):
        """Generate FastMCP instances for the given plugin classes.

        Args:
            plugin_classes: List of plugin classes to generate FastMCP instances for
            mcp_name: The base name for the MCP instances

        Returns:
            Dictionary mapping plugin names to FastMCP instances
        """
    @contextlib.asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Lifespan context manager for the FastAPI app.

        This method ensures that all MCP sessions are properly managed during the app's lifespan.

        this is the example of how to use this lifespan if you already have another lifespan:
        ```python
        @contextlib.asynccontextmanager
            async def yourlifespan(app: FastAPI):
                ### something todo in your lifespan
                async with lifespan() as result:
                    yield
        ```
        you just need to call `lifespan()` in your lifespan context manager.

        Args:
            app: The FastAPI app instance
        """

class McpFastApiHandler(HttpHandler):
    """MCP interface for FastAPI."""
    excluded_endpoints: Incomplete
    app: Incomplete
    mcp_name: Incomplete
    mcps: Incomplete
    def __init__(self, app: FastAPI, mcps: dict[str, FastMCP], base_api_prefix: str = '/api', authentication_schema: AuthenticationSchema = None, mcp_name: str = 'bosa') -> None:
        """Initialize the MCP FastAPI interface.

        Args:
            app: The FastAPI app
            mcps: Dictionary mapping plugin names to FastMCP instances
            base_api_prefix: The base API prefix
            authentication_schema: The authentication schema
            mcp_name: The MCP name
        """
    @classmethod
    def initialize_plugin(cls, instance: HttpHandler, plugin: Plugin) -> None:
        """Initialize HTTP-specific resources for the plugin.

        If the plugin has a router attribute, register its routes with the HTTP interface.
        At the same time, register the plugin's routes for MCP-compliance.

        Args:
            instance: The HTTP interface instance
            plugin: The plugin instance to initialize
        """
    def initialize_mcp(self, plugin: Plugin):
        """Initialize the MCP for the plugin.

        Args:
            plugin: The plugin instance to initialize
        """
    def get_schema_extractor(self) -> SchemaExtractor:
        """Get the schema extractor for this interface.

        Returns:
            SchemaExtractor implementation for this interface
        """
    def handle_routing(self, prefix: str, router: Router):
        """Register routes with the HTTP interface.

        Args:
            prefix: The prefix for the routes
            router: The router instance
        """
