"""
Configuration management for A3.

This module handles loading and managing A3 configuration from various sources.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class A3Config:
    """A3 configuration settings."""
    
    # API settings
    api_key: Optional[str] = None
    model: str = "anthropic/claude-3-sonnet"
    max_retries: int = 3
    
    # Project settings
    default_workspace: Optional[str] = None
    auto_install_deps: bool = False
    generate_tests: bool = True
    
    # Code style settings
    code_style: str = "black"
    line_length: int = 88
    type_checking: str = "strict"
    
    # Quality settings
    enforce_single_responsibility: bool = True
    max_functions_per_module: int = 10
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'A3Config':
        """Load configuration from file or environment."""
        config = cls()
        
        # Load from environment variables
        config.api_key = os.getenv('A3_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        config.default_workspace = os.getenv('A3_WORKSPACE')
        
        if max_retries := os.getenv('A3_MAX_RETRIES'):
            try:
                config.max_retries = int(max_retries)
            except ValueError:
                pass
        
        # Load from config file
        if config_path:
            config_file = Path(config_path)
        else:
            # Try common config locations
            config_locations = [
                Path.cwd() / '.a3config.json',
                Path.home() / '.a3config.json',
                Path.cwd() / '.A3' / 'config.json'
            ]
            config_file = None
            for location in config_locations:
                if location.exists():
                    config_file = location
                    break
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Update config with file values
                for key, value in file_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                        
            except (json.JSONDecodeError, IOError) as e:
                # Log warning but continue with defaults
                print(f"Warning: Could not load config from {config_file}: {e}")
        
        return config
    
    def save(self, config_path: str) -> None:
        """Save configuration to file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Don't save sensitive data like API keys to file
        config_dict = asdict(self)
        config_dict.pop('api_key', None)
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_workspace_path(self, relative_path: str) -> str:
        """Resolve path relative to workspace if configured."""
        if self.default_workspace and not os.path.isabs(relative_path):
            return str(Path(self.default_workspace) / relative_path)
        return relative_path