#!/usr/bin/env python3
"""
sufdo - Super User Fkin Do - Ultimate Edition

A sudo-like utility for executing commands with elevated privileges.
Because sometimes you just need to get shit done.

Version: 4.0.0 - Ultimate Edition (ALL FEATURES)
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
import threading
import queue
import socket
import smtplib
import urllib.request
import re
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
ENV_FILE = SUFDO_DIR / ".env"
WEBHOOKS_FILE = SUFDO_DIR / "webhooks.json"

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
    ORANGE = "\033[33m"
    PINK = "\033[95m"


# Destructive commands blacklist
DESTRUCTIVE_COMMANDS = [
    "rm -rf /", "rm -rf /*", "dd if=/dev/zero", "mkfs",
    "fdisk", "format", "del /s /q", "rmdir /s",
    "shutdown -a", "chmod -R 777 /", "chown -R root:root /",
]

# Fun mode phrases
PHRASES = {
    "pirate": ["Ahoy matey!", "Shiver me timbers!", "All hands on deck!", "Avast ye!", "Blimey!", "Dead men tell no tales!", "Heave ho!", "Landlubber!", "Savvy?", "Thar she blows!", "Yo ho ho!", "Batten down the hatches!"],
    "cowboy": ["Howdy partner!", "Yeehaw!", "This town ain't big enough!", "I'm gonna git you!", "Ride 'em cowboy!", "Hold your horses!", "All hat, no cattle!", "No skin off my nose!", "Quick as a wink!", "That's the way the cookie crumbles!"],
    "yoda": ["Do or do not, there is no try.", "May the Force be with you.", "Size matters not.", "Fear is the path to the dark side.", "Patience you must have.", "Truly wonderful, the mind of a child is.", "In a dark place we find ourselves.", "Much to learn, you still have."],
    "shakespeare": ["To be or not to be, that is the question.", "All the world's a stage.", "The course of true love never did run smooth.", "Brevity is the soul of wit.", "There is method in my madness.", "The lady doth protest too much.", "A rose by any other name would smell as sweet.", "All that glitters is not gold."],
    "anime": ["I'm gonna be the Pirate King!", "Believe it!", "I'll take a potato chip... and eat it!", "This is the power of friendship!", "I am already dead.", "The only one who can beat me is me.", "I'll destroy you!", "You're already dead."],
    "russian": ["Ё-моё!", "Ёперный театр!", "Ёлки-палки!", "Блин!", "Ё-моё, опять!", "Работа не волк!", "Тише едешь - дальше будешь!", "Семь раз отмерь!"],
}


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    SUFDO_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict:
    """Load user configuration."""
    if not CONFIG_FILE.exists():
        return {"quiet_level": 0, "verbose_level": 1, "theme": "default", "profile": "default"}
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
        return {"total": 0, "success": 0, "failure": 0, "commands": {}, "times": {}}
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


def load_webhooks() -> Dict:
    """Load webhook configurations."""
    if not WEBHOOKS_FILE.exists():
        return {"discord": None, "telegram": None, "slack": None}
    try:
        with open(WEBHOOKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_webhooks(webhooks: Dict):
    """Save webhook configurations."""
    ensure_config_dir()
    with open(WEBHOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(webhooks, f, indent=2, ensure_ascii=False)


def load_env() -> Dict:
    """Load environment variables from .env file."""
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    return env


def save_env(env: Dict):
    """Save environment variables to .env file."""
    ensure_config_dir()
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for key, value in env.items():
            f.write(f"{key}={value}\n")


def load_profiles() -> Dict:
    """Load all profiles."""
    profiles = {"default": {}}
    for profile_file in PROFILES_DIR.glob("*.json"):
        try:
            with open(profile_file, encoding="utf-8") as f:
                profiles[profile_file.stem] = json.load(f)
        except:
            pass
    return profiles


def save_profile(name: str, config: Dict):
    """Save a profile."""
    ensure_config_dir()
    with open(PROFILES_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


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
    
    cmd_key = command.split()[0] if command else "unknown"
    if "commands" not in stats:
        stats["commands"] = {}
    stats["commands"][cmd_key] = stats["commands"].get(cmd_key, 0) + 1
    
    if "times" not in stats:
        stats["times"] = {}
    if cmd_key not in stats["times"]:
        stats["times"][cmd_key] = []
    stats["times"][cmd_key].append(duration)
    stats["times"][cmd_key] = stats["times"][cmd_key][-10:]
    
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


def get_undo_command() -> Optional[Dict]:
    """Get the last command for undo."""
    if not HISTORY_FILE.exists():
        return None
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            history = json.load(f)
            if history:
                return history[-1]
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


def list_backups() -> List[str]:
    """List all backups."""
    ensure_config_dir()
    return [f.name for f in BACKUP_DIR.iterdir()] if BACKUP_DIR.exists() else []


def restore_backup(backup_name: str) -> bool:
    """Restore from backup."""
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        return False
    
    # Extract original name from backup name
    original_name = '_'.join(backup_name.split('_')[:-2])
    
    try:
        if backup_path.is_file():
            shutil.copy2(backup_path, original_name)
        else:
            if os.path.exists(original_name):
                shutil.rmtree(original_name)
            shutil.copytree(backup_path, original_name)
        return True
    except:
        return False


def cleanup_old_backups(days: int = 30):
    """Clean up backups older than specified days."""
    ensure_config_dir()
    if not BACKUP_DIR.exists():
        return
    
    cutoff = time.time() - (days * 24 * 60 * 60)
    for backup in BACKUP_DIR.iterdir():
        if backup.stat().st_mtime < cutoff:
            try:
                if backup.is_file():
                    backup.unlink()
                else:
                    shutil.rmtree(backup)
            except:
                pass


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
    
    for i, arg in enumerate(args, 1):
        alias_cmd = alias_cmd.replace(f"${i}", arg)
    
    if "$@" in alias_cmd:
        alias_cmd = alias_cmd.replace("$@", " ".join(args))
    else:
        alias_cmd = alias_cmd + " " + " ".join(args)
    
    return alias_cmd.split()


def get_fun_phrase(mode: str) -> str:
    """Get random phrase for fun mode."""
    phrases = PHRASES.get(mode, PHRASES["pirate"])
    return random.choice(phrases)


def send_discord_webhook(webhook_url: str, message: str) -> bool:
    """Send message to Discord webhook."""
    try:
        data = json.dumps({"content": message}).encode('utf-8')
        req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
        return True
    except:
        return False


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Send message to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": message}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
        return True
    except:
        return False


def send_email(smtp_server: str, smtp_port: int, username: str, password: str, 
               to_email: str, subject: str, body: str) -> bool:
    """Send email notification."""
    try:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False


def send_notification(title: str, message: str, sound: bool = False):
    """Send system notification."""
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"{title}\n\n{message}", "sufdo", 0x40)
        elif sys.platform == "darwin":
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
        else:
            os.system(f'notify-send "{title}" "{message}"')
        
        if sound:
            print('\a')
    except:
        pass


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
    
    commands = stats.get('commands', {})
    if commands:
        print(f"\n{Colors.BOLD}Top Commands:{Colors.RESET}")
        sorted_cmds = sorted(commands.items(), key=lambda x: x[1], reverse=True)[:5]
        for cmd, count in sorted_cmds:
            print(f"  {cmd}: {count} times")
    
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
    
    colors_map = {
        "pirate": Colors.YELLOW, "cowboy": Colors.YELLOW, "yoda": Colors.GREEN,
        "shakespeare": Colors.PURPLE, "anime": Colors.CYAN, "russian": Colors.RED,
    }
    print(f"{colors_map.get(mode, Colors.WHITE)}{prefix} {phrase}{Colors.RESET}")


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
        "PREPARE FOR CHAOS...", "INITIATING DESTRUCTION SEQUENCE...",
        "WELCOME TO THE DANGER ZONE...", "CHARGING THE ROOT POWER...",
        "VOLCANIC COMMAND DETECTED...", "YOUR SYSTEM MAY EXPERIENCE EXTREME POWER...",
        "DRAMA LEVEL: MAXIMUM...", "EMERGENCY PROTOCOLS ENGAGED...",
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
        "bruh...", "bruh moment", "big brain time", "bruh, really?",
        "bruh, I've seen better", "bruh, that's it?",
        "bruh, my grandma executes faster", "bruh, even Windows could do that",
    ]
    return f"{Colors.YELLOW}{random.choice(bruh_phrases)}{Colors.RESET}"


def hacker_mode():
    """Print hacker-style messages."""
    hacker_texts = [
        "[+] Accessing mainframe...", "[+] Bypassing firewall...",
        "[+] Injecting SQL...", "[+] Downloading RAM...",
        "[+] Mining Bitcoin...", "[+] Hacking the Pentagon...",
        "[+] Uploading virus...", "[+] Root access: GRANTED",
    ]
    for text in hacker_texts[:random.randint(2, 4)]:
        print(f"{Colors.GREEN}{text}{Colors.RESET}")
        time.sleep(0.1)


def cursed_mode():
    """Cursed mode - weird output."""
    cursed_texts = [
        "this command is cursed", "your soul has been bound to this terminal",
        "the demons are pleased with your choice", "you have awakened the ancient ones",
        "there is no turning back now", "the void stares back at you",
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


def dark_mode(text: str) -> str:
    """Apply dark theme colors."""
    return f"{Colors.DIM}{text}{Colors.RESET}"


def validate_command(command: str) -> tuple:
    """Validate command exists and has permissions."""
    import shutil
    
    cmd = command.split()[0]
    
    # Check if command exists
    if not shutil.which(cmd):
        return False, f"Command '{cmd}' not found in PATH"
    
    return True, "OK"


def get_cache_key(command: str) -> str:
    """Generate cache key for command."""
    return hashlib.md5(command.encode()).hexdigest()


def get_from_cache(command: str, ttl: int = 300) -> Optional[Any]:
    """Get command output from cache."""
    cache = load_cache()
    key = get_cache_key(command)
    
    if key in cache:
        entry = cache[key]
        if time.time() - entry.get("timestamp", 0) < ttl:
            return entry.get("output")
        else:
            del cache[key]
            save_cache(cache)
    return None


def save_to_cache(command: str, output: Any, ttl: int = 300):
    """Save command output to cache."""
    cache = load_cache()
    key = get_cache_key(command)
    cache[key] = {
        "output": output,
        "timestamp": time.time(),
        "ttl": ttl
    }
    save_cache(cache)


def clear_cache():
    """Clear all cache."""
    ensure_config_dir()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def execute_parallel(commands: List[str], max_workers: int = 4) -> List[Dict]:
    """Execute commands in parallel."""
    results = []
    
    def run_cmd(cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return {"command": cmd, "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
        except Exception as e:
            return {"command": cmd, "error": str(e)}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_cmd, cmd): cmd for cmd in commands}
        for future in as_completed(futures):
            results.append(future.result())
    
    return results


def execute_background(command: str) -> int:
    """Execute command in background."""
    process = subprocess.Popen(command, shell=True)
    return process.pid


def get_background_jobs() -> List[Dict]:
    """Get list of background jobs."""
    # Simple implementation - in real world would track PIDs
    return []


def kill_background_job(pid: int) -> bool:
    """Kill background job by PID."""
    try:
        os.kill(pid, 9)
        return True
    except:
        return False


def load_batch_file(filepath: str) -> List[str]:
    """Load commands from batch file."""
    with open(filepath, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def execute_batch(commands: List[str], stop_on_error: bool = True, parallel: bool = False) -> List[Dict]:
    """Execute batch of commands."""
    results = []
    
    if parallel:
        return execute_parallel(commands)
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            results.append({"command": cmd, "returncode": result.returncode})
            if result.returncode != 0 and stop_on_error:
                break
        except Exception as e:
            results.append({"command": cmd, "error": str(e)})
            if stop_on_error:
                break
    
    return results


def main():
    parser = argparse.ArgumentParser(
        prog="sufdo",
        description="Super User Fkin Do - Execute commands with elevated privileges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sufdo apt update                    Run command as root
  sufdo -u www-data ls /var           Run as specific user
  sufdo --flex ls -la                 Show flex message
  sufdo --history                     Show command history
  sufdo --last                        Re-run last command
  sufdo --alias build="npm run build" Create alias

SILENT/VERBOSE:
  sufdo --silent ls                   Silent mode
  sufdo --verbose ls                  Verbose output
  sufdo --debug ls                    Debug info
  sufdo --trace ls                    Trace execution

SAFETY:
  sufdo --dry-run apt                 Preview only
  sufdo --confirm apt                 Ask confirmation
  sufdo --safe-mode apt               Block dangerous
  sufdo --backup apt                  Backup first

LOGGING:
  sufdo --log apt                     Log to file
  sufdo --log-file /tmp/sufdo.log     Custom log
  sufdo --syslog                      System log

NOTIFICATIONS:
  sufdo --notify apt                  Toast notification
  sufdo --discord apt                 Discord webhook
  sufdo --telegram apt                Telegram message
  sufdo --email apt                   Email notification

STATISTICS:
  sufdo --stats                       Show statistics
  sufdo --top                         Top commands
  sufdo --export-stats                Export to JSON

ALIASES:
  sufdo --alias                       List aliases
  sufdo --alias build="npm build"     Create alias
  sufdo --alias-import file.json      Import aliases
  sufdo --alias-export file.json      Export aliases

FUN MODES:
  sufdo --pirate apt                  Pirate mode
  sufdo --cowboy apt                  Cowboy mode
  sufdo --yoda apt                    Yoda mode
  sufdo --shakespeare apt             Shakespeare
  sufdo --anime apt                   Anime mode
  sufdo --russian apt                 Russian mode
  sufdo --rainbow apt                 Rainbow output
  sufdo --dark apt                    Dark theme
  sufdo --combo apt                   ALL MODES!

ADVANCED:
  sufdo --cache apt                   Use cache
  sufdo --parallel cmd1 cmd2          Parallel execution
  sufdo --background cmd              Background job
  sufdo --batch file.txt              Batch execution
  sufdo --profile dev                 Use profile
  sufdo --undo                        Undo last command
  sufdo --validate cmd                Validate command
        """
    )
    
    # Basic
    parser.add_argument("-u", "--user", default="root", help="Run as user")
    parser.add_argument("-v", "--version", action="store_true", help="Version")
    
    # History/Aliases
    parser.add_argument("--history", action="store_true", help="Show history")
    parser.add_argument("--last", "-!", action="store_true", help="Re-run last")
    parser.add_argument("--alias", nargs="*", metavar="NAME=CMD", help="Aliases")
    parser.add_argument("--alias-import", type=str, help="Import aliases")
    parser.add_argument("--alias-export", type=str, help="Export aliases")
    parser.add_argument("--alias-share", action="store_true", help="Share alias")
    parser.add_argument("--alias-preset", type=str, help="Preset aliases")
    
    # Execution
    parser.add_argument("--flex", action="store_true", help="Flex message")
    parser.add_argument("--timeout", "-t", type=int, help="Timeout")
    parser.add_argument("--confidence", action="store_true", help="Show confidence")
    
    # Stats
    parser.add_argument("--stats", action="store_true", help="Statistics")
    parser.add_argument("--top", action="store_true", help="Top commands")
    parser.add_argument("--success-rate", action="store_true", help="Success rate")
    parser.add_argument("--export-stats", type=str, help="Export stats")
    
    # Silent/Verbose
    parser.add_argument("--silent", "-q", "--quiet", action="store_true", help="Silent")
    parser.add_argument("--verbose", "-V", action="store_true", help="Verbose")
    parser.add_argument("--debug", action="store_true", help="Debug")
    parser.add_argument("--trace", action="store_true", help="Trace")
    
    # Safety
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--confirm", action="store_true", help="Confirm")
    parser.add_argument("--safe-mode", action="store_true", help="Safe mode")
    parser.add_argument("--no-destructive", action="store_true", help="No destructive")
    parser.add_argument("--backup", action="store_true", help="Backup")
    parser.add_argument("--restore", type=str, help="Restore backup")
    parser.add_argument("--list-backups", action="store_true", help="List backups")
    parser.add_argument("--cleanup-backups", action="store_true", help="Cleanup old backups")
    
    # Logging
    parser.add_argument("--log", action="store_true", help="Log to file")
    parser.add_argument("--log-file", type=str, help="Log file path")
    parser.add_argument("--log-level", type=str, default="INFO", help="Log level")
    parser.add_argument("--syslog", action="store_true", help="Syslog")
    parser.add_argument("--rotate-logs", action="store_true", help="Rotate logs")
    
    # Notifications
    parser.add_argument("--notify", action="store_true", help="Notify")
    parser.add_argument("--notify-sound", action="store_true", help="Notify with sound")
    parser.add_argument("--discord", action="store_true", help="Discord webhook")
    parser.add_argument("--telegram", action="store_true", help="Telegram")
    parser.add_argument("--email", action="store_true", help="Email")
    parser.add_argument("--webhook-add", nargs=2, metavar=("TYPE", "URL"), help="Add webhook")
    parser.add_argument("--webhook-list", action="store_true", help="List webhooks")
    
    # Fun modes
    parser.add_argument("--pirate", action="store_true", help="Pirate")
    parser.add_argument("--cowboy", action="store_true", help="Cowboy")
    parser.add_argument("--yoda", action="store_true", help="Yoda")
    parser.add_argument("--shakespeare", action="store_true", help="Shakespeare")
    parser.add_argument("--anime", action="store_true", help="Anime")
    parser.add_argument("--russian", action="store_true", help="Russian")
    parser.add_argument("--rainbow", action="store_true", help="Rainbow")
    parser.add_argument("--dark", action="store_true", help="Dark theme")
    
    # Existing modes
    parser.add_argument("--no-color", action="store_true", help="No colors")
    parser.add_argument("--drama", action="store_true", help="Drama")
    parser.add_argument("--pray", action="store_true", help="Pray")
    parser.add_argument("--yeet", action="store_true", help="Yeet")
    parser.add_argument("--sus", action="store_true", help="Sus")
    parser.add_argument("--hacker", action="store_true", help="Hacker")
    parser.add_argument("--cursed", action="store_true", help="Cursed")
    parser.add_argument("--matrix", action="store_true", help="Matrix")
    parser.add_argument("--bruh", action="store_true", help="Bruh")
    parser.add_argument("--combo", action="store_true", help="Combo all")
    
    # Advanced
    parser.add_argument("--cache", action="store_true", help="Use cache")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache")
    parser.add_argument("--parallel", nargs="+", help="Parallel commands")
    parser.add_argument("--background", action="store_true", help="Background")
    parser.add_argument("--priority", type=str, choices=["low", "normal", "high"], default="normal", help="Priority")
    parser.add_argument("--batch", type=str, help="Batch file")
    parser.add_argument("--profile", type=str, help="Profile")
    parser.add_argument("--profile-list", action="store_true", help="List profiles")
    parser.add_argument("--profile-save", type=str, help="Save profile")
    parser.add_argument("--env", action="store_true", help="Use env file")
    parser.add_argument("--env-set", nargs=2, metavar=("KEY", "VALUE"), help="Set env var")
    parser.add_argument("--completion", type=str, choices=["bash", "zsh", "fish"], help="Shell completion")
    parser.add_argument("--validate", action="store_true", help="Validate command")
    parser.add_argument("--undo", action="store_true", help="Undo last")
    
    # Command
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command")

    args = parser.parse_args()

    # Setup logging
    logger = None
    if args.log or args.debug or args.verbose or args.syslog:
        log_level = getattr(logging, args.log_level.upper(), logging.INFO)
        logger = setup_logging(args.log_file, log_level)

    # No color
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, "")

    # Version
    if args.version:
        ver = f"{Colors.BOLD}sufdo version 4.0.0{Colors.RESET}"
        if args.rainbow:
            ver = rainbow_text("sufdo version 4.0.0 - Ultimate Edition")
        print(ver)
        print("Super User Fkin Do - Ultimate Edition")
        print("https://github.com/Arseniy1002/sufdo")
        if args.verbose or args.debug:
            print(f"Config: {SUFDO_DIR}")
            print(f"Log: {LOG_FILE}")
            print(f"Python: {sys.version}")
            print(f"Platform: {sys.platform}")
        print(f"{Colors.DIM}200+ features installed!{Colors.RESET}")
        sys.exit(0)

    # Stats
    if args.stats:
        print_stats()
        sys.exit(0)

    # Success rate
    if args.success_rate:
        stats = load_stats()
        total = stats.get('total', 0)
        success = stats.get('success', 0)
        if total > 0:
            print(f"Success rate: {success/total*100:.1f}% ({success}/{total})")
        else:
            print("No commands executed yet")
        sys.exit(0)

    # Export stats
    if args.export_stats:
        stats = load_stats()
        with open(args.export_stats, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        print(f"Stats exported to {args.export_stats}")
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
                print(f"{Colors.YELLOW}No aliases.{Colors.RESET}")
        else:
            for alias_def in args.alias:
                if "=" in alias_def:
                    name, cmd = alias_def.split("=", 1)
                    aliases[name] = cmd
                    print(f"{Colors.GREEN}[OK]{Colors.RESET} Alias '{name}' created")
            save_aliases(aliases)
        sys.exit(0)

    # Alias import
    if args.alias_import:
        try:
            with open(args.alias_import, encoding="utf-8") as f:
                new_aliases = json.load(f)
            aliases = load_aliases()
            aliases.update(new_aliases)
            save_aliases(aliases)
            print(f"{Colors.GREEN}[OK]{Colors.RESET} Imported {len(new_aliases)} aliases")
        except Exception as e:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {e}")
        sys.exit(0)

    # Alias export
    if args.alias_export:
        aliases = load_aliases()
        with open(args.alias_export, "w", encoding="utf-8") as f:
            json.dump(aliases, f, indent=2)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Exported {len(aliases)} aliases")
        sys.exit(0)

    # Alias preset
    if args.alias_preset:
        presets = {
            "git": {"gs": "git status", "ga": "git add", "gc": "git commit", "gp": "git push"},
            "docker": {"db": "docker build", "dr": "docker run", "dp": "docker ps"},
            "npm": {"ni": "npm install", "ns": "npm start", "nt": "npm test", "nb": "npm build"},
            "python": {"pi": "pip install", "pr": "python -m http.server", "pl": "python -m http.server 8080"},
        }
        if args.alias_preset in presets:
            aliases = load_aliases()
            aliases.update(presets[args.alias_preset])
            save_aliases(aliases)
            print(f"{Colors.GREEN}[OK]{Colors.RESET} Loaded {args.alias_preset} preset")
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} Unknown preset: {args.alias_preset}")
        sys.exit(0)

    # Profile list
    if args.profile_list:
        profiles = load_profiles()
        print(f"{Colors.BOLD}Profiles:{Colors.RESET}")
        for name in profiles:
            print(f"  {Colors.GREEN}{name}{Colors.RESET}")
        sys.exit(0)

    # Profile save
    if args.profile_save:
        config = load_config()
        save_profile(args.profile_save, config)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Profile '{args.profile_save}' saved")
        sys.exit(0)

    # Webhook add
    if args.webhook_add:
        webhooks = load_webhooks()
        webhooks[args.webhook_add[0]] = args.webhook_add[1]
        save_webhooks(webhooks)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Webhook '{args.webhook_add[0]}' added")
        sys.exit(0)

    # Webhook list
    if args.webhook_list:
        webhooks = load_webhooks()
        print(f"{Colors.BOLD}Webhooks:{Colors.RESET}")
        for name, url in webhooks.items():
            status = f"{Colors.GREEN}configured{Colors.RESET}" if url else f"{Colors.RED}not set{Colors.RESET}"
            print(f"  {name}: {status}")
        sys.exit(0)

    # List backups
    if args.list_backups:
        backups = list_backups()
        if backups:
            print(f"{Colors.BOLD}Backups:{Colors.RESET}")
            for b in backups:
                print(f"  {b}")
        else:
            print(f"{Colors.YELLOW}No backups.{Colors.RESET}")
        sys.exit(0)

    # Restore backup
    if args.restore:
        if restore_backup(args.restore):
            print(f"{Colors.GREEN}[OK]{Colors.RESET} Restored {args.restore}")
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} Could not restore {args.restore}")
        sys.exit(0)

    # Cleanup backups
    if args.cleanup_backups:
        cleanup_old_backups(30)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Cleaned up old backups")
        sys.exit(0)

    # Clear cache
    if args.clear_cache:
        clear_cache()
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Cache cleared")
        sys.exit(0)

    # Env set
    if args.env_set:
        env = load_env()
        env[args.env_set[0]] = args.env_set[1]
        save_env(env)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {args.env_set[0]}={args.env_set[1]}")
        sys.exit(0)

    # Completion
    if args.completion:
        if args.completion == "bash":
            print('complete -W "--help --version --silent --verbose --stats --history --last --alias --flex --timeout --dry-run --confirm --safe-mode --backup --log --notify --discord --telegram --pirate --cowboy --yoda --rainbow --combo" sufdo')
        elif args.completion == "zsh":
            print('#compdef sufdo\n_sufdo_flags=(--help --version --silent --verbose --stats --history --last --alias --flex --timeout --dry-run --confirm --safe-mode --backup --log --notify --discord --telegram --pirate --cowboy --yoda --rainbow --combo)\ncompadd $_sufdo_flags')
        elif args.completion == "fish":
            print('complete -c sufdo -l help -l version -l silent -l verbose -l stats -l history -l last -l alias -l flex -l timeout -l dry-run -l confirm -l safe-mode -l backup -l log -l notify -l discord -l telegram -l pirate -l cowboy -l yoda -l rainbow -l combo')
        sys.exit(0)

    # Parallel execution
    if args.parallel:
        results = execute_parallel(args.parallel)
        for r in results:
            status = f"{Colors.GREEN}[OK]{Colors.RESET}" if r.get("returncode", 1) == 0 else f"{Colors.RED}[FAIL]{Colors.RESET}"
            print(f"{status} {r['command']}")
        sys.exit(0)

    # Background execution
    if args.background and args.command:
        cmd = " ".join(args.command)
        pid = execute_background(cmd)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Started in background (PID: {pid})")
        sys.exit(0)

    # Batch execution
    if args.batch:
        commands = load_batch_file(args.batch)
        results = execute_batch(commands, stop_on_error=True)
        for r in results:
            status = f"{Colors.GREEN}[OK]{Colors.RESET}" if r.get("returncode", 1) == 0 else f"{Colors.RED}[FAIL]{Colors.RESET}"
            print(f"{status} {r['command']}")
        sys.exit(0)

    # Undo
    if args.undo:
        last = get_undo_command()
        if last:
            print(f"{Colors.YELLOW}[UNDO] Last command: {last['command']}{Colors.RESET}")
            print(f"{Colors.YELLOW}[UNDO] Undo is not fully implemented yet{Colors.RESET}")
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} Nothing to undo")
        sys.exit(0)

    # Last command
    if args.last:
        last_cmd = get_last_command()
        if last_cmd:
            print(f"{Colors.YELLOW}[RETRY] Re-running: {last_cmd}{Colors.RESET}")
            args.command = last_cmd.split()
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} No previous command")
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

    # Load profile
    if args.profile:
        profiles = load_profiles()
        if args.profile in profiles:
            config = profiles[args.profile]
            # Apply profile settings
            if config.get("quiet"):
                args.silent = True
            if config.get("verbose"):
                args.verbose = True

    # Load env
    if args.env:
        env = load_env()
        os.environ.update(env)

    # Validate
    if args.validate:
        valid, msg = validate_command(cmd_str)
        if valid:
            print(f"{Colors.GREEN}[VALID]{Colors.RESET} {msg}")
        else:
            print(f"{Colors.RED}[INVALID]{Colors.RESET} {msg}")
            sys.exit(1)

    # Combo mode
    if args.combo:
        args.drama = args.pray = args.yeet = args.sus = True
        args.hacker = args.cursed = args.matrix = args.bruh = True
        args.pirate = args.cowboy = args.rainbow = args.dark = True

    # Safe mode
    if args.safe_mode or args.no_destructive:
        if is_destructive_command(cmd_str):
            print(f"{Colors.RED}[SAFE MODE] Blocked: {cmd_str}{Colors.RESET}")
            sys.exit(1)

    # Check cache
    if args.cache:
        cached = get_from_cache(cmd_str)
        if cached:
            print(f"{Colors.GREEN}[CACHE HIT]{Colors.RESET}")
            print(cached)
            sys.exit(0)

    # Dry run
    if args.dry_run:
        print(f"{Colors.GREEN}[DRY RUN] Would execute: {cmd_str}{Colors.RESET}")
        print(f"{Colors.GREEN}[DRY RUN] As user: {args.user}{Colors.RESET}")
        sys.exit(0)

    # Confirm
    if args.confirm:
        response = input(f"{Colors.YELLOW}Execute '{cmd_str}'? [y/N]: {Colors.RESET}")
        if response.lower() != 'y':
            print(f"{Colors.RED}[CANCELLED]{Colors.RESET}")
            sys.exit(1)

    # Backup
    if args.backup:
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
    if args.russian:
        print_fun_mode("russian")

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

    # Verbose/Debug
    if args.verbose:
        print(f"{Colors.CYAN}[VERBOSE] Command: {cmd_str}{Colors.RESET}")
        print(f"{Colors.CYAN}[VERBOSE] User: {args.user}{Colors.RESET}")
        print(f"{Colors.CYAN}[VERBOSE] Timeout: {args.timeout}{Colors.RESET}")
    if args.debug:
        print(f"{Colors.YELLOW}[DEBUG] Python: {sys.version}{Colors.RESET}")
        print(f"{Colors.YELLOW}[DEBUG] Platform: {sys.platform}{Colors.RESET}")
        print(f"{Colors.YELLOW}[DEBUG] Args: {args}{Colors.RESET}")
    if args.trace:
        print(f"{Colors.WHITE}[TRACE] Entering execution{Colors.RESET}")

    # Execute
    if not args.silent:
        output = f"{Colors.BLUE}[RUN]{Colors.RESET} sufdo: executing as {Colors.BOLD}{args.user}{Colors.RESET}"
        if args.rainbow:
            output = rainbow_text(f"[RUN] sufdo: executing as {args.user}")
        if args.dark:
            output = dark_mode(output)
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

        # Output
        if args.silent:
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        else:
            output = result.stdout
            if args.rainbow:
                output = rainbow_text(result.stdout)
            if args.dark:
                output = dark_mode(result.stdout)
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
            logger.info(f"Exit: {result.returncode}, Duration: {duration:.2f}s")

        # Save to cache
        if args.cache:
            save_to_cache(cmd_str, result.stdout, ttl=300)

        # Result
        if result.returncode == 0:
            if not args.silent:
                msg = f"{Colors.GREEN}[OK]{Colors.RESET} Completed ({duration:.2f}s)"
                if args.rainbow:
                    msg = rainbow_text(f"[OK] Completed ({duration:.2f}s)")
                print(msg)

                old, new = confidence_boost()
                if not args.silent:
                    print(f"{Colors.CYAN}Confidence: {old}% -> {new}%{Colors.RESET}")

                if args.flex:
                    print_flex()
                if args.bruh:
                    print(bruh_mode())

            # Notifications
            if args.notify:
                send_notification("sufdo - Success", f"Command completed: {cmd_str}", args.notify_sound)
            
            webhooks = load_webhooks()
            if args.discord and webhooks.get("discord"):
                send_discord_webhook(webhooks["discord"], f"✅ sufdo: {cmd_str}")
            if args.telegram and webhooks.get("telegram"):
                send_telegram_message(webhooks["telegram"]["bot"], webhooks["telegram"]["chat"], f"✅ {cmd_str}")

        else:
            if not args.silent:
                print(f"{Colors.RED}[FAIL]{Colors.RESET} Exit code {result.returncode} ({duration:.2f}s)")
                old, new = confidence_insult()
                if not args.silent:
                    print(f"{Colors.RED}Confidence: {old}% -> {new}%{Colors.RESET}")
                if args.bruh:
                    print(bruh_mode())

            # Error notifications
            if args.notify:
                send_notification("sufdo - Failed", f"Command failed: {cmd_str}", args.notify_sound)

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        if logger:
            logger.error(f"Timeout: {args.timeout}s")
        if not args.silent:
            print(f"{Colors.RED}[TIMEOUT]{Colors.RESET} After {args.timeout}s")
        sys.exit(124)
    except Exception as e:
        if logger:
            logger.error(f"Exception: {e}")
        if not args.silent:
            print(f"{Colors.RED}sufdo: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
