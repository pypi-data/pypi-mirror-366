"""MCP Server for ILSpy .NET Decompiler."""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    Prompt,
    PromptMessage,
    PromptArgument,
)

from .ilspy_wrapper import ILSpyWrapper
from .models import (
    DecompileRequest, ListTypesRequest, GenerateDiagrammerRequest,
    AssemblyInfoRequest, LanguageVersion, EntityType
)

# Set up logging
log_level = os.getenv('LOGLEVEL', 'INFO').upper()
numeric_level = getattr(logging, log_level, logging.INFO)
logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("ilspy-mcp-server")

# Global ILSpy wrapper instance
ilspy_wrapper: Optional[ILSpyWrapper] = None


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="decompile_assembly",
                description="Decompile a .NET assembly to C# source code",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assembly_path": {
                            "type": "string",
                            "description": "Path to the .NET assembly file (.dll or .exe)"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for decompiled files (optional)"
                        },
                        "type_name": {
                            "type": "string",
                            "description": "Fully qualified name of specific type to decompile (optional)"
                        },
                        "language_version": {
                            "type": "string",
                            "enum": [lv.value for lv in LanguageVersion],
                            "description": "C# language version to use",
                            "default": "Latest"
                        },
                        "create_project": {
                            "type": "boolean",
                            "description": "Create a compilable project with multiple files",
                            "default": False
                        },
                        "show_il_code": {
                            "type": "boolean",
                            "description": "Show IL code instead of C#",
                            "default": False
                        },
                        "remove_dead_code": {
                            "type": "boolean",
                            "description": "Remove dead code during decompilation",
                            "default": False
                        },
                        "nested_directories": {
                            "type": "boolean",
                            "description": "Use nested directories for namespaces",
                            "default": False
                        }
                    },
                    "required": ["assembly_path"]
                }
            ),
            Tool(
                name="list_types",
                description="List types (classes, interfaces, structs, etc.) in a .NET assembly",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assembly_path": {
                            "type": "string",
                            "description": "Path to the .NET assembly file (.dll or .exe)"
                        },
                        "entity_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [et.value for et in EntityType]
                            },
                            "description": "Types of entities to list (c=class, i=interface, s=struct, d=delegate, e=enum)",
                            "default": ["c"]
                        }
                    },
                    "required": ["assembly_path"]
                }
            ),
            Tool(
                name="generate_diagrammer",
                description="Generate an interactive HTML diagrammer for visualizing assembly structure",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assembly_path": {
                            "type": "string",
                            "description": "Path to the .NET assembly file (.dll or .exe)"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for the diagrammer (optional)"
                        },
                        "include_pattern": {
                            "type": "string",
                            "description": "Regex pattern for types to include (optional)"
                        },
                        "exclude_pattern": {
                            "type": "string",
                            "description": "Regex pattern for types to exclude (optional)"
                        }
                    },
                    "required": ["assembly_path"]
                }
            ),
            Tool(
                name="get_assembly_info",
                description="Get basic information about a .NET assembly",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assembly_path": {
                            "type": "string",
                            "description": "Path to the .NET assembly file (.dll or .exe)"
                        }
                    },
                    "required": ["assembly_path"]
                }
            )
        ]
    )


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    global ilspy_wrapper
    
    if ilspy_wrapper is None:
        try:
            ilspy_wrapper = ILSpyWrapper()
        except RuntimeError as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
    
    try:
        if name == "decompile_assembly":
            request = DecompileRequest(**arguments)
            response = await ilspy_wrapper.decompile(request)
            
            if response.success:
                if response.source_code:
                    content = f"# Decompiled: {response.assembly_name}"
                    if response.type_name:
                        content += f" - {response.type_name}"
                    content += "\n\n```csharp\n" + response.source_code + "\n```"
                else:
                    content = f"Decompilation successful. Files saved to: {response.output_path}"
            else:
                content = f"Decompilation failed: {response.error_message}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=content)]
            )
        
        elif name == "list_types":
            request = ListTypesRequest(**arguments)
            response = await ilspy_wrapper.list_types(request)
            
            if response.success:
                if response.types:
                    content = f"# Types in {arguments['assembly_path']}\n\n"
                    content += f"Found {response.total_count} types:\n\n"
                    
                    # Group by namespace
                    by_namespace = {}
                    for type_info in response.types:
                        ns = type_info.namespace or "(Global)"
                        if ns not in by_namespace:
                            by_namespace[ns] = []
                        by_namespace[ns].append(type_info)
                    
                    for namespace, types in sorted(by_namespace.items()):
                        content += f"## {namespace}\n\n"
                        for type_info in sorted(types, key=lambda t: t.name):
                            content += f"- **{type_info.name}** ({type_info.kind})\n"
                            content += f"  - Full name: `{type_info.full_name}`\n"
                        content += "\n"
                else:
                    content = "No types found in the assembly."
            else:
                content = f"Failed to list types: {response.error_message}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=content)]
            )
        
        elif name == "generate_diagrammer":
            request = GenerateDiagrammerRequest(**arguments)
            response = await ilspy_wrapper.generate_diagrammer(request)
            
            if response["success"]:
                content = f"HTML diagrammer generated successfully!\n"
                content += f"Output directory: {response['output_directory']}\n"
                content += f"Open the HTML file in a web browser to view the interactive diagram."
            else:
                content = f"Failed to generate diagrammer: {response['error_message']}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=content)]
            )
        
        elif name == "get_assembly_info":
            request = AssemblyInfoRequest(**arguments)
            info = await ilspy_wrapper.get_assembly_info(request)
            
            content = f"# Assembly Information\n\n"
            content += f"- **Name**: {info.name}\n"
            content += f"- **Full Name**: {info.full_name}\n"
            content += f"- **Location**: {info.location}\n"
            content += f"- **Version**: {info.version}\n"
            if info.target_framework:
                content += f"- **Target Framework**: {info.target_framework}\n"
            if info.runtime_version:
                content += f"- **Runtime Version**: {info.runtime_version}\n"
            content += f"- **Is Signed**: {info.is_signed}\n"
            content += f"- **Has Debug Info**: {info.has_debug_info}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=content)]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    
    except ValueError as e:
        # Handle validation errors with user-friendly messages
        logger.warning(f"Validation error in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Validation Error: {str(e)}")]
        )
    except FileNotFoundError as e:
        logger.warning(f"File not found in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"File Not Found: {str(e)}")]
        )
    except PermissionError as e:
        logger.warning(f"Permission error in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Permission Error: {str(e)}. Please check file permissions.")]
        )
    except Exception as e:
        logger.error(f"Unexpected error in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unexpected Error: {str(e)}. Please check the logs for more details.")]
        )


