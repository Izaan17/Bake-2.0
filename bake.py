#!/usr/bin/env python3
import argparse
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional, Tuple

import rich.box
from rich.table import Table

import constants
from printer import CustomPrinter


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration"""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory
    log_dir = os.path.join(constants.INSTALL_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Setup file logging
    log_file = os.path.join(log_dir, "bake.log")
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() if debug else logging.NullHandler()
        ]
    )
    
    # Set specific logger for bake
    logger = logging.getLogger('bake')
    logger.setLevel(log_level)


def validate_command_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate command name for proper format and conflicts"""
    if not name:
        return False, "Command name cannot be empty"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        return False, "Command name must start with a letter and contain only letters, numbers, hyphens, and underscores"
    
    if name.lower() == "bake":
        return False, 'Cannot use "bake" as a command name (conflicts with main script)'
    
    # Check for reserved names
    reserved_names = {'python', 'python3', 'pip', 'pip3', 'git', 'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'mkdir', 'rm', 'cp', 'mv'}
    if name.lower() in reserved_names:
        return False, f'"{name}" is a reserved system command name'
    
    return True, None


def validate_script_path(script_path: str) -> Tuple[bool, Optional[str]]:
    """Validate that the script path exists and is a Python file"""
    if not script_path:
        return False, "Script path cannot be empty"
    
    path = Path(script_path)
    if not path.exists():
        return False, f"Script not found: {script_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {script_path}"
    
    if not path.suffix.lower() in ['.py', '.pyw']:
        return False, f"File must be a Python script (.py or .pyw), got: {path.suffix}"
    
    # Check if file is readable
    if not os.access(path, os.R_OK):
        return False, f"Cannot read file: {script_path}"
    
    return True, None


def safe_remove_file(file_path: str, printer: CustomPrinter) -> bool:
    """Safely remove a file with error handling"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError as e:
        printer.error(f"Failed to remove {file_path}: {e}")
        return False
    return True


def safe_remove_symlink(symlink_path: str, printer: CustomPrinter) -> bool:
    """Safely remove a symlink with error handling"""
    try:
        if os.path.exists(symlink_path) or os.path.islink(symlink_path):
            os.remove(symlink_path)
            return True
    except OSError as e:
        printer.error(f"Failed to remove symlink {symlink_path}: {e}")
        return False
    return True


def create_parser() -> argparse.ArgumentParser:
    # Create the main parser
    parser = argparse.ArgumentParser(description="Bake: A tool for managing custom commands")

    # Group common installation/management flags
    management_group = parser.add_argument_group("management options")
    management_group.add_argument("-i", "--install", action="store_true", help="Install bake.")
    management_group.add_argument("-d", "--debug", action="store_true", help="Set debug status.")
    management_group.add_argument("--uninstall", action="store_true", help="Uninstall bake.")
    management_group.add_argument("--hard", action="store_true",
                                  help="Also remove all bake command aliases during uninstall.")
    management_group.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompts.")
    management_group.add_argument("-v", "--version", action="store_true", help="Outputs the current version number")

    # Create subparsers
    subparsers = parser.add_subparsers(dest="action", help="The action to perform")

    # Create parent parser for commands that need a name argument
    name_parser = argparse.ArgumentParser(add_help=False)
    name_parser.add_argument("name", help="Name of the command")

    # Add subparsers with their specific arguments
    subparsers.add_parser("list", help="List all installed commands")

    add_parser = subparsers.add_parser("add", help="Add a new command", parents=[name_parser])
    add_parser.add_argument("script_path", type=argparse.FileType(), help="Path to the Python script")

    subparsers.add_parser("edit", help="Edit an existing command", parents=[name_parser])
    subparsers.add_parser("delete", help="Delete an existing command", parents=[name_parser])
    
    # Create parser for rename command that needs both old and new names
    rename_parser = subparsers.add_parser("rename", help="Rename an existing command")
    rename_parser.add_argument("old_name", help="Current name of the command")
    rename_parser.add_argument("new_name", help="New name for the command")
    
    # Add health check command
    subparsers.add_parser("health", help="Check installation health and diagnose issues")
    
    # Add update command
    subparsers.add_parser("update", help="Update Bake to the latest version")

    return parser


def create_wrapper_script(script_path: str) -> str:
    """Create a robust wrapper script with error handling"""
    return f'''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

script_path = "{script_path}"

def main():
    # Validate script exists
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {{script_path}}", file=sys.stderr)
        sys.exit(1)
    
    # Check if script is readable
    if not os.access(script_path, os.R_OK):
        print(f"Error: Cannot read script: {{script_path}}", file=sys.stderr)
        sys.exit(1)
    
    # Get script arguments
    args = sys.argv[1:]
    
    try:
        # Execute the script
        os.execv(sys.executable, [sys.executable, script_path] + args)
    except OSError as e:
        print(f"Error executing script: {{e}}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {{e}}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''


def ensure_bin_in_path() -> None:
    """Ensure user's local bin directory is in PATH"""
    bin_dir = os.path.dirname(constants.INSTALL_LINK)
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir, exist_ok=True)

    # Check if already in PATH
    if constants.is_bin_in_path():
        return

    # Add to PATH in shell config if not already there
    shell_config = constants.get_shell_config_file()
    if shell_config:
        try:
            with open(shell_config, 'r') as f:
                content = f.read()

            # Different PATH formats for different shells
            shell = constants.SHELL_NAME.lower()
            if shell == "fish":
                path_line = f'set -gx PATH $PATH "{bin_dir}"'
            else:
                path_line = f'export PATH="$PATH:{bin_dir}"'
            
            if path_line not in content and bin_dir not in content:
                with open(shell_config, 'a') as f:
                    f.write(f'\n# Added by Bake\n{path_line}\n')
                print(f"Added {bin_dir} to PATH in {shell_config}")
                print("Please restart your terminal or run:")
                print(f"    source {shell_config}")
        except Exception as e:
            print(f"Warning: Could not update shell config: {e}")
    else:
        print(f"Warning: Could not detect shell config file.")
        print(f"Please add {bin_dir} to your PATH manually.")


