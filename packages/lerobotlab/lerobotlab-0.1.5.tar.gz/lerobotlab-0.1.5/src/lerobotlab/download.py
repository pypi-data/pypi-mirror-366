"""
LeRobotLab Tools - Download Module

Handles downloading of robot datasets from repositories specified in selection files.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Check if lerobot module is installed
try:
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
except ImportError:
    print("lerobotlab requires the latest version of lerobot.")
    print('Please install it by running: "pip install git+https://github.com/huggingface/lerobot.git"')
    sys.exit(1)


def download_dataset(dataset_repo_id, download_dir, verbose: bool = False):
    """
    Download dataset using LeRobot
    
    Args:
        dataset_repo_id: Dataset name in format "username/foldername"
        download_dir: Base folder to store downloads
    
    Returns:
        dict: Download result with status and details
    """
    try:
        # Parse username and foldername from dataset
        username, foldername = dataset_repo_id.split('/')
        
        # Create folder structure: download_dir/username/foldername
        dataset_folder = Path(download_dir) / username / foldername
        dataset_folder.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            print(f"  Downloading dataset: {dataset_repo_id} to {dataset_folder}")
        
        # Load/download dataset using LeRobot
        dataset_obj = LeRobotDataset(dataset_repo_id, root=str(dataset_folder))
                
        return True
        
    except Exception as e:
        print(f"  Error downloading dataset {dataset_repo_id}: {e}")
        return False



def download_datasets(
    selection_data: Dict[str, Any], 
    download_path: str, 
    verbose: bool = False
) -> None:
    try:
        # Create download directory if it doesn't exist
        download_dir = Path(download_path)
        download_dir.mkdir(parents=True, exist_ok=True)       # Get datasets from selection
        datasets = selection_data.get('datasets', [])
        
        if verbose:
            metadata = selection_data.get('metadata', {})
            print(f"Downloading {len(datasets)} datasets to {download_dir.absolute()}")
          
        error_count = 0
        # Process each dataset
        for i, dataset in enumerate(datasets, 1): 
            result = download_dataset(dataset['repo_id'], download_dir, verbose)
            if result is False:
                error_count += 1
            
        print(f"\nAll {len(datasets)} datasets downloaded to: {download_dir.absolute()} with {error_count} errors")
        
    except Exception as e:
        print(f"Error: Download failed: {e}", file=sys.stderr)
        sys.exit(1)


def validate_download_path(download_path: str) -> Path:
    try:
        path = Path(download_path)
        
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
        print(f"Error: Invalid download path: {e}", file=sys.stderr)
        sys.exit(1)


