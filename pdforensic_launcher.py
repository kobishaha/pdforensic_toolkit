import json
import subprocess
import shutil
import os
import datetime
from pathlib import Path

CONFIG_PATH = "pdforensic_config.json"
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
    print("Enter file or folder path to analyze:")
    path = input("> ").strip()
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
    cmd = cmd_template.replace("{input}", str(input_path)).replace("{output}", str(output_dir))

    print(f"\n🔧 Running {tool['name']}:")
    print(f"[DEBUG] Executing command: {cmd}")

    log_dir = output_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{tool['flag']}_output.log"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(result.stderr)

        if result.returncode == 0:
            print(f"✅ {tool['name']} completed successfully. Log saved to {log_file}")
        else:
            print(f"❌ {tool['name']} failed with return code {result.returncode}. See log at {log_file}")
    except Exception as e:
        print(f"❌ Error running {tool['name']}: {e}")


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
    print(f"🔒 Output saved to: {output_dir}")
    
    if not any(output_dir.iterdir()):
        output_dir.rmdir()

    print("📝 Logs saved to:", output_dir / "logs")
    print("🎉 All done!")