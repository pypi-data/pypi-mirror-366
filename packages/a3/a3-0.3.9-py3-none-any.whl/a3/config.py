"""
Configuration management for A3.

This module handles loading and managing A3 configuration from various sources.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class A3Config:
    """A3 configuration settings."""
    
    # API settings
    api_key: Optional[str] = None
    model: str = "anthropic/claude-3-sonnet"
    max_retries: int = 3
    use_fallback_models: bool = False
    
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
    
    # Test generation preferences
    test_framework: str = "pytest"
    test_coverage_threshold: float = 80.0
    generate_integration_tests: bool = True
    test_file_naming: str = "test_{module_name}.py"
    mock_external_dependencies: bool = True
    
    # Database connection settings
    default_database_url: Optional[str] = None
    database_connection_timeout: int = 30
    database_pool_size: int = 5
    database_ssl_mode: str = "prefer"
    
    # Package management settings
    package_aliases: Dict[str, str] = None
    enforce_import_consistency: bool = True
    auto_generate_requirements: bool = True
    requirements_file_name: str = "requirements.txt"
    
    # Data source analysis settings
    analyze_data_sources_by_default: bool = False
    max_data_file_size_mb: int = 100
    data_sample_size: int = 1000
    supported_data_formats: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for complex types."""
        if self.package_aliases is None:
            self.package_aliases = {
                "pandas": "pd",
                "numpy": "np",
                "matplotlib.pyplot": "plt",
                "seaborn": "sns",
                "tensorflow": "tf",
                "torch": "torch",
                "requests": "requests",
                "json": "json",
                "os": "os",
                "sys": "sys",
                "pathlib": "Path",
                "datetime": "datetime",
                "typing": "typing"
            }
        
        if self.supported_data_formats is None:
            self.supported_data_formats = ["csv", "json", "xml", "xlsx", "xls", "yaml", "yml"]
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'A3Config':
        """Load configuration from file or environment."""
        config = cls()
        
        # Load from environment variables
        config.api_key = os.getenv('A3_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        config.default_workspace = os.getenv('A3_WORKSPACE')
        config.default_database_url = os.getenv('A3_DATABASE_URL')
        
        if max_retries := os.getenv('A3_MAX_RETRIES'):
            try:
                config.max_retries = int(max_retries)
            except ValueError:
                pass
        
        if generate_tests := os.getenv('A3_GENERATE_TESTS'):
            config.generate_tests = generate_tests.lower() in ('true', '1', 'yes', 'on')
        
        if test_framework := os.getenv('A3_TEST_FRAMEWORK'):
            config.test_framework = test_framework
        
        if database_timeout := os.getenv('A3_DATABASE_TIMEOUT'):
            try:
                config.database_connection_timeout = int(database_timeout)
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
        
        # Don't save sensitive data like API keys or database URLs to file
        config_dict = asdict(self)
        config_dict.pop('api_key', None)
        config_dict.pop('default_database_url', None)
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_workspace_path(self, relative_path: str) -> str:
        """Resolve path relative to workspace if configured."""
        if self.default_workspace and not os.path.isabs(relative_path):
            return str(Path(self.default_workspace) / relative_path)
        return relative_path