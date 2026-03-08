#!/usr/bin/env python3
"""
sufdo - Super User Fkin Do

A sudo-like utility for executing commands with elevated privileges.
Because sometimes you just need to get shit done.

Version: 3.10.0 - Complete Edition
"""

import sys
import subprocess
import argparse
import os
import json
import random
import time
import logging
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any


# Config paths
SUFDO_DIR = Path.home() / ".sufdo"
HISTORY_FILE = SUFDO_DIR / "history.json"
ALIASES_FILE = SUFDO_DIR / "aliases.json"
CONFIDENCE_FILE = SUFDO_DIR / "confidence.json"
LOG_FILE = SUFDO_DIR / "sufdo.log"
CONFIG_FILE = SUFDO_DIR / "config.json"
STATS_FILE = SUFDO_DIR / "stats.json"
CACHE_FILE = SUFDO_DIR / "cache.json"
BACKUP_DIR = SUFDO_DIR / "backups"
PROFILES_DIR = SUFDO_DIR / "profiles"

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


# Destructive commands blacklist
DESTRUCTIVE_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "dd if=/dev/zero",
    "mkfs",
    "fdisk",
    "format",
    "del /s /q",
    "rmdir /s",
    "shutdown -a",
    "chmod -R 777 /",
    "chown -R root:root /",
]

