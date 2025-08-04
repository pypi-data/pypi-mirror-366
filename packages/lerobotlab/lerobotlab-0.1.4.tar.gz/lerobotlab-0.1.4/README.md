# LeRobotLab Tools

A command-line interface (CLI) tool for working with LeRobot dataset. Selections can be made visualy online at [www.lerobotlab.com](https://www.lerobotlab.com). Users can then save a JSON file of this selectionand  use this tool to download the selection's datasets. The tool alos offers conversion of the downloaded files to different formats in order to use them to train models. 

Right now we only support V-JEPA2-AC, which is a format derived from the droid dataset used to train the VJEPA2 Action Conditionned model.

We plan to uspport other formats soon. Please reach out on the websiote if you see a clear need.

## Installation

### From PyPI (Recommended)

LeRobotLab requires the latest version of LeRobot. 
Install both packages: 

```bash
# Install latest LeRobot from GitHub
pip install git+https://github.com/huggingface/lerobot.git

# Install LeRobotLab
pip install lerobotlab
```

This is the easiest and recommended installation method for most users.

### From Source (Development)

For the latest features, bug fixes, or development purposes:

#### Prerequisites

- Python 3.10 or higher
- conda (Anaconda or Miniconda)
- git

#### Step-by-step Installation

1. **Create and activate a conda environment:**
```bash
conda create -n lerobotlab-tools python=3.10
conda activate lerobotlab-tools
```

2. **Clone and install LeRobot:**
```bash
# Clone this repository
git clone https://github.com/huggingface/lerobot.git

# Install the package in development mode (includes lerobot from source)
cd lerobot
pip install -e .
```


3. **Clone and install LeRobotLab Tools:**
```bash
# Clone this repository
git clone https://github.com/newtechmitch/lerobotlab-tools.git

# Install the package in development mode (includes lerobot from source)
cd lerobotlab-tools
pip install -e .
```

## Usage

The CLI provides two main commands: `download` and `convert`.

### Download Command

Download datasets specified in a selection JSON file:

```bash
lerobotlab download selection.json --download-path ./datasets
```

**Arguments:**
- `selection.json`: Path to the JSON file exported from lerobotlab.com

**Options:**
- `--download-path`: Directory where datasets will be downloaded (required)
- `--verbose, -v`: Enable verbose output
- `--help`: Show command help

### Convert Command

Convert datasets to a specified format:

```bash
lerobotlab convert selection.json --output-path ./output --input-path ./datasets
```

**Arguments:**
- `selection.json`: Path to the JSON file exported from lerobotlab.com

**Options:**
- `--output-path`: Directory where converted datasets will be saved (required)
- `--input-path`: Directory containing downloaded datasets (required)
- `--format`: Output format for converted datasets (choices: vjepa2-ac; default: vjepa2-ac)
- `--verbose, -v`: Enable verbose output
- `--help`: Show command help

## Selection JSON Format

The selection should be created and saved from [www.lerobotlab.com](https://www.lerobotlab.com) and follow this JSON format:

```json
{
  "metadata": {
    "saved_at": "2025-08-02T19:18:32.940Z",
    "total_datasets": 3,
    "total_episodes": 150,
    "total_frames": 77576
  },
  "datasets": [
    {
      "repo_id": "qownscks/3x2blueblock2",
      "selected_videos": [
        "observation.images.up"
      ]
    },
    {
      "repo_id": "LightwheelAI/leisaac-pick-orange",
      "selected_videos": [
        "observation.images.front",
        "observation.images.wrist"
      ]
    },
    {
      "repo_id": "initie/picking",
      "selected_videos": [
        "observation.images.front",
        "observation.images.side"
      ]
    }
  ]
}
```

### Required Fields

- `datasets`: Array of dataset objects
  - Each dataset must have:
    - `repo_id`: Unique identifier for the dataset repository
    - `selected_videos`: Array of selected video streams

### Optional Fields

- `metadata`: Object containing selection metadata
  - `saved_at`: Timestamp when selection was saved
  - `total_datasets`: Number of datasets in selection
  - `total_episodes`: Total number of episodes across all datasets
  - `total_frames`: Total number of frames across all datasets

## Examples

### Basic Download

```bash
# Download datasets to local directory
lerobotlab download my_selection.json --download-path ./robot_datasets
```

### Download with Verbose Output

```bash
# Download with detailed output
lerobotlab download my_selection.json --download-path ./robot_datasets --verbose
```

### Convert to DROID Format

```bash
# Convert datasets to DROID format
lerobotlab convert my_selection.json --output-path ./converted --input-path ./robot_datasets --format droid
```

### Convert to V-JEPA2-AC Format

```bash
# Convert datasets to V-JEPA2-AC format
lerobotlab convert my_selection.json --output-path ./converted --input-path ./robot_datasets --format vjepa2-ac
```

## Error Handling

The CLI provides clear error messages for common issues:

- **File not found**: When the selection JSON file doesn't exist
- **Invalid JSON**: When the file contains malformed JSON
- **Missing fields**: When required fields are missing from the JSON structure
- **Invalid structure**: When the JSON doesn't match the expected format
- **Path validation**: When input/output directories are invalid or inaccessible

## Development

### Project Structure

```
lerobotlab-tools/
├── src/
│   └── lerobotlab/
│       ├── __init__.py                    # Package initialization
│       ├── cli.py                        # Main CLI interface and argument parsing
│       ├── download.py                   # Dataset download functionality
│       ├── convert.py                    # Dataset conversion coordination
│       ├── droid_conversion.py           # DROID format converter (future support)
│       └── vjepa2_ac_conversion.py       # V-JEPA2-AC format converter
├── test_env/                             # Test environment and sample data
├── .vscode/                              # VS Code debug configurations
├── dist/                                 # Built packages
├── pyproject.toml                        # Package configuration and metadata
├── requirements.txt                      # Development dependencies
├── test_setup.py                         # Test environment setup script
├── README.md                             # This file
└── .gitignore                           # Git ignore patterns
```

### Dependencies

#### Core Runtime Dependencies

- **h5py>=3.0.0**: HDF5 file format support for trajectory data
- **pandas>=1.0.0**: Data manipulation and analysis
- **numpy>=1.19.0**: Numerical computing foundation
- **lerobot*

#### System Requirements

- **Python 3.10+**: Minimum Python version requirement
- **conda**: Package and environment manager (Anaconda or Miniconda)
- **pip**: Package installer (included with conda)

### Testing

To set up test environments and run tests:

```bash
# Activate your conda environment
conda activate lerobotlab-tools

# Setup test environment
python test_setup.py

# List available test cases
python test_setup.py list

# Run specific test case
python test_setup.py download_single_dataset

# Clean up test environment
python test_setup.py cleanup
```

### Debugging

VS Code debug configurations are provided in `.vscode/launch.json`:

- **Debug convert single**: Test conversion with single dataset
- **Debug convert multi**: Test conversion with multiple datasets  
- **Debug download single**: Test download with single dataset
- **Debug download multi**: Test download with multiple datasets

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Format code (`black src/`)
7. Check linting (`flake8 src/`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## Support

For issues and questions:
- Create an issue on [GitHub Issues](https://github.com/newtechmitch/lerobotlab-tools/issues)
- Visit [www.lerobotlab.com](https://www.lerobotlab.com) for dataset-related questions

## Changelog

### v0.1.0
- Initial release
- CLI interface with download and convert commands
- Support for V-JEPA2-AC conversion formats
- JSON validation and comprehensive error handling
- Verbose logging and debug configurations
