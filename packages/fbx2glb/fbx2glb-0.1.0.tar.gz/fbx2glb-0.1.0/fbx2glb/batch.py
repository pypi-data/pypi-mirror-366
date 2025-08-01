"""
Batch FBX to GLB conversion module.
"""

import os
import sys
import argparse
import multiprocessing
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union, Any, Callable
import logging

from .converter import convert_file_with_params
from .utils import setup_logging

logger = logging.getLogger(__name__)


def find_fbx_files(source_dir: str, recursive: bool = False) -> List[Path]:
    """
    Find all FBX files in the source directory.

    Args:
        source_dir: Source directory containing FBX files
        recursive: Process subdirectories recursively

    Returns:
        List of paths to FBX files
    """
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Source directory '{source_dir}' does not exist or is not a directory")
        return []

    if recursive:
        return list(source_path.glob('**/*.fbx'))
    else:
        return list(source_path.glob('*.fbx'))


def get_output_path(fbx_file: Path, source_dir: str, output_dir: Optional[str] = None) -> Path:
    """
    Determine the output path for a GLB file.

    Args:
        fbx_file: Path to the FBX file
        source_dir: Source directory containing FBX files
        output_dir: Output directory for GLB files (optional)

    Returns:
        Path to the output GLB file
    """
    if output_dir:
        # Preserve directory structure relative to source_dir
        rel_path = fbx_file.relative_to(source_dir)
        output_path = Path(output_dir) / rel_path.with_suffix('.glb')
    else:
        # Use the same directory as the source file
        output_path = fbx_file.with_suffix('.glb')

    # Create the output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def convert_file_task(args: Tuple[Path, Path, str, bool, bool, Dict[str, Any]]) -> Tuple[Path, bool, str]:
    """
    Convert a single FBX file to GLB (for multiprocessing).

    Args:
        args: Tuple containing (fbx_file, output_path, method, force, verbose, kwargs)

    Returns:
        Tuple containing (fbx_file, success, status_message)
    """
    fbx_file, output_path, method, force, verbose, kwargs = args

    # Skip if output file exists and force is not specified
    if output_path.exists() and not force:
        if verbose:
            logger.info(f"Skipping '{fbx_file}' (output file exists)")
        return (fbx_file, False, "Output file exists")

    try:
        success = convert_file(
            str(fbx_file),
            str(output_path),
            method=method,
            force=force,
            verbose=verbose,
            **kwargs
        )

        status_msg = "Success" if success else "Failed"

        if verbose:
            status_icon = "✅" if success else "❌"
            logger.info(f"{status_icon} {fbx_file.name} → {output_path.name}")

        return (fbx_file, success, status_msg)
    except Exception as e:
        return (fbx_file, False, str(e))


def batch_convert(
    source_dir: str,
    output_dir: Optional[str] = None,
    recursive: bool = False,
    method: Optional[str] = None,
    force: bool = False,
    parallel: int = 0,
    verbose: bool = False,
    **kwargs
) -> Tuple[int, int]:
    """
    Batch convert FBX files to GLB format.

    Args:
        source_dir: Source directory containing FBX files
        output_dir: Output directory for GLB files (optional)
        recursive: Process subdirectories recursively
        method: Conversion method to use ('fbx-sdk', 'fbx2gltf', 'blender')
        force: Force overwrite if output files exist
        parallel: Number of parallel conversion processes (0 = auto)
        verbose: Enable verbose output
        **kwargs: Additional method-specific parameters

    Returns:
        Tuple containing (number of successes, number of failures)
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level)

    # Find all FBX files in the source directory
    fbx_files = find_fbx_files(source_dir, recursive)

    if not fbx_files:
        logger.warning(f"No FBX files found in '{source_dir}'")
        return (0, 0)

    logger.info(f"Found {len(fbx_files)} FBX files to convert")

    # Prepare conversion arguments
    conversion_args = []
    for fbx_file in fbx_files:
        output_path = get_output_path(fbx_file, source_dir, output_dir)
        conversion_args.append((fbx_file, output_path, method, force, verbose, kwargs))

    # Determine number of processes
    num_processes = parallel
    if num_processes <= 0:
        num_processes = min(multiprocessing.cpu_count(), len(fbx_files))

    # Show summary before starting
    logger.info(f"Starting conversion with {num_processes} processes:")
    logger.info(f"  Source directory: {source_dir}")
    logger.info(f"  Output directory: {output_dir if output_dir else 'Same as source'}")
    logger.info(f"  Recursive: {'Yes' if recursive else 'No'}")
    logger.info(f"  Force overwrite: {'Yes' if force else 'No'}")

    # Perform conversion
    results = []
    if num_processes > 1 and len(fbx_files) > 1:
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.map(convert_file_task, conversion_args)
    else:
        results = [convert_file_task(args) for args in conversion_args]

    # Count successes and failures
    successes = sum(1 for _, success, _ in results if success)
    failures = len(results) - successes

    # Print summary
    logger.info(f"\nConversion complete: {successes} succeeded, {failures} failed")

    if failures > 0 and verbose:
        logger.warning("\nFailed conversions:")
        for fbx_file, success, msg in results:
            if not success:
                logger.warning(f"  {fbx_file.name}: {msg}")

    return (successes, failures)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Batch convert FBX files to GLB format')
    parser.add_argument('source_dir', help='Source directory containing FBX files')
    parser.add_argument('output_dir', nargs='?', help='Output directory for GLB files (optional)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process subdirectories recursively')
    parser.add_argument('--method', choices=['fbx-sdk', 'fbx2gltf', 'blender'], help='Conversion method to use')
    parser.add_argument('--force', '-f', action='store_true', help='Force overwrite if output files exist')
    parser.add_argument('--parallel', '-p', type=int, default=0, help='Number of parallel conversion processes (0 = auto)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    # Advanced options
    parser.add_argument('--draco', action='store_true', help='Use Draco compression (fbx2gltf only)')
    parser.add_argument('--no-texture-optimization', action='store_true', help='Disable texture optimization (fbx2gltf only)')
    parser.add_argument('--blender-path', help='Path to Blender executable')

    return parser.parse_args()


def main() -> int:
    """Main entry point for batch conversion."""
    args = parse_args()

    # Extract kwargs for additional parameters
    kwargs = {
        'draco': args.draco,
        'no_texture_optimization': args.no_texture_optimization,
        'blender_path': args.blender_path
    }

    successes, failures = batch_convert(
        args.source_dir,
        args.output_dir,
        recursive=args.recursive,
        method=args.method,
        force=args.force,
        parallel=args.parallel,
        verbose=args.verbose,
        **kwargs
    )

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
