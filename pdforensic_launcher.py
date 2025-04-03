import json
import subprocess
import shutil
import os
import datetime
from pathlib import Path
import shlex # Import shlex for potential quoting

CONFIG_PATH = "pdforensic_tools_config.json"
DEFAULT_OUTPUT_DIR = Path("output")
# DEFAULT_SOURCE_DIR = Path("Documents/Source") # Removed if unused

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found at {CONFIG_PATH}")
        exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Configuration file {CONFIG_PATH} contains invalid JSON.")
        exit(1)

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
    while True: # Loop until valid path is given
        path_str = input("> ").strip()
        p = Path(path_str)
        if p.exists():
            return p
        else:
            print(f"❌ Path '{path_str}' does not exist. Please try again.")
            # Optionally add 'exit()' here if you don't want to loop

def choose_tools(tools_config):
    print("\nAvailable tools:")
    for i, tool in enumerate(tools_config):
        # Skip the 'Run All Tools' meta-entry if it exists and has no commands
        if tool.get('id') == 'a' and not tool.get('commands'):
            continue
        print(f"{i + 1}. {tool['name']} ({tool['id']}) - {tool['description']}")

    selected_tools = []
    max_choice = len(tools_config) # Adjust if filtering out 'a'

    while not selected_tools:
        choices_str = input(f"Select tools to run (e.g., 1,3,5 or 'all' for 1-{max_choice}): ").strip().lower()
        if choices_str == 'all':
            # Exclude the 'all' meta-tool itself if it exists
            return [t for t in tools_config if not (t.get('id') == 'a' and not t.get('commands'))]

        try:
            selected_indices = []
            parts = choices_str.split(',')
            for part in parts:
                part = part.strip()
                if not part: continue
                if '-' in part: # Handle ranges like 1-3
                    start, end = map(int, part.split('-'))
                    selected_indices.extend(range(start - 1, end))
                else:
                    selected_indices.append(int(part) - 1)

            # Validate indices and prevent duplicates
            valid_tools = []
            seen_indices = set()
            for i in selected_indices:
                if 0 <= i < len(tools_config) and i not in seen_indices:
                    # Ensure we don't add the 'all' meta-tool
                    if not (tools_config[i].get('id') == 'a' and not tools_config[i].get('commands')):
                        valid_tools.append(tools_config[i])
                        seen_indices.add(i)
            if valid_tools:
                selected_tools = valid_tools
            else:
                 print("❌ Invalid selection or numbers out of range. Please try again.")

        except ValueError:
            print("❌ Invalid input. Please use numbers, commas, hyphens (e.g., 1,3,5-7) or 'all'.")

    return selected_tools


def run_tool(tool, input_path: Path, session_output_dir: Path, global_settings: dict):
    tool_id = tool['id']
    tool_name = tool['name']
    tool_commands = tool['commands']
    tool_output_subdir_name = tool.get('output_dir') # Use .get() for safety

    if not tool_commands:
        print(f"ℹ️ Skipping {tool_name} as it has no commands defined.")
        return

    # --- Create Tool Specific Output Directory ---
    if tool_output_subdir_name:
        tool_output_dir = session_output_dir / tool_output_subdir_name
        tool_output_dir.mkdir(exist_ok=True)
    else:
        # Default to session dir if no specific subdir is defined for the tool
        tool_output_dir = session_output_dir

    print(f"\n🔧 Running {tool_name} (Output Dir: {tool_output_dir}):")

    log_dir = session_output_dir / "logs" # Keep logs in session root/logs
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{tool_id}_output.log"

    # --- Prepare Placeholder Dictionary ---
    # Use shlex.quote for paths going into shell commands if using shell=True
    # If switching to shell=False, you wouldn't quote here but ensure paths are separate list items.
    placeholders = {
        "input": shlex.quote(str(input_path)),
        "session_output_dir": shlex.quote(str(session_output_dir)),
        "tool_output_dir": shlex.quote(str(tool_output_dir)),
        # Add global settings - ensure they are safe for command line use
        "ocr_language": global_settings.get('ocr_language', 'eng'), # Example
        "ocr_dpi": str(global_settings.get('ocr_dpi', 300)),      # Example
        # Add more global settings as needed
    }

    # --- Execute Each Command for the Tool ---
    success = True
    for cmd_template in tool_commands:
        # More robust templating using format()
        try:
            # Use .format_map() for dictionary-based formatting
            # Handle potential KeyError if JSON uses undefined placeholder
            cmd = cmd_template.format_map(placeholders)
        except KeyError as e:
            print(f"❌ Error: Placeholder {e} not found for command in tool '{tool_name}'. Skipping command.")
            print(f"   Command Template: {cmd_template}")
            success = False
            continue # Skip this specific command

        print(f"   Executing: {cmd}")

        try:
            # Consider using shell=False if cmd can be split reliably (e.g., using shlex.split(cmd))
            # But given the redirects '>', shell=True might be needed here. Be mindful of security.
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

            # Append to log file for multiple commands within a tool
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- Command: {cmd} ---\n")
                f.write("=== STDOUT ===\n")
                f.write(result.stdout or "")
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr or "")
                f.write("\n--------------------\n")

            if result.returncode != 0:
                print(f"   ❌ Command failed with return code {result.returncode}. See log: {log_file}")
                success = False # Mark tool as failed if any command fails
            else:
                print(f"   ✅ Command completed successfully.")

        except Exception as e:
            print(f"   ❌ Error running command: {e}")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- ERROR Running Command: {cmd} ---\n{e}\n")
            success = False

    # --- Final Tool Status ---
    if success:
        print(f"✅ {tool_name} finished.") # Changed message slightly
    else:
        print(f"❌ {tool_name} encountered errors.")

