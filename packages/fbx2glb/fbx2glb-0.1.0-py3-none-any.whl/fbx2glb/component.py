"""
Generate Three.js React components from 3D models.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import fbx
    FBX_SDK_AVAILABLE = True
except ImportError:
    FBX_SDK_AVAILABLE = False

from .utils import setup_logging

logger = logging.getLogger(__name__)


def analyze_model(input_file: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Analyze a 3D model file to extract structure and animation info.

    Args:
        input_file: Path to the input 3D model file
        verbose: Enable verbose output

    Returns:
        Dictionary with model metadata
    """
    # Default model info
    model_info = {
        'filename': os.path.basename(input_file),
        'animations': [],
        'has_skeleton': False,
        'has_mesh': True,
        'node_count': 0,
        'mesh_count': 0,
        'bone_count': 0,
        'is_mixamo': False,
        'root_bone': None
    }

    # Try to determine if it's an FBX file
    is_fbx = input_file.lower().endswith('.fbx')

    if is_fbx and FBX_SDK_AVAILABLE:
        # Use FBX SDK for better analysis
        try:
            # Initialize FBX SDK
            sdk_manager = fbx.FbxManager.Create()
            if not sdk_manager:
                logger.error("Error: Unable to create FBX Manager")
                return model_info

            if verbose:
                logger.debug(f"FBX SDK version: {fbx.FbxManager.GetVersion()}")

            # Create an IOSettings object
            ios = fbx.FbxIOSettings.Create(sdk_manager, fbx.IOSROOT)
            sdk_manager.SetIOSettings(ios)

            # Create an importer
            importer = fbx.FbxImporter.Create(sdk_manager, "")

            # Initialize the importer
            import_status = importer.Initialize(input_file, -1, sdk_manager.GetIOSettings())
            if not import_status:
                logger.error(f"Error: Unable to initialize FBX importer: {importer.GetStatus().GetErrorString()}")
                return model_info

            # Create a new scene
            scene = fbx.FbxScene.Create(sdk_manager, "")

            # Import the contents of the file into the scene
            importer.Import(scene)
            importer.Destroy()

            # Get animation stack info
            stack_count = scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))

            for i in range(stack_count):
                anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
                anim_name = anim_stack.GetName()

                # Get time info
                timespan = anim_stack.GetLocalTimeSpan()
                start_frame = timespan.GetStart().GetFrameCount()
                end_frame = timespan.GetStop().GetFrameCount()
                duration = (end_frame - start_frame) / 30.0  # Assuming 30 fps

                model_info['animations'].append({
                    'name': anim_name,
                    'start_frame': start_frame,
                    'end_frame': end_frame,
                    'duration': duration,
                    'frames': end_frame - start_frame
                })

            # Process scene nodes to get skeleton and mesh info
            root_node = scene.GetRootNode()
            if root_node:
                # Count nodes, bones, and meshes
                model_info['node_count'], model_info['bone_count'], model_info['mesh_count'] = count_node_types(root_node)
                model_info['has_skeleton'] = model_info['bone_count'] > 0
                model_info['has_mesh'] = model_info['mesh_count'] > 0

                # Try to detect if it's a Mixamo model
                model_info['is_mixamo'] = is_mixamo_model(root_node)

                # Get the root bone name if it exists
                model_info['root_bone'] = get_root_bone_name(root_node)

            # Clean up
            sdk_manager.Destroy()

        except Exception as e:
            logger.error(f"Error analyzing FBX file: {str(e)}")

    else:
        # Simple heuristic approach for non-FBX files or when FBX SDK is not available

        # Try to detect animation names from filename
        filename = os.path.basename(input_file).lower()

        # Try to detect if it's a Mixamo model from the filename
        if 'mixamo' in filename or 'xbot' in filename or 'ybot' in filename:
            model_info['is_mixamo'] = True
            model_info['has_skeleton'] = True
            model_info['bone_count'] = 1  # At least 1 bone

        # Try to detect animations from filename
        animation_names = ['idle', 'walk', 'run', 'jump', 'attack', 'death', 'dance', 'samba']
        for anim_name in animation_names:
            if anim_name in filename:
                model_info['animations'].append({
                    'name': anim_name.capitalize(),
                    'duration': 1.0,  # Default duration
                    'frames': 30,     # Default frame count
                })

        # If no specific animation detected, add a generic one
        if not model_info['animations']:
            model_info['animations'].append({
                'name': 'Animation',
                'duration': 1.0,
                'frames': 30,
            })

    if verbose:
        logger.debug(f"Model analysis: {model_info}")

    return model_info


