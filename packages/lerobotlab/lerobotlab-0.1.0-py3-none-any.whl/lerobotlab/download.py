"""
LeRobotLab Tools - Download Module

Handles downloading of robot datasets from repositories specified in selection files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from lerobot.datasets.lerobot_dataset import LeRobotDataset

import click

def download_dataset(video_key, dataset_repo_id, download_dir):
    """
    Download dataset using LeRobot
    
    Args:
        video_key: The video key identifier
        dataset_repo_id: Dataset name in format "username/foldername"
        download_dir: Base folder to store downloads
    
    Returns:
        dict: Download result with status and details
    """
    try:
        # Parse username and foldername from dataset
        username, foldername = dataset_repo_id.split('/')
        
        # Create folder structure: storage_folder/username/foldername
        dataset_folder = Path(download_dir) / username / foldername
        dataset_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"  Downloading dataset: {dataset_repo_id}")
        print(f"  Video key: {video_key}")
        print(f"  Target folder: {dataset_folder}")
        
        # Load/download dataset using LeRobot
        dataset_obj = LeRobotDataset(dataset_repo_id, root=str(dataset_folder))
                
        return {
            'status': 'success',
            'video_key': video_key,
            'dataset': dataset_repo_id,
            'folder': str(dataset_folder),
            'dataset_length': len(dataset_obj),
            'message': f"Downloaded {dataset_repo_id} ({len(dataset_obj)} episodes) to {dataset_folder}"
        }
        
    except Exception as e:
        print(f"  Error downloading dataset {dataset_repo_id}: {e}")
        return {
            'status': 'error',
            'video_key': video_key,
            'dataset': dataset_repo_id,
            'folder': None,
            'dataset_length': 0,
            'message': f"Error downloading {dataset_repo_id}: {str(e)}"
        }



def download_datasets(
    selection_data: Dict[str, Any], 
    download_path: str, 
    verbose: bool = False
) -> None:
    try:
        # Create download directory if it doesn't exist
        download_dir = Path(download_path)
        download_dir.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            click.echo(f"Created download directory: {download_dir.absolute()}")
        
        # Get datasets from selection
        datasets = selection_data.get('datasets', [])
        
        if verbose:
            metadata = selection_data.get('metadata', {})
            click.echo(f"Processing {len(datasets)} datasets...")
            if 'total_episodes' in metadata:
                click.echo(f"Total episodes to download: {metadata['total_episodes']}")
            if 'total_frames' in metadata:
                click.echo(f"Total frames to download: {metadata['total_frames']}")
        
        # Process each dataset
        for i, dataset in enumerate(datasets, 1):
            repo_id = dataset['repo_id']
            selected_videos = dataset['selected_videos']
            
            if verbose:
                click.echo(f"\n[{i}/{len(datasets)}] Processing dataset: {repo_id}")
                click.echo(f"Selected videos: {', '.join(selected_videos)}")
            
            for video in selected_videos:
                download_dataset(video, repo_id, download_dir)
            
            if verbose:
                click.echo(f"  -> Dataset {repo_id} downloaded successfully")
        
        click.echo(f"\nAll {len(datasets)} datasets downloaded to: {download_dir.absolute()}")
        
    except Exception as e:
        raise click.ClickException(f"Download failed: {e}")


def validate_download_path(download_path: str) -> Path:
    try:
        path = Path(download_path)
        
        # Check if parent directory is writable
        parent = path.parent
        if not parent.exists():
            raise click.ClickException(f"Parent directory does not exist: {parent}")
        
        if not os.access(parent, os.W_OK):
            raise click.ClickException(f"No write permission for directory: {parent}")
        
        return path
        
    except Exception as e:
        if isinstance(e, click.ClickException):
            raise
        raise click.ClickException(f"Invalid download path: {e}")


def estimate_download_size(selection_data: Dict[str, Any]) -> Optional[str]:
    metadata = selection_data.get('metadata', {})
    total_frames = metadata.get('total_frames')
    
    if total_frames:
        # Rough estimate: assume ~100KB per frame (varies greatly by resolution/compression)
        estimated_bytes = total_frames * 100 * 1024
        
        # Convert to human readable format
        if estimated_bytes < 1024**2:
            return f"~{estimated_bytes / 1024:.1f} KB"
        elif estimated_bytes < 1024**3:
            return f"~{estimated_bytes / (1024**2):.1f} MB"
        else:
            return f"~{estimated_bytes / (1024**3):.1f} GB"
    
    return None 