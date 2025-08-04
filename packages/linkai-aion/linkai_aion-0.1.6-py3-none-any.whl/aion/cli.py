import subprocess  # Import subprocess module to run shell commands

def run_command(command):
    """Run a shell command and return its output."""
    # Execute the command in the shell, capture output, and decode as text
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()  # Return the trimmed standard output of the command

def run_help():
    """Return the help message of the CLI."""
    from io import StringIO  # Import StringIO to capture print output as a string
    import sys  # Import sys to redirect stdout temporarily
    import argparse  # Import argparse for CLI argument parsing

    # Create the main argument parser with a description
    parser = argparse.ArgumentParser(description="Aion CLI")
    
    # Create subparsers for different CLI commands
    subparsers = parser.add_subparsers(dest="command")

    # Add 'chat' command parser with help description
    subparsers.add_parser("chat", help="Start Aion Chat CLI")

    # Add 'embed' command parser with help description
    subparsers.add_parser("embed", help="Embed a text/code file")

    # Add 'eval' command parser with arguments for predictions and answers files
    eval_parser = subparsers.add_parser("eval", help="Evaluate prediction accuracy")
    eval_parser.add_argument("preds", type=str, help="Predictions file")
    eval_parser.add_argument("answers", type=str, help="Answers file")

    # Add 'prompt' command parser with optional '--type' argument (system/user)
    prompt_parser = subparsers.add_parser("prompt", help="Show a prompt template")
    prompt_parser.add_argument("--type", choices=["system", "user"], default="user")

    # Add 'watch' command parser with required 'filepath' argument
    watch_parser = subparsers.add_parser("watch", help="Watch a file for changes and embed")
    watch_parser.add_argument("filepath", type=str, help="File to watch for changes")

    # Redirect stdout to a StringIO object to capture the help output
    help_io = StringIO()
    sys.stdout = help_io  # Redirect stdout to StringIO buffer
    
    parser.print_help()  # Print the help message of the parser (goes to help_io)
    
    sys.stdout = sys.__stdout__  # Restore the original stdout

    # Return the captured help message as a string
    return help_io.getvalue()