def count_node_types(node):
    """Count total nodes, bones, and meshes in the hierarchy."""
    # Initialize counters
    total_nodes = 1  # Count this node
    bone_count = 0
    mesh_count = 0

    # Check if this node is a bone or mesh
    if node.GetNodeAttribute():
        attr_type = node.GetNodeAttribute().GetAttributeType()
        if attr_type == fbx.FbxNodeAttribute.eSkeleton:
            bone_count = 1
        elif attr_type == fbx.FbxNodeAttribute.eMesh:
            mesh_count = 1

    # Process child nodes
    for i in range(node.GetChildCount()):
        child_nodes, child_bones, child_meshes = count_node_types(node.GetChild(i))
        total_nodes += child_nodes
        bone_count += child_bones
        mesh_count += child_meshes

    return total_nodes, bone_count, mesh_count


def is_mixamo_model(root_node):
    """Check if this appears to be a Mixamo model."""
    # Mixamo models often have specific bone naming conventions
    mixamo_patterns = ['mixamo', 'Hips', 'Spine', 'mixamorig']

    def check_node(node):
        name = node.GetName()
        for pattern in mixamo_patterns:
            if pattern in name:
                return True

        for i in range(node.GetChildCount()):
            if check_node(node.GetChild(i)):
                return True

        return False

    return check_node(root_node)


def get_root_bone_name(root_node):
    """Get the name of the root bone if it exists."""
    # Common root bone names
    root_bone_names = ['Hips', 'root', 'Armature', 'Bip01', 'Root']

    def find_root_bone(node):
        # Check if this is a likely root bone
        if node.GetNodeAttribute() and node.GetNodeAttribute().GetAttributeType() == fbx.FbxNodeAttribute.eSkeleton:
            name = node.GetName()
            for root_name in root_bone_names:
                if root_name in name:
                    return name

        # Check children
        for i in range(node.GetChildCount()):
            result = find_root_bone(node.GetChild(i))
            if result:
                return result

        return None

    result = find_root_bone(root_node)
    if result:
        return result

    # If no standard root bone found, just return the first bone
    def find_first_bone(node):
        if node.GetNodeAttribute() and node.GetNodeAttribute().GetAttributeType() == fbx.FbxNodeAttribute.eSkeleton:
            return node.GetName()

        for i in range(node.GetChildCount()):
            result = find_first_bone(node.GetChild(i))
            if result:
                return result

        return None

    return find_first_bone(root_node)


def generate_component(
    input_file: str,
    output_file: Optional[str] = None,
    component_name: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Generate a React/Three.js component for a 3D model.

    Args:
        input_file: Path to the input 3D model file
        output_file: Path to the output component file (optional)
        component_name: Name of the component (optional)
        verbose: Enable verbose output

    Returns:
        True if component generation was successful, False otherwise
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level)

    # Validate input file
    if not os.path.exists(input_file):
        logger.error(f"Input file '{input_file}' does not exist")
        return False

    # Analyze the model
    model_info = analyze_model(input_file, verbose)

    # Determine component name if not specified
    if not component_name:
        base_name = os.path.splitext(model_info['filename'])[0]
        # Clean up the name for use as a component
        base_name = ''.join(c if c.isalnum() else ' ' for c in base_name)
        words = base_name.split()
        component_name = ''.join(word.capitalize() for word in words) + 'Model'

    # Determine output file if not specified
    if not output_file:
        output_file = f"src/components/models/{component_name}.tsx"

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Determine relative path to model
    input_path = Path(input_file)
    if input_path.suffix.lower() == '.fbx':
        # Assume there will be a GLB version with the same name
        rel_path = input_path.with_suffix('.glb').name
    else:
        rel_path = input_path.name

    # Determine appropriate model path
    if input_path.is_relative_to(Path.cwd()):
        # Try to make a relative path from the current directory
        rel_to_current = input_path.relative_to(Path.cwd())

        # Check if it's in a standard model directory
        for model_dir in ['public/models', 'models', 'assets/models']:
            if str(rel_to_current).startswith(model_dir):
                # Strip the public part if present
                if model_dir.startswith('public/'):
                    model_path = f"/{'/'.join(rel_to_current.parts[1:])}"
                    break
                else:
                    model_path = f"/{str(rel_to_current)}"
                    break
        else:
            # Not in a standard location, make a best guess
            if str(rel_to_current).startswith('public/'):
                model_path = f"/{'/'.join(rel_to_current.parts[1:])}"
            else:
                model_path = f"/{str(rel_to_current)}"

        # If it's an FBX, change to GLB
        if model_path.lower().endswith('.fbx'):
            model_path = model_path[:-4] + '.glb'
    else:
        # Just use the filename
        model_path = f"/models/{rel_path}"
        if model_path.lower().endswith('.fbx'):
            model_path = model_path[:-4] + '.glb'

    # Generate component code
    component_code = generate_component_code(component_name, model_path, model_info)

    # Write the component to the output file
    try:
        with open(output_file, 'w') as f:
            f.write(component_code)

        if verbose:
            logger.debug(f"Component successfully generated: {output_file}")

        logger.info(f"Component '{component_name}' generated successfully: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error writing component file: {str(e)}")
        return False


