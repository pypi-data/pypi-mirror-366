from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

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
    assembly_path: str
    output_dir: Optional[str] = None
    type_name: Optional[str] = None
    language_version: LanguageVersion = LanguageVersion.LATEST
    create_project: bool = False
    show_il_code: bool = False
    reference_paths: List[str] = Field(default_factory=list)
    remove_dead_code: bool = False
    nested_directories: bool = False

class ListTypesRequest(BaseModel):
    """Request to list types in an assembly."""
    assembly_path: str
    entity_types: List[EntityType] = Field(default_factory=lambda: [EntityType.CLASS])
    reference_paths: List[str] = Field(default_factory=list)

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
    assembly_path: str
    output_dir: Optional[str] = None
    include_pattern: Optional[str] = None
    exclude_pattern: Optional[str] = None
    docs_path: Optional[str] = None
    strip_namespaces: List[str] = Field(default_factory=list)
    report_excluded: bool = False

class AssemblyInfoRequest(BaseModel):
    """Request to get assembly information."""
    assembly_path: str

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