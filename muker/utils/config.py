"""Configuration management for Muker."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Manages application configuration."""

    DEFAULT_CONFIG = {
        'volume': 0.7,
        'last_directory': '',
        'visualizer_style': 'spectrum',
        'visualizer_fps': 30,
        'theme': 'default',
        'save_last_position': True,
        'autoplay': False
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file. Defaults to data/config.json
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent.parent / 'data' / 'config.json'
        else:
            self.config_path = config_path

        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """Load configuration from file."""
        if not self.config_path.exists():
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.save()
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config: {e}. Using defaults.")

    def save(self):
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value

    def reset(self):
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
