# Bake - Python Script Command Manager

Bake is a simple tool that makes it easy to convert your Python scripts into terminal commands. Instead of typing
`python3 /path/to/your/script.py`, you can create simple command aliases that run your scripts from anywhere.

## Why I Made This Tool

As a developer, I often found myself running various Python scripts from different directories, which required typing
long file paths and using `python3` every time. This was not only inefficient but also cumbersome. I wanted a way to
quickly execute my scripts as if they were native terminal commands, without manually adding them to my system's PATH or
creating shell aliases. Thus, Bake was born—a lightweight, user-friendly tool to simplify command management for Python
scripts.

## Purpose and Need

Bake addresses a common problem faced by developers, sysadmins, and automation enthusiasts who frequently use Python
scripts. Instead of repeatedly navigating directories and running scripts with `python3 script.py`, Bake allows users to
create system-wide aliases with ease. It eliminates the need for manual shell configurations and provides a seamless way
to manage script-based commands across different shell environments.

## Features

- Convert Python scripts into system-wide commands
- Add, edit, delete, rename, and list your commands
- Automatic update system with GitHub integration
- Robust error handling and validation
- Comprehensive logging system
- No sudo required - everything is installed in your user space
- Automatic PATH management
- Works with bash, zsh, and fish shells
- Reserved command name protection
- Safe file operations with cleanup
- Health check and diagnostics

## Installation

### Option 1: Pip Installation (Recommended)

```bash
pip install bake-command-manager
bake --install
```

### Option 2: Manual Installation

1. Clone this repository:

```bash
git clone https://github.com/Izaan17/Bake-2.0.git
cd Bake-2.0
```

2. Install the project requirements:

```bash
pip install -r requirements.txt
```

3. Install bake:

```bash
python bake.py --install
```

### Post-Installation

After installation, restart your terminal or source your shell configuration:

```bash
# For bash
source ~/.bashrc

# For zsh
source ~/.zshrc

# For fish
source ~/.config/fish/config.fish
```

### Verify Installation

Check if everything is working correctly:

```bash
bake health
```

## Usage

### Example File `hello.py`

```python
import sys

print(f"Hello {sys.argv[1]}!")
```

### Add a new command

Convert a Python script into a command:

```bash
bake add hello ~/scripts/hello.py
```

Now you can run `hello` from anywhere in your terminal.

Input:

`hello John`

Output:

`Hello John!`

### List all commands

View all installed commands:

```bash
bake list
```

### Edit a command

Open the wrapper script in your default editor (set by $EDITOR):

```bash
bake edit hello
```

### Delete a command

Remove a command:

```bash
bake delete hello
```

### Rename a command

Rename an existing command:

```bash
bake rename hello greet
```

### Update Bake

Update Bake to the latest version:

```bash
bake update
```

### Health check

Check installation health and diagnose issues:

```bash
bake health
```

## Uninstalling

### Basic Uninstall

Remove Bake but keep all your command aliases:

```bash
bake --uninstall
```

### Hard Uninstall

Remove Bake and all command aliases:

```bash
bake --uninstall --hard
```

This will show you what commands will be removed and ask for confirmation.

> ⚠️ Warning: Hard uninstall will remove all commands created with Bake. Make sure to back up any important script paths
> before proceeding.

To skip the confirmation prompt:

```bash
bake --uninstall --hard -f
```

> 🚨️ Warning: Hard uninstall will remove all commands created with Bake. **With the -f flag you are skipping the
> confirmation prompt**. Make sure to back up any important script paths
> before proceeding.

## File Structure

Bake creates the following directory structure in your home directory:

```
~/.local/
├── bin/          # Command symlinks
└── lib/bake/     # Installation directory
    ├── bake.py   # Main script
    ├── scripts/  # Wrapper scripts
    └── ...       # Other required files
```

## Options

```bash
bake [-h] [-i] [-d] [--uninstall] [--hard] [-f] [-v] {add,edit,delete,rename,update,health,list} ...

optional arguments:
  -h, --help     show this help message and exit
  -i, --install  Install bake
  -d, --debug    Enable debug output and logging
  --uninstall    Uninstall bake
  --hard         Also remove all bake command aliases during uninstall
  -f, --force    Skip confirmation prompts
  -v, --version  Outputs the current version number

actions:
  {add,edit,delete,rename,update,health,list}
    add          Add a new command
    edit         Edit an existing command
    delete       Delete an existing command
    rename       Rename an existing command
    update       Update Bake to the latest version
    health       Check installation health and diagnose issues
    list         List all installed commands
```

## New Features & Improvements

### Enhanced Validation

- **Command Name Validation**: Ensures command names follow proper naming conventions
- **Reserved Name Protection**: Prevents using system command names like `python`, `git`, `ls`, etc.
- **Script Path Validation**: Validates that script files exist and are readable Python files

### Update System

- **Automatic Updates**: Check for updates from GitHub releases
- **One-Click Updates**: Update with a single `bake update` command
- **Release Notes**: View what's new in each update
- **Safe Updates**: Automatic backup and rollback on failure
- **Update Notifications**: Get notified when updates are available

### Improved Error Handling

- **Safe File Operations**: All file operations include proper error handling and cleanup
- **Detailed Error Messages**: Clear, actionable error messages for better debugging
- **Graceful Degradation**: Partial failures are handled gracefully with appropriate warnings

### Logging System

- **Debug Logging**: Comprehensive logging when using `--debug` flag
- **Log Files**: Persistent logging to `~/.local/lib/bake/logs/bake.log`
- **Operation Tracking**: All operations are logged for troubleshooting

### Enhanced Wrapper Scripts

- **Error Handling**: Wrapper scripts include proper error handling and validation
- **Better Error Messages**: Clear error messages when scripts fail to execute
- **Path Validation**: Wrapper scripts validate script existence before execution

## Requirements

- Python 3.10+
- Unix-like operating system (Linux, macOS)
- Either bash, zsh, or fish