def generate_component_code(component_name: str, model_path: str, model_info: Dict[str, Any]) -> str:
    """
    Generate the React component code.

    Args:
        component_name: Name of the component
        model_path: Path to the model file
        model_info: Dictionary with model metadata

    Returns:
        String containing the component code
    """
    # Determine if we have animations
    has_animations = len(model_info['animations']) > 0
    default_animation = model_info['animations'][0]['name'] if has_animations else 'undefined'

    # Build animation list for documentation
    animation_list = ', '.join(f"'{a['name']}'" for a in model_info['animations']) if has_animations else 'None'

    # Skeleton information
    skeleton_info = "Has skeleton" if model_info['has_skeleton'] else "No skeleton"
    if model_info['root_bone']:
        skeleton_info += f", root bone: '{model_info['root_bone']}'"

    # Build the component code
    return f"""import {{ useRef, useEffect, useState }} from 'react';
import {{ useFrame, useThree }} from '@react-three/fiber';
import {{ useGLTF, useAnimations }} from '@react-three/drei';
import * as THREE from 'three';

/**
 * Component for the {component_name} 3D model
 * Generated by fbx2glb from {model_info['filename']}
 * 
 * Animations: {animation_list}
 * {skeleton_info}
 * Meshes: {model_info['mesh_count']}
 */
export function {component_name}({{
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = [1, 1, 1],
  animation = {repr(default_animation) if has_animations else 'undefined'},
  animationSpeed = 1.0,
  debug = false,
  ...props
}}) {{
  const group = useRef();
  const {{ scene, animations }} = useGLTF('{model_path}');
  const {{ actions, names }} = useAnimations(animations, group);
  const [currentAnimation, setCurrentAnimation] = useState(animation);

  // Handle animation changes
  useEffect(() => {{
    if (!actions || Object.keys(actions).length === 0) return;

    // Stop any playing animations
    Object.values(actions).forEach(action => action?.stop());

    // If animation is defined and exists, play it
    if (currentAnimation && actions[currentAnimation]) {{
      const action = actions[currentAnimation];
      action.reset().play();
      action.setEffectiveTimeScale(animationSpeed);

      if (debug) {{
        console.log(`Playing animation: ${{currentAnimation}}`);
      }}
    }}

    return () => {{
      // Cleanup animations on unmount
      Object.values(actions).forEach(action => action?.stop());
    }};
  }}, [actions, currentAnimation, animationSpeed, debug]);

  // Update animation speed when it changes
  useEffect(() => {{
    if (!actions || !currentAnimation || !actions[currentAnimation]) return;
    actions[currentAnimation].setEffectiveTimeScale(animationSpeed);
  }}, [animationSpeed, actions, currentAnimation]);

  // Change animation
  const setAnimation = (animName) => {{
    if (animName && actions && actions[animName]) {{
      setCurrentAnimation(animName);
    }}
  }};

  // Debug output when the component mounts
  useEffect(() => {{
    if (debug) {{
      console.log('Model loaded:', scene);
      console.log('Available animations:', names);
      console.log('Animation actions:', actions);
    }}

    // Preload the model
    return () => {{
      // Cleanup on unmount
    }};
  }}, [scene, animations, actions, names, debug]);

  return (
    <group ref={{group}} position={{position}} rotation={{rotation}} scale={{scale}} {{...props}}>
      <primitive object={{scene}} />
    </group>
  );
}}

// Add animation control methods to the component
{component_name}.setAnimation = (group, animName) => {{
  if (!group.current) return;
  const actions = group.current._currentActions;
  if (actions && actions[animName]) {{
    // Stop all current animations
    Object.values(actions).forEach(action => action?.stop());
    // Play the requested animation
    actions[animName].reset().play();
  }}
}};

// List available animations
{component_name}.animations = {str([a['name'] for a in model_info['animations']])};

// Preload the model
useGLTF.preload('{model_path}');
"""


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate React/Three.js component from a 3D model')
    parser.add_argument('input_file', help='Path to input 3D model file')
    parser.add_argument('output_file', nargs='?', help='Path to output component file (optional)')
    parser.add_argument('--name', help='Component name (default: derived from filename)')
    parser.add_argument('--force', '-f', action='store_true', help='Force overwrite if output file exists')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    return parser.parse_args()


def main() -> int:
    """Main entry point for component generation."""
    args = parse_args()

    # Validate input file
    if not os.path.exists(args.input_file):
        logger.error(f"Input file '{args.input_file}' does not exist")
        return 1

    # Check if output file exists
    if args.output_file and os.path.exists(args.output_file) and not args.force:
        logger.error(f"Output file '{args.output_file}' already exists. Use --force to overwrite.")
        return 1

    # Generate the component
    success = generate_component(
        args.input_file,
        args.output_file,
        args.name,
        args.verbose
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
