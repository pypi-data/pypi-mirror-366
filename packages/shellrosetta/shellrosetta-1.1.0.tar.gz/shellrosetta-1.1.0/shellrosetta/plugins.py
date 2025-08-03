# shellrosetta/plugins.py

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
import json

class CommandPlugin(ABC):
    """Base class for command translation plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the plugin name"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return the plugin version"""
        pass
    
    @abstractmethod
    def get_supported_commands(self) -> List[str]:
        """Return list of commands this plugin supports"""
        pass
    
    @abstractmethod
    def translate(self, command: str, direction: str) -> Optional[str]:
        """Translate a command in the specified direction"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata"""
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "supported_commands": self.get_supported_commands(),
            "description": getattr(self, 'description', ''),
            "author": getattr(self, 'author', ''),
        }

class PluginManager:
    """Manages loading and using command translation plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, CommandPlugin] = {}
        self.plugin_dir = Path.home() / ".shellrosetta" / "plugins"
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.load_plugins()
    
    def load_plugins(self):
        """Load all available plugins"""
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load user plugins
        self._load_user_plugins()
    
    def _load_builtin_plugins(self):
        """Load built-in plugins"""
        # Create plugin instances directly instead of importing modules
        self.plugins["docker"] = docker_plugin
        self.plugins["kubernetes"] = kubernetes_plugin
        self.plugins["aws"] = aws_plugin
        self.plugins["git"] = git_plugin
    
    def _load_user_plugins(self):
        """Load user-installed plugins"""
        for plugin_file in self.plugin_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'plugin'):
                    plugin = module.plugin
                    self.plugins[plugin.get_name()] = plugin
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")
    
    def get_plugin_for_command(self, command: str, direction: str) -> Optional[CommandPlugin]:
        """Find a plugin that can handle the given command"""
        for plugin in self.plugins.values():
            supported_commands = plugin.get_supported_commands()
            for supported_cmd in supported_commands:
                if supported_cmd in command:
                    return plugin
        return None
    
    def translate_with_plugins(self, command: str, direction: str) -> Optional[str]:
        """Try to translate using plugins first, fall back to core"""
        plugin = self.get_plugin_for_command(command, direction)
        if plugin:
            return plugin.translate(command, direction)
        return None
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [plugin.get_metadata() for plugin in self.plugins.values()]
    
    def install_plugin(self, plugin_path: str) -> bool:
        """Install a plugin from a file path"""
        try:
            plugin_file = Path(plugin_path)
            if not plugin_file.exists():
                return False
            
            # Copy to plugins directory
            target_path = self.plugin_dir / plugin_file.name
            import shutil
            shutil.copy2(plugin_file, target_path)
            
            # Reload plugins
            self._load_user_plugins()
            return True
        except Exception as e:
            print(f"Failed to install plugin: {e}")
            return False

# Example built-in plugins

class DockerPlugin(CommandPlugin):
    """Plugin for Docker command translations"""
    
    def get_name(self) -> str:
        return "docker"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_supported_commands(self) -> List[str]:
        return ["docker", "docker-compose"]
    
    def translate(self, command: str, direction: str) -> Optional[str]:
        if "docker" not in command:
            return None
        
        if direction == "lnx2ps":
            return self._docker_to_powershell(command)
        else:
            return self._powershell_to_docker(command)
    
    def _docker_to_powershell(self, command: str) -> str:
        """Translate Docker commands to PowerShell"""
        # Docker commands are generally the same across platforms
        return command
    
    def _powershell_to_docker(self, command: str) -> str:
        """Translate PowerShell Docker commands to Linux"""
        return command

class KubernetesPlugin(CommandPlugin):
    """Plugin for Kubernetes command translations"""
    
    def get_name(self) -> str:
        return "kubernetes"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_supported_commands(self) -> List[str]:
        return ["kubectl"]
    
    def translate(self, command: str, direction: str) -> Optional[str]:
        if "kubectl" not in command:
            return None
        
        # kubectl commands are generally the same across platforms
        return command

class AWSPlugin(CommandPlugin):
    """Plugin for AWS CLI command translations"""
    
    def get_name(self) -> str:
        return "aws"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_supported_commands(self) -> List[str]:
        return ["aws"]
    
    def translate(self, command: str, direction: str) -> Optional[str]:
        if "aws" not in command:
            return None
        
        # AWS CLI commands are generally the same across platforms
        return command

class GitPlugin(CommandPlugin):
    """Plugin for Git command translations"""
    
    def get_name(self) -> str:
        return "git"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_supported_commands(self) -> List[str]:
        return ["git"]
    
    def translate(self, command: str, direction: str) -> Optional[str]:
        if "git" not in command:
            return None
        
        # Git commands are generally the same across platforms
        return command

# Create plugin instances
docker_plugin = DockerPlugin()
kubernetes_plugin = KubernetesPlugin()
aws_plugin = AWSPlugin()
git_plugin = GitPlugin()

# Global plugin manager instance
plugin_manager = PluginManager() 