def add_command(args: argparse.Namespace, printer: CustomPrinter) -> None:
    logger = logging.getLogger('bake')
    logger.info(f"Adding command: {args.name}")
    
    # Validate command name
    is_valid, error_msg = validate_command_name(args.name)
    if not is_valid:
        logger.warning(f"Invalid command name '{args.name}': {error_msg}")
        printer.error(error_msg)
        return

    # Validate script path
    script_path = os.path.abspath(args.script_path.name)
    is_valid, error_msg = validate_script_path(script_path)
    if not is_valid:
        logger.warning(f"Invalid script path '{script_path}': {error_msg}")
        printer.error(error_msg)
        return
    
    logger.debug(f"Command '{args.name}' validated successfully")

    wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, args.name)
    symlink_path = os.path.join(constants.USER_BIN_DIR, args.name)

    # Check if command already exists and confirm overwrite
    if (os.path.exists(wrapper_path) or os.path.exists(symlink_path)) and not args.force:
        printer.warn(f"Command '{args.name}' already exists!")
        if os.path.exists(wrapper_path):
            with open(wrapper_path, 'r') as f:
                content = f.read()
                current_script = content.split('script_path = "')[1].split('"')[0]
                printer.info(f"Current script: {current_script}")
                printer.info(f"New script: {script_path}")

        confirm = printer.input("\nDo you want to overwrite it? [y/N]: ").lower()
        if confirm != 'y':
            printer.info("Command creation cancelled.")
            return

    try:
        # Create wrapper script
        with open(wrapper_path, 'w') as f:
            f.write(create_wrapper_script(script_path))

        # Make executable
        os.chmod(wrapper_path, 0o755)

        # Create symlink
        if os.path.exists(symlink_path):
            safe_remove_symlink(symlink_path, printer)
        os.symlink(wrapper_path, symlink_path)

        logger.info(f"Successfully added command '{args.name}' pointing to {script_path}")
        printer.success(f"Added command '{args.name}' pointing to {script_path}")
        
    except OSError as e:
        logger.error(f"Failed to create command '{args.name}': {e}")
        printer.error(f"Failed to create command: {e}")
        # Clean up wrapper script if it was created
        safe_remove_file(wrapper_path, printer)
        return


def edit_command(args: argparse.Namespace, printer: CustomPrinter) -> None:
    wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, args.name)
    if not os.path.exists(wrapper_path):
        printer.error(f"Command not found: {args.name}")
        return

    editor = os.environ.get('EDITOR', 'nano')
    os.system(f"{editor} {wrapper_path}")
    printer.success(f"Edited command '{args.name}'")


