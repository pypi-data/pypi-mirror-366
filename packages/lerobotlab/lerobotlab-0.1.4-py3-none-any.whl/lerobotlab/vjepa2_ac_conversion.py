"""
LeRobotLab Tools - V-JEPA2-AC Conversion Module

Handles conversion of robot datasets to V-JEPA2-AC format for actor-critic training.
"""
from pathlib import Path
from typing import Dict, Any, List
# Removed click dependency
import json
import pandas as pd
import shutil
import h5py
import numpy as np


class VJEPA2ACConverter:
    """
    Converter class for transforming robot datasets to V-JEPA2-AC format.
    
    V-JEPA2-AC (Video Joint Embedding Predictive Architecture 2 - Actor Critic) 
    is designed for vision-based robotic learning with temporal prediction.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the V-JEPA2-AC converter.
        
        Args:
            verbose: Whether to enable verbose logging
        """
        self.verbose = verbose
        self.format_name = "V-JEPA2-AC"
        self.converted_episode_paths = []
        self.total_converted_episodes = 0
        
    def convert_dataset(
        self,
        repo_id: str,
        selected_videos: List[str],
        input_dir: Path,
        output_dir: Path
        ) -> Dict[str, Any]:
        """
        Convert a single dataset to V-JEPA2-AC format.
        
        Args:
            repo_id: Repository ID of the dataset (e.g., 'username/dataset_name')
            selected_videos: List of selected video streams to convert
            input_dir: Directory containing the input dataset
            output_file: Path where the converted file should be saved
            
        Returns:
            dict: Conversion result with status and metadata
        """
        username, foldername = repo_id.split('/')
        video_key = selected_videos[0]
                
        if self.verbose:
            print(f"    Starting {self.format_name} conversion for: {repo_id}")
            print(f"    Input directory: {input_dir}")
            print(f"    Output directory: {output_dir}")
            print(f"    Selected videos: {', '.join(selected_videos)}")
        
    
        # Load dataset info
        try:
            input_path = Path(input_dir) / username / foldername
            episodes_dir = output_dir / "episodes"
            episodes_dir.mkdir(exist_ok=True)
            dataset_info = self.load_dataset_info(input_path)
        except Exception as e:
            error_result = {
                'status': 'error',
                'repo_id': repo_id,
                'episodes_converted': 0,
            }
            return error_result
    
        # Process each episode in this dataset
       

        try:
            for episode_index in range(dataset_info["total_episodes"]):
                episode_paths = self.get_episode_paths(dataset_info, selected_videos, episode_index)
                print(f"Processing episode {episode_index}")
                episode_dir_name = self.convert_episode_to_vjepa2_ac(input_path,episode_index,episode_paths, repo_id, video_key, episodes_dir)
                converted_episode_path = f"episodes/{episode_dir_name}"               
                if episode_dir_name:            
                    self.converted_episode_paths.append(converted_episode_path)
                self.total_converted_episodes += 1

            # Create dataset_list.txt - single file with all episodes
            dataset_list_path = output_dir / "dataset_list.txt"
            with open(dataset_list_path, 'w') as f:
                for episode_path in self.converted_episode_paths:
                    f.write(f"{episode_path}\n")
            
            if self.verbose:
                print(f"Conversion complete!")
                print(f"Dataset list saved to: {dataset_list_path}")


            conversion_result = {
                'status': 'success',
                'repo_id': repo_id,
                'episodes_converted': self.total_converted_episodes,
            }  

            return conversion_result                
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'repo_id': repo_id,
                'episodes_converted': 0,
            }
            return error_result
        
    
    def load_dataset_info(self, dataset_path: Path) -> Dict:
        """Load dataset info from meta/info.json"""
        info_path = dataset_path / "meta" / "info.json"
        if not info_path.exists():
            raise FileNotFoundError(f"Dataset info file not found: {info_path}")

        with open(info_path, 'r') as f:
            return json.load(f)

    def get_episode_paths(self, metadata: Dict, video_keys: List[str], episode_index: int) -> Dict:
        """Get episode paths from metadata"""
        episode_chunk = episode_index // metadata["chunks_size"]

        data_path = metadata["data_path"].format(
            episode_chunk=episode_chunk,
            episode_index=episode_index
        )

        video_paths = {
            key: {
                "key": key,
                "path": metadata["video_path"].format(
                    episode_chunk=episode_chunk,
                    video_key=key,
                    episode_index=episode_index
                )
            }
            for key in video_keys
        }
        return {
            "data": data_path,
            "videos": video_paths
        }

    def load_episode_data(self, episode_data_path: Path, episode_idx: int) -> pd.DataFrame:
        """Load episode data from parquet file"""
        if not episode_data_path.exists():
            raise FileNotFoundError(f"Episode file not found: {episode_data_path}")

        return pd.read_parquet(episode_data_path)

    def convert_episode_to_vjepa2_ac(self, input_path: Path, episode_idx: int, episode_paths: Dict, repo_id: str, video_key: str, episode_output_dir: Path):
        """Convert a single episode to VJEPA2-AC format"""
        try:
            #dataset info
            converted_dataset_dir_name = repo_id.replace('/', '+')
            episode_data_path = input_path / episode_paths["data"]
            episode_data = self.load_episode_data(episode_data_path, episode_idx)
            
            # Find corresponding video file
            video_path = input_path / episode_paths["videos"][video_key]["path"]
            original_dataset = repo_id
            
            if not video_path.exists():
                print(f"Warning: Video file not found: {video_path}")
                return None
            
            # Create episode directory with dataset name prefix
            episode_dir_name = f"{converted_dataset_dir_name}-episode_{episode_idx:03d}"
            episode_dir = episode_output_dir / episode_dir_name
            episode_dir.mkdir(exist_ok=True)
            
            # Create recordings/MP4 directory
            recordings_dir = episode_dir / "recordings" / "MP4"
            recordings_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy video file
            output_video_path = recordings_dir / "video.mp4"
            shutil.copy2(video_path, output_video_path)
            
            # Create trajectory.h5
            trajectory_path = episode_dir / "trajectory.h5"
            self.create_trajectory_h5(episode_data, trajectory_path)
            
            # Create metadata.json
            metadata = self.create_episode_metadata(episode_idx, episode_data,
                                                trajectory_path, converted_dataset_dir_name, input_path, original_dataset)
            metadata_path = episode_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            if self.verbose:
                print(f"=> Created {episode_dir_name} with {len(episode_data)} frames")
            
        except Exception as e:
            print(f"Error processing episode {episode_idx}: {e}")
            return None
        
        return episode_dir_name



    def create_episode_metadata(self, episode_idx: int, episode_data: pd.DataFrame,
                          trajectory_path: Path, dataset_name: str, source_dataset_path: str, original_dataset: str) -> Dict:
        """Create metadata.json content for an episode"""
        metadata = {
            "episode_id": episode_idx,
            "episode_name": f"{dataset_name}-episode_{episode_idx:03d}",
            "source_dataset_path": f"{source_dataset_path}",
            "original_lerobot_dataset": original_dataset,
            "total_frames": len(episode_data),

            "files": {
                "trajectory": str(trajectory_path.name),
                "video": {
                    "front_camera": str(Path("recordings/MP4/video.mp4"))
                }
            },
            "data_keys": {
                "action": {
                    "shape": [6],
                    "dtype": "float32",
                    "names": [
                        "shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos",
                        "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"
                    ]
                },
                "observation.state": {
                    "shape": [6],
                    "dtype": "float32", 
                    "names": [
                        "shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos",
                        "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"
                    ]
                }
            },
            "task": "n/a"  # Based on the dataset
        }
        return metadata

    def create_trajectory_h5(self, episode_data: pd.DataFrame, output_path: Path):
        """Convert episode data to HDF5 trajectory format"""
        with h5py.File(output_path, 'w') as f:
            # Create groups for different data types
            action_group = f.create_group('action')
            observation_group = f.create_group('observation')
            metadata_group = f.create_group('metadata')

            # Save action data
            if 'action' in episode_data.columns:
                action_data = np.stack(episode_data['action'].values)
                action_group.create_dataset('data', data=action_data)
                
                # Add action names if available
                action_names = [
                    "shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos",
                    "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"
                ]
                action_group.attrs['names'] = action_names

            # Save observation state data
            if 'observation.state' in episode_data.columns:
                obs_data = np.stack(episode_data['observation.state'].values)
                observation_group.create_dataset('state', data=obs_data)
                
                # Add state names
                state_names = [
                    "shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos",
                    "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"
                ]
                observation_group.attrs['state_names'] = state_names

            # Save timestamps
            if 'timestamp' in episode_data.columns:
                timestamps = episode_data['timestamp'].values
                metadata_group.create_dataset('timestamp', data=timestamps)

            # Save frame indices
            if 'frame_index' in episode_data.columns:
                frame_indices = episode_data['frame_index'].values
                metadata_group.create_dataset('frame_index', data=frame_indices)


    def validate_input(self, input_dir: Path, selected_videos: List[str]) -> bool:
        """
        Validate input dataset and video streams for V-JEPA2-AC conversion.
        
        Args:
            input_dir: Input directory to validate
            selected_videos: List of video streams to validate
            
        Returns:
            bool: True if input is valid, False otherwise
        """
    
        if not input_dir.exists():
            if self.verbose:
                print(f"Error: Input directory does not exist: {input_dir}")
            return False
        
        if not selected_videos:
            if self.verbose:
                print(f"Error: No video streams selected for conversion")
            return False
        
        return True 