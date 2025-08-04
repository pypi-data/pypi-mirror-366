"""Wrapper for ICSharpCode.ILSpyCmd command line tool."""

import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import re
import logging

from .models import (
    DecompileRequest, DecompileResponse, 
    ListTypesRequest, ListTypesResponse, TypeInfo,
    GenerateDiagrammerRequest, AssemblyInfoRequest, AssemblyInfo,
    EntityType
)

logger = logging.getLogger(__name__)


class ILSpyWrapper:
    """Wrapper class for ILSpy command line tool."""
    
    def __init__(self, ilspycmd_path: Optional[str] = None):
        """Initialize the wrapper.
        
        Args:
            ilspycmd_path: Path to ilspycmd executable. If None, will try to find it in PATH.
        """
        self.ilspycmd_path = ilspycmd_path or self._find_ilspycmd()
        if not self.ilspycmd_path:
            raise RuntimeError("ILSpyCmd not found. Please install it with: dotnet tool install --global ilspycmd")
    
    def _find_ilspycmd(self) -> Optional[str]:
        """Find ilspycmd executable in PATH."""
        # Try common names
        for cmd_name in ["ilspycmd", "ilspycmd.exe"]:
            path = shutil.which(cmd_name)
            if path:
                return path
        return None
    
    async def _run_command(self, args: List[str], input_data: Optional[str] = None) -> Tuple[int, str, str]:
        """Run ilspycmd with given arguments.
        
        Args:
            args: Command line arguments
            input_data: Optional input data to pass to stdin
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = [self.ilspycmd_path] + args
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE if input_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            input_bytes = input_data.encode('utf-8') if input_data else None
            stdout_bytes, stderr_bytes = await process.communicate(input=input_bytes)
            
            stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
            stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""
            
            return process.returncode, stdout, stderr
            
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return -1, "", str(e)
    
    async def decompile(self, request: DecompileRequest) -> DecompileResponse:
        """Decompile a .NET assembly.
        
        Args:
            request: Decompilation request
            
        Returns:
            Decompilation response
        """
        if not os.path.exists(request.assembly_path):
            return DecompileResponse(
                success=False,
                error_message=f"Assembly file not found: {request.assembly_path}",
                assembly_name=os.path.basename(request.assembly_path)
            )
        
        args = [request.assembly_path]
        
        # Add language version
        args.extend(["-lv", request.language_version.value])
        
        # Add type filter if specified
        if request.type_name:
            args.extend(["-t", request.type_name])
        
        # Add output directory if specified
        temp_dir = None
        output_dir = request.output_dir
        if not output_dir:
            temp_dir = tempfile.mkdtemp()
            output_dir = temp_dir
        
        args.extend(["-o", output_dir])
        
        # Add project creation flag
        if request.create_project:
            args.append("-p")
        
        # Add IL code flag
        if request.show_il_code:
            args.append("-il")
        
        # Add reference paths
        for ref_path in request.reference_paths:
            args.extend(["-r", ref_path])
        
        # Add optimization flag
        if request.remove_dead_code:
            args.append("--no-dead-code")
        
        # Add directory structure flag
        if request.nested_directories:
            args.append("--nested-directories")
        
        # Disable update check for automation
        args.append("--disable-updatecheck")
        
        try:
            return_code, stdout, stderr = await self._run_command(args)
            
            assembly_name = os.path.splitext(os.path.basename(request.assembly_path))[0]
            
            if return_code == 0:
                # If no output directory was specified, return stdout as source code
                source_code = None
                output_path = None
                
                if request.output_dir is None:
                    source_code = stdout
                else:
                    output_path = output_dir
                    # Try to read the main generated file if it exists
                    if request.type_name:
                        # Single type decompilation
                        type_file = os.path.join(output_dir, f"{request.type_name.split('.')[-1]}.cs")
                        if os.path.exists(type_file):
                            with open(type_file, 'r', encoding='utf-8') as f:
                                source_code = f.read()
                    elif not request.create_project:
                        # Single file decompilation
                        cs_file = os.path.join(output_dir, f"{assembly_name}.cs")
                        if os.path.exists(cs_file):
                            with open(cs_file, 'r', encoding='utf-8') as f:
                                source_code = f.read()
                
                return DecompileResponse(
                    success=True,
                    source_code=source_code,
                    output_path=output_path,
                    assembly_name=assembly_name,
                    type_name=request.type_name
                )
            else:
                error_msg = stderr or stdout or "Unknown error occurred"
                return DecompileResponse(
                    success=False,
                    error_message=error_msg,
                    assembly_name=assembly_name,
                    type_name=request.type_name
                )
                
        except Exception as e:
            return DecompileResponse(
                success=False,
                error_message=str(e),
                assembly_name=os.path.basename(request.assembly_path),
                type_name=request.type_name
            )
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def list_types(self, request: ListTypesRequest) -> ListTypesResponse:
        """List types in a .NET assembly.
        
        Args:
            request: List types request
            
        Returns:
            List types response
        """
        if not os.path.exists(request.assembly_path):
            return ListTypesResponse(
                success=False,
                error_message=f"Assembly file not found: {request.assembly_path}"
            )
        
        args = [request.assembly_path]
        
        # Add entity types to list
        entity_types_str = "".join([et.value for et in request.entity_types])
        args.extend(["-l", entity_types_str])
        
        # Add reference paths
        for ref_path in request.reference_paths:
            args.extend(["-r", ref_path])
        
        # Disable update check
        args.append("--disable-updatecheck")
        
        try:
            return_code, stdout, stderr = await self._run_command(args)
            
            if return_code == 0:
                types = self._parse_types_output(stdout)
                return ListTypesResponse(
                    success=True,
                    types=types,
                    total_count=len(types)
                )
            else:
                error_msg = stderr or stdout or "Unknown error occurred"
                return ListTypesResponse(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            return ListTypesResponse(
                success=False,
                error_message=str(e)
            )
    
    def _parse_types_output(self, output: str) -> List[TypeInfo]:
        """Parse the output from list types command.
        
        Args:
            output: Raw output from ilspycmd
            
        Returns:
            List of TypeInfo objects
        """
        types = []
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse the line format: "TypeKind: FullTypeName"
            match = re.match(r'^(\w+):\s*(.+)$', line)
            if match:
                kind = match.group(1)
                full_name = match.group(2)
                
                # Extract namespace and name
                parts = full_name.split('.')
                if len(parts) > 1:
                    namespace = '.'.join(parts[:-1])
                    name = parts[-1]
                else:
                    namespace = None
                    name = full_name
                
                types.append(TypeInfo(
                    name=name,
                    full_name=full_name,
                    kind=kind,
                    namespace=namespace
                ))
        
        return types
    
    async def generate_diagrammer(self, request: GenerateDiagrammerRequest) -> Dict[str, Any]:
        """Generate HTML diagrammer for an assembly.
        
        Args:
            request: Generate diagrammer request
            
        Returns:
            Dictionary with success status and details
        """
        if not os.path.exists(request.assembly_path):
            return {
                "success": False,
                "error_message": f"Assembly file not found: {request.assembly_path}"
            }
        
        args = [request.assembly_path, "--generate-diagrammer"]
        
        # Add output directory
        output_dir = request.output_dir
        if not output_dir:
            # Generate next to assembly
            assembly_dir = os.path.dirname(request.assembly_path)
            output_dir = os.path.join(assembly_dir, "diagrammer")
        
        args.extend(["-o", output_dir])
        
        # Add include/exclude patterns
        if request.include_pattern:
            args.extend(["--generate-diagrammer-include", request.include_pattern])
        if request.exclude_pattern:
            args.extend(["--generate-diagrammer-exclude", request.exclude_pattern])
        
        # Add documentation file
        if request.docs_path:
            args.extend(["--generate-diagrammer-docs", request.docs_path])
        
        # Add namespace stripping
        if request.strip_namespaces:
            args.extend(["--generate-diagrammer-strip-namespaces"] + request.strip_namespaces)
        
        # Add report excluded flag
        if request.report_excluded:
            args.append("--generate-diagrammer-report-excluded")
        
        # Disable update check
        args.append("--disable-updatecheck")
        
        try:
            return_code, stdout, stderr = await self._run_command(args)
            
            if return_code == 0:
                return {
                    "success": True,
                    "output_directory": output_dir,
                    "message": "HTML diagrammer generated successfully"
                }
            else:
                error_msg = stderr or stdout or "Unknown error occurred"
                return {
                    "success": False,
                    "error_message": error_msg
                }
                
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_assembly_info(self, request: AssemblyInfoRequest) -> AssemblyInfo:
        """Get basic information about an assembly.
        
        Args:
            request: Assembly info request
            
        Returns:
            Assembly information
        """
        if not os.path.exists(request.assembly_path):
            raise FileNotFoundError(f"Assembly file not found: {request.assembly_path}")
        
        # For now, we'll extract basic info from the file path
        # In a more complete implementation, we could use reflection or metadata reading
        assembly_path = Path(request.assembly_path)
        
        return AssemblyInfo(
            name=assembly_path.stem,
            version="Unknown",
            full_name=assembly_path.name,
            location=str(assembly_path.absolute()),
            target_framework=None,
            runtime_version=None,
            is_signed=False,
            has_debug_info=os.path.exists(assembly_path.with_suffix('.pdb'))
        )