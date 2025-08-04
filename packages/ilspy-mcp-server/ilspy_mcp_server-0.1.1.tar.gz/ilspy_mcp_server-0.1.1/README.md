# ILSpy MCP Server

A Model Context Protocol (MCP) server that provides .NET assembly decompilation capabilities using ILSpy.

## Features

- **Decompile Assemblies**: Convert .NET assemblies back to readable C# source code
- **List Types**: Enumerate classes, interfaces, structs, delegates, and enums in assemblies
- **Generate Diagrammer**: Create interactive HTML visualizations of assembly structure
- **Assembly Information**: Get metadata about .NET assemblies

## Prerequisites

1. **ILSpy Command Line Tool**: Install the global dotnet tool:
   ```bash
   dotnet tool install --global ilspycmd
   ```

2. **Python 3.8+**: Required for running the MCP server

## Installation

Install from PyPI:

```bash
pip install ilspy-mcp-server
```

Or for development:

```bash
git clone https://github.com/Borealin/ilspy-mcp-server.git
cd ilspy-mcp-server
pip install -e .
```

## Usage

### MCP Client Configuration

Configure your MCP client (e.g., Claude Desktop) to use the server:

```json
{
  "mcpServers": {
    "ilspy": {
      "command": "python",
      "args": ["-m", "ilspy_mcp_server.server"]
    }
  }
}
```

### Available Tools

#### 1. `decompile_assembly`
Decompile a .NET assembly to C# source code.

**Parameters:**
- `assembly_path` (required): Path to the .NET assembly file
- `output_dir` (optional): Output directory for decompiled files
- `type_name` (optional): Specific type to decompile
- `language_version` (optional): C# language version (default: "Latest")
- `create_project` (optional): Create a compilable project structure
- `show_il_code` (optional): Show IL code instead of C#
- `remove_dead_code` (optional): Remove dead code during decompilation
- `nested_directories` (optional): Use nested directories for namespaces

**Example:**
```json
{
  "name": "decompile_assembly",
  "arguments": {
    "assembly_path": "/path/to/MyAssembly.dll",
    "type_name": "MyNamespace.MyClass",
    "language_version": "CSharp10_0"
  }
}
```

#### 2. `list_types`
List types in a .NET assembly.

**Parameters:**
- `assembly_path` (required): Path to the .NET assembly file
- `entity_types` (optional): Array of entity types to list ("c", "i", "s", "d", "e")

**Example:**
```json
{
  "name": "list_types",
  "arguments": {
    "assembly_path": "/path/to/MyAssembly.dll",
    "entity_types": ["c", "i"]
  }
}
```

#### 3. `generate_diagrammer`
Generate an interactive HTML diagrammer.

**Parameters:**
- `assembly_path` (required): Path to the .NET assembly file
- `output_dir` (optional): Output directory for the diagrammer
- `include_pattern` (optional): Regex pattern for types to include
- `exclude_pattern` (optional): Regex pattern for types to exclude

#### 4. `get_assembly_info`
Get basic information about an assembly.

**Parameters:**
- `assembly_path` (required): Path to the .NET assembly file

### Available Prompts

#### 1. `analyze_assembly`
Analyze a .NET assembly and provide insights about its structure.

#### 2. `decompile_and_explain`
Decompile a specific type and provide explanation of its functionality.

## Supported Assembly Types

- .NET Framework assemblies (.dll, .exe)
- .NET Core/.NET 5+ assemblies
- Portable Executable (PE) files with .NET metadata

## Supported C# Language Versions

- CSharp1 through CSharp12_0
- Preview
- Latest (default)

## Quick Start

1. **Install the package**:
   ```bash
   pip install ilspy-mcp-server
   ```

2. **Configure your MCP client** (Claude Desktop example):
   ```json
   {
     "mcpServers": {
       "ilspy": {
         "command": "python",
         "args": ["-m", "ilspy_mcp_server.server"]
       }
     }
   }
   ```

3. **Use the tools** in your MCP client:
   - Ask to decompile a .NET assembly
   - List types in an assembly
   - Generate interactive diagrams
   - Get assembly information

## Error Handling

The server provides detailed error messages for common issues:
- Assembly file not found
- Invalid assembly format
- ILSpyCmd not installed or not in PATH
- Permission issues
- Decompilation failures

## Configuration

### Environment Variables

- `LOGLEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO

### MCP Client Examples

**Claude Desktop** (`config.json`):
```json
{
  "mcpServers": {
    "ilspy": {
      "command": "python",
      "args": ["-m", "ilspy_mcp_server.server"],
      "env": {
        "LOGLEVEL": "INFO"
      }
    }
  }
}
```

**Development/Testing**:
```json
{
  "mcpServers": {
    "ilspy": {
      "command": "python",
      "args": ["-m", "ilspy_mcp_server.server"],
      "env": {
        "LOGLEVEL": "DEBUG"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"ILSpyCmd not found"**:
   ```bash
   dotnet tool install --global ilspycmd
   ```

2. **"Assembly file not found"**:
   - Check the file path is correct
   - Ensure the file has .dll or .exe extension

3. **Permission errors**:
   - Ensure read access to assembly files
   - Check output directory permissions

### Debug Mode

Enable debug logging to see detailed operation info:
```json
{
  "env": {
    "LOGLEVEL": "DEBUG"
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of the excellent [ILSpy](https://github.com/icsharpcode/ILSpy) decompiler
- Uses the [Model Context Protocol](https://modelcontextprotocol.io/) for integration