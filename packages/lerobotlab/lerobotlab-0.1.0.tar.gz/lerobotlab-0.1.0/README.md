# LeRobotLab Tools

A command-line interface (CLI) tool for processing robot dataset selections from [lerobotlab.com](https://lerobotlab.com). Users can export a JSON configuration from the website and use this tool to download datasets and convert them to different formats.

## Installation

### From Source

1. Clone this repository:
```bash
git clone https://github.com/lerobotlab/lerobotlab-tools.git
cd lerobotlab-tools
```

2. Install the package:
```bash
pip install -e .
```

### From PyPI (when available)

```bash
pip install lerobotlab
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
- `--input-path`: Directory containing downloaded datasets (optional, will download if not provided)
- `--format`: Output format for converted datasets (choices: droid, vjepa2-ac; default: droid)
- `--verbose, -v`: Enable verbose output
- `--help`: Show command help

## Selection JSON Format

The selection JSON file should be exported from lerobotlab.com and follow this format:

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

### Convert Existing Datasets

```bash
# Convert already downloaded datasets
lerobotlab convert my_selection.json --output-path ./converted --input-path ./robot_datasets --format vjepa2-ac
```

### Download and Convert in One Step

```bash
# Convert without pre-downloaded datasets (will download first)
lerobotlab convert my_selection.json --output-path ./converted --format droid
```

## Error Handling

The CLI provides clear error messages for common issues:

- **File not found**: When the selection JSON file doesn't exist
- **Invalid JSON**: When the file contains malformed JSON
- **Missing fields**: When required fields are missing from the JSON structure
- **Invalid structure**: When the JSON doesn't match the expected format

## Development

### Prerequisites

- Python 3.8 or higher
- pip

### Development Installation

1. Clone the repository:
```bash
git clone https://github.com/lerobotlab/lerobotlab-tools.git
cd lerobotlab-tools
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

### Project Structure

```
lerobotlab-tools/
├── src/
│   └── lerobotlab/
│       ├── __init__.py       # Package initialization
│       └── cli.py            # CLI implementation
├── pyproject.toml            # Package configuration
├── README.md                 # This file
└── .gitignore               # Git ignore patterns
```

## Dependencies

- **click**: Command-line interface framework
- **Python 3.8+**: Minimum Python version requirement

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Visit [lerobotlab.com](https://lerobotlab.com) for dataset-related questions

## Changelog

### v0.1.0
- Initial release
- Basic CLI structure with download and convert commands
- JSON validation and error handling
- Placeholder implementations for future development
