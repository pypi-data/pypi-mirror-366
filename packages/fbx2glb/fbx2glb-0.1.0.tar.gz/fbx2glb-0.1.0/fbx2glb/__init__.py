"""
FBX2GLB - FBX to GLB Conversion Toolkit

A toolkit for converting FBX 3D models to GLB format for web applications.
"""

__version__ = "0.1.0"

from .converter import convert_file_with_params, detect_fbx_version
from .batch import batch_convert
from .component import generate_component
from .utils import setup_logging, find_conversion_tool

# Check for FBX SDK availability
try:
    import fbx
    FBX_SDK_AVAILABLE = True
except ImportError:
    FBX_SDK_AVAILABLE = False

__all__ = [
    "convert_file",
    "batch_convert",
    "generate_component",
    "detect_fbx_version",
    "setup_logging",
    "find_conversion_tool",
    "FBX_SDK_AVAILABLE"
]
