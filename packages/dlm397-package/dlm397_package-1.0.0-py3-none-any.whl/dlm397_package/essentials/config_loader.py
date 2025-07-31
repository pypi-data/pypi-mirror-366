import json
import os

def get_home_path():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_config(config_path="config\\config.json"):
    # Get the package config directory, where config.json is located
    package_root = get_home_path() # Gets home directory
    config_file = os.path.join(package_root, config_path)
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_file}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in config file: {config_file}")

def get_path(key, config=None): # key input is some path setting, like "input_dir" which returns the directory designated as inputs
    config = config or load_config()
    relative_path = config.get("paths", {}).get(key, "")
    if not relative_path:
        raise KeyError(f"Path key '{key}' not found in config")
    # Resolve relative path to absolute path
    package_root = get_home_path()
    return os.path.join(package_root, relative_path) # Returns the file path for the input key, joined with the package root so it can be called

def get_setting(key, config=None): # key input is some setting that is not a path, like "default_form"
    """Get a setting from the config."""
    config = config or load_config()
    return config.get("settings", {}).get(key, None)

def save_config(data):
    package_root = get_home_path() # Gets home directory
    config_path="config\\config.json"
    config_file = os.path.join(package_root, config_path)
    with open(config_file, "w") as file:
        json.dump(data, file, indent=4)
    return True

def change_path(key, change, config=None):
    config = config or load_config()
    if str(type(change)) == "<class 'str'>":
        config["paths"][key] = change
        result = save_config(config)
        if result:
            print("Path successfully updated")
            return True
        else:
            print("Path did not update")
            return False
    else:
        print("Config path doesn't exist, or change value not acceptable.")
        return False
    
def change_setting(key, change, config=None):
    config = config or load_config()
    if str(type(change)) == "<class 'str'>" and key in config:
        config["setting"][key] = change
        result = save_config(config)
        if result:
            print("Path successfully updated")
            return True
        else:
            print("Path did not update")
            return False
    else:
        print("Config setting doesn't exist, or change value not acceptable.")
        return False

