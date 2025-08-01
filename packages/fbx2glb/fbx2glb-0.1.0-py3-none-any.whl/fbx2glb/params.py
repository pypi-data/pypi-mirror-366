"""
Parameter structures for FBX to GLB conversion using params-proto.
"""

from params_proto import ParamsProto, Flag, Proto
from typing import Optional


class ConversionParams(ParamsProto):
    """Parameters for FBX to GLB conversion."""
    # Basic conversion parameters
    input_file: str = Proto(help="Path to input FBX file")
    output_file: Optional[str] = Proto(default=None, help="Path to output GLB file")
    method: Optional[str] = Proto(default=None, help="Conversion method to use")
    force: bool = Flag(default=False, help="Force overwrite if output file exists")
    verbose: bool = Flag(default=False, help="Enable verbose output")
    
    # Blender-specific parameters
    blender_path: Optional[str] = Proto(default=None, help="Path to Blender executable")
    fix_axis: bool = Flag(default=False, help="Fix axis orientation (rotate model to face up)")
    export_yup: bool = Flag(default=True, help="Export with Y-up coordinate system")
    
    # fbx2gltf-specific parameters
    draco: bool = Flag(default=False, help="Use Draco compression")
    no_texture_optimization: bool = Flag(default=False, help="Disable texture optimization")
    keep_attribute_info: bool = Flag(default=False, help="Keep attribute info")
    
    # FBX upgrade parameters
    upgrade_fbx: bool = Flag(default=False, help="Upgrade FBX file to newer version before conversion")
    
    # Utility commands
    check_dependencies: bool = Flag(default=False, help="Check for required dependencies and exit")
    version: bool = Flag(default=False, help="Show version information and exit")


 