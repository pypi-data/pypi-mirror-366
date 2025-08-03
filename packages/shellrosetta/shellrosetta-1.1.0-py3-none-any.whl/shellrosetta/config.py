# shellrosetta/config.py

import os
import json
from pathlib import Path

class Config:
    """Configuration management for ShellRosetta"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".shellrosetta"
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "show_notes": True,
            "show_warnings": True,
            "preferred_shell": "auto",  # auto, powershell, bash
            "color_output": True,
            "max_history": 100,
            "auto_complete": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                return self.default_config.copy()
        else:
            # Create config directory and file
            self.config_dir.mkdir(exist_ok=True)
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't write config
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def reset(self):
        """Reset to default configuration"""
        self.config = self.default_config.copy()
        self.save_config()

# Global config instance
config = Config() 