"""
FBX file upgrader utility.
Handles upgrading FBX files to newer versions when the FBX SDK is not available.
"""

import os
import tempfile
import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def upgrade_fbx_with_blender_legacy(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Attempt to upgrade FBX file using Blender's export/import cycle.
    This can sometimes help with version compatibility issues.
    
    Args:
        input_file: Path to input FBX file
        output_file: Path to output upgraded FBX file
        verbose: Enable verbose output
        
    Returns:
        True if upgrade was successful, False otherwise
    """
    if not output_file:
        input_base = os.path.splitext(input_file)[0]
        output_file = f"{input_base}_upgraded.fbx"
    
    # Create a temporary Python script for Blender
    blender_script = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
    
    try:
        # Write upgrade script to the temp file
        with open(blender_script.name, 'w') as f:
            f.write(f"""
import bpy
import sys
import os

# Clear default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

try:
    # Import FBX with minimal settings to avoid version issues
    bpy.ops.import_scene.fbx(filepath="{input_file}", 
                             use_custom_props=False,
                             use_custom_props_enum_as_string=False,
                             use_anim=False, 
                             use_image_search=False)
    
    # Export as newer FBX version
    bpy.ops.export_scene.fbx(filepath="{output_file}",
                             use_selection=False,
                             global_scale=1.0,
                             apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL',
                             bake_space_transform=False,
                             object_types={'MESH', 'ARMATURE', 'EMPTY', 'CAMERA', 'LIGHT'},
                             use_mesh_modifiers=True,
                             mesh_smooth_type='OFF',
                             use_mesh_edges=False,
                             use_tspace=False,
                             use_custom_props=False,
                             add_leaf_bones=False,
                             primary_bone_axis='Y',
                             secondary_bone_axis='X',
                             use_armature_deform_only=False,
                             bake_anim=True,
                             bake_anim_use_all_bones=True,
                             bake_anim_use_nla_strips=True,
                             bake_anim_use_all_actions=True,
                             bake_anim_force_startend_keying=True,
                             bake_anim_step=1,
                             bake_anim_simplify_factor=1.0,
                             path_mode='AUTO',
                             embed_textures=False,
                             batch_mode='OFF',
                             use_metadata=True)
    
    print("FBX upgrade completed successfully")
    
except Exception as e:
    print(f"Error during FBX upgrade: {{str(e)}}")
    sys.exit(1)
""")
        
        # Find Blender executable
        blender_path = None
        for path in ['/Applications/Blender.app/Contents/MacOS/Blender', 'blender']:
            try:
                result = subprocess.run([path, '--version'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
                if result.returncode == 0:
                    blender_path = path
                    break
            except (FileNotFoundError, subprocess.SubprocessError):
                continue
        
        if not blender_path:
            logger.error("Error: Blender executable not found")
            return False
        
        # Run Blender with the script
        cmd = [blender_path, '--background', '--python', blender_script.name]
        
        if verbose:
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd)
        else:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            logger.error(f"Error during FBX upgrade. Return code: {result.returncode}")
            if not verbose and result.stderr:
                error_output = result.stderr.decode('utf-8')
                logger.error(f"Error output: {error_output}")
            return False
        
        return os.path.exists(output_file)
        
    except Exception as e:
        logger.error(f"Error during FBX upgrade: {str(e)}")
        return False
    finally:
        # Clean up the temporary script
        os.unlink(blender_script.name)


def upgrade_fbx_file(
    input_file: str,
    output_file: Optional[str] = None,
    method: str = "blender",
    verbose: bool = False
) -> bool:
    """
    Upgrade an FBX file to a newer version.
    
    Args:
        input_file: Path to input FBX file
        output_file: Path to output upgraded FBX file
        method: Upgrade method to use ('blender', 'fbx-sdk')
        verbose: Enable verbose output
        
    Returns:
        True if upgrade was successful, False otherwise
    """
    logger.info(f"Upgrading FBX file: {input_file}")
    
    if method == "blender":
        return upgrade_fbx_with_blender_legacy(input_file, output_file, verbose)
    elif method == "fbx-sdk":
        logger.error("FBX SDK method not implemented yet")
        return False
    else:
        logger.error(f"Unsupported upgrade method: {method}")
        return False


def check_fbx_upgrade_needed(input_file: str) -> Tuple[bool, str]:
    """
    Check if an FBX file needs upgrading.
    
    Args:
        input_file: Path to FBX file
        
    Returns:
        Tuple of (needs_upgrade, version_info)
    """
    from .converter import detect_fbx_version
    
    version_info = detect_fbx_version(input_file)
    
    # Extract version number for comparison
    version_match = None
    if "Binary FBX" in version_info:
        import re
        version_match = re.search(r'Binary FBX ([\d.]+)', version_info)
    
    if version_match:
        version_num = float(version_match.group(1))
        needs_upgrade = version_num < 7.1
        return needs_upgrade, version_info
    
    return False, version_info 