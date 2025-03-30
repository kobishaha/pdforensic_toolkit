# PDF Forensic CLI Toolkit

This toolkit is a lightweight and modular PDF forensic command runner.
It uses a JSON configuration to define tools and commands per analysis type.

## Usage
Run with: `python pdforensic_launcher.py <file|folder> [-o -m -t ...]`
Or run interactively with no flags.

## JSON Configuration
Each tool has:
- `name`: Tool name
- `description`: What it does
- `output_folder`: Where to save results
- `command`: CLI command to run (with {input}, {output}, {output_base})
