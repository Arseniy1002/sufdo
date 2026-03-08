#!/usr/bin/env python3
"""
sufdo - Super User Fkin Do

A sudo-like utility for executing commands with elevated privileges.
Because sometimes you just need to get shit done.
"""

import sys
import subprocess
import argparse
import os
import json
from datetime import datetime
from pathlib import Path


# Config paths
SUFDO_DIR = Path.home() / ".sufdo"
HISTORY_FILE = SUFDO_DIR / "history.json"
ALIASES_FILE = SUFDO_DIR / "aliases.json"

# Colors
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    SUFDO_DIR.mkdir(parents=True, exist_ok=True)


def log_command(command, user, exit_code, duration):
    """Log command execution to history."""
    ensure_config_dir()
    
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except:
            history = []
    
    history.append({
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "user": user,
        "exit_code": exit_code,
        "duration": duration
    })
    
    # Keep last 100 commands
    history = history[-100:]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_last_command():
    """Get the last executed command from history."""
    if not HISTORY_FILE.exists():
        return None
    
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
            if history:
                return history[-1]["command"]
    except:
        pass
    return None


def load_aliases():
    """Load user aliases."""
    if not ALIASES_FILE.exists():
        return {}
    
    try:
        with open(ALIASES_FILE) as f:
            return json.load(f)
    except:
        return {}


def save_aliases(aliases):
    """Save aliases to file."""
    ensure_config_dir()
    with open(ALIASES_FILE, "w") as f:
        json.dump(aliases, f, indent=2)


def expand_alias(command, aliases):
    """Expand alias to actual command."""
    if command and command[0] in aliases:
        return aliases[command[0]] + " " + " ".join(command[1:])
    return command


def print_history():
    """Print command history."""
    if not HISTORY_FILE.exists():
        print(f"{Colors.YELLOW}No history yet. Go break something!{Colors.RESET}")
        return
    
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        
        if not history:
            print(f"{Colors.YELLOW}No history yet. Go break something!{Colors.RESET}")
            return
        
        print(f"{Colors.BOLD}Command History:{Colors.RESET}\n")
        for i, entry in enumerate(history[-10:], 1):
            status = "[OK]" if entry["exit_code"] == 0 else "[FAIL]"
            print(f"  {i}. {status} {entry['command']}")
            print(f"     {Colors.CYAN}{entry['timestamp']}{Colors.RESET} | user: {entry['user']} | exit: {entry['exit_code']} | {entry['duration']:.2f}s")
    except Exception as e:
        print(f"{Colors.RED}Error reading history: {e}{Colors.RESET}")


def print_flex():
    """Print flex message."""
    messages = [
        "Command executed with extreme prejudice!",
        "You're the root of all problems!",
        "Super User Fkin Do - because permissions are for mortals!",
        "Another day, another sudo command!",
        "Your command has been blessed by the root gods!",
        "Target acquired and executed!",
        "Bow down to the super user!",
    ]
    import random
    print(f"{Colors.PURPLE}{random.choice(messages)}{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="sufdo",
        description="Super User Fkin Do - Execute commands with elevated privileges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sufdo apt update              Run command as root
  sufdo -u www-data ls /var     Run as specific user
  sufdo --flex ls -la           Show flex message after execution
  sufdo --history               Show command history
  sufdo --last                  Re-run last command
  sufdo --alias build="npm run build"   Create an alias
        """
    )
    parser.add_argument(
        "-u", "--user",
        default="root",
        help="Run command as specified user (default: root)"
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show command history"
    )
    parser.add_argument(
        "--last", "-!",
        action="store_true",
        help="Re-run the last executed command"
    )
    parser.add_argument(
        "--flex",
        action="store_true",
        help="Show a flex message after successful execution"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=None,
        help="Timeout in seconds for command execution"
    )
    parser.add_argument(
        "--alias",
        nargs="*",
        metavar="NAME=CMD",
        help="Create or list aliases"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute"
    )

    args = parser.parse_args()

    # Handle --no-color
    if args.no_color:
        Colors.RED = Colors.GREEN = Colors.YELLOW = Colors.BLUE = ""
        Colors.PURPLE = Colors.CYAN = Colors.RESET = Colors.BOLD = ""

    if args.version:
        print(f"{Colors.BOLD}sufdo version 2.0.0{Colors.RESET}")
        print("Super User Fkin Do")
        print("https://github.com/Arseniy1002/sufdo")
        sys.exit(0)

    if args.history:
        print_history()
        sys.exit(0)

    # Handle aliases
    if args.alias is not None:
        aliases = load_aliases()
        if not args.alias:
            # List all aliases
            if aliases:
                print(f"{Colors.BOLD}Aliases:{Colors.RESET}")
                for name, cmd in aliases.items():
                    print(f"  {Colors.GREEN}{name}{Colors.RESET} = {Colors.CYAN}{cmd}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No aliases defined.{Colors.RESET}")
        else:
            # Create new alias
            for alias_def in args.alias:
                if "=" in alias_def:
                    name, cmd = alias_def.split("=", 1)
                    aliases[name] = cmd
                    print(f"{Colors.GREEN}[OK]{Colors.RESET} Alias '{name}' created")
            save_aliases(aliases)
        sys.exit(0)

    # Handle --last
    if args.last:
        last_cmd = get_last_command()
        if last_cmd:
            print(f"{Colors.YELLOW}[RETRY] Re-running: {last_cmd}{Colors.RESET}")
            args.command = last_cmd.split()
        else:
            print(f"{Colors.RED}No previous command in history.{Colors.RESET}")
            sys.exit(1)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Expand aliases
    aliases = load_aliases()
    cmd_str = " ".join(args.command) if isinstance(args.command, list) else args.command
    
    # Check for alias
    if args.command and args.command[0] in aliases:
        expanded = aliases[args.command[0]] + " " + " ".join(args.command[1:])
        print(f"{Colors.YELLOW}[ALIAS] {args.command[0]} -> {expanded}{Colors.RESET}")
        cmd_str = expanded

    # Execute the command
    print(f"{Colors.BLUE}[RUN]{Colors.RESET} sufdo: executing as {Colors.BOLD}{args.user}{Colors.RESET}")
    
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            cmd_str,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=args.timeout
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        
        # Log to history
        log_command(cmd_str, args.user, result.returncode, duration)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}[OK]{Colors.RESET} Command completed successfully ({duration:.2f}s)")
            if args.flex:
                print_flex()
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} Command failed with exit code {result.returncode} ({duration:.2f}s)")
        
        sys.exit(result.returncode)
        
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}[TIMEOUT]{Colors.RESET} Command timed out after {args.timeout}s")
        sys.exit(124)
    except Exception as e:
        print(f"{Colors.RED}sufdo: error executing command: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