def zip_output(out_path):
    # Only zip if the directory exists and is not empty (or contains more than just 'logs')
    if out_path.exists() and any(f for f in out_path.iterdir() if f.name != 'logs' or any(out_path.joinpath('logs').iterdir())):
        try:
            zip_filename = f"{out_path.name}.zip"
            zip_path_obj = out_path.parent / zip_filename # Place zip next to the folder
            # Use make_archive without full path in filename arg
            shutil.make_archive(str(out_path.parent / out_path.name), 'zip', root_dir=out_path)
            print(f"📦 Output zipped to: {zip_path_obj}")
            return zip_path_obj # Return path to zip file
        except Exception as e:
            print(f"❌ Error zipping output: {e}")
            return None
    elif out_path.exists():
        print(f"ℹ️ Skipping zip for empty output directory: {out_path}")
        return None
    return None

def main():
    print_banner()
    config = load_config()
    tools_config = config.get('tools', [])
    global_settings = config.get('global_settings', {}) # Correct key and provide default

    if not tools_config:
        print("❌ No tools defined in the configuration file.")
        exit(1)

    # --- Setup Output Directory ---
    output_base = Path(global_settings.get('output_base_dir', DEFAULT_OUTPUT_DIR))
    session_dir_name = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_output_dir = output_base / session_dir_name
    try:
        session_output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"❌ Error creating output directory {session_output_dir}: {e}")
        exit(1)

    print(f"📂 Session output directory: {session_output_dir}")

    input_path = choose_input_path()
    selected_tools = choose_tools(tools_config)

    # --- Run Tools ---
    for tool in selected_tools:
        run_tool(tool, input_path, session_output_dir, global_settings)

    # --- Zip Output ---
    zipped_path = None
    if global_settings.get('zip_output', True): # Check flag in config
       zipped_path = zip_output(session_output_dir)

    print("\n--- Summary ---")
    print(f"Input processed: {input_path}")
    print(f"Session output folder: {session_output_dir}")
    print(f"Logs saved in: {session_output_dir / 'logs'}")
    if zipped_path:
        print(f"Output zipped to: {zipped_path}")
    elif global_settings.get('zip_output', True):
         print("Zipping skipped (directory likely empty or error occurred).")

    # Optional: Clean up empty session dir *after* deciding not to zip
    # try:
    #     if not zipped_path and not any(session_output_dir.iterdir()):
    #         print(f"🧹 Cleaning up empty session directory: {session_output_dir}")
    #         session_output_dir.rmdir()
    # except OSError as e:
    #     print(f"⚠️ Warning: Could not remove empty session directory {session_output_dir}: {e}")


    print("\n🎉 All selected tasks done!")


if __name__ == "__main__":
    main()
