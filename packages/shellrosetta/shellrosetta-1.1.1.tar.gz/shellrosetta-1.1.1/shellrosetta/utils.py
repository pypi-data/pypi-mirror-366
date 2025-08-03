# shellrosetta/utils.py

import os
import sys
from .config import config

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colored(text, color):
    """Return colored text if color output is enabled"""
    if config.get('color_output', True) and sys.stdout.isatty():
        return f"{color}{text}{Colors.ENDC}"
    return text

def print_header():
    """Print the ShellRosetta header with optional colors"""
    header = "=" * 65
    title = "ShellRosetta: Linux ↔ PowerShell CLI Command Translator"
    author = "Author: David Donohue"
    repo = "Repo: github.com/sdirishguy/shellrosetta"
    
    print(colored(header, Colors.HEADER))
    print(colored(title, Colors.BOLD))
    print(colored(author, Colors.OKBLUE))
    print(colored(repo, Colors.OKBLUE))
    print(colored(header, Colors.HEADER))

def print_translation(original, translated, direction):
    """Print translation with formatting"""
    print(f"\n{colored('--- Translation ---', Colors.OKCYAN)}")
    
    if direction == "lnx2ps":
        print(f"{colored('PowerShell Equivalent:', Colors.OKGREEN)}")
    else:
        print(f"{colored('Linux Equivalent:', Colors.OKGREEN)}")
    
    print(f"  {colored(translated, Colors.BOLD)}")
    print(f"{colored('-------------------', Colors.OKCYAN)}\n")

def print_warning(message):
    """Print a warning message"""
    if config.get('show_warnings', True):
        print(f"{colored('⚠️  Warning:', Colors.WARNING)} {message}")

def print_note(message):
    """Print a note message"""
    if config.get('show_notes', True):
        print(f"{colored('📝 Note:', Colors.OKBLUE)} {message}")

def detect_shell():
    """Detect the current shell environment"""
    shell = os.environ.get('SHELL', '').lower()
    if 'powershell' in shell or 'pwsh' in shell:
        return 'powershell'
    elif 'bash' in shell or 'zsh' in shell or 'sh' in shell:
        return 'bash'
    else:
        return 'unknown'

def sanitize_command(command):
    """Sanitize command input for safe processing"""
    # Remove any potentially dangerous characters
    dangerous_chars = [';', '&&', '||', '`', '$(']
    for char in dangerous_chars:
        if char in command:
            print_warning(f"Command contains potentially dangerous character: {char}")
            return None
    return command.strip()

def format_command_history(history):
    """Format command history for display"""
    if not history:
        return "No commands in history"
    
    formatted = []
    for i, (cmd, translation, direction) in enumerate(history[-10:], 1):
        formatted.append(f"{i:2d}. {direction.upper()}: {cmd}")
        formatted.append(f"    → {translation}")
    
    return "\n".join(formatted) 