def delete_command(args: argparse.Namespace, printer: CustomPrinter) -> None:
    wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, args.name)
    symlink_path = os.path.join(constants.USER_BIN_DIR, args.name)

    if not os.path.exists(wrapper_path):
        printer.error(f"Command not found: {args.name}")
        return

    # Remove symlink first
    symlink_removed = safe_remove_symlink(symlink_path, printer)
    
    # Remove wrapper script
    wrapper_removed = safe_remove_file(wrapper_path, printer)
    
    if symlink_removed and wrapper_removed:
        printer.success(f"Deleted command '{args.name}'")
    else:
        printer.warn(f"Partially deleted command '{args.name}' (some files may remain)")


def rename_command(args: argparse.Namespace, printer: CustomPrinter) -> None:
    """Rename an existing command"""
    old_name = args.old_name
    new_name = args.new_name
    
    # Validate new command name
    is_valid, error_msg = validate_command_name(new_name)
    if not is_valid:
        printer.error(error_msg)
        return
    
    # Prevent renaming to the same name
    if old_name == new_name:
        printer.error("Old name and new name are the same.")
        return
    
    old_wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, old_name)
    old_symlink_path = os.path.join(constants.USER_BIN_DIR, old_name)
    new_wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, new_name)
    new_symlink_path = os.path.join(constants.USER_BIN_DIR, new_name)
    
    # Check if old command exists
    if not os.path.exists(old_wrapper_path):
        printer.error(f"Command not found: {old_name}")
        return
    
    # Check if new command already exists and confirm overwrite
    if (os.path.exists(new_wrapper_path) or os.path.exists(new_symlink_path)) and not args.force:
        printer.warn(f"Command '{new_name}' already exists!")
        if os.path.exists(new_wrapper_path):
            with open(new_wrapper_path, 'r') as f:
                content = f.read()
                current_script = content.split('script_path = "')[1].split('"')[0]
                printer.info(f"Current script: {current_script}")
        
        confirm = printer.input("\nDo you want to overwrite it? [y/N]: ").lower()
        if confirm != 'y':
            printer.info("Command rename cancelled.")
            return
    
    try:
        # Read the current wrapper script to get the target script path
        with open(old_wrapper_path, 'r') as f:
            content = f.read()
            script_path = content.split('script_path = "')[1].split('"')[0]
        
        # Create new wrapper script with the new name
        with open(new_wrapper_path, 'w') as f:
            f.write(create_wrapper_script(script_path))
        
        # Make new wrapper script executable
        os.chmod(new_wrapper_path, 0o755)
        
        # Create new symlink
        if os.path.exists(new_symlink_path):
            safe_remove_symlink(new_symlink_path, printer)
        os.symlink(new_wrapper_path, new_symlink_path)
        
        # Remove old symlink
        safe_remove_symlink(old_symlink_path, printer)
        
        # Remove old wrapper script
        safe_remove_file(old_wrapper_path, printer)
        
        printer.success(f"Renamed command '{old_name}' to '{new_name}'")
        
    except Exception as e:
        printer.error(f"Failed to rename command: {str(e)}")
        # Clean up if something went wrong
        safe_remove_file(new_wrapper_path, printer)
        safe_remove_symlink(new_symlink_path, printer)


