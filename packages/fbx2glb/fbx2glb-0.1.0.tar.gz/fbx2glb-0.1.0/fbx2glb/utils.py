"""
Utility functions for the fbx2glb package.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

def setup_logging(level=logging.INFO):
    """
    Set up logging configuration.

    Args:
        level: Logging level
    """
    # Get the root logger
    logger = logging.getLogger('fbx2glb')

    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configure the logger
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


def find_conversion_tool() -> Optional[str]:
    """
    Find available conversion tool.

    Returns:
        Name of the available conversion tool, or None if none found
    """
    # Check for fbx2gltf
    try:
        subprocess.run(['fbx2gltf', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'fbx2gltf'
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    # Check for Blender
    for blender_path in ['/Applications/Blender.app/Contents/MacOS/Blender', 
                         'blender']:
        try:
            result = subprocess.run([blender_path, '--version'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
            if result.returncode == 0:
                return 'blender'
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

    return None


def load_config(config_path=None):
    """
    Load configuration from a .fbx2glb.json file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    # Default configuration
    default_config = {
        'defaultMethod': None,
        'fallbackMethods': ['fbx2gltf', 'blender'],
        'blenderPath': None,
        'outputFormat': 'glb',
        'preserveAnimations': True,
        'optimizeMeshes': True
    }

    if not config_path:
        # Look for config in current directory and parent directories
        current_dir = Path.cwd()
        while current_dir.parent != current_dir:  # Stop at root
            config_file = current_dir / '.fbx2glb.json'
            if config_file.exists():
                config_path = str(config_file)
                break
            current_dir = current_dir.parent

    # Load configuration if found
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        except Exception as e:
            logging.warning(f"Error loading configuration from {config_path}: {str(e)}")

    return default_config


def find_models_directory() -> Optional[Path]:
    """
    Find the models directory in the project.

    Returns:
        Path to the models directory, or None if not found
    """
    # Common model directory names
    model_dir_names = ['models', 'assets/models', 'public/models', '3d', 'assets/3d']

    # Start from current directory and check common locations
    current_dir = Path.cwd()

    # First, check direct subdirectories
    for name in model_dir_names:
        model_dir = current_dir / name
        if model_dir.exists() and model_dir.is_dir():
            return model_dir

    # Then check for a 'public' directory
    public_dir = current_dir / 'public'
    if public_dir.exists() and public_dir.is_dir():
        for name in model_dir_names:
            model_dir = public_dir / name.split('/')[-1]
            if model_dir.exists() and model_dir.is_dir():
                return model_dir

    # Check for an 'assets' directory
    assets_dir = current_dir / 'assets'
    if assets_dir.exists() and assets_dir.is_dir():
        for name in model_dir_names:
            model_dir = assets_dir / name.split('/')[-1]
            if model_dir.exists() and model_dir.is_dir():
                return model_dir

    # As a last resort, look for any directory with FBX files
    for root, dirs, files in os.walk(current_dir, topdown=True, followlinks=False):
        if any(f.lower().endswith('.fbx') for f in files):
            return Path(root)

        # Limit depth to prevent excessive searching
        if root.count(os.sep) - current_dir.count(os.sep) > 3:
            dirs.clear()  # Don't go deeper

    return None


def check_dependencies():
    """
    Check for required and optional dependencies.

    Returns:
        Dictionary with dependency status
    """
    dependencies = {
        'fbx_sdk': False,
        'fbx2gltf': False,
        'blender': False,
        'numpy': False
    }

    # Check for FBX SDK
    try:
        import fbx
        dependencies['fbx_sdk'] = True
    except ImportError:
        pass

    # Check for NumPy
    try:
        import numpy
        dependencies['numpy'] = True
    except ImportError:
        pass

    # Check for fbx2gltf
    try:
        subprocess.run(['fbx2gltf', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        dependencies['fbx2gltf'] = True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    # Check for Blender
    for blender_path in ['/Applications/Blender.app/Contents/MacOS/Blender', 
                        'blender']:
        try:
            result = subprocess.run([blender_path, '--version'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
            if result.returncode == 0:
                dependencies['blender'] = True
                break
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

    return dependencies
