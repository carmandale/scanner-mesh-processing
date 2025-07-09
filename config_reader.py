#!/usr/bin/env python3
"""
Configuration reader for scanner mesh processing pipeline.
Provides centralized path management for all scripts.
"""

import json
import os
import sys
from pathlib import Path

class ConfigReader:
    def __init__(self, config_file=None, environment=None):
        """
        Initialize config reader.
        
        Args:
            config_file: Path to config file (defaults to config.json in script directory)
            environment: Environment to use ('server', 'local', or None for default)
        """
        if config_file is None:
            script_dir = Path(__file__).parent
            config_file = script_dir / "config.json"
        
        self.config_file = Path(config_file)
        self.environment = environment
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        
        # Set default environment if not specified
        if self.environment is None:
            self.environment = self._config.get('default_environment', 'server')
        
        # Validate environment exists
        if self.environment not in self._config.get('environments', {}):
            available = list(self._config.get('environments', {}).keys())
            raise ValueError(f"Environment '{self.environment}' not found. Available: {available}")
    
    def get_path(self, path_key):
        """Get a path from the current environment configuration."""
        env_config = self._config['environments'][self.environment]
        if path_key not in env_config:
            raise KeyError(f"Path '{path_key}' not found in environment '{self.environment}'")
        return env_config[path_key]
    
    def get_asset_path(self, asset_key):
        """Get full path to an asset file."""
        asset_filename = self._config['assets'].get(asset_key)
        if not asset_filename:
            raise KeyError(f"Asset '{asset_key}' not found in config")
        
        scannermeshprocessing_path = self.get_path('scannermeshprocessing_path')
        return os.path.join(scannermeshprocessing_path, asset_filename)
    
    def get_executable_path(self, executable_key):
        """Get full path to an executable."""
        executable_path = self._config['executables'].get(executable_key)
        if not executable_path:
            raise KeyError(f"Executable '{executable_key}' not found in config")
        
        software_path = self.get_path('software_path')
        return os.path.join(software_path, executable_path)
    
    @property
    def software_path(self):
        """Get software path for current environment."""
        return self.get_path('software_path')
    
    @property
    def takes_path(self):
        """Get takes path for current environment."""
        return self.get_path('takes_path')
    
    @property
    def scannermeshprocessing_path(self):
        """Get scannermeshprocessing path for current environment."""
        return self.get_path('scannermeshprocessing_path')
    
    @property
    def blender_path(self):
        """Get blender path for current environment."""
        return self.get_path('blender_path')
    
    def get_environment_info(self):
        """Get current environment information."""
        return {
            'environment': self.environment,
            'config_file': str(self.config_file),
            'paths': self._config['environments'][self.environment]
        }

def get_config(environment=None):
    """
    Convenience function to get a ConfigReader instance.
    
    Args:
        environment: Environment to use ('server', 'local', or None for default)
    
    Returns:
        ConfigReader instance
    """
    return ConfigReader(environment=environment)

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test configuration reader")
    parser.add_argument('--environment', '-e', help="Environment to use (server, local)")
    parser.add_argument('--path', '-p', help="Path key to retrieve")
    parser.add_argument('--info', '-i', action='store_true', help="Show environment info")
    
    args = parser.parse_args()
    
    try:
        config = get_config(args.environment)
        
        if args.info:
            info = config.get_environment_info()
            print(f"Environment: {info['environment']}")
            print(f"Config file: {info['config_file']}")
            print("Paths:")
            for key, value in info['paths'].items():
                print(f"  {key}: {value}")
        
        if args.path:
            try:
                path = config.get_path(args.path)
                print(f"{args.path}: {path}")
            except KeyError as e:
                print(f"Error: {e}")
                sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 