def health_check(printer: CustomPrinter) -> None:
    """Check installation health and diagnose issues"""
    printer.info("Running Bake health check...")
    
    issues = []
    warnings = []
    
    # Check installation directory
    if not os.path.exists(constants.INSTALL_DIR):
        issues.append("Installation directory not found")
    else:
        printer.success("✓ Installation directory exists")
    
    # Check symlink
    if not os.path.exists(constants.INSTALL_LINK):
        issues.append("Symlink not found")
    else:
        printer.success("✓ Symlink exists")
        
        # Check if symlink is executable
        if not os.access(constants.INSTALL_LINK, os.X_OK):
            issues.append("Symlink is not executable")
        else:
            printer.success("✓ Symlink is executable")
    
    # Check installation script
    if not os.path.exists(constants.INSTALL_SCRIPT):
        issues.append("Installation script not found")
    else:
        printer.success("✓ Installation script exists")
    
    # Check PATH
    if not constants.is_bin_in_path():
        warnings.append("~/.local/bin is not in PATH")
        printer.warn("⚠ ~/.local/bin is not in PATH")
    else:
        printer.success("✓ ~/.local/bin is in PATH")
    
    # Check shell config
    shell_config = constants.get_shell_config_file()
    if not shell_config:
        warnings.append("Could not detect shell config file")
        printer.warn("⚠ Could not detect shell config file")
    else:
        printer.success(f"✓ Shell config detected: {shell_config}")
    
    # Check wrapper scripts directory
    if not os.path.exists(constants.WRAPPER_SCRIPTS_FOLDER):
        warnings.append("Wrapper scripts directory not found")
        printer.warn("⚠ Wrapper scripts directory not found")
    else:
        printer.success("✓ Wrapper scripts directory exists")
    
    # Test script execution
    try:
        import subprocess
        result = subprocess.run([constants.INSTALL_LINK, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            printer.success("✓ Script execution test passed")
        else:
            issues.append(f"Script execution failed: {result.stderr}")
    except Exception as e:
        issues.append(f"Script execution test failed: {e}")
    
    # Summary
    print("\n" + "="*50)
    if not issues and not warnings:
        printer.success("🎉 All checks passed! Bake is healthy.")
    else:
        if issues:
            printer.error(f"❌ Found {len(issues)} critical issue(s):")
            for issue in issues:
                printer.error(f"  • {issue}")
        
        if warnings:
            printer.warn(f"⚠️  Found {len(warnings)} warning(s):")
            for warning in warnings:
                printer.warn(f"  • {warning}")
        
        print("\nRecommendations:")
        if not constants.is_bin_in_path():
            printer.info("  • Add ~/.local/bin to your PATH")
            printer.info("  • Restart your terminal or run: source ~/.bashrc")
        
        if not shell_config:
            printer.info("  • Ensure you have a shell config file (.bashrc, .zshrc, etc.)")


def check_for_updates() -> Tuple[bool, Optional[str], Optional[dict]]:
    """Check if there are updates available"""
    try:
        import urllib.request
        import json
        
        with urllib.request.urlopen(constants.GITHUB_API_URL, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        latest_version = data.get("tag_name", "").lstrip("v")
        current_version = constants.VERSION
        
        if latest_version and latest_version != current_version:
            return True, latest_version, data
        return False, None, None
        
    except Exception as e:
        return False, None, None


def update_bake(args: argparse.Namespace, printer: CustomPrinter) -> None:
    """Update Bake to the latest version"""
    logger = logging.getLogger('bake')
    logger.info("Checking for updates...")
    
    printer.info("Checking for updates...")
    
    has_update, latest_version, release_data = check_for_updates()
    
    if not has_update:
        printer.success("You're already running the latest version!")
        return
    
    if not latest_version or not release_data:
        printer.error("Failed to check for updates. Please try again later.")
        return
    
    current_version = constants.VERSION
    printer.info(f"Current version: {current_version}")
    printer.info(f"Latest version: {latest_version}")
    
    # Show release notes if available
    if release_data.get("body"):
        printer.info("\nRelease notes:")
        printer.info("-" * 50)
        # Truncate long release notes
        body = release_data["body"]
        if len(body) > 500:
            body = body[:500] + "\n... (truncated)"
        printer.info(body)
        printer.info("-" * 50)
    
    # Confirm update
    if not args.force:
        confirm = printer.input(f"\nUpdate to version {latest_version}? [y/N]: ").lower()
        if confirm != 'y':
            printer.info("Update cancelled.")
            return
    
    printer.info("Starting update process...")
    
    try:
        # Download the latest release
        download_url = None
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".py") or "bake" in asset["name"].lower():
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            # Fallback: download from main branch
            download_url = "https://raw.githubusercontent.com/Izaan17/Bake-2.0/main/bake.py"
        
        printer.info("Downloading latest version...")
        
        import urllib.request
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.py') as temp_file:
            with urllib.request.urlopen(download_url, timeout=30) as response:
                temp_file.write(response.read())
            temp_file_path = temp_file.name
        
        # Backup current installation
        backup_path = f"{constants.INSTALL_SCRIPT}.backup"
        if os.path.exists(constants.INSTALL_SCRIPT):
            shutil.copy2(constants.INSTALL_SCRIPT, backup_path)
            printer.debug(f"Created backup: {backup_path}")
        
        # Update the main script
        shutil.copy2(temp_file_path, constants.INSTALL_SCRIPT)
        os.chmod(constants.INSTALL_SCRIPT, 0o755)
        
        # Update constants.py if it exists in the download
        try:
            constants_url = "https://raw.githubusercontent.com/Izaan17/Bake-2.0/main/constants.py"
            with urllib.request.urlopen(constants_url, timeout=10) as response:
                constants_content = response.read().decode()
            
            constants_path = os.path.join(constants.INSTALL_DIR, "constants.py")
            with open(constants_path, 'w') as f:
                f.write(constants_content)
            printer.debug("Updated constants.py")
        except Exception as e:
            printer.warn(f"Could not update constants.py: {e}")
        
        # Update printer.py if it exists in the download
        try:
            printer_url = "https://raw.githubusercontent.com/Izaan17/Bake-2.0/main/printer.py"
            with urllib.request.urlopen(printer_url, timeout=10) as response:
                printer_content = response.read().decode()
            
            printer_path = os.path.join(constants.INSTALL_DIR, "printer.py")
            with open(printer_path, 'w') as f:
                f.write(printer_content)
            printer.debug("Updated printer.py")
        except Exception as e:
            printer.warn(f"Could not update printer.py: {e}")
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        # Validate the update
        printer.info("Validating update...")
        is_valid, message = validate_installation()
        
        if is_valid:
            printer.success(f"Successfully updated to version {latest_version}!")
            printer.info("You can now use the updated Bake commands.")
            
            # Remove backup if update was successful
            if os.path.exists(backup_path):
                os.remove(backup_path)
        else:
            printer.error(f"Update validation failed: {message}")
            printer.info("Restoring from backup...")
            
            # Restore from backup
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, constants.INSTALL_SCRIPT)
                os.remove(backup_path)
                printer.info("Restored from backup.")
            else:
                printer.error("No backup found. You may need to reinstall Bake.")
        
    except Exception as e:
        logger.error(f"Update failed: {e}")
        printer.error(f"Update failed: {e}")
        printer.info("You can try updating manually by visiting:")
        printer.info(constants.GITHUB_RELEASE_URL)


def list_commands(printer: CustomPrinter) -> None:
    """List all installed commands with their target scripts"""
    if not os.path.exists(constants.WRAPPER_SCRIPTS_FOLDER):
        printer.warn("Wrapper scripts folder missing.")
        return

    commands = os.listdir(constants.WRAPPER_SCRIPTS_FOLDER)
    if not commands:
        printer.info("No commands baked yet.")
        return

    table = Table(show_header=True, header_style="bold", box=rich.box.SIMPLE)
    table.add_column("#", style="dim", width=6, header_style="blue", justify="center")
    table.add_column("Command Name", min_width=20, justify="left")
    table.add_column("Script Location", min_width=12)

    # Add all command information to the table
    for index, cmd in enumerate(sorted(commands), start=1):
        wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, cmd)
        # Read the script to get the target path
        with open(wrapper_path, 'r') as f:
            content = f.read()
            # Extract the script path from the wrapper
            script_path = content.split('script_path = "')[1].split('"')[0]
        table.add_row(str(index), cmd, script_path)
    printer.print(table)


