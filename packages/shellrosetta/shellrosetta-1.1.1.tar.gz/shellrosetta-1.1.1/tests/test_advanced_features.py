# tests/test_advanced_features.py

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from shellrosetta.parser import CommandParser, ASTNode, NodeType
from shellrosetta.plugins import CommandPlugin, PluginManager
from shellrosetta.ml_engine import MLEngine, CommandPattern
from shellrosetta.core import lnx2ps, ps2lnx


class TestCommandParser(unittest.TestCase):
    """Test the advanced command parser"""
    
    def setUp(self):
        self.parser = CommandParser()
    
    def test_parse_simple_command(self):
        """Test parsing a simple command"""
        ast = self.parser.parse("ls -la")
        
        self.assertEqual(ast.node_type, NodeType.COMMAND)
        self.assertEqual(ast.value, "ls")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].node_type, NodeType.FLAG)
        self.assertEqual(ast.children[0].value, "-la")
    
    def test_parse_piped_commands(self):
        """Test parsing piped commands"""
        ast = self.parser.parse("ls -la | grep error")
        
        self.assertEqual(ast.node_type, NodeType.PIPE)
        self.assertEqual(len(ast.children), 2)
        
        # First command
        self.assertEqual(ast.children[0].node_type, NodeType.COMMAND)
        self.assertEqual(ast.children[0].value, "ls")
        
        # Second command
        self.assertEqual(ast.children[1].node_type, NodeType.COMMAND)
        self.assertEqual(ast.children[1].value, "grep")
    
    def test_extract_flags(self):
        """Test flag extraction"""
        ast = self.parser.parse("ls -la -R")
        flags = self.parser.extract_flags(ast)
        
        self.assertIn("-la", flags)
        self.assertIn("-R", flags)
    
    def test_extract_arguments(self):
        """Test argument extraction"""
        ast = self.parser.parse("cp file1.txt file2.txt")
        args = self.parser.extract_arguments(ast)
        
        self.assertIn("file1.txt", args)
        self.assertIn("file2.txt", args)
    
    def test_get_command_name(self):
        """Test command name extraction"""
        ast = self.parser.parse("ls -la")
        cmd_name = self.parser.get_command_name(ast)
        
        self.assertEqual(cmd_name, "ls")
    
    def test_empty_command(self):
        """Test parsing empty command"""
        ast = self.parser.parse("")
        self.assertEqual(ast.node_type, NodeType.COMMAND)
        self.assertEqual(ast.value, "")


class TestPluginSystem(unittest.TestCase):
    """Test the plugin system"""
    
    def setUp(self):
        self.plugin_manager = PluginManager()
    
    def test_plugin_creation(self):
        """Test creating a custom plugin"""
        class TestPlugin(CommandPlugin):
            def get_name(self):
                return "test"
            
            def get_version(self):
                return "1.0.0"
            
            def get_supported_commands(self):
                return ["test_cmd"]
            
            def translate(self, command, direction):
                if "test_cmd" in command:
                    return "translated_command"
                return None
        
        plugin = TestPlugin()
        
        self.assertEqual(plugin.get_name(), "test")
        self.assertEqual(plugin.get_version(), "1.0.0")
        self.assertEqual(plugin.get_supported_commands(), ["test_cmd"])
        
        result = plugin.translate("test_cmd arg1", "lnx2ps")
        self.assertEqual(result, "translated_command")
    
    def test_plugin_manager_list_plugins(self):
        """Test listing plugins"""
        plugins = self.plugin_manager.list_plugins()
        
        # Should have at least the built-in plugins
        self.assertIsInstance(plugins, list)
        self.assertGreater(len(plugins), 0)
    
    def test_plugin_translation(self):
        """Test plugin-based translation"""
        # Test with a command that should be handled by a plugin
        result = self.plugin_manager.translate_with_plugins("docker ps", "lnx2ps")
        
        # Should return the same command (Docker commands are cross-platform)
        # Note: This might return None if no plugin handles it exactly
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result, "docker ps")


