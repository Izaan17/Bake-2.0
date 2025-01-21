# Bake - Python Script Command Manager

Bake is a simple tool that makes it easy to convert your Python scripts into terminal commands. Instead of typing `python3 /path/to/your/script.py`, you can create simple command aliases that run your scripts from anywhere.

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

2. Make the script executable:
```bash
chmod +x bake.py
```

3. Install bake:
```bash
./bake.py --install
```

4. Restart your terminal or source your shell configuration:
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

### Uninstall bake
Remove bake and all its components:
```bash
bake --uninstall
```

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

## Notes

- All commands are installed in your user space (`~/.local/`) - no sudo required
- Bake automatically adds its bin directory to your PATH
- You can use any text editor by setting the EDITOR environment variable

## Requirements

- Python 3.6+
- Unix-like operating system (Linux, macOS)
- Either bash, zsh, or fish
