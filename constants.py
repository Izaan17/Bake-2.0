import os

# Get user's home directory
HOME = os.path.expanduser("~")
USER_BIN_DIR = os.path.join(HOME, ".local", "bin")
VERSION = "1.1.0"

# Update configuration
GITHUB_REPO = "Izaan17/Bake-2.0"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASE_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"

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

    # Check for common shell config files
    config_files = {
        "bash": [".bashrc", ".bash_profile", ".profile"],
        "zsh": [".zshrc", ".zprofile"],
        "fish": ["config.fish"],
        "sh": [".profile"],
        "dash": [".profile"]
    }
    
    if shell in config_files:
        for config_file in config_files[shell]:
            if shell == "fish":
                config_path = os.path.join(home, ".config", "fish", config_file)
            else:
                config_path = os.path.join(home, config_file)
            
            if os.path.exists(config_path):
                return config_path
    
    # Fallback to common config files
    fallback_files = [".bashrc", ".zshrc", ".profile"]
    for config_file in fallback_files:
        config_path = os.path.join(home, config_file)
        if os.path.exists(config_path):
            return config_path
    
    return None


def is_bin_in_path() -> bool:
    """Check if the user's bin directory is in PATH"""
    bin_dir = USER_BIN_DIR
    current_path = os.environ.get("PATH", "")
    return bin_dir in current_path.split(":")
