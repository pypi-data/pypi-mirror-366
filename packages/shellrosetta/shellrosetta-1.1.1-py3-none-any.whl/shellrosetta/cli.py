# shellrosetta/cli.py

import sys
try:
    import readline
except ImportError:
    # readline not available on Windows
    pass
from .core import lnx2ps, ps2lnx
from .utils import print_header, print_translation, print_warning, print_note, sanitize_command, format_command_history
from .config import config
from .ml_engine import ml_engine
from .plugins import plugin_manager
from .api import run_api_server

def show_help():
    print_header()
    print("Usage:")
    print("  shellrosetta lnx2ps \"linux command here\"")
    print("  shellrosetta ps2lnx \"powershell command here\"")
    print("  shellrosetta          # Interactive shell mode")
    print("  shellrosetta config   # Show configuration")
    print("  shellrosetta history  # Show command history")
    print("  shellrosetta api      # Start web API server")
    print("  shellrosetta plugins  # List available plugins")
    print("  shellrosetta ml       # Show ML insights")
    print("")
    print("Examples:")
    print("  shellrosetta lnx2ps \"ls -alh | grep foo\"")
    print("  shellrosetta ps2lnx \"Get-ChildItem -Force | Select-String foo\"")
    print("  shellrosetta api --port 8080  # Start API on port 8080")
    print("=" * 65)

def run_interactive():
    print_header()
    print("Welcome to ShellRosetta Interactive Mode!")
    print("Type 'exit' to quit, 'mode' to switch translation direction, or 'help' for commands.")
    
    # Initialize history
    history = []
    mode = ""
    
    # Ask user for translation direction
    while mode not in ("lnx2ps", "ps2lnx"):
        mode = input("Mode [lnx2ps/ps2lnx] (or 'exit'): ").strip().lower()
        if mode == "exit":
            print("Goodbye!")
            return
        if mode == "help":
            show_interactive_help()
            continue
    
    print(f"Type your {mode.upper()} commands below. Type 'mode' to switch, 'exit' to quit.\n")
    
    while True:
        try:
            inp = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if inp.lower() == "exit":
            print("Goodbye!")
            break
        elif inp.lower() == "help":
            show_interactive_help()
            continue
        elif inp.lower() == "history":
            print(format_command_history(history))
            continue
        elif inp.lower() == "config":
            show_config()
            continue
        elif inp.lower() == "plugins":
            show_plugins()
            continue
        elif inp.lower() == "ml":
            show_ml_insights()
            continue
        elif inp.lower() == "mode":
            # Allow switching translation direction anytime
            while True:
                mode = input("Mode [lnx2ps/ps2lnx] (or 'exit'): ").strip().lower()
                if mode == "exit":
                    print("Goodbye!")
                    return
                if mode in ("lnx2ps", "ps2lnx"):
                    print(f"Switched to {mode.upper()} mode.\n")
                    break
            continue
        
        if not inp:
            continue
        
        # Sanitize command
        sanitized = sanitize_command(inp)
        if sanitized is None:
            continue
        
        # Translate command
        if mode == "lnx2ps":
            translated = lnx2ps(sanitized)
        else:
            translated = ps2lnx(sanitized)
        
        # Store in history
        history.append((sanitized, translated, mode))
        if len(history) > config.get('max_history', 100):
            history.pop(0)
        
        # Print translation
        print_translation(sanitized, translated, mode)

def show_interactive_help():
    """Show help for interactive mode"""
    print("\nInteractive Mode Commands:")
    print("  <command>     - Translate the command")
    print("  mode          - Switch translation direction")
    print("  history       - Show recent command history")
    print("  config        - Show current configuration")
    print("  plugins       - List available plugins")
    print("  ml            - Show ML insights")
    print("  help          - Show this help")
    print("  exit          - Exit interactive mode")
    print()

def show_config():
    """Show current configuration"""
    print("\nCurrent Configuration:")
    for key, value in config.config.items():
        print(f"  {key}: {value}")
    print()

def show_plugins():
    """Show available plugins"""
    print("\nAvailable Plugins:")
    plugins = plugin_manager.list_plugins()
    if plugins:
        for plugin in plugins:
            print(f"  {plugin['name']} v{plugin['version']}")
            print(f"    Commands: {', '.join(plugin['supported_commands'])}")
            if plugin.get('description'):
                print(f"    Description: {plugin['description']}")
            print()
    else:
        print("  No plugins available")
    print()

def show_ml_insights():
    """Show machine learning insights"""
    print("\nMachine Learning Insights:")
    analysis = ml_engine.analyze_patterns()
    
    if analysis:
        print(f"  Total Patterns: {analysis.get('total_patterns', 0)}")
        print(f"  Success Rate: {analysis.get('success_rate', 0):.1%}")
        print(f"  Command Types: {dict(analysis.get('command_types', {}))}")
        
        top_patterns = analysis.get('top_successful_patterns', [])
        if top_patterns:
            print("\n  Top Successful Patterns:")
            for cmd, rate in top_patterns[:5]:
                print(f"    {cmd}: {rate:.1%}")
    else:
        print("  No patterns learned yet")
    print()

def main():
    # If no args, drop into interactive mode
    if len(sys.argv) == 1:
        run_interactive()
        return
    
    # Handle special commands
    if len(sys.argv) == 2:
        if sys.argv[1] in ('-h', '--help', 'help'):
            show_help()
            sys.exit(0)
        elif sys.argv[1] == 'config':
            show_config()
            sys.exit(0)
        elif sys.argv[1] == 'history':
            print("History feature not yet implemented for non-interactive mode.")
            sys.exit(0)
        elif sys.argv[1] == 'plugins':
            show_plugins()
            sys.exit(0)
        elif sys.argv[1] == 'ml':
            show_ml_insights()
            sys.exit(0)
        elif sys.argv[1] == 'api':
            run_api_server()
            return
    
    if len(sys.argv) < 3:
        show_help()
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    if mode not in ['lnx2ps', 'ps2lnx']:
        print("Unknown mode:", mode)
        show_help()
        sys.exit(1)
    
    command = sys.argv[2]
    sanitized = sanitize_command(command)
    if sanitized is None:
        sys.exit(1)
    
    print_header()
    print(f"Original command: {command}\n")
    
    if mode == "lnx2ps":
        translated = lnx2ps(sanitized)
        print_translation(command, translated, mode)
    else:
        translated = ps2lnx(sanitized)
        print_translation(command, translated, mode)

# Allow both python -m and entry point execution
if __name__ == "__main__" or __name__ == "shellrosetta.cli":
    main()
