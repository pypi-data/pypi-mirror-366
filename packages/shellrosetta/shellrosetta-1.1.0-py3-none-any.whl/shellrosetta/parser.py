# shellrosetta/parser.py

import re
import shlex
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    COMMAND = "command"
    ARGUMENT = "argument"
    FLAG = "flag"
    PIPE = "pipe"
    REDIRECT = "redirect"
    SUBSTITUTION = "substitution"
    CONDITIONAL = "conditional"

@dataclass
class ASTNode:
    """Abstract Syntax Tree node for command parsing"""
    node_type: NodeType
    value: str
    children: List['ASTNode'] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

class CommandParser:
    """Advanced command parser with AST generation"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\$(\w+)')
        self.substitution_pattern = re.compile(r'\$\(([^)]+)\)')
        self.redirect_pattern = re.compile(r'([><])([^|&]*?)(?:\||$)')
        self.conditional_pattern = re.compile(r'([&|]{2})')
    
    def parse(self, command: str) -> ASTNode:
        """Parse a command string into an AST"""
        if not command.strip():
            return ASTNode(NodeType.COMMAND, "", [])
        
        # Split by pipes first
        pipe_parts = command.split('|')
        if len(pipe_parts) == 1:
            return self._parse_single_command(command.strip())
        
        # Handle piped commands
        root = ASTNode(NodeType.PIPE, "|", [])
        for part in pipe_parts:
            if part.strip():
                root.children.append(self._parse_single_command(part.strip()))
        
        return root
    
    def _parse_single_command(self, command: str) -> ASTNode:
        """Parse a single command (no pipes)"""
        # Handle variable substitutions
        command = self._expand_variables(command)
        
        # Parse with shlex for proper tokenization
        try:
            tokens = shlex.split(command)
        except ValueError:
            # Fallback for malformed commands
            tokens = command.split()
        
        if not tokens:
            return ASTNode(NodeType.COMMAND, "", [])
        
        cmd_node = ASTNode(NodeType.COMMAND, tokens[0], [])
        
        # Parse arguments and flags
        for token in tokens[1:]:
            if token.startswith('-'):
                flag_node = ASTNode(NodeType.FLAG, token, [])
                cmd_node.children.append(flag_node)
            elif token in ['>', '>>', '<', '2>', '&>']:
                redirect_node = ASTNode(NodeType.REDIRECT, token, [])
                cmd_node.children.append(redirect_node)
            else:
                arg_node = ASTNode(NodeType.ARGUMENT, token, [])
                cmd_node.children.append(arg_node)
        
        return cmd_node
    
    def _expand_variables(self, command: str) -> str:
        """Expand environment variables in command"""
        def replace_var(match):
            var_name = match.group(1)
            # In a real implementation, you'd get the actual env var
            return f"${{{var_name}}}"
        
        command = self.variable_pattern.sub(replace_var, command)
        return command
    
    def extract_flags(self, node: ASTNode) -> List[str]:
        """Extract all flags from an AST node"""
        flags = []
        for child in node.children:
            if child.node_type == NodeType.FLAG:
                flags.append(child.value)
            elif child.node_type == NodeType.COMMAND:
                flags.extend(self.extract_flags(child))
        return flags
    
    def extract_arguments(self, node: ASTNode) -> List[str]:
        """Extract all arguments from an AST node"""
        args = []
        for child in node.children:
            if child.node_type == NodeType.ARGUMENT:
                args.append(child.value)
            elif child.node_type == NodeType.COMMAND:
                args.extend(self.extract_arguments(child))
        return args
    
    def get_command_name(self, node: ASTNode) -> str:
        """Get the command name from an AST node"""
        if node.node_type == NodeType.COMMAND:
            return node.value
        for child in node.children:
            if child.node_type == NodeType.COMMAND:
                return child.value
        return ""
    
    def has_redirects(self, node: ASTNode) -> bool:
        """Check if command has any redirects"""
        for child in node.children:
            if child.node_type == NodeType.REDIRECT:
                return True
        return False
    
    def get_redirects(self, node: ASTNode) -> List[Tuple[str, str]]:
        """Get all redirects from an AST node"""
        redirects = []
        for child in node.children:
            if child.node_type == NodeType.REDIRECT:
                redirects.append((child.value, ""))
        return redirects

# Global parser instance
parser = CommandParser() 