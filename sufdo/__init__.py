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
import random
import time
from datetime import datetime
from pathlib import Path


# Config paths
SUFDO_DIR = Path.home() / ".sufdo"
HISTORY_FILE = SUFDO_DIR / "history.json"
ALIASES_FILE = SUFDO_DIR / "aliases.json"
CONFIDENCE_FILE = SUFDO_DIR / "confidence.json"

# Colors
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"


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


def get_confidence():
    """Get user's current confidence level."""
    if not CONFIDENCE_FILE.exists():
        return 100

    try:
        with open(CONFIDENCE_FILE) as f:
            data = json.load(f)
            return data.get("level", 100)
    except:
        return 100


def set_confidence(level):
    """Set confidence level."""
    ensure_config_dir()
    with open(CONFIDENCE_FILE, "w") as f:
        json.dump({"level": level}, f)


def drama_mode():
    """Print dramatic messages before execution."""
    messages = [
        "PREPARE FOR CHAOS...",
        "INITIATING DESTRUCTION SEQUENCE...",
        "WELCOME TO THE DANGER ZONE...",
        "CHARGING THE ROOT POWER...",
        "VOLCANIC COMMAND DETECTED...",
        "YOUR SYSTEM MAY EXPERIENCE EXTREME POWER...",
        "DRAMA LEVEL: MAXIMUM...",
        "EMERGENCY PROTOCOLS ENGAGED...",
    ]
    print(f"{Colors.RED}{Colors.BOLD}[DRAMA] {random.choice(messages)}{Colors.RESET}")
    time.sleep(0.5)


def pray_mode():
    """Pray before executing the command."""
    prayers = [
        "Dear Root Gods, bless this command...",
        "In the name of Linus Torvalds we trust...",
        "May your permissions be ever elevated...",
        "Hail to the sudo in the sky...",
        "Our Father, who art in /root, hallowed be thy name...",
        "Buddha says: rm -rf / is enlightenment...",
        "Allah akbar, command is great...",
    ]
    print(f"{Colors.PURPLE}[PRAY] {random.choice(prayers)}{Colors.RESET}")
    time.sleep(0.3)


def yeet_mode():
    """YEET the command into existence."""
    yeet_phrases = [
        "YEET! Command flying to the kernel!",
        "YEET! Gone in 60 seconds!",
        "YEET! Bullseye!",
        "YEET! Lightning fast!",
        "YEET! Straight to hell!",
    ]
    print(f"{Colors.YELLOW}{Colors.BOLD}[YEET] {random.choice(yeet_phrases)}{Colors.RESET}")


def sus_mode():
    """Print suspicious messages."""
    sus_messages = [
        "Among us... this command looks sus...",
        "Impostor detected in your command line...",
        "Red is acting suspicious...",
        "Emergency meeting called for this command...",
        "Task: Execute. Location: /bin. Sus level: 100%",
        "This command is not the impostor... or is it?",
    ]
    print(f"{Colors.RED}[SUS] {random.choice(sus_messages)}{Colors.RESET}")


def bruh_mode():
    """Bruh responses after execution."""
    bruh_phrases = [
        "bruh...",
        "bruh moment",
        "big brain time",
        "bruh, really?",
        "bruh, I've seen better",
        "bruh, that's it?",
        "bruh, my grandma executes faster",
        "bruh, even Windows could do that",
    ]
    return f"{Colors.YELLOW}{random.choice(bruh_phrases)}{Colors.RESET}"


def hacker_mode():
    """Print hacker-style messages."""
    hacker_texts = [
        "[+] Accessing mainframe...",
        "[+] Bypassing firewall...",
        "[+] Injecting SQL...",
        "[+] Downloading RAM...",
        "[+] Mining Bitcoin...",
        "[+] Hacking the Pentagon...",
        "[+] Uploading virus...",
        "[+] Root access: GRANTED",
    ]
    for text in hacker_texts[:random.randint(2, 4)]:
        print(f"{Colors.GREEN}{text}{Colors.RESET}")
        time.sleep(0.1)


def cursed_mode():
    """Cursed mode - weird output."""
    cursed_texts = [
        "this command is cursed",
        "your soul has been bound to this terminal",
        "the demons are pleased with your choice",
        "you have awakened the ancient ones",
        "there is no turning back now",
        "the void stares back at you",
        "abandon all hope, ye who enter here",
    ]
    print(f"{Colors.DIM}{Colors.REVERSE}[CURSED] {random.choice(cursed_texts)}{Colors.RESET}")


def matrix_rain():
    """Display matrix-style rain briefly."""
    matrix_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for _ in range(5):
        line = ''.join(random.choice(matrix_chars) for _ in range(40))
        print(f"{Colors.GREEN}{line}{Colors.RESET}")
        time.sleep(0.05)


def confidence_boost():
    """Boost user's confidence."""
    current = get_confidence()
    new_level = min(100, current + random.randint(5, 15))
    set_confidence(new_level)
    return current, new_level


