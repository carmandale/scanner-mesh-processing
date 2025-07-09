#!/bin/bash

# Configuration reader for scanner mesh processing pipeline (Shell version)
# Usage: source config_reader.sh [environment]
# or: ./config_reader.sh --get path_key [environment]

# Get the directory containing this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Default environment
DEFAULT_ENVIRONMENT="server"

# Function to get a path from the config
get_config_path() {
    local path_key="$1"
    local environment="${2:-$DEFAULT_ENVIRONMENT}"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Error: Config file not found: $CONFIG_FILE" >&2
        return 1
    fi
    
    # Use Python to parse JSON (since jq might not be available)
    python3 -c "
import json
import sys

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    
    environment = '$environment'
    if environment not in config.get('environments', {}):
        available = list(config.get('environments', {}).keys())
        print(f'Error: Environment \'{environment}\' not found. Available: {available}', file=sys.stderr)
        sys.exit(1)
    
    path_key = '$path_key'
    env_config = config['environments'][environment]
    
    if path_key not in env_config:
        print(f'Error: Path \'{path_key}\' not found in environment \'{environment}\'', file=sys.stderr)
        sys.exit(1)
    
    print(env_config[path_key])
    
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Function to set environment variables from config
set_config_vars() {
    local environment="${1:-$DEFAULT_ENVIRONMENT}"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Error: Config file not found: $CONFIG_FILE" >&2
        return 1
    fi
    
    # Use Python to parse JSON and output shell variable assignments
    eval "$(python3 -c "
import json
import sys

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    
    environment = '$environment'
    if environment not in config.get('environments', {}):
        available = list(config.get('environments', {}).keys())
        print(f'Error: Environment \'{environment}\' not found. Available: {available}', file=sys.stderr)
        sys.exit(1)
    
    env_config = config['environments'][environment]
    
    # Output shell variable assignments
    for key, value in env_config.items():
        var_name = key.upper()
        print(f'export {var_name}=\"{value}\"')
    
    # Also export some convenience variables
    software_path = env_config.get('software_path', '')
    scannermeshprocessing_path = env_config.get('scannermeshprocessing_path', '')
    
    # Export asset paths
    for asset_key, asset_file in config.get('assets', {}).items():
        var_name = f'{asset_key.upper()}_PATH'
        full_path = f'{scannermeshprocessing_path}/{asset_file}'
        print(f'export {var_name}=\"{full_path}\"')
    
    # Export executable paths
    for exec_key, exec_path in config.get('executables', {}).items():
        var_name = f'{exec_key.upper()}_PATH'
        full_path = f'{software_path}/{exec_path}'
        print(f'export {var_name}=\"{full_path}\"')
    
    print(f'export CONFIG_ENVIRONMENT=\"{environment}\"')
    
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
")"
}

# Function to show environment info
show_environment_info() {
    local environment="${1:-$DEFAULT_ENVIRONMENT}"
    
    python3 -c "
import json
import sys

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    
    environment = '$environment'
    if environment not in config.get('environments', {}):
        available = list(config.get('environments', {}).keys())
        print(f'Error: Environment \'{environment}\' not found. Available: {available}', file=sys.stderr)
        sys.exit(1)
    
    print(f'Environment: {environment}')
    print(f'Config file: $CONFIG_FILE')
    print('Paths:')
    
    env_config = config['environments'][environment]
    for key, value in env_config.items():
        print(f'  {key}: {value}')
    
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Command line interface
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Script is being executed directly
    case "${1:-}" in
        --get)
            if [ $# -lt 2 ]; then
                echo "Usage: $0 --get path_key [environment]"
                exit 1
            fi
            get_config_path "$2" "$3"
            ;;
        --info)
            show_environment_info "$2"
            ;;
        --set-vars)
            set_config_vars "$2"
            ;;
        *)
            echo "Usage: $0 [--get path_key] [--info] [--set-vars] [environment]"
            echo ""
            echo "Commands:"
            echo "  --get path_key [env]    Get a specific path"
            echo "  --info [env]            Show environment info"
            echo "  --set-vars [env]        Output shell variable assignments"
            echo ""
            echo "Or source this script to use functions:"
            echo "  source $0 [environment]"
            exit 1
            ;;
    esac
else
    # Script is being sourced
    ENVIRONMENT="${1:-$DEFAULT_ENVIRONMENT}"
    set_config_vars "$ENVIRONMENT"
    echo "Config loaded for environment: $ENVIRONMENT" >&2
fi 