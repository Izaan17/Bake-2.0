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
- Add, edit, delete, and list your commands
- No sudo required - everything is installed in your user space
- Automatic PATH management
- Works with bash, zsh, and fish shells

## Installation

1. Clone this repository:

```bash
git clone https://github.com/Izaan17/Bake-2.0.git
cd bake
```

2. Install bake:

```bash
python bake.py --install
```

3. Restart your terminal or source your shell configuration:

```bash
# For bash
source ~/.bashrc

# For zsh
source ~/.zshrc

# For fish
source ~/.config/fish/config.fish
```

## Usage

### Example File `hello.py`

```python
print("hello world")
```

### Add a new command

Convert a Python script into a command:

```bash
bake add hello ~/scripts/hello.py
```

Now you can run `hello` from anywhere in your terminal.

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

> ⚠️ Warning: Hard uninstall will remove all commands created with Bake. **With the -f flag you are skipping the
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
bake [-h] [-i] [-d] [--uninstall] {add,edit,delete,list} ...

optional arguments:
  -h, --help     show this help message and exit
  -i, --install  Install bake
  -d, --debug    Enable debug output
  --uninstall    Uninstall bake

actions:
  {add,edit,delete,list}
    add          Add a new command
    edit         Edit an existing command
    delete       Delete an existing command
    list         List all installed commands
```

## Requirements

- Python 3.6+
- Unix-like operating system (Linux, macOS)
- Either bash, zsh, or fish

