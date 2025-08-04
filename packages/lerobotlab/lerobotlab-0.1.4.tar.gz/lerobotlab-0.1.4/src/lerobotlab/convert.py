"""
LeRobotLab Tools - Convert Module

Handles conversion of robot datasets to V-JEPA2-AC format.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from .droid_conversion import DROIDConverter
from .vjepa2_ac_conversion import VJEPA2ACConverter


def convert_datasets(
    selection_data: Dict[str, Any],
    output_path: str,
    input_path: str,
    format: str,
    verbose: bool = False
) -> None:
    try:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Created output directory: {output_dir.absolute()}")

        input_dir = Path(input_path)
        if not input_dir.exists():
            print(f"Error: Input directory does not exist: {input_path}", file=sys.stderr)
            sys.exit(1)
 
        datasets = selection_data.get('datasets', [])
        
        if verbose:
            metadata = selection_data.get('metadata', {})
            print(f"Converting {len(datasets)} datasets to {format.upper()} format...")
            if 'total_episodes' in metadata:
                print(f"Total episodes to convert: {metadata['total_episodes']}")
        
        # Process each dataset
        converter = _get_converter(format, verbose)
        for i, dataset in enumerate(datasets, 1):
            repo_id = dataset['repo_id']
            selected_videos = dataset['selected_videos']    
            if verbose:
                print(f"\n[{i}/{len(datasets)}] Converting dataset: {repo_id}")
                print(f"Selected videos: {', '.join(selected_videos)}")
            
            result = converter.convert_dataset(repo_id, selected_videos, input_dir, output_dir)
            
            if result['status'] == 'error':
                print(f"Conversion failed")
            elif verbose:
                if 'episodes_converted' in result:
                    print(f"Converted {result['episodes_converted']} episodes")
                    print(f"Output directory: {output_dir}")

    except Exception as e:
        print(f"Error: Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


def validate_output_path(output_path: str) -> Path:
    try:
        path = Path(output_path)
        
        # Check if parent directory is writable
        parent = path.parent
        if not parent.exists():
            print(f"Error: Parent directory does not exist: {parent}", file=sys.stderr)
            sys.exit(1)
        
        if not os.access(parent, os.W_OK):
            print(f"Error: No write permission for directory: {parent}", file=sys.stderr)
            sys.exit(1)
        
        return path
        
    except Exception as e:
        print(f"Error: Invalid output path: {e}", file=sys.stderr)
        sys.exit(1)


def validate_input_path(input_path: str) -> Path:
    try:
        path = Path(input_path)
        
        if not path.exists():
            print(f"Error: Input directory does not exist: {input_path}", file=sys.stderr)
            sys.exit(1)
        
        if not path.is_dir():
            print(f"Error: Input path is not a directory: {input_path}", file=sys.stderr)
            sys.exit(1)
        
        if not os.access(path, os.R_OK):
            print(f"Error: No read permission for directory: {input_path}", file=sys.stderr)
            sys.exit(1)
        
        return path
        
    except Exception as e:
        print(f"Error: Invalid input path: {e}", file=sys.stderr)
        sys.exit(1)


def get_supported_formats() -> List[str]:
    """Get all supported conversion formats (including those not yet available in CLI)."""
    return ['droid', 'vjepa2-ac']


def validate_format(format: str) -> str:
    format_lower = format.lower()
    supported = get_supported_formats()
    
    if format_lower not in supported:
        print(f"Error: Unsupported format '{format}'. Supported formats: {', '.join(supported)}", file=sys.stderr)
        sys.exit(1)
    
    return format_lower



def _get_converter(format: str, verbose: bool = False):
    """
    Factory function to get the appropriate converter based on format.
    
    Args:
        format: Target conversion format ('droid' or 'vjepa2-ac')
        verbose: Whether to enable verbose logging
        
    Returns:
        Converter instance for the specified format
        
    Raises:
        SystemExit: If format is not supported
    """
    if format == 'droid':
        return DROIDConverter(verbose=verbose)
    elif format == 'vjepa2-ac':
        return VJEPA2ACConverter(verbose=verbose)
    else:
        print(f"Error: Unsupported format: {format}. Supported formats: {get_supported_formats()}", file=sys.stderr)
        sys.exit(1) 