import argparse
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

# Load config
CONFIG_PATH = Path("pdforensic_tools_config.json")
with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = json.load(f)

global_settings = config.get("global_settings", {})
tools = config.get("tools", {})

def run_command(cmd):
    console.print(f"[bold yellow]🔧 Running:[/bold yellow] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        console.print(f"[bold red]❌ Command failed:[/bold red] {cmd}")
    else:
        console.print("[bold green]✅ Command succeeded[/bold green]")

def zip_output(output_dir):
    zip_name = output_dir.with_suffix(".zip")
    subprocess.run(f"zip -r '{zip_name}' '{output_dir.name}'", shell=True)
    console.print(f"📦 Zipped to: {zip_name}")

def create_output_dir(base_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(global_settings["default_output"])/f"{base_name}_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def list_tools():
    table = Table(title="PDF Forensic CLI Tool - Menu")
    table.add_column("Flag", justify="center", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for key, val in tools.items():
        table.add_row(val["flag"], val["name"], val["description"])
    console.print(table)

def choose_tools():
    list_tools()
    choice = Prompt.ask("Select tools to run (e.g. m,t,o,a or all)")
    return choice.lower().split(',') if choice != 'all' else list(tools.keys())

def process_file(file_path, selected_tools):
    console.print(f"\n[bold blue]🔍 Processing:[/bold blue] {file_path}")
    out_dir = create_output_dir(Path(file_path).stem)
    for key in selected_tools:
        if key in tools:
            for cmd in tools[key]["commands"]:
                cmd_formatted = cmd.format(input=file_path, output=out_dir)
                run_command(cmd_formatted)
    if global_settings.get("zip_output"):
        zip_output(out_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="PDF file or folder to process")
    parser.add_argument("-f", "--flags", help="Comma-separated tool flags to run (e.g. -m,t,o)")
    args = parser.parse_args()

    if not args.target:
        target = Prompt.ask("Enter PDF file or folder path")
    else:
        target = args.target

    selected_tools = []
    if not args.flags:
        selected_tools = choose_tools()
    else:
        selected_tools = args.flags.lower().split(',')

    target_path = Path(target)
    if target_path.is_dir():
        for pdf in target_path.glob("*.pdf"):
            process_file(pdf, selected_tools)
    elif target_path.is_file():
        process_file(target_path, selected_tools)
    else:
        console.print("[bold red]❌ Invalid input path[/bold red]")

if __name__ == "__main__":
    main()