@server.list_prompts()
async def handle_list_prompts() -> ListPromptsResult:
    """List available prompts."""
    return ListPromptsResult(
        prompts=[
            Prompt(
                name="analyze_assembly",
                description="Analyze a .NET assembly and provide insights about its structure and types",
                arguments=[
                    PromptArgument(
                        name="assembly_path",
                        description="Path to the .NET assembly file",
                        required=True
                    ),
                    PromptArgument(
                        name="focus_area",
                        description="Specific area to focus on (types, namespaces, dependencies)",
                        required=False
                    )
                ]
            ),
            Prompt(
                name="decompile_and_explain",
                description="Decompile a specific type and provide explanation of its functionality",
                arguments=[
                    PromptArgument(
                        name="assembly_path",
                        description="Path to the .NET assembly file",
                        required=True
                    ),
                    PromptArgument(
                        name="type_name",
                        description="Fully qualified name of the type to analyze",
                        required=True
                    )
                ]
            )
        ]
    )


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
    """Handle prompt requests."""
    if name == "analyze_assembly":
        assembly_path = arguments.get("assembly_path", "")
        focus_area = arguments.get("focus_area", "types")
        
        prompt_text = f"""I need to analyze the .NET assembly at "{assembly_path}".

Please help me understand:
1. The overall structure and organization of the assembly
2. Key types and their relationships
3. Main namespaces and their purposes
4. Any notable patterns or architectural decisions

Focus area: {focus_area}

Start by listing the types in the assembly, then provide insights based on what you find."""
        
        return GetPromptResult(
            description=f"Analysis of .NET assembly: {assembly_path}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    elif name == "decompile_and_explain":
        assembly_path = arguments.get("assembly_path", "")
        type_name = arguments.get("type_name", "")
        
        prompt_text = f"""I want to understand the type "{type_name}" from the assembly "{assembly_path}".

Please:
1. Decompile this specific type
2. Explain what this type does and its purpose
3. Highlight any interesting patterns, design decisions, or potential issues
4. Suggest how this type fits into the overall architecture

Type to analyze: {type_name}
Assembly: {assembly_path}"""
        
        return GetPromptResult(
            description=f"Decompilation and analysis of {type_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ilspy-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())