class TestMLEngine(unittest.TestCase):
    """Test the machine learning engine"""
    
    def setUp(self):
        # Use a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.ml_engine = MLEngine()
        self.ml_engine.data_dir = Path(self.temp_dir)
        self.ml_engine.patterns_file = self.ml_engine.data_dir / "patterns.json"
        self.ml_engine.context_file = self.ml_engine.data_dir / "context.json"
        self.ml_engine.suggestions_file = self.ml_engine.data_dir / "suggestions.json"
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_learn_pattern(self):
        """Test learning a new pattern"""
        # Clear existing patterns for this test
        self.ml_engine.patterns.clear()
        
        self.ml_engine.learn_pattern("ls -la", "Get-ChildItem -Force | Format-List", "lnx2ps", success=True)
        
        # Check if pattern was learned
        key = "lnx2ps:ls -la"
        self.assertIn(key, self.ml_engine.patterns)
        
        pattern = self.ml_engine.patterns[key]
        self.assertEqual(pattern.command, "ls -la")
        self.assertEqual(pattern.translation, "Get-ChildItem -Force | Format-List")
        self.assertEqual(pattern.success_count, 1)
        self.assertEqual(pattern.failure_count, 0)
    
    def test_get_best_translation(self):
        """Test getting the best learned translation"""
        # Learn a pattern
        self.ml_engine.learn_pattern("ls -la", "Get-ChildItem -Force | Format-List", "lnx2ps", success=True)
        
        # Get the translation
        result = self.ml_engine.get_best_translation("ls -la", "lnx2ps")
        self.assertEqual(result, "Get-ChildItem -Force | Format-List")
    
    def test_get_suggestions(self):
        """Test getting suggestions for partial commands"""
        # Learn some patterns
        self.ml_engine.learn_pattern("ls -la", "Get-ChildItem -Force | Format-List", "lnx2ps", success=True)
        self.ml_engine.learn_pattern("ls -lh", "Get-ChildItem | Format-List", "lnx2ps", success=True)
        
        # Get suggestions
        suggestions = self.ml_engine.get_suggestions("ls -l", "lnx2ps", limit=5)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
    
    def test_analyze_patterns(self):
        """Test pattern analysis"""
        # Clear existing patterns for this test
        self.ml_engine.patterns.clear()
        
        # Learn some patterns
        self.ml_engine.learn_pattern("ls -la", "Get-ChildItem -Force | Format-List", "lnx2ps", success=True)
        self.ml_engine.learn_pattern("ls -lh", "Get-ChildItem | Format-List", "lnx2ps", success=True)
        
        # Analyze patterns
        analysis = self.ml_engine.analyze_patterns()
        
        self.assertIn('total_patterns', analysis)
        self.assertIn('success_rate', analysis)
        self.assertIn('command_types', analysis)
        
        self.assertEqual(analysis['total_patterns'], 2)
        self.assertEqual(analysis['success_rate'], 1.0)
    
    def test_command_classification(self):
        """Test command type classification"""
        self.assertEqual(self.ml_engine._classify_command("ls -la"), "file_listing")
        self.assertEqual(self.ml_engine._classify_command("grep error"), "search")
        self.assertEqual(self.ml_engine._classify_command("cp file1 file2"), "file_operation")
        self.assertEqual(self.ml_engine._classify_command("docker ps"), "container")
        self.assertEqual(self.ml_engine._classify_command("git commit"), "version_control")
        self.assertEqual(self.ml_engine._classify_command("unknown command"), "general")


class TestEnhancedCore(unittest.TestCase):
    """Test the enhanced core functions with ML and plugins"""
    
    def test_lnx2ps_with_ml(self):
        """Test Linux to PowerShell translation with ML enabled"""
        # This should work with the enhanced core
        result = lnx2ps("ls -la", use_ml=True, use_plugins=True)
        self.assertIn("Get-ChildItem", result)
    
    def test_ps2lnx_with_ml(self):
        """Test PowerShell to Linux translation with ML enabled"""
        # This should work with the enhanced core
        result = ps2lnx("Get-ChildItem -Force", use_ml=True, use_plugins=True)
        self.assertIn("ls", result)
    
    def test_lnx2ps_without_ml(self):
        """Test Linux to PowerShell translation with ML disabled"""
        result = lnx2ps("ls -la", use_ml=False, use_plugins=False)
        self.assertIn("Get-ChildItem", result)
    
    def test_ps2lnx_without_ml(self):
        """Test PowerShell to Linux translation with ML disabled"""
        result = ps2lnx("Get-ChildItem -Force", use_ml=False, use_plugins=False)
        self.assertIn("ls", result)


class TestCommandPattern(unittest.TestCase):
    """Test the CommandPattern class"""
    
    def test_pattern_creation(self):
        """Test creating a command pattern"""
        pattern = CommandPattern("ls -la", "Get-ChildItem -Force | Format-List", "lnx2ps")
        
        self.assertEqual(pattern.command, "ls -la")
        self.assertEqual(pattern.translation, "Get-ChildItem -Force | Format-List")
        self.assertEqual(pattern.direction, "lnx2ps")
        self.assertEqual(pattern.success_count, 0)
        self.assertEqual(pattern.failure_count, 0)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        pattern = CommandPattern("test", "translation", "lnx2ps")
        
        # Initially 0
        self.assertEqual(pattern.get_success_rate(), 0.0)
        
        # After success
        pattern.record_success()
        self.assertEqual(pattern.get_success_rate(), 1.0)
        
        # After failure
        pattern.record_failure()
        self.assertEqual(pattern.get_success_rate(), 0.5)
    
    def test_pattern_serialization(self):
        """Test pattern serialization and deserialization"""
        pattern = CommandPattern("ls -la", "Get-ChildItem -Force | Format-List", "lnx2ps")
        pattern.record_success()
        pattern.record_failure()
        
        # Serialize
        data = pattern.to_dict()
        
        # Deserialize
        new_pattern = CommandPattern.from_dict(data)
        
        self.assertEqual(new_pattern.command, pattern.command)
        self.assertEqual(new_pattern.translation, pattern.translation)
        self.assertEqual(new_pattern.direction, pattern.direction)
        self.assertEqual(new_pattern.success_count, pattern.success_count)
        self.assertEqual(new_pattern.failure_count, pattern.failure_count)


if __name__ == '__main__':
    unittest.main() 