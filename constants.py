import os

# Get user's home directory
HOME = os.path.expanduser("~")
USER_BIN_DIR = os.path.join(HOME, ".local", "bin")
VERSION = 1.0

# Installation paths
INSTALL_DIR = os.path.join(HOME, ".local", "lib", "bake")
INSTALL_SCRIPT = os.path.join(INSTALL_DIR, "bake.py")
INSTALL_LINK = os.path.join(USER_BIN_DIR, "bake")

# Wrapper scripts location
WRAPPER_SCRIPTS_FOLDER = os.path.join(INSTALL_DIR, "scripts")

# Shell detection
SHELL_NAME = os.environ.get("SHELL", "").split("/")[-1]


def get_shell_config_file():
    """Get the appropriate shell config file path"""
    shell = SHELL_NAME.lower()
    home = os.path.expanduser("~")

    if shell == "bash":
        return os.path.join(home, ".bashrc")
    elif shell == "zsh":
        return os.path.join(home, ".zshrc")
    elif shell == "fish":
        return os.path.join(home, ".config", "fish", "config.fish")
    return None
