"""
Command-line interface for fbx2glb.
"""

import os
import sys
import logging
from pathlib import Path

from .converter import convert_file_with_params
from .utils import setup_logging, check_dependencies
from .params import ConversionParams
from params_proto import ARGS as Args

logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for single file conversion."""
    # Parse arguments using argparse for now
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert FBX files to GLB format")
    parser.add_argument("input_file", help="Path to input FBX file")
    parser.add_argument("output_file", nargs="?", help="Path to output GLB file")
    parser.add_argument("--method", choices=["fbx-sdk", "fbx2gltf", "blender"], help="Conversion method to use")
    parser.add_argument("--force", action="store_true", help="Force overwrite if output file exists")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--fix-axis", action="store_true", help="Fix axis orientation (rotate model to face up)")
    parser.add_argument("--export-yup", action="store_true", default=True, help="Export with Y-up coordinate system")
    parser.add_argument("--no-export-yup", action="store_true", help="Export with Z-up coordinate system")
    parser.add_argument("--upgrade-fbx", action="store_true", help="Upgrade FBX file to newer version before conversion")
    parser.add_argument("--check-dependencies", action="store_true", help="Check for required dependencies and exit")
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    
    args = parser.parse_args()
    
    # Handle export-yup vs no-export-yup
    if args.no_export_yup:
        args.export_yup = False

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    # Handle utility commands
    if args.check_dependencies:
        deps = check_dependencies()
        print("FBX2GLB Dependencies:")
        print(f"  FBX SDK: {'✅' if deps['fbx_sdk'] else '❌'}")
        print(f"  fbx2gltf: {'✅' if deps['fbx2gltf'] else '❌'}")
        print(f"  Blender: {'✅' if deps['blender'] else '❌'}")
        print(f"  NumPy: {'✅' if deps['numpy'] else '❌'}")

        # Check if at least one conversion method is available
        if not (deps['fbx_sdk'] or deps['fbx2gltf'] or deps['blender']):
            print("\n❌ No conversion methods available. Please install at least one of:")
            print("  - Autodesk FBX SDK Python bindings")
            print("  - Facebook's fbx2gltf command line tool")
            print("  - Blender")
            return 1
        else:
            print("\n✅ At least one conversion method is available.")
            return 0

    if args.version:
        from . import __version__
        print(f"fbx2glb version {__version__}")
        return 0

    # For utility commands, we don't need input_file
    if args.check_dependencies or args.version:
        return 0

    # Validate input file
    if not args.input_file:
        logger.error("Input file is required")
        return 1
        
    if not os.path.exists(args.input_file):
        logger.error(f"Input file '{args.input_file}' does not exist")
        return 1

    # Check if FBX upgrade is needed
    if args.upgrade_fbx:
        from .fbx_upgrader import check_fbx_upgrade_needed, upgrade_fbx_file
        
        needs_upgrade, version_info = check_fbx_upgrade_needed(args.input_file)
        if needs_upgrade:
            logger.info(f"FBX file needs upgrade: {version_info}")
            logger.info("Attempting to upgrade FBX file...")
            
            # Create upgraded file path
            input_base = os.path.splitext(args.input_file)[0]
            upgraded_file = f"{input_base}_upgraded.fbx"
            
            if upgrade_fbx_file(args.input_file, upgraded_file, verbose=args.verbose):
                logger.info(f"FBX upgrade successful: {upgraded_file}")
                # Update the input file path
                args.input_file = upgraded_file
            else:
                logger.error("FBX upgrade failed")
                return 1
        else:
            logger.info(f"FBX file is already compatible: {version_info}")

    # Perform conversion
    success = convert_file_with_params(args)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