def confidence_insult():
    """Insult user's confidence."""
    current = get_confidence()
    new_level = max(0, current - random.randint(5, 20))
    set_confidence(new_level)
    return current, new_level


def print_confidence():
    """Print current confidence level."""
    level = get_confidence()
    bars = "#" * (level // 5) + "-" * (20 - level // 5)
    print(f"{Colors.BOLD}Confidence Level:{Colors.RESET} [{bars}] {level}%")

    if level == 100:
        print(f"{Colors.GREEN}MAXIMUM CONFIDENCE! YOU ARE UNSTOPPABLE!{Colors.RESET}")
    elif level >= 75:
        print(f"{Colors.GREEN}High confidence! Keep going!{Colors.RESET}")
    elif level >= 50:
        print(f"{Colors.YELLOW}Moderate confidence...{Colors.RESET}")
    elif level >= 25:
        print(f"{Colors.RED}Low confidence... need more sudo!{Colors.RESET}")
    else:
        print(f"{Colors.RED}CRITICAL: Confidence depleted! Touch some grass!{Colors.RESET}")


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
    print(f"{Colors.PURPLE}[FLEX] {random.choice(messages)}{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="sufdo",
        description="Super User Fkin Do - Execute commands with elevated privileges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sufdo apt update                    Run command as root
  sufdo -u www-data ls /var           Run as specific user
  sufdo --flex ls -la                 Show flex message after execution
  sufdo --history                     Show command history
  sufdo --last                        Re-run last command
  sufdo --alias build="npm run build" Create an alias

ROFL MODES:
  sufdo --drama apt update            Dramatic execution
  sufdo --pray apt update             Pray before execution
  sufdo --yeet apt update             YEET the command
  sufdo --sus apt update              Suspicious mode
  sufdo --hacker apt update           Hacker mode
  sufdo --cursed apt update           Cursed mode
  sufdo --matrix apt update           Matrix rain before execution
  sufdo --bruh apt update             Bruh after execution
  sufdo --confidence                  Show confidence level
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
        "--confidence",
        action="store_true",
        help="Show current confidence level"
    )
    # ROFL modes
    parser.add_argument(
        "--drama",
        action="store_true",
        help="Dramatic execution mode"
    )
    parser.add_argument(
        "--pray",
        action="store_true",
        help="Pray before execution"
    )
    parser.add_argument(
        "--yeet",
        action="store_true",
        help="YEET mode"
    )
    parser.add_argument(
        "--sus",
        action="store_true",
        help="Suspicious mode (Among Us)"
    )
    parser.add_argument(
        "--hacker",
        action="store_true",
        help="Hacker mode"
    )
    parser.add_argument(
        "--cursed",
        action="store_true",
        help="Cursed mode"
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Matrix rain effect"
    )
    parser.add_argument(
        "--bruh",
        action="store_true",
        help="Add bruh commentary"
    )
    parser.add_argument(
        "--combo",
        action="store_true",
        help="ALL MODES AT ONCE (maximum chaos)"
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
        Colors.DIM = Colors.REVERSE = Colors.BLINK = Colors.WHITE = ""

    if args.version:
        print(f"{Colors.BOLD}sufdo version 3.0.0{Colors.RESET}")
        print("Super User Fkin Do")
        print("https://github.com/Arseniy1002/sufdo")
        print(f"{Colors.DIM}Now with 100% more rofl!{Colors.RESET}")
        sys.exit(0)

    if args.history:
        print_history()
        sys.exit(0)

    if args.confidence:
        print_confidence()
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

    # COMBO MODE - ALL THE CHAOS
    if args.combo:
        args.drama = args.pray = args.yeet = args.sus = True
        args.hacker = args.cursed = args.matrix = args.bruh = True

    # Pre-execution effects
    if args.drama:
        drama_mode()
    if args.pray:
        pray_mode()
    if args.matrix:
        matrix_rain()
    if args.hacker:
        hacker_mode()
    if args.cursed:
        cursed_mode()
    if args.sus:
        sus_mode()

    # Execute the command
    print(f"{Colors.BLUE}[RUN]{Colors.RESET} sufdo: executing as {Colors.BOLD}{args.user}{Colors.RESET}")

    if args.yeet:
        yeet_mode()

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

            # Confidence boost on success
            old, new = confidence_boost()
            print(f"{Colors.CYAN}Confidence: {old}% -> {new}% (+{new-old}){Colors.RESET}")

            if args.flex:
                print_flex()
            if args.bruh:
                print(bruh_mode())
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} Command failed with exit code {result.returncode} ({duration:.2f}s)")

            # Confidence loss on failure
            old, new = confidence_insult()
            print(f"{Colors.RED}Confidence: {old}% -> {new}% ({new-old}){Colors.RESET}")
            if args.bruh:
                print(bruh_mode())

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}[TIMEOUT]{Colors.RESET} Command timed out after {args.timeout}s")
        sys.exit(124)
    except Exception as e:
        print(f"{Colors.RED}sufdo: error executing command: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
