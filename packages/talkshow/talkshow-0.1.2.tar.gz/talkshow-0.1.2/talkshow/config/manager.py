"""
TalkShow Configuration Manager

Implements industry-standard configuration management with proper precedence:
Environment Variables > User Config > Project Config > Default Config
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from rich.console import Console

console = Console()

@dataclass
class ConfigManager:
    """Configuration manager with proper precedence handling."""
    
    # Configuration paths
    default_config_path: Path = field(default_factory=lambda: Path("config/default.yaml"))
    project_config_path: Optional[Path] = None
    user_config_path: Optional[Path] = None
    
    # Configuration data
    _config: Dict[str, Any] = field(default_factory=dict)
    _loaded: bool = False
    
    def __post_init__(self):
        """Initialize configuration paths."""
        # Find project config (.specstory/talkshow.yaml)
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            project_config = parent / ".specstory" / "talkshow.yaml"
            if project_config.exists():
                self.project_config_path = project_config
                # Set default config path relative to project root
                self.default_config_path = parent / "config" / "default.yaml"
                break
        
        # User config path (future use)
        self.user_config_path = Path.home() / ".talkshow" / "config.yaml"
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with proper precedence."""
        if self._loaded:
            return self._config
        
        # 1. Load default configuration
        default_config = self._load_yaml(self.default_config_path) or {}
        
        # 2. Load project configuration (overrides default)
        project_config = {}
        if self.project_config_path and self.project_config_path.exists():
            project_config = self._load_yaml(self.project_config_path) or {}
        
        # 3. Load user configuration (overrides project)
        user_config = {}
        if self.user_config_path and self.user_config_path.exists():
            user_config = self._load_yaml(self.user_config_path) or {}
        
        # 4. Merge configurations with proper precedence
        self._config = self._merge_configs(default_config, project_config, user_config)
        
        # 5. Override with environment variables
        self._apply_env_overrides()
        
        self._loaded = True
        return self._config
    
    def _load_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML configuration file."""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load config from {path}: {e}[/yellow]")
        return None
    
    def _merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries with proper precedence."""
        result = {}
        for config in configs:
            if config:
                self._deep_merge(result, config)
        return result
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        env_mappings = {
            "TALKSHOW_DATA_FILE": ["storage", "json", "file_path"],
            "TALKSHOW_HOST": ["web", "host"],
            "TALKSHOW_PORT": ["web", "port"],
            "TALKSHOW_HISTORY_DIR": ["parser", "history_directory"],
            "TALKSHOW_OUTPUT_DIR": ["storage", "json", "file_path"],
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(self._config, config_path, env_value)
    
    def _set_nested_value(self, config: Dict[str, Any], path: list, value: Any):
        """Set a nested value in configuration."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        config = self.load_config()
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def get_data_file_path(self) -> Path:
        """Get the data file path with proper resolution."""
        # 1. Environment variable (highest priority)
        env_path = os.getenv("TALKSHOW_DATA_FILE")
        if env_path:
            return Path(env_path)
        
        # 2. From project configuration (check paths.output_dir first)
        config = self.load_config()
        if config and "paths" in config:
            output_dir = config["paths"].get("output_dir")
            if output_dir:
                project_root = self._get_project_root()
                data_file = project_root / output_dir / "sessions.json"
                if data_file.exists():
                    return data_file
        
        # 3. From storage configuration
        config_path = self.get("storage.json.file_path")
        if config_path:
            # If relative path, resolve relative to project root
            if not Path(config_path).is_absolute():
                project_root = self._get_project_root()
                return project_root / config_path
            return Path(config_path)
        
        # 4. Default fallback
        return Path("data/sessions.json")
    
    def get_history_dir(self) -> Path:
        """Get the history directory path."""
        # 1. Environment variable
        env_path = os.getenv("TALKSHOW_HISTORY_DIR")
        if env_path:
            return Path(env_path)
        
        # 2. From configuration
        config_path = self.get("parser.history_directory")
        if config_path:
            project_root = self._get_project_root()
            return project_root / config_path
        
        # 3. Default fallback
        return Path(".specstory/history")
    
    def get_output_dir(self) -> Path:
        """Get the output directory path."""
        # 1. Environment variable
        env_path = os.getenv("TALKSHOW_OUTPUT_DIR")
        if env_path:
            return Path(env_path)
        
        # 2. From configuration
        config_path = self.get("storage.json.file_path")
        if config_path:
            # Extract directory from file path
            file_path = Path(config_path)
            if not file_path.is_absolute():
                project_root = self._get_project_root()
                return (project_root / file_path).parent
            return file_path.parent
        
        # 3. Default fallback
        return Path(".specstory/data")
    
    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        if self.project_config_path:
            # If we have a project config, its parent is the project root
            if self.project_config_path.name == "talkshow.yaml" and self.project_config_path.parent.name == ".specstory":
                return self.project_config_path.parent.parent
            return self.project_config_path.parent
        
        # Fallback: current directory
        return Path.cwd()
    
    def save_project_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to project config file."""
        if not self.project_config_path:
            return False
        
        try:
            self.project_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.project_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False
    
    def print_config_info(self):
        """Print configuration information for debugging."""
        console.print("\n[bold]Configuration Information:[/bold]")
        console.print(f"  Default config: {self.default_config_path}")
        console.print(f"  Project config: {self.project_config_path}")
        console.print(f"  User config: {self.user_config_path}")
        console.print(f"  Data file: {self.get_data_file_path()}")
        console.print(f"  History dir: {self.get_history_dir()}")
        console.print(f"  Output dir: {self.get_output_dir()}")
        
        # Environment variables
        env_vars = {k: v for k, v in os.environ.items() if k.startswith("TALKSHOW_")}
        if env_vars:
            console.print("\n[bold]Environment Variables:[/bold]")
            for k, v in env_vars.items():
                console.print(f"  {k}: {v}") 