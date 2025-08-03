"""
LeRobotLab Tools CLI

Command-line interface for downloading and converting robot datasets from lerobotlab.com.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import click

from .download import download_datasets, validate_download_path, estimate_download_size
from .convert import convert_datasets, validate_output_path, validate_input_path, validate_format, estimate_conversion_time


def validate_selection_json(json_path: str) -> Dict[str, Any]:
    """
    Validate and load the selection JSON file.
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        click.ClickException: If file doesn't exist or JSON is invalid
    """
    json_file = Path(json_path)
    
    if not json_file.exists():
        raise click.ClickException(f"Selection file not found: {json_path}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON format in {json_path}: {e}")
    except Exception as e:
        raise click.ClickException(f"Error reading file {json_path}: {e}")
    
    # Validate required structure
    if not isinstance(data, dict):
        raise click.ClickException("Selection JSON must be an object")
    
    if 'datasets' not in data:
        raise click.ClickException("Selection JSON must contain 'datasets' field")
    
    if not isinstance(data['datasets'], list):
        raise click.ClickException("'datasets' field must be an array")
    
    # Validate each dataset entry
    for i, dataset in enumerate(data['datasets']):
        if not isinstance(dataset, dict):
            raise click.ClickException(f"Dataset entry {i} must be an object")
        
        if 'repo_id' not in dataset:
            raise click.ClickException(f"Dataset entry {i} missing 'repo_id' field")
        
        if 'selected_videos' not in dataset:
            raise click.ClickException(f"Dataset entry {i} missing 'selected_videos' field")
        
        if not isinstance(dataset['selected_videos'], list):
            raise click.ClickException(f"Dataset entry {i} 'selected_videos' must be an array")
    
    return data


def display_selection_summary(data: Dict[str, Any]) -> None:
    """Display a summary of the selection data."""
    metadata = data.get('metadata', {})
    datasets = data.get('datasets', [])
    
    click.echo(f"Selection contains {len(datasets)} datasets")
    
    if metadata:
        if 'total_episodes' in metadata:
            click.echo(f"Total episodes: {metadata['total_episodes']}")
        if 'total_frames' in metadata:
            click.echo(f"Total frames: {metadata['total_frames']}")
        if 'saved_at' in metadata:
            click.echo(f"Saved at: {metadata['saved_at']}")
    
    # Show download size estimate
    size_estimate = estimate_download_size(data)
    if size_estimate:
        click.echo(f"Estimated download size: {size_estimate}")
    
    click.echo("\nDatasets:")
    for dataset in datasets:
        click.echo(f"  - {dataset['repo_id']}")
        for video in dataset['selected_videos']:
            click.echo(f"    * {video}")


@click.group()
@click.version_option(version="0.1.0", prog_name="lerobotlab")
def main():
    """
    LeRobotLab Tools - CLI for processing robot dataset selections.
    
    Export a JSON configuration from lerobotlab.com and use this tool to download
    datasets and convert them to different formats.
    """
    pass


@main.command()
@click.argument('selection_file', type=click.Path(exists=True, path_type=str))
@click.option(
    '--download-path', 
    required=True,
    type=click.Path(path_type=str),
    help='Directory where datasets will be downloaded'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
def download(selection_file: str, download_path: str, verbose: bool):
    """
    Download datasets specified in the selection JSON file.
    
    SELECTION_FILE: Path to the JSON file exported from lerobotlab.com
    """
    try:
        # Validate and load selection data
        click.echo("Validating selection file...")
        data = validate_selection_json(selection_file)
        
        # Validate download path
        validate_download_path(download_path)
        
        # Display summary
        click.echo("=== Download Command ===")
        if verbose:
            display_selection_summary(data)
            
            # Show conversion time estimate
            time_estimate = estimate_conversion_time(data)
            if time_estimate:
                click.echo(f"Estimated download time: {time_estimate}")
        
        # Confirm before proceeding
        if not verbose:
            datasets_count = len(data.get('datasets', []))
            click.echo(f"Ready to download {datasets_count} datasets to: {download_path}")
        
        # Execute download
        download_datasets(data, download_path, verbose)
        
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


@main.command()
@click.argument('selection_file', type=click.Path(exists=True, path_type=str))
@click.option(
    '--output-path',
    required=True,
    type=click.Path(path_type=str),
    help='Directory where converted datasets will be saved'
)
@click.option(
    '--input-path',
    type=click.Path(path_type=str),
    help='Directory containing downloaded datasets (will download if not provided)'
)
@click.option(
    '--format',
    type=click.Choice(['droid', 'vjepa2-ac'], case_sensitive=False),
    default='droid',
    help='Output format for converted datasets'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
def convert(selection_file: str, output_path: str, input_path: Optional[str], 
           format: str, verbose: bool):
    """
    Convert datasets to specified format.
    
    SELECTION_FILE: Path to the JSON file exported from lerobotlab.com
    """
    try:
        # Validate and load selection data
        click.echo("Validating selection file...")
        data = validate_selection_json(selection_file)
        
        # Validate paths and format
        validate_output_path(output_path)
        if input_path:
            validate_input_path(input_path)
        format = validate_format(format)
        
        # Display summary
        click.echo(f"=== Convert Command ({format.upper()}) ===")
        if verbose:
            display_selection_summary(data)
            
            # Show conversion time estimate
            time_estimate = estimate_conversion_time(data)
            if time_estimate:
                click.echo(f"Estimated conversion time: {time_estimate}")
        
        # Confirm before proceeding
        if not verbose:
            datasets_count = len(data.get('datasets', []))
            if input_path:
                click.echo(f"Ready to convert {datasets_count} datasets from: {input_path}")
            else:
                click.echo(f"Ready to download and convert {datasets_count} datasets")
            click.echo(f"Output: {output_path} ({format.upper()} format)")
        
        # Execute conversion
        convert_datasets(data, output_path, input_path, format, verbose)
        
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
