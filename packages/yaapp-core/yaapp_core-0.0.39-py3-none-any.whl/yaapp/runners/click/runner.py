"""
Click CLI runner for yaapp.
Provides standard CLI interface.
"""

def help():
    """Return click runner help text."""
    return """
🖱️ CLICK CLI RUNNER: Standard CLI interface (default)
  --verbose       Enable verbose output
  --quiet         Suppress output
  --interactive   Start interactive shell mode
    """

def run(app_instance, **kwargs):
    """Execute the Click runner with the app instance."""
    try:
        import click
    except ImportError:
        print("click not available. Install with: pip install click")
        return
    
    # Extract configuration
    verbose = kwargs.get('verbose', False)
    quiet = kwargs.get('quiet', False)
    interactive = kwargs.get('interactive', False)
    
    if not quiet:
        print("YApp CLI Interface")
        if verbose:
            current_commands = app_instance._get_current_context_commands()
            print(f"Available functions: {list(current_commands.keys())}")
        print("Use --help for command help")
    
    # Check if interactive mode is requested
    if interactive:
        _run_interactive(app_instance, verbose, quiet)
    else:
        if not quiet:
            print("Click CLI runner loaded successfully")


def _run_interactive(app_instance, verbose=False, quiet=False):
    """Run interactive Click shell mode."""
    import sys
    
    if not quiet:
        print("YApp Interactive Shell (Click)")
        print("Type 'help' for help, 'exit' to quit")
        print()

    while True:
        try:
            user_input = input(f"{app_instance._get_app_name()}> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            elif user_input.lower() == "help":
                _show_help(app_instance)
            elif user_input.lower() == "list":
                _list_commands(app_instance)
            else:
                _execute_command(app_instance, user_input)

        except (EOFError, KeyboardInterrupt):
            print("\\nGoodbye!")
            break


def _show_help(app_instance):
    """Show help information."""
    print("\\nAvailable Commands:")
    print("  help          - Show this help message")
    print("  list          - List available commands")
    print("  exit / quit   - Exit the interactive shell")
    print("  <command>     - Execute function")
    print()


def _list_commands(app_instance):
    """List available commands."""
    import inspect
    
    current_commands = app_instance._get_current_context_commands()
    print("\\nAvailable Functions:")
    if not current_commands:
        print("  No functions exposed")
        return
    
    for name, func in sorted(current_commands.items()):
        func_type = "function"
        if inspect.isclass(func):
            func_type = "class"
        elif hasattr(func, '__self__'):
            func_type = "method"
            
        doc = getattr(func, '__doc__', '') or 'No description'
        if doc:
            doc = doc.split('\\n')[0][:50] + ('...' if len(doc.split('\\n')[0]) > 50 else '')
        print(f"  {name:<20} | {func_type:<8} | {doc}")
    print()


def _execute_command(app_instance, command):
    """Execute a command."""
    try:
        parts = command.split()
        if not parts:
            return
        
        command_name = parts[0]
        args = parts[1:]
        
        current_commands = app_instance._get_current_context_commands()
        if command_name not in current_commands:
            print(f"Command '{command_name}' not found")
            return
        
        func = current_commands[command_name]
        
        # Use the simple interface: yaapp._call_function_with_args
        result = app_instance._call_function_with_args(func, args)
        
        if result is not None:
            print(f"Result: {result}")
        else:
            print("Command executed successfully")
            
    except Exception as e:
        print(f"Error: {str(e)}")