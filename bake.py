#!/usr/bin/env python3
import argparse
import os
import shutil
import sys

import rich.box
from rich.table import Table

import constants
from printer import CustomPrinter


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

    return parser


def create_wrapper_script(script_path: str) -> str:
    return f'''#!/usr/bin/env python3
import sys
import os

script_path = "{script_path}"

if __name__ == "__main__":
    args = sys.argv[1:]
    os.execv(sys.executable, [sys.executable, script_path] + args)
'''


def ensure_bin_in_path() -> None:
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


def add_command(args: argparse.Namespace, printer: CustomPrinter) -> None:
    # Prevent creating a command named "bake"
    if args.name.lower() == "bake":
        printer.error('Cannot create a command named "bake" as it would conflict with the main script.')
        return

    script_path = os.path.abspath(args.script_path.name)
    if not os.path.exists(script_path):
        printer.error(f"Script not found: {script_path}")
        return

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

    # Create wrapper script
    with open(wrapper_path, 'w') as f:
        f.write(create_wrapper_script(script_path))

    # Make executable
    os.chmod(wrapper_path, 0o755)

    # Create symlink
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(wrapper_path, symlink_path)

    printer.success(f"Added command '{args.name}' pointing to {script_path}")


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
    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    # Remove wrapper script
    os.remove(wrapper_path)
    printer.success(f"Deleted command '{args.name}'")


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


def install(args: argparse.Namespace) -> None:
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
    printer = CustomPrinter(args.debug)

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
                case "list":
                    list_commands(printer)
        except Exception as e:
            printer.error(f"Operation failed: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
