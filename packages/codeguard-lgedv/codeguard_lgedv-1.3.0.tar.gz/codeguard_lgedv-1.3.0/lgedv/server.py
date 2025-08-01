"""
LGEDV MCP Server - Modular Architecture
Main server file với cấu trúc module đã được tối ưu
"""
import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from pydantic import FileUrl
import os
import sys

# Import modules từ package structure mới
from lgedv.modules.config import RESOURCE_FILES, CUSTOM_RULE_URL, setup_logging
from lgedv.handlers.tool_handlers import ToolHandler
from lgedv.handlers.prompt_handlers import PromptHandler
from lgedv.handlers.resource_handler import get_all_resources

# Setup logging
logger = setup_logging()

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str):
    """Main entry point for the MCP server"""
    try:
        logger.info("Server started and ready to receive requests")
        logger.info(f"Starting server with transport: {transport}, port: {port}")
        
        # Initialize server and handlers
        app = Server("mcp-misra-tool")
        tool_handler = ToolHandler()
        prompt_handler = PromptHandler()
        
        logger.debug("App server object created")

        # Register tool handler
        @app.call_tool()
        async def fetch_tool(name: str, arguments: dict) -> list[
            types.TextContent | types.ImageContent | types.AudioContent | types.EmbeddedResource
        ]:
            """Route tool calls to appropriate handler"""
            return await tool_handler.handle_tool_call(name, arguments)

        # Register tool list handler
        @app.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            logger.info("list_tools called")
            return [
                types.Tool(
                    name="fetch_misra_rule",
                    description="Fetches the MISRA C++ 2008 rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch MISRA rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_lgedv_rule",
                    description="Fetches the LGEDV rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch LGEDV rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_certcpp_rule",
                    description="Fetches the CERT C++ rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch CERT C++ rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_custom_rule",
                    description="Fetches the Custom rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch Custom rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="list_cpp_files",
                    description="List all .cpp files in the current CPP_DIR or given directory.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dir_path": {
                                "type": "string",
                                "description": "Directory to search for .cpp files (optional, default is CPP_DIR or cwd)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="get_cpp_files_content",
                    description="Get the content of all .cpp files in the current CPP_DIR or given directory as a single response for context.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dir_path": {
                                "type": "string",
                                "description": "Directory to search for .cpp files (optional, default is CPP_DIR or cwd)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="detect_races",
                    description="Detect potential race conditions in the codebase using CPP_DIR.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="analyze_leaks",
                    description="AI-powered memory leak detection in C++ codebase using CPP_DIR.",
                    inputSchema={
                        "type": "object", 
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="analyze_resources",
                    description="AI-powered resource leak detection in Linux C++ codebase using CPP_DIR.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        # Register prompt list handler
        @app.list_prompts()
        async def list_prompts() -> list[types.Prompt]:
            """List all available prompts"""
            logger.info("list_prompts called")
            return [
                types.Prompt(
                    name="check_lgedv",
                    description="check code violations based on LGEDV rule guide for current file."
                ),
                types.Prompt(
                    name="check_misra",
                    description="check code violations based on MISRA C++ 2008 rule guide for current file."
                ),
                types.Prompt(
                    name="check_certcpp",
                    description="check code violations based on CERT C++ rule guide for current file."
                ),
                types.Prompt(
                    name="check_custom",
                    description="check code violations based on Custom rule guide for current file."
                ),
                types.Prompt(
                    name="check_races",
                    description="Analyze potential race conditions in C++ codebase using AI.",
                ),
                types.Prompt(
                    name="check_leaks",
                    description="Analyze potential memory leaks in C++ codebase using AI.",
                ),
                types.Prompt(
                    name="check_resources",
                    description="Analyze potential resource leaks (file/socket/handle) in Linux C++ codebase using AI.",
                ),
            ]

        # Register prompt handler
        @app.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
            """Route prompt calls to appropriate handler"""
            return await prompt_handler.handle_prompt(name, arguments)

        # Register resource list handler
        @app.list_resources()
        async def list_resources() -> list[types.Resource]:
            """List all available resources"""
            logger.info("list_resources called")
            return get_all_resources()

        logger.info("All handlers registered. Entering main event loop...")
        
        # Start server based on transport type
        if transport == "sse":
            _run_sse_server(app, port)
        else:
            _run_stdio_server(app)
            
        logger.info("Server stopped")
        return 0
        
    except Exception as e:
        logger.exception(f"Fatal error in main: {e}")
        print(f"Fatal error in main: {e}", file=sys.stderr)
        raise

def _run_sse_server(app: Server, port: int):
    """Run SSE server (if needed)"""
    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        
        sse = SseServerTransport("/messages/")
        
        async def handle_sse(request):
            logger.info("Handling SSE connection")
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())
            return Response()
            
        # Note: Full SSE implementation would need Starlette app setup
        logger.warning("SSE transport not fully implemented in this refactored version")
        
    except ImportError as e:
        logger.error(f"SSE dependencies not available: {e}")
        raise

def _run_stdio_server(app: Server):
    """Run stdio server"""
    async def arun():
        logger.info("Running stdio server")
        try:
            import mcp.server.stdio
            async with mcp.server.stdio.stdio_server() as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())
            logger.info("stdio server run completed")
        except Exception as e:
            logger.exception(f"Exception in stdio server: {e}")
    
    anyio.run(arun)

if __name__ == "__main__":
    main()
