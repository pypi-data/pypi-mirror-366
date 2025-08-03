import json
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR_NAME = "ssh_tunnel_manager"
CONFIG_FILE_NAME = "config.json"

# Define a default profile structure
DEFAULT_PROFILE = {
    "server": "",
    "port": 22,
    "key_path": "",
    "auth_method": "key",  # "key" or "password"
    "password": "",  # Note: passwords are stored in plain text - consider security implications
    "port_mappings": [] # List of "local_port:remote_port" strings
}

DEFAULT_CONFIG = {
    "profiles": {"Default": DEFAULT_PROFILE.copy()},
    "last_profile": "Default"
}

def get_config_path() -> Path:
    """Gets the path to the configuration file, ensuring the directory exists."""
    config_dir = Path.home() / ".config" / CONFIG_DIR_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILE_NAME

def load_config() -> Dict[str, Any]:
    """Loads the configuration from the JSON file."""
    config_path = get_config_path()
    if not config_path.exists():
        print(f"Config file not found at {config_path}. Creating default.")
        save_config(DEFAULT_CONFIG) # Save default config if file doesn't exist
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Basic validation/migration could be added here if needed
            if "profiles" not in config or "last_profile" not in config:
                print("Config file is missing expected keys. Using default.")
                return DEFAULT_CONFIG.copy()
            # Ensure default profile exists if mentioned as last_profile but missing
            if config["last_profile"] not in config["profiles"]:
                 if not config["profiles"]: # No profiles left?
                     config["profiles"]["Default"] = DEFAULT_PROFILE.copy()
                     config["last_profile"] = "Default"
                 else: # Point to the first available profile
                    config["last_profile"] = next(iter(config["profiles"]))

            # Ensure all profiles have all keys from default
            for profile_name, profile_data in config["profiles"].items():
                for key, default_value in DEFAULT_PROFILE.items():
                    if key not in profile_data:
                        profile_data[key] = default_value
            return config
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {config_path}. Using default config.")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error loading config: {e}. Using default config.")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Saves the configuration to the JSON file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}")

# Example usage (can be removed later)
if __name__ == '__main__':
    conf = load_config()
    print("Loaded config:")
    print(json.dumps(conf, indent=4))
