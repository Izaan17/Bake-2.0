#!/usr/bin/env python3
# Goal:
# Make it easier to make python scripts into terminal commands.
# MVP:
#   - Be able to add a script as a command so you can easily run it in the terminal.
#   - Be able to edit the wrapper script.
#   - Be able to read each wrapper script.
#   - Be able to delete the wrapper script.
import argparse
import os
import shutil
import sys

import rich.box
from rich.table import Table

import constants
from printer import CustomPrinter


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Optional arguments for main parser
    parser.add_argument("-i", "--install", action="store_true", help="Install bake.")
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="Set debug status.")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall bake.")
    # Add --hard flag to uninstall
    parser.add_argument("--hard", action="store_true", help="Also remove all bake command aliases during uninstall.")
    parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompts.")

    # Create subparsers for different actions
    subparsers = parser.add_subparsers(dest="action", help="The action to perform")

    # Add command parser
    add_parser = subparsers.add_parser("add", help="Add a new command")
    add_parser.add_argument("name", type=str, help="Name of the command")
    add_parser.add_argument("script_path", type=str, help="Path to the Python script")

    # Edit command parser
    edit_parser = subparsers.add_parser("edit", help="Edit an existing command")
    edit_parser.add_argument("name", help="Name of the command to edit")

    # Delete command parser
    delete_parser = subparsers.add_parser("delete", help="Delete an existing command")
    delete_parser.add_argument("name", help="Name of the command to delete")

    # List command parser
    list_parser = subparsers.add_parser("list", help="List all installed commands")

    return parser


def create_wrapper_script(name: str, script_path: str) -> str:
    return f'''#!/usr/bin/env python3
import sys
import os

script_path = "{script_path}"

if __name__ == "__main__":
    args = sys.argv[1:]
    os.execv(sys.executable, [sys.executable, script_path] + args)
'''


def ensure_bin_in_path():
    """Ensure user's local bin directory is in PATH"""
    bin_dir = os.path.dirname(constants.INSTALL_LINK)
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir, exist_ok=True)

    # Add to PATH in shell config if not already there
    shell_config = constants.get_shell_config_file()
    if shell_config:
        with open(shell_config, 'r') as f:
            content = f.read()

        path_line = f'export PATH="$PATH:{bin_dir}"'
        if path_line not in content:
            with open(shell_config, 'a') as f:
                f.write(f'\n{path_line}\n')
            print(f"Added {bin_dir} to PATH in {shell_config}")
            print("Please restart your terminal or run:")
            print(f"    source {shell_config}")


def add_command(args, printer: CustomPrinter):
    script_path = os.path.abspath(args.script_path)
    if not os.path.exists(script_path):
        printer.error(f"Script not found: {script_path}")
        return

    wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, args.name)

    # Create wrapper script
    with open(wrapper_path, 'w') as f:
        f.write(create_wrapper_script(args.name, script_path))

    # Make executable
    os.chmod(wrapper_path, 0o755)

    # Create symlink
    symlink_path = os.path.join(constants.USER_BIN_DIR, args.name)
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(wrapper_path, symlink_path)

    printer.success(f"Added command '{args.name}' pointing to {script_path}")


def edit_command(args, printer: CustomPrinter):
    wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, args.name)
    if not os.path.exists(wrapper_path):
        printer.error(f"Command not found: {args.name}")
        return

    editor = os.environ.get('EDITOR', 'nano')
    os.system(f"{editor} {wrapper_path}")
    printer.success(f"Edited command '{args.name}'")


def delete_command(args, printer: CustomPrinter):
    wrapper_path = os.path.join(constants.WRAPPER_SCRIPTS_FOLDER, args.name)
    symlink_path = os.path.join(constants.USER_BIN_DIR, args.name)

    if not os.path.exists(wrapper_path):
        printer.error(f"Command not found: {args.name}")
        return

    # Remove symlink first
    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    # Remove wrapper script
    os.remove(wrapper_path)
    printer.success(f"Deleted command '{args.name}'")


def list_commands(args, printer: CustomPrinter):
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
    table.add_column("Command Name", min_width=20, justify="center")
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


def install(args):
    printer = CustomPrinter(args.debug)

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

        printer.success(f"Successfully installed! You can now use 'bake' from anywhere.")

    except Exception as e:
        printer.error(f"Installation failed: {str(e)}")
        sys.exit(1)


def uninstall(args):
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
    printer = CustomPrinter(args.debug)

    if args.install:
        install(args)
        return
    elif args.uninstall:
        uninstall(args)
        return

    if args.action:
        try:
            match args.action:
                case "add":
                    add_command(args, printer)
                case "edit":
                    edit_command(args, printer)
                case "delete":
                    delete_command(args, printer)
                case "list":
                    list_commands(args, printer)
        except Exception as e:
            printer.error(f"Operation failed: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
