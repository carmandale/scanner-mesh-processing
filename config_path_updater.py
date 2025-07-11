#!/usr/bin/env python3
"""
Config Path Updater for Scanner Pipeline Installation
Updates config.json paths to match the detected installation directory
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def update_config_paths(config_file: str, server_base: str) -> bool:
    """
    Update config.json paths to match the installation directory.
    
    Args:
        config_file: Path to config.json file
        server_base: Base directory where groove-test is installed
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config_path = Path(config_file)
        
        # Validate inputs
        if not config_path.exists():
            print(f"ERROR: Config file not found: {config_file}")
            return False
        
        if not Path(server_base).exists():
            print(f"ERROR: Server base directory not found: {server_base}")
            return False
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.with_suffix(f".original.{timestamp}.json")
        
        print(f"Creating backup: {backup_path}")
        with open(config_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate structure
        if 'environments' not in config:
            print("ERROR: No 'environments' section found in config")
            return False
        
        if 'server' not in config['environments']:
            print("ERROR: No 'server' environment found in config")
            return False
        
        # Update server environment paths
        server_config = config['environments']['server']
        old_paths = server_config.copy()
        
        # Update paths
        server_config['software_path'] = os.path.join(server_base, 'software')
        server_config['takes_path'] = os.path.join(server_base, 'takes')
        server_config['scannermeshprocessing_path'] = os.path.join(server_base, 'software', 'scannermeshprocessing-2023')
        
        # Keep blender_path unchanged (system-wide installation)
        # Keep other paths unchanged
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Show what was updated
        print("SUCCESS: Config paths updated")
        print("Updated paths:")
        for key in ['software_path', 'takes_path', 'scannermeshprocessing_path']:
            if key in old_paths and old_paths[key] != server_config[key]:
                print(f"  • {key}: {old_paths[key]} → {server_config[key]}")
            else:
                print(f"  • {key}: {server_config[key]}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to update config: {e}")
        return False

def main():
    """Main function for command line usage."""
    if len(sys.argv) != 3:
        print("Usage: python3 config_path_updater.py <config_file> <server_base>")
        print("Example: python3 config_path_updater.py /path/to/config.json /Users/dalecarman/groove-test")
        sys.exit(1)
    
    config_file = sys.argv[1]
    server_base = sys.argv[2]
    
    success = update_config_paths(config_file, server_base)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 