def validate_installation() -> Tuple[bool, str]:
    """Validate that the installation is working correctly"""
    try:
        # Check if symlink exists and is executable
        if not os.path.exists(constants.INSTALL_LINK):
            return False, "Symlink not found"
        
        if not os.access(constants.INSTALL_LINK, os.X_OK):
            return False, "Symlink is not executable"
        
        # Check if the symlink points to the correct file
        if not os.path.exists(constants.INSTALL_SCRIPT):
            return False, "Installation script not found"
        
        # Test if the script can be executed
        import subprocess
        result = subprocess.run([constants.INSTALL_LINK, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, f"Script execution failed: {result.stderr}"
        
        return True, "Installation is valid"
    except Exception as e:
        return False, f"Validation error: {e}"


def install(args: argparse.Namespace) -> None:
    printer = CustomPrinter(args.debug)
    logger = logging.getLogger('bake')
    
    logger.info("Starting installation process")

    # Create necessary directories
    os.makedirs(constants.WRAPPER_SCRIPTS_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(constants.INSTALL_LINK), exist_ok=True)

    printer.info("Creating directories...")
    printer.success("Created necessary directories.")

    # Get the absolute path of the current script
    current_script = os.path.abspath(__file__)

    try:
        # Create installation directory if it doesn't exist
        os.makedirs(constants.INSTALL_DIR, exist_ok=True)

        # Create the executable script with shebang
        printer.info("Creating executable script...")
        with open(current_script, 'r') as source:
            script_content = source.read()

        with open(constants.INSTALL_SCRIPT, 'w') as dest:
            dest.write('#!/usr/bin/env python3\n')
            dest.write(script_content)

        # Make the script executable
        os.chmod(constants.INSTALL_SCRIPT, 0o755)

        # Create symbolic link
        if os.path.exists(constants.INSTALL_LINK):
            printer.info("Removing existing symbolic link...")
            os.remove(constants.INSTALL_LINK)

        printer.info(f"Creating symbolic link at {constants.INSTALL_LINK}...")
        os.symlink(constants.INSTALL_SCRIPT, constants.INSTALL_LINK)

        # Copy dependencies
        current_dir = os.path.dirname(current_script)
        for file in ["constants.py", "printer.py"]:
            src = os.path.join(current_dir, file)
            dst = os.path.join(constants.INSTALL_DIR, file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                printer.debug(f"Copied {file}")

        # Ensure bin directory is in PATH
        ensure_bin_in_path()

        # Validate installation
        printer.info("Validating installation...")
        is_valid, message = validate_installation()
        if is_valid:
            printer.success(f"Successfully installed! You can now use 'bake' from anywhere.")
            printer.info("Installation validated successfully.")
        else:
            printer.warn(f"Installation completed but validation failed: {message}")
            printer.info("You may need to restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc)")

    except Exception as e:
        logger.error(f"Installation failed: {e}")
        printer.error(f"Installation failed: {str(e)}")
        sys.exit(1)


def uninstall(args: argparse.Namespace) -> None:
    printer = CustomPrinter(args.debug)
    try:
        # Check if paths exist
        wrapper_scripts_exists = os.path.exists(constants.WRAPPER_SCRIPTS_FOLDER)
        install_link_exists = os.path.exists(constants.INSTALL_LINK)
        install_dir_exists = os.path.exists(constants.INSTALL_DIR)

        # For hard uninstall, confirm unless force flag is used
        if args.hard and not args.force:
            printer.warn("WARNING: Hard uninstall will remove all bake command aliases!")
            printer.info("This will delete the following commands:")

            # List commands that will be deleted
            if wrapper_scripts_exists:
                commands = os.listdir(constants.WRAPPER_SCRIPTS_FOLDER)
                if commands:
                    for cmd in commands:
                        printer.print(f"  - {cmd}")
                else:
                    printer.info("  No commands found.")

            confirm = input("\nAre you sure you want to proceed? [y/N]: ").lower()
            if confirm != 'y':
                printer.info("Uninstall cancelled.")
                return

        # Remove symbolic link if it exists
        if install_link_exists:
            printer.info("Removing symbolic link...")
            os.remove(constants.INSTALL_LINK)

        # If hard uninstall requested, remove all command symlinks
        if args.hard and wrapper_scripts_exists:
            printer.info("Removing all bake command aliases...")
            for cmd in os.listdir(constants.WRAPPER_SCRIPTS_FOLDER):
                symlink_path = os.path.join(constants.USER_BIN_DIR, cmd)
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                    printer.debug(f"Removed alias: {cmd}")

        # Remove installation directory if it exists
        if install_dir_exists:
            printer.info("Removing installation directory...")
            shutil.rmtree(constants.INSTALL_DIR)

        printer.success("Successfully uninstalled bake.")
    except FileNotFoundError as e:
        printer.error(f"File not found during uninstallation: {str(e)}")
        sys.exit(1)
    except PermissionError as e:
        printer.error(f"Permission error during uninstallation: {str(e)}")
        sys.exit(1)
    except Exception as e:
        printer.error(f"Uninstallation failed: {str(e)}")
        sys.exit(1)


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger('bake')
    
    printer = CustomPrinter(args.debug)
    
    logger.info(f"Bake started with args: {vars(args)}")

    # Check for updates (only for certain commands to avoid spam)
    if args.action in ["add", "list", "health"] and not args.debug:
        has_update, latest_version, _ = check_for_updates()
        if has_update:
            printer.info(f"💡 Update available! Version {latest_version} is available.")
            printer.info(f"Run 'bake update' to update from {constants.VERSION} to {latest_version}")

    if args.install:
        return install(args)
    elif args.uninstall:
        return uninstall(args)

    if args.version:
        return printer.info(f"v{constants.VERSION}")

    if args.action:
        try:
            match args.action:
                case "add":
                    add_command(args, printer)
                case "edit":
                    edit_command(args, printer)
                case "delete":
                    delete_command(args, printer)
                case "rename":
                    rename_command(args, printer)
                case "health":
                    health_check(printer)
                case "update":
                    update_bake(args, printer)
                case "list":
                    list_commands(printer)
        except Exception as e:
            printer.error(f"Operation failed: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
