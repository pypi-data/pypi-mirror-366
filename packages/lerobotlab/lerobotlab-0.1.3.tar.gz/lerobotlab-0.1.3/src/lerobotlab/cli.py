"""
LeRobotLab Tools CLI

Command-line interface for downloading and converting robot datasets from lerobotlab.com.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .download import download_datasets, validate_download_path
from .convert import convert_datasets, validate_output_path, validate_input_path, validate_format


def validate_selection_json(json_path: str) -> Dict[str, Any]:
    """
    Validate and load the selection JSON file.
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        SystemExit: If file doesn't exist or JSON is invalid
    """
    json_file = Path(json_path)
    
    if not json_file.exists():
        print(f"Error: Selection file not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Error reading file {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate required structure
    if not isinstance(data, dict):
        print("Error: Selection JSON must be an object", file=sys.stderr)
        sys.exit(1)
    
    if 'datasets' not in data:
        print("Error: Selection JSON must contain 'datasets' field", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(data['datasets'], list):
        print("Error: 'datasets' field must be an array", file=sys.stderr)
        sys.exit(1)
    
    # Validate each dataset entry
    for i, dataset in enumerate(data['datasets']):
        if not isinstance(dataset, dict):
            print(f"Error: Dataset entry {i} must be an object", file=sys.stderr)
            sys.exit(1)
        
        if 'repo_id' not in dataset:
            print(f"Error: Dataset entry {i} missing 'repo_id' field", file=sys.stderr)
            sys.exit(1)
        
        if 'selected_videos' not in dataset:
            print(f"Error: Dataset entry {i} missing 'selected_videos' field", file=sys.stderr)
            sys.exit(1)
        
        if not isinstance(dataset['selected_videos'], list):
            print(f"Error: Dataset entry {i} 'selected_videos' must be an array", file=sys.stderr)
            sys.exit(1)
    
    return data


def display_selection_summary(data: Dict[str, Any]) -> None:
    """Display a summary of the selection data."""
    metadata = data.get('metadata', {})
    datasets = data.get('datasets', [])
    
    print(f"Total datasets: {len(datasets)}")
    
    if metadata:
        if 'total_episodes' in metadata:
            print(f"Total episodes: {metadata['total_episodes']}")
        if 'total_frames' in metadata:
            print(f"Total frames: {metadata['total_frames']}")
        if 'saved_at' in metadata:
            print(f"Saved at: {metadata['saved_at']}")
    


def handle_download(args):
    """Handle download command."""
    try:
 
        data = validate_selection_json(args.selection_file)
        
        # Validate download path
        validate_download_path(args.download_path)
        
        # Display summary
        print("=== Download Command ===")
        if args.verbose:
            display_selection_summary(data)
            
        # Execute download
        download_datasets(data, args.download_path, args.verbose)
        
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_convert(args):
    """Handle convert command."""
    try:
        # Validate and load selection data
        print("Validating selection file...")
        data = validate_selection_json(args.selection_file)
        
        # Validate paths and format
        validate_output_path(args.output_path)
        validate_input_path(args.input_path)
        format_validated = validate_format(args.format)
        
        # Display summary
        print(f"=== Convert Command ({format_validated.upper()}) ===")
        if args.verbose:
            display_selection_summary(data)
                           
        # Execute conversion
        convert_datasets(data, args.output_path, args.input_path, format_validated, args.verbose)
        
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    LeRobotLab Tools - CLI for processing robot dataset selections.
    
    Export a JSON configuration from lerobotlab.com and use this tool to download
    datasets and convert them to different formats.
    """
    parser = argparse.ArgumentParser(
        description='LeRobotLab Tools - CLI for processing robot dataset selections',
        prog='lerobotlab'
    )
    parser.add_argument('--version', action='version', version='lerobotlab 0.1.2')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Download command
    download_parser = subparsers.add_parser(
        'download',
        help='Download datasets specified in the selection JSON file'
    )
    download_parser.add_argument(
        'selection_file',
        help='Path to the JSON file exported from lerobotlab.com'
    )
    download_parser.add_argument(
        '--download-path',
        required=True,
        help='Directory where datasets will be downloaded'
    )
    download_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    download_parser.set_defaults(func=handle_download)
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert datasets to specified format'
    )
    convert_parser.add_argument(
        'selection_file',
        help='Path to the JSON file exported from lerobotlab.com'
    )
    convert_parser.add_argument(
        '--output-path',
        required=True,
        help='Directory where converted datasets will be saved'
    )
    convert_parser.add_argument(
        '--input-path',
        required=True,
        help='Directory containing downloaded datasets'
    )
    convert_parser.add_argument(
        '--format',
        choices=['vjepa2-ac'],
        required=True,
        help='Output format for converted datasets'
    )
    convert_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    convert_parser.set_defaults(func=handle_convert)
    
    # Parse arguments and call appropriate handler
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    # Check if selection file exists
    if not Path(args.selection_file).exists():
        print(f"Error: Selection file not found: {args.selection_file}", file=sys.stderr)
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