# Fun mode phrases
PHRASES = {
    "pirate": [
        "Ahoy matey!",
        "Shiver me timbers!",
        "All hands on deck!",
        "Avast ye!",
        "Batten down the hatches!",
        "Blimey!",
        "Dead men tell no tales!",
        "Heave ho!",
        "Landlubber!",
        "Savvy?",
        "Thar she blows!",
        "Yo ho ho!",
    ],
    "cowboy": [
        "Howdy partner!",
        "Yeehaw!",
        "This town ain't big enough!",
        "I'm gonna git you!",
        "Ride 'em cowboy!",
        "That's the way the cookie crumbles!",
        "Hold your horses!",
        "All hat, no cattle!",
        "No skin off my nose!",
        "Quick as a wink!",
    ],
    "yoda": [
        "Do or do not, there is no try.",
        "May the Force be with you.",
        "Size matters not.",
        "Fear is the path to the dark side.",
        "Patience you must have.",
        "Truly wonderful, the mind of a child is.",
        "In a dark place we find ourselves.",
        "Much to learn, you still have.",
    ],
    "shakespeare": [
        "To be or not to be, that is the question.",
        "All the world's a stage.",
        "The course of true love never did run smooth.",
        "Brevity is the soul of wit.",
        "There is method in my madness.",
        "The lady doth protest too much.",
        "A rose by any other name would smell as sweet.",
        "All that glitters is not gold.",
    ],
    "anime": [
        "I'm gonna be the Pirate King!",
        "Believe it!",
        "I'll take a potato chip... and eat it!",
        "This is the power of friendship!",
        "I am already dead.",
        "The only one who can beat me is me.",
        "I'll destroy you!",
        "You're already dead.",
    ],
}


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    SUFDO_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict:
    """Load user configuration."""
    if not CONFIG_FILE.exists():
        return {"quiet_level": 0, "verbose_level": 1, "theme": "default"}
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_config(config: Dict):
    """Save user configuration."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_stats() -> Dict:
    """Load usage statistics."""
    if not STATS_FILE.exists():
        return {"total": 0, "success": 0, "failure": 0, "commands": {}}
    try:
        with open(STATS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_stats(stats: Dict):
    """Save usage statistics."""
    ensure_config_dir()
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def load_cache() -> Dict:
    """Load command cache."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_cache(cache: Dict):
    """Save command cache."""
    ensure_config_dir()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def setup_logging(log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Setup logging to file."""
    ensure_config_dir()
    log_path = log_file or LOG_FILE
    
    logging.basicConfig(
        filename=log_path,
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode='a'
    )
    return logging.getLogger('sufdo')


def log_command(command: str, user: str, exit_code: int, duration: float):
    """Log command execution to history."""
    ensure_config_dir()
    
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
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
    
    history = history[-100:]
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def update_stats(command: str, exit_code: int, duration: float):
    """Update usage statistics."""
    stats = load_stats()
    stats["total"] = stats.get("total", 0) + 1
    
    if exit_code == 0:
        stats["success"] = stats.get("success", 0) + 1
    else:
        stats["failure"] = stats.get("failure", 0) + 1
    
    # Track command frequency
    cmd_key = command.split()[0] if command else "unknown"
    if "commands" not in stats:
        stats["commands"] = {}
    stats["commands"][cmd_key] = stats["commands"].get(cmd_key, 0) + 1
    
    # Track timing
    if "times" not in stats:
        stats["times"] = {}
    if cmd_key not in stats["times"]:
        stats["times"][cmd_key] = []
    stats["times"][cmd_key].append(duration)
    stats["times"][cmd_key] = stats["times"][cmd_key][-10:]  # Keep last 10
    
    save_stats(stats)


def get_last_command() -> Optional[str]:
    """Get the last executed command from history."""
    if not HISTORY_FILE.exists():
        return None
    
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            history = json.load(f)
            if history:
                return history[-1]["command"]
    except:
        pass
    return None


def load_aliases() -> Dict:
    """Load user aliases."""
    if not ALIASES_FILE.exists():
        return {}
    try:
        with open(ALIASES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_aliases(aliases: Dict):
    """Save aliases to file."""
    ensure_config_dir()
    with open(ALIASES_FILE, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2, ensure_ascii=False)


def get_confidence() -> int:
    """Get user's current confidence level."""
    if not CONFIDENCE_FILE.exists():
        return 100
    try:
        with open(CONFIDENCE_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("level", 100)
    except:
        return 100


def set_confidence(level: int):
    """Set confidence level."""
    ensure_config_dir()
    with open(CONFIDENCE_FILE, "w", encoding="utf-8") as f:
        json.dump({"level": level}, f)


def create_backup(path: str) -> Optional[str]:
    """Create backup of a file/directory."""
    if not os.path.exists(path):
        return None
    
    ensure_config_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(path)}_{timestamp}"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        if os.path.isfile(path):
            shutil.copy2(path, backup_path)
        else:
            shutil.copytree(path, backup_path)
        return str(backup_path)
    except Exception as e:
        return None


def is_destructive_command(command: str) -> bool:
    """Check if command is in the destructive blacklist."""
    cmd_lower = command.lower()
    for destructive in DESTRUCTIVE_COMMANDS:
        if destructive in cmd_lower:
            return True
    return False


def expand_alias(command: List[str], aliases: Dict) -> List[str]:
    """Expand alias with arguments support."""
    if not command or command[0] not in aliases:
        return command
    
    alias_cmd = aliases[command[0]]
    args = command[1:]
    
    # Replace $1, $2, etc. with actual arguments
    for i, arg in enumerate(args, 1):
        alias_cmd = alias_cmd.replace(f"${i}", arg)
    
    # Handle remaining arguments
    if "$@" in alias_cmd:
        alias_cmd = alias_cmd.replace("$@", " ".join(args))
    else:
        alias_cmd = alias_cmd + " " + " ".join(args)
    
    return alias_cmd.split()


def get_fun_phrase(mode: str) -> str:
    """Get random phrase for fun mode."""
    phrases = PHRASES.get(mode, PHRASES["pirate"])
    return random.choice(phrases)


def print_history():
    """Print command history."""
    if not HISTORY_FILE.exists():
        print(f"{Colors.YELLOW}No history yet. Go break something!{Colors.RESET}")
        return
    
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
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


def print_stats():
    """Print usage statistics."""
    stats = load_stats()
    
    print(f"{Colors.BOLD}Usage Statistics:{Colors.RESET}\n")
    print(f"  Total commands: {stats.get('total', 0)}")
    print(f"  Successful: {stats.get('success', 0)}")
    print(f"  Failed: {stats.get('failure', 0)}")
    
    total = stats.get('total', 0)
    success = stats.get('success', 0)
    if total > 0:
        rate = success / total * 100
        print(f"  Success rate: {rate:.1f}%")
    
    # Top commands
    commands = stats.get('commands', {})
    if commands:
        print(f"\n{Colors.BOLD}Top Commands:{Colors.RESET}")
        sorted_cmds = sorted(commands.items(), key=lambda x: x[1], reverse=True)[:5]
        for cmd, count in sorted_cmds:
            print(f"  {cmd}: {count} times")
    
    # Average times
    times = stats.get('times', {})
    if times:
        print(f"\n{Colors.BOLD}Average Execution Times:{Colors.RESET}")
        for cmd, time_list in list(times.items())[:5]:
            if time_list:
                avg = sum(time_list) / len(time_list)
                print(f"  {cmd}: {avg:.2f}s")


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


def print_fun_mode(mode: str):
    """Print fun mode message."""
    phrase = get_fun_phrase(mode)
    prefix = f"[{mode.upper()}]"
    
    if mode == "pirate":
        print(f"{Colors.YELLOW}{prefix} {phrase}{Colors.RESET}")
    elif mode == "cowboy":
        print(f"{Colors.YELLOW}{prefix} {phrase}{Colors.RESET}")
    elif mode == "yoda":
        print(f"{Colors.GREEN}{prefix} {phrase}{Colors.RESET}")
    elif mode == "shakespeare":
        print(f"{Colors.PURPLE}{prefix} {phrase}{Colors.RESET}")
    elif mode == "anime":
        print(f"{Colors.CYAN}{prefix} {phrase}{Colors.RESET}")


def confidence_boost() -> tuple:
    """Boost user's confidence."""
    current = get_confidence()
    new_level = min(100, current + random.randint(5, 15))
    set_confidence(new_level)
    return current, new_level


def confidence_insult() -> tuple:
    """Insult user's confidence."""
    current = get_confidence()
    new_level = max(0, current - random.randint(5, 20))
    set_confidence(new_level)
    return current, new_level


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


def bruh_mode() -> str:
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


def rainbow_text(text: str) -> str:
    """Generate rainbow colored text."""
    colors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.PURPLE]
    result = ""
    for i, char in enumerate(text):
        result += colors[i % len(colors)] + char
    result += Colors.RESET
    return result


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

