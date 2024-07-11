# ComfyUI Launcher Project Updater

This script automates the process of updating ComfyUI projects and their custom nodes.

## Features

- Updates all ComfyUI projects and their custom nodes
- Provides a progress bar for visual feedback
- Handles git operations including pulling, resolving conflicts, and managing stashes
- Offers verbose and force modes for different update scenarios
- Provides a summary of any issues encountered during the update process

## Installation

1. Clone this repository or download the \`update_comfyui.py\` script.
2. Make the script executable:

   ```bash
   chmod +x update_comfyui.py
   ```

## Usage

Run the script from the command line:

```bash
./update_comfyui.py [OPTIONS]
```

### Options

- `-h`, `--help`: Show the help message and exit
- `-v`, `--verbose`: Run in verbose mode for detailed output
- `-f`, `--force`: Force update, discarding local changes

### Examples

Update all projects with minimal output:
```bash
./update_comfyui.py
```

Update with detailed information:
```bash
./update_comfyui.py -v
```

Force update, discarding local changes:
```bash
./update_comfyui.py -f
```

Combine options:
```bash
./update_comfyui.py -v -f
```

## Note

If run from within a specific project directory, only that project will be updated.

## Requirements

- Python 3.6+
- Git

## License

[MIT License](LICENSE)
