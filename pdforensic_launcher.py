import json
import subprocess
import shutil
import os
import datetime
from pathlib import Path

CONFIG_PATH = "pdforensic_tools_config.json"
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_SOURCE_DIR = Path("Documents/Source")


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_banner():
    print(r"""
██████╗ ███████╗██████╗ ███████╗ ██████╗ ██████╗ ███████╗███╗   ██╗██╗ ██████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝████╗  ██║██║██╔════╝
██║  ██║█████╗  ██████╔╝█████╗  ██║  ███╗██████╔╝█████╗  ██╔██╗ ██║██║██║     
██║  ██║██╔══╝  ██╔══██╗██╔══╝  ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║██║     
██████╔╝███████╗██║  ██║███████╗╚██████╔╝██║     ███████╗██║ ╚████║██║╚██████╗
╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝
              Forensic CLI Tool for PDF Analysis
""")


def choose_input_path():
    path = input("Enter file or folder path to analyze: ").strip()
    p = Path(path)
    if not p.exists():
        print("❌ Path does not exist.")
        exit(1)
    return p


def choose_tools(tools_config):
    print("Available tools:")
    for i, tool in enumerate(tools_config):
        print(f"{i + 1}. {tool['name']} ({tool['flag']}) - {tool['description']}")
    choices = input("Select tools to run (e.g. 1,3,5 or 'all'): ").strip().lower()
    if choices == 'all':
        return tools_config
    selected_indices = [int(c) - 1 for c in choices.split(',') if c.isdigit()]
    return [tools_config[i] for i in selected_indices if 0 <= i < len(tools_config)]


def run_tool(tool, input_path: Path, output_dir: Path):
    cmd_template = tool['command']
    input_type = 'folder' if input_path.is_dir() else 'file'
    cmd = cmd_template.replace("{input}", str(input_path)).replace("{output}", str(output_dir))
    print(f"\n🔧 Running {tool['name']}:")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {tool['name']} completed successfully.")
        else:
            print(f"❌ {tool['name']} failed:\n{result.stderr}")
    except Exception as e:
        print(f"❌ Error: {e}")


def zip_output(out_path):
    zip_path = shutil.make_archive(str(out_path), 'zip', root_dir=out_path)
    print(f"📦 Output zipped to: {zip_path}")


def main():
    print_banner()
    config = load_config()
    tools = config['tools']
    global_output = Path(config['global'].get('output_dir', DEFAULT_OUTPUT_DIR))
    output_dir = global_output / f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = choose_input_path()
    selected_tools = choose_tools(tools)

    for tool in selected_tools:
        run_tool(tool, input_path, output_dir)

    zip_output(output_dir)

if __name__ == '__main__':
    main()
