import logging
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context
from .ilspy_wrapper import ILSpyWrapper
from .models import LanguageVersion, EntityType

# Setup logging
log_level = os.getenv('LOGLEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server - much simpler than before!
mcp = FastMCP("ilspy-mcp-server")

# Global ILSpy wrapper
ilspy_wrapper: Optional[ILSpyWrapper] = None

def get_wrapper() -> ILSpyWrapper:
    """Get ILSpy wrapper instance"""
    global ilspy_wrapper
    if ilspy_wrapper is None:
        ilspy_wrapper = ILSpyWrapper()
    return ilspy_wrapper

@mcp.tool()
async def decompile_assembly(
    assembly_path: str,
    output_dir: str = None,
    type_name: str = None,
    language_version: str = "Latest",
    create_project: bool = False,
    show_il_code: bool = False,
    remove_dead_code: bool = False,
    nested_directories: bool = False,
    ctx: Context = None
) -> str:
    """Decompile a .NET assembly to C# source code
    
    Args:
        assembly_path: Path to the .NET assembly file (.dll or .exe)
        output_dir: Output directory for decompiled files (optional)
        type_name: Fully qualified name of specific type to decompile (optional)
        language_version: C# language version to use (default: Latest)
        create_project: Create a compilable project with multiple files
        show_il_code: Show IL code instead of C#
        remove_dead_code: Remove dead code during decompilation
        nested_directories: Use nested directories for namespaces
    """
    if ctx:
        await ctx.info(f"Starting decompilation of assembly: {assembly_path}")
    
    try:
        wrapper = get_wrapper()
        
        # Use simplified request object (no complex pydantic validation needed)
        from .models import DecompileRequest
        request = DecompileRequest(
            assembly_path=assembly_path,
            output_dir=output_dir,
            type_name=type_name,
            language_version=LanguageVersion(language_version),
            create_project=create_project,
            show_il_code=show_il_code,
            remove_dead_code=remove_dead_code,
            nested_directories=nested_directories
        )
        
        response = await wrapper.decompile(request)
        
        if response.success:
            if response.source_code:
                content = f"# Decompilation result: {response.assembly_name}"
                if response.type_name:
                    content += f" - {response.type_name}"
                content += f"\n\n```csharp\n{response.source_code}\n```"
                return content
            else:
                return f"Decompilation successful! Files saved to: {response.output_path}"
        else:
            return f"Decompilation failed: {response.error_message}"
            
    except Exception as e:
        logger.error(f"Decompilation error: {e}")
        return f"Error: {str(e)}"

@mcp.tool()  
async def list_types(
    assembly_path: str,
    entity_types: list[str] = None,
    ctx: Context = None
) -> str:
    """List types (classes, interfaces, structs, etc.) in a .NET assembly
    
    Args:
        assembly_path: Path to the .NET assembly file (.dll or .exe)
        entity_types: Types of entities to list (c=class, i=interface, s=struct, d=delegate, e=enum)
    """
    if ctx:
        await ctx.info(f"Listing types in assembly: {assembly_path}")
    
    try:
        wrapper = get_wrapper()
        
        # Default to list only classes
        if entity_types is None:
            entity_types = ["c"]
        
        # Convert to EntityType enums
        entity_type_enums = []
        for et in entity_types:
            try:
                entity_type_enums.append(EntityType(et))
            except ValueError:
                continue
        
        from .models import ListTypesRequest
        request = ListTypesRequest(
            assembly_path=assembly_path,
            entity_types=entity_type_enums
        )
        
        response = await wrapper.list_types(request)
        
        if response.success and response.types:
            content = f"# Types in {assembly_path}\n\n"
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
            
            return content
        else:
            return response.error_message or "No types found in assembly"
            
    except Exception as e:
        logger.error(f"Error listing types: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_diagrammer(
    assembly_path: str,
    output_dir: str = None,
    include_pattern: str = None,
    exclude_pattern: str = None,
    ctx: Context = None
) -> str:
    """Generate an interactive HTML diagrammer for visualizing assembly structure
    
    Args:
        assembly_path: Path to the .NET assembly file (.dll or .exe)
        output_dir: Output directory for the diagrammer (optional)
        include_pattern: Regex pattern for types to include (optional)
        exclude_pattern: Regex pattern for types to exclude (optional)
    """
    if ctx:
        await ctx.info(f"Generating assembly diagram: {assembly_path}")
    
    try:
        wrapper = get_wrapper()
        
        from .models import GenerateDiagrammerRequest
        request = GenerateDiagrammerRequest(
            assembly_path=assembly_path,
            output_dir=output_dir,
            include_pattern=include_pattern,
            exclude_pattern=exclude_pattern
        )
        
        response = await wrapper.generate_diagrammer(request)
        
        if response["success"]:
            return f"HTML diagram generated successfully!\nOutput directory: {response['output_directory']}\nOpen the HTML file in a web browser to view the interactive diagram."
        else:
            return f"Failed to generate diagram: {response['error_message']}"
            
    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
async def get_assembly_info(
    assembly_path: str,
    ctx: Context = None
) -> str:
    """Get basic information about a .NET assembly
    
    Args:
        assembly_path: Path to the .NET assembly file (.dll or .exe)
    """
    if ctx:
        await ctx.info(f"Getting assembly info: {assembly_path}")
    
    try:
        wrapper = get_wrapper()
        
        from .models import AssemblyInfoRequest
        request = AssemblyInfoRequest(assembly_path=assembly_path)
        
        info = await wrapper.get_assembly_info(request)
        
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
        
        return content
        
    except Exception as e:
        logger.error(f"Error getting assembly info: {e}")
        return f"Error: {str(e)}"

# FastMCP automatically handles prompts
@mcp.prompt()  
def analyze_assembly_prompt(assembly_path: str, focus_area: str = "types") -> str:
    """Prompt template for analyzing .NET assemblies"""
    return f"""I need to analyze the .NET assembly at "{assembly_path}".

Please help me understand:
1. The overall structure and organization of the assembly
2. Key types and their relationships
3. Main namespaces and their purposes
4. Any notable patterns or architectural decisions

Focus area: {focus_area}

Start by listing the types in the assembly, then provide insights based on what you find."""

@mcp.prompt()
def decompile_and_explain_prompt(assembly_path: str, type_name: str) -> str:
    """Prompt template for decompiling and explaining specific types"""
    return f"""I want to understand the type "{type_name}" from the assembly "{assembly_path}".

Please:
1. Decompile this specific type
2. Explain what this type does and its purpose
3. Highlight any interesting patterns, design decisions, or potential issues
4. Suggest how this type fits into the overall architecture

Type to analyze: {type_name}
Assembly: {assembly_path}"""

if __name__ == "__main__":
    # FastMCP automatically handles running
    mcp.run()