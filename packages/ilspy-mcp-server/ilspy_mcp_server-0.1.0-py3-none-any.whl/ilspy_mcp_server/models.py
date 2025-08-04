"""Data models for ILSpy MCP Server."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import os


class LanguageVersion(str, Enum):
    """C# Language versions supported by ILSpy."""
    CSHARP1 = "CSharp1"
    CSHARP2 = "CSharp2"
    CSHARP3 = "CSharp3"
    CSHARP4 = "CSharp4"
    CSHARP5 = "CSharp5"
    CSHARP6 = "CSharp6"
    CSHARP7 = "CSharp7"
    CSHARP7_1 = "CSharp7_1"
    CSHARP7_2 = "CSharp7_2"
    CSHARP7_3 = "CSharp7_3"
    CSHARP8_0 = "CSharp8_0"
    CSHARP9_0 = "CSharp9_0"
    CSHARP10_0 = "CSharp10_0"
    CSHARP11_0 = "CSharp11_0"
    CSHARP12_0 = "CSharp12_0"
    PREVIEW = "Preview"
    LATEST = "Latest"


class EntityType(str, Enum):
    """Entity types that can be listed."""
    CLASS = "c"
    INTERFACE = "i"
    STRUCT = "s"
    DELEGATE = "d"
    ENUM = "e"


class DecompileRequest(BaseModel):
    """Request to decompile a .NET assembly."""
    assembly_path: str = Field(..., description="Path to the .NET assembly file")
    output_dir: Optional[str] = Field(None, description="Output directory for decompiled files")
    type_name: Optional[str] = Field(None, description="Fully qualified name of the type to decompile")
    language_version: LanguageVersion = Field(LanguageVersion.LATEST, description="C# language version")
    create_project: bool = Field(False, description="Create a compilable project")
    show_il_code: bool = Field(False, description="Show IL code")
    show_il_sequence_points: bool = Field(False, description="Show IL with sequence points")
    generate_pdb: bool = Field(False, description="Generate PDB file")
    use_pdb: Optional[str] = Field(None, description="Path to PDB file for variable names")
    reference_paths: List[str] = Field(default_factory=list, description="Reference assembly paths")
    remove_dead_code: bool = Field(False, description="Remove dead code")
    remove_dead_stores: bool = Field(False, description="Remove dead stores")
    nested_directories: bool = Field(False, description="Use nested directories for namespaces")
    
    @validator('assembly_path')
    def validate_assembly_path(cls, v):
        """Validate that the assembly path exists and has a valid extension."""
        if not v:
            raise ValueError("Assembly path cannot be empty")
        
        if not os.path.exists(v):
            raise ValueError(f"Assembly file not found: {v}")
        
        valid_extensions = ['.dll', '.exe']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid assembly file extension. Expected: {', '.join(valid_extensions)}")
        
        return v
    
    @validator('output_dir')
    def validate_output_dir(cls, v):
        """Validate output directory if specified."""
        if v and not os.path.isdir(os.path.dirname(v) if os.path.dirname(v) else '.'):
            raise ValueError(f"Output directory parent does not exist: {v}")
        return v
    
    @validator('use_pdb')
    def validate_pdb_path(cls, v):
        """Validate PDB file path if specified."""
        if v and not os.path.exists(v):
            raise ValueError(f"PDB file not found: {v}")
        return v
    
    @validator('reference_paths')
    def validate_reference_paths(cls, v):
        """Validate reference assembly paths."""
        for ref_path in v:
            if not os.path.exists(ref_path):
                raise ValueError(f"Reference assembly not found: {ref_path}")
        return v


class ListTypesRequest(BaseModel):
    """Request to list types in an assembly."""
    assembly_path: str = Field(..., description="Path to the .NET assembly file")
    entity_types: List[EntityType] = Field(default_factory=lambda: [EntityType.CLASS], description="Types of entities to list")
    reference_paths: List[str] = Field(default_factory=list, description="Reference assembly paths")
    
    @validator('assembly_path')
    def validate_assembly_path(cls, v):
        """Validate that the assembly path exists and has a valid extension."""
        if not v:
            raise ValueError("Assembly path cannot be empty")
        
        if not os.path.exists(v):
            raise ValueError(f"Assembly file not found: {v}")
        
        valid_extensions = ['.dll', '.exe']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid assembly file extension. Expected: {', '.join(valid_extensions)}")
        
        return v
    
    @validator('reference_paths')
    def validate_reference_paths(cls, v):
        """Validate reference assembly paths."""
        for ref_path in v:
            if not os.path.exists(ref_path):
                raise ValueError(f"Reference assembly not found: {ref_path}")
        return v


class TypeInfo(BaseModel):
    """Information about a type in an assembly."""
    name: str
    full_name: str
    kind: str
    namespace: Optional[str] = None


class DecompileResponse(BaseModel):
    """Response from decompilation operation."""
    success: bool
    source_code: Optional[str] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    assembly_name: str
    type_name: Optional[str] = None


class ListTypesResponse(BaseModel):
    """Response from list types operation."""
    success: bool
    types: List[TypeInfo] = Field(default_factory=list)
    total_count: int = 0
    error_message: Optional[str] = None


class GenerateDiagrammerRequest(BaseModel):
    """Request to generate HTML diagrammer."""
    assembly_path: str = Field(..., description="Path to the .NET assembly file")
    output_dir: Optional[str] = Field(None, description="Output directory for diagrammer")
    include_pattern: Optional[str] = Field(None, description="Regex pattern for types to include")
    exclude_pattern: Optional[str] = Field(None, description="Regex pattern for types to exclude")
    docs_path: Optional[str] = Field(None, description="Path to XML documentation file")
    strip_namespaces: List[str] = Field(default_factory=list, description="Namespaces to strip from docs")
    report_excluded: bool = Field(False, description="Generate report of excluded types")
    
    @validator('assembly_path')
    def validate_assembly_path(cls, v):
        """Validate that the assembly path exists and has a valid extension."""
        if not v:
            raise ValueError("Assembly path cannot be empty")
        
        if not os.path.exists(v):
            raise ValueError(f"Assembly file not found: {v}")
        
        valid_extensions = ['.dll', '.exe']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid assembly file extension. Expected: {', '.join(valid_extensions)}")
        
        return v
    
    @validator('docs_path')
    def validate_docs_path(cls, v):
        """Validate XML documentation file path if specified."""
        if v and not os.path.exists(v):
            raise ValueError(f"Documentation file not found: {v}")
        return v


class AssemblyInfoRequest(BaseModel):
    """Request to get assembly information."""
    assembly_path: str = Field(..., description="Path to the .NET assembly file")
    
    @validator('assembly_path')
    def validate_assembly_path(cls, v):
        """Validate that the assembly path exists and has a valid extension."""
        if not v:
            raise ValueError("Assembly path cannot be empty")
        
        if not os.path.exists(v):
            raise ValueError(f"Assembly file not found: {v}")
        
        valid_extensions = ['.dll', '.exe']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid assembly file extension. Expected: {', '.join(valid_extensions)}")
        
        return v


class AssemblyInfo(BaseModel):
    """Information about an assembly."""
    name: str
    version: str
    full_name: str
    location: str
    target_framework: Optional[str] = None
    runtime_version: Optional[str] = None
    is_signed: bool = False
    has_debug_info: bool = False