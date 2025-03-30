import argparse
import os
import sys
from pathlib import Path
import json
import subprocess

# === Banner ===
BANNER = r"""
██████╗ ███████╗██████╗ ███████╗ ██████╗ ██████╗ ███████╗███╗   ██╗██╗ ██████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝████╗  ██║██║██╔════╝
██║  ██║█████╗  ██████╔╝█████╗  ██║  ███╗██████╔╝█████╗  ██╔██╗ ██║██║██║     
██║  ██║██╔══╝  ██╔══██╗██╔══╝  ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║██║     
██████╔╝███████╗██║  ██║███████╗╚██████╔╝██║     ███████╗██║ ╚████║██║╚██████╗
╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝
            Forensic CLI Tool for PDF Analysis ✨
"""

# === Load tool config ===
def load_tool_config():
    with open("tools_config.json", encoding="utf-8") as f:
        return json.load(f)

tool_config = load_tool_config()

def list_available_tools():
    print("Available tools:")
    for key, val in tool_config.items():
        print(f"  -{key} : {val['description']}")

def run_tool(tool_key, input_path):
    cfg = tool_config.get(tool_key)
    if not cfg:
        print(f"Unknown tool key: {tool_key}")
        return
    for cmd in cfg['commands']:
        formatted_cmd = cmd.replace("{input}", str(input_path))
        print(f"Running: {formatted_cmd}")
        subprocess.run(formatted_cmd, shell=True)

def interactive_mode():
    print(BANNER)
    path = input("Enter PDF file or folder: ").strip()
    if not Path(path).exists():
        print("❌ Path does not exist.")
        sys.exit(1)
    print("\nWhat would you like to do? (select letters, comma-separated, or 'all')")
    list_available_tools()
    choice = input("\nYour choice: ").strip().lower()
    selected = tool_config.keys() if choice == "all" else [x.strip() for x in choice.split(",")]

    if Path(path).is_file():
        for tool in selected:
            run_tool(tool, path)
    else:
        for file in Path(path).glob("*.pdf"):
            print(f"\n🔍 Processing: {file.name}")
            for tool in selected:
                run_tool(tool, file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Forensic CLI Tool")
    parser.add_argument("path", nargs="?", help="PDF file or folder")
    parser.add_argument("-t", "--tools", nargs="*", help="Tool letters to run (e.g., -t m o i)")
    args = parser.parse_args()

    if not args.path:
        interactive_mode()
    else:
        input_path = Path(args.path)
        selected = tool_config.keys() if not args.tools else args.tools
        if input_path.is_file():
            for tool in selected:
                run_tool(tool, input_path)
        elif input_path.is_dir():
            for file in input_path.glob("*.pdf"):
                print(f"\n🔍 Processing: {file.name}")
                for tool in selected:
                    run_tool(tool, file)
        else:
            print("❌ Invalid input path.")