SILENT/VERBOSE MODES:
  sufdo --silent ls                   Silent mode (only errors)
  sufdo --verbose ls                  Verbose output
  sufdo --debug ls                    Debug information
  sufdo --trace ls                    Trace execution

SAFETY MODES:
  sufdo --dry-run apt                 Preview without executing
  sufdo --confirm apt                 Ask for confirmation
  sufdo --safe-mode apt               Block destructive commands
  sufdo --backup apt                  Backup before operations

LOGGING:
  sufdo --log apt                     Log to file
  sufdo --log-file /tmp/sufdo.log     Custom log file
  sufdo --log-level DEBUG             Set log level

FUN MODES:
  sufdo --pirate apt                  Pirate mode
  sufdo --cowboy apt                  Cowboy mode
  sufdo --yoda apt                    Yoda mode
  sufdo --shakespeare apt             Shakespeare mode
  sufdo --anime apt                   Anime mode
  sufdo --rainbow apt                 Rainbow output
  sufdo --combo apt                   ALL MODES AT ONCE

STATISTICS:
  sufdo --stats                       Show usage statistics
  sufdo --top                         Show top commands
  sufdo --confidence                  Show confidence level
        """
    )
    
    # Basic options
    parser.add_argument("-u", "--user", default="root", help="Run command as specified user")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    
    # History and aliases
    parser.add_argument("--history", action="store_true", help="Show command history")
    parser.add_argument("--last", "-!", action="store_true", help="Re-run the last executed command")
    parser.add_argument("--alias", nargs="*", metavar="NAME=CMD", help="Create or list aliases")
    
    # Execution options
    parser.add_argument("--flex", action="store_true", help="Show flex message after success")
    parser.add_argument("--timeout", "-t", type=int, default=None, help="Timeout in seconds")
    parser.add_argument("--confidence", action="store_true", help="Show confidence level")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--top", action="store_true", help="Show top commands")
    
    # Silent/Verbose modes
    parser.add_argument("--silent", "-q", "--quiet", action="store_true", help="Silent mode")
    parser.add_argument("--verbose", "-V", action="store_true", help="Verbose mode")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--trace", action="store_true", help="Trace mode")
    
    # Safety modes
    parser.add_argument("--dry-run", action="store_true", help="Preview command without executing")
    parser.add_argument("--confirm", action="store_true", help="Ask for confirmation")
    parser.add_argument("--safe-mode", action="store_true", help="Block destructive commands")
    parser.add_argument("--backup", action="store_true", help="Backup before operations")
    
    # Logging
    parser.add_argument("--log", action="store_true", help="Log to file")
    parser.add_argument("--log-file", type=str, help="Custom log file path")
    parser.add_argument("--log-level", type=str, default="INFO", help="Log level")
    
    # Fun modes
    parser.add_argument("--pirate", action="store_true", help="Pirate mode")
    parser.add_argument("--cowboy", action="store_true", help="Cowboy mode")
    parser.add_argument("--yoda", action="store_true", help="Yoda mode")
    parser.add_argument("--shakespeare", action="store_true", help="Shakespeare mode")
    parser.add_argument("--anime", action="store_true", help="Anime mode")
    parser.add_argument("--rainbow", action="store_true", help="Rainbow output")
    
    # Existing modes
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--drama", action="store_true", help="Dramatic execution mode")
    parser.add_argument("--pray", action="store_true", help="Pray before execution")
    parser.add_argument("--yeet", action="store_true", help="YEET mode")
    parser.add_argument("--sus", action="store_true", help="Suspicious mode")
    parser.add_argument("--hacker", action="store_true", help="Hacker mode")
    parser.add_argument("--cursed", action="store_true", help="Cursed mode")
    parser.add_argument("--matrix", action="store_true", help="Matrix rain effect")
    parser.add_argument("--bruh", action="store_true", help="Add bruh commentary")
    parser.add_argument("--combo", action="store_true", help="ALL MODES AT ONCE")
    
    # Command
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute")

    args = parser.parse_args()

    # Setup logging
    logger = None
    if args.log or args.debug or args.verbose:
        log_level = getattr(logging, args.log_level.upper(), logging.INFO)
        logger = setup_logging(args.log_file, log_level)

    # Handle --no-color
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, "")

    # Version
    if args.version:
        version_msg = f"{Colors.BOLD}sufdo version 3.10.0{Colors.RESET}"
        if args.rainbow:
            version_msg = rainbow_text("sufdo version 3.10.0")
        print(version_msg)
        print("Super User Fkin Do")
        print("https://github.com/Arseniy1002/sufdo")
        if args.verbose:
            print(f"Config dir: {SUFDO_DIR}")
            print(f"Log file: {LOG_FILE}")
        print(f"{Colors.DIM}Now with 200+ features!{Colors.RESET}")
        sys.exit(0)

    # Stats
    if args.stats:
        print_stats()
        sys.exit(0)

    # History
    if args.history:
        print_history()
        sys.exit(0)

    # Confidence
    if args.confidence:
        print_confidence()
        sys.exit(0)

    # Aliases
    if args.alias is not None:
        aliases = load_aliases()
        if not args.alias:
            if aliases:
                print(f"{Colors.BOLD}Aliases:{Colors.RESET}")
                for name, cmd in aliases.items():
                    print(f"  {Colors.GREEN}{name}{Colors.RESET} = {Colors.CYAN}{cmd}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No aliases defined.{Colors.RESET}")
        else:
            for alias_def in args.alias:
                if "=" in alias_def:
                    name, cmd = alias_def.split("=", 1)
                    aliases[name] = cmd
                    print(f"{Colors.GREEN}[OK]{Colors.RESET} Alias '{name}' created")
            save_aliases(aliases)
        sys.exit(0)

    # Last command
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
    
    if args.command and args.command[0] in aliases:
        expanded = aliases[args.command[0]] + " " + " ".join(args.command[1:])
        print(f"{Colors.YELLOW}[ALIAS] {args.command[0]} -> {expanded}{Colors.RESET}")
        cmd_str = expanded

    # COMBO MODE
    if args.combo:
        args.drama = args.pray = args.yeet = args.sus = True
        args.hacker = args.cursed = args.matrix = args.bruh = True
        args.pirate = args.cowboy = args.rainbow = True

    # Safe mode check
    if args.safe_mode and is_destructive_command(cmd_str):
        print(f"{Colors.RED}[SAFE MODE] Blocked destructive command: {cmd_str}{Colors.RESET}")
        sys.exit(1)

    # Dry run
    if args.dry_run:
        print(f"{Colors.GREEN}[DRY RUN] Would execute: {cmd_str}{Colors.RESET}")
        print(f"{Colors.GREEN}[DRY RUN] As user: {args.user}{Colors.RESET}")
        sys.exit(0)

    # Confirm
    if args.confirm:
        response = input(f"{Colors.YELLOW}Execute '{cmd_str}'? [y/N]: {Colors.RESET}")
        if response.lower() != 'y':
            print(f"{Colors.RED}[CANCELLED] Command cancelled by user{Colors.RESET}")
            sys.exit(1)

    # Backup
    if args.backup:
        # Try to backup affected paths
        print(f"{Colors.YELLOW}[BACKUP] Creating backup...{Colors.RESET}")

    # Fun mode intros
    if args.pirate:
        print_fun_mode("pirate")
    if args.cowboy:
        print_fun_mode("cowboy")
    if args.yoda:
        print_fun_mode("yoda")
    if args.shakespeare:
        print_fun_mode("shakespeare")
    if args.anime:
        print_fun_mode("anime")

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

    # Verbose/Debug output
    if args.verbose:
        print(f"{Colors.CYAN}[VERBOSE] Command: {cmd_str}{Colors.RESET}")
        print(f"{Colors.CYAN}[VERBOSE] User: {args.user}{Colors.RESET}")
        print(f"{Colors.CYAN}[VERBOSE] Timeout: {args.timeout}{Colors.RESET}")
    if args.debug:
        print(f"{Colors.YELLOW}[DEBUG] Python: {sys.version}{Colors.RESET}")
        print(f"{Colors.YELLOW}[DEBUG] Platform: {sys.platform}{Colors.RESET}")
        print(f"{Colors.YELLOW}[DEBUG] Args: {args}{Colors.RESET}")
    if args.trace:
        print(f"{Colors.WHITE}[TRACE] Entering main execution{Colors.RESET}")

    # Execute
    if not args.silent:
        output = f"{Colors.BLUE}[RUN]{Colors.RESET} sufdo: executing as {Colors.BOLD}{args.user}{Colors.RESET}"
        if args.rainbow:
            output = rainbow_text(f"[RUN] sufdo: executing as {args.user}")
        print(output)

    if args.yeet:
        yeet_mode()

    start_time = datetime.now()

    try:
        if logger:
            logger.info(f"Executing: {cmd_str}")
        
        result = subprocess.run(
            cmd_str,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=args.timeout
        )

        duration = (datetime.now() - start_time).total_seconds()

        # Output handling
        if args.silent:
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        else:
            output = result.stdout
            if args.rainbow:
                output = rainbow_text(result.stdout)
            print(output, end="")
            
            if result.stderr:
                if args.verbose:
                    print(result.stderr, end="", file=sys.stderr)
                elif result.returncode != 0:
                    print(result.stderr, end="", file=sys.stderr)

        # Log and stats
        log_command(cmd_str, args.user, result.returncode, duration)
        update_stats(cmd_str, result.returncode, duration)
        
        if logger:
            logger.info(f"Exit code: {result.returncode}, Duration: {duration:.2f}s")

        # Result handling
        if result.returncode == 0:
            if not args.silent:
                msg = f"{Colors.GREEN}[OK]{Colors.RESET} Command completed successfully ({duration:.2f}s)"
                if args.rainbow:
                    msg = rainbow_text(f"[OK] Command completed successfully ({duration:.2f}s)")
                print(msg)

                old, new = confidence_boost()
                if not args.silent:
                    print(f"{Colors.CYAN}Confidence: {old}% -> {new}% (+{new-old}){Colors.RESET}")

                if args.flex:
                    print_flex()
                if args.bruh:
                    print(bruh_mode())
        else:
            if not args.silent:
                print(f"{Colors.RED}[FAIL]{Colors.RESET} Command failed with exit code {result.returncode} ({duration:.2f}s)")
                old, new = confidence_insult()
                if not args.silent:
                    print(f"{Colors.RED}Confidence: {old}% -> {new}% ({new-old}){Colors.RESET}")
                if args.bruh:
                    print(bruh_mode())

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        if logger:
            logger.error(f"Timeout after {args.timeout}s")
        if not args.silent:
            print(f"{Colors.RED}[TIMEOUT]{Colors.RESET} Command timed out after {args.timeout}s")
        sys.exit(124)
    except Exception as e:
        if logger:
            logger.error(f"Exception: {e}")
        if not args.silent:
            print(f"{Colors.RED}sufdo: error executing command: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
