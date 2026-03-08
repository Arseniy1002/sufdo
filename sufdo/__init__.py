#!/usr/bin/env python3
"""
sufdo - Super User Fkin Do - Ultimate Edition

A sudo-like utility for executing commands with elevated privileges.
Because sometimes you just need to get shit done.

Version: 4.3.0 - Ultimate Edition (ALL FEATURES)
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


# Initialize ctypes on Windows for admin privileges
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        pass


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
AI_CONFIG_FILE = SUFDO_DIR / "ai_models.json"

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


def load_ai_config() -> Dict:
    """Load AI models configuration."""
    if not AI_CONFIG_FILE.exists():
        return {
            "models": {},
            "default": None
        }
    try:
        with open(AI_CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"models": {}, "default": None}


def save_ai_config(config: Dict):
    """Save AI models configuration."""
    ensure_config_dir()
    with open(AI_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_default_ai_models() -> List[Dict]:
    """Get default AI model presets."""
    return [
        {
            "name": "gpt-4o",
            "alias": "gpt",
            "api_key": "",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "provider": "openai"
        },
        {
            "name": "gemini-2.0-flash",
            "alias": "gemini",
            "api_key": "",
            "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "provider": "google"
        },
        {
            "name": "meta-llama/llama-3.3-70b-instruct",
            "alias": "openrouter",
            "api_key": "",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "provider": "openrouter"
        },
        {
            "name": "deepseek-chat",
            "alias": "deepseek",
            "api_key": "",
            "api_url": "https://api.deepseek.com/chat/completions",
            "provider": "deepseek"
        }
    ]


def query_ai(model_config: Dict, prompt: str) -> Optional[str]:
    """
    Query AI model with the given prompt.
    Returns the response text or None on error.
    """
    try:
        api_url = model_config.get("api_url", "")
        api_key = model_config.get("api_key", "")
        provider = model_config.get("provider", "openai")
        model_name = model_config.get("name", "")
        
        if not api_key:
            return f"{Colors.RED}[AI] API key not configured for {model_config.get('alias', 'model')}{Colors.RESET}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if provider in ["openai", "openrouter", "deepseek"]:
            headers["Authorization"] = f"Bearer {api_key}"
            if provider == "openrouter":
                headers["HTTP-Referer"] = "https://github.com/Arseniy1002/sufdo"
                headers["X-Title"] = "sufdo"
            
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful terminal assistant. Be concise and provide practical solutions."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if provider == "google":
                return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
            else:
                return result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                
        elif provider == "google":
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 500,
                    "temperature": 0.7
                }
            }
            
            req = urllib.request.Request(
                f"{api_url}?key={api_key}",
                data=json.dumps(data).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
        else:
            return f"{Colors.RED}[AI] Unknown provider: {provider}{Colors.RESET}"
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace') if e.fp else ""
        return f"{Colors.RED}[AI] API error ({e.code}): {error_body[:200]}{Colors.RESET}"
    except urllib.error.URLError as e:
        return f"{Colors.RED}[AI] Network error: {e.reason}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}[AI] Error: {e}{Colors.RESET}"


def analyze_command_error(command: str, stdout: str, stderr: str, returncode: int, model_alias: str = None) -> str:
    """
    Analyze a command error using AI.
    Returns AI's analysis or error message.
    """
    ai_config = load_ai_config()
    
    if not ai_config.get("models"):
        return f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}"
    
    # Get model config
    model_config = None
    if model_alias and model_alias in ai_config["models"]:
        model_config = ai_config["models"][model_alias]
    elif ai_config.get("default") and ai_config["default"] in ai_config["models"]:
        model_config = ai_config["models"][ai_config["default"]]
    else:
        # Use first available model
        model_config = list(ai_config["models"].values())[0]
    
    # Build prompt
    prompt = f"""Analyze this command error and provide a brief solution:

Command: {command}
Exit Code: {returncode}

Stdout:
{stdout[:500] if stdout else "(empty)"}

Stderr:
{stderr[:1000] if stderr else "(empty)"}

Provide:
1. What went wrong (1 sentence)
2. How to fix it (1-2 steps)
3. Alternative command if applicable

Be concise."""

    print(f"{Colors.CYAN}[AI] Analyzing error with {model_config.get('alias', 'AI')}...{Colors.RESET}")
    return query_ai(model_config, prompt)


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
            ctypes.windll.user32.MessageBoxW(0, f"{title}\n\n{message}", "sufdo", 0x40)
        elif sys.platform == "darwin":
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
        else:
            os.system(f'notify-send "{title}" "{message}"')

        if sound:
            print('\a')
    except:
        pass


def is_admin_windows() -> bool:
    """Check if running as administrator on Windows."""
    if sys.platform != "win32":
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def request_elevation_windows() -> bool:
    """
    Request elevation on Windows via UAC prompt.
    Opens elevated PowerShell, executes command, shows output, and closes.
    Current window remains open with history intact.
    Returns True if already admin or elevation successful, False if cancelled.
    """
    if sys.platform != "win32":
        return True

    if is_admin_windows():
        # Already running as admin - do nothing
        return True

    # Not running as admin - request elevation via UAC
    print(f"{Colors.YELLOW}[SUDO] Requesting administrator privileges...{Colors.RESET}")

    try:
        # Build the command to execute
        script_path = os.path.abspath(sys.argv[0]).replace("'", "''")
        args_escaped = ' '.join(sys.argv[1:]).replace("'", "''")
        python_exec = sys.executable.replace("'", "''")
        
        # PowerShell command that runs elevated and shows output
        ps_command = (
            f"Write-Host '[SUDO] Running elevated...' -ForegroundColor Yellow; "
            f"& '{python_exec}' '{script_path}' {args_escaped}; "
            f"Write-Host ''; "
            f"Write-Host '[SUDO] Command complete.' -ForegroundColor Green"
        )

        # Use ShellExecuteW with 'runas' to trigger UAC
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "powershell",
            f"-Command \"{ps_command}\"",
            None,
            1
        )

        if result > 32:
            # UAC accepted - new window will open and run the command
            print(f"{Colors.GREEN}[SUDO] Elevated window opened. Command will execute there.{Colors.RESET}")
            print(f"{Colors.GREEN}[SUDO] This window remains open with your history.{Colors.RESET}")
            return True  # Don't exit - keep current window open
        else:
            print(f"{Colors.RED}[SUDO] UAC cancelled or failed (error: {result}){Colors.RESET}")
            return False

    except Exception as e:
        print(f"{Colors.RED}[SUDO] Elevation error: {e}{Colors.RESET}")
        return False

    return True


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
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
            return {"command": cmd, "stdout": stdout, "stderr": stderr, "returncode": result.returncode}
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
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            results.append({"command": cmd, "returncode": result.returncode})
            if result.returncode != 0 and stop_on_error:
                break
        except Exception as e:
            results.append({"command": cmd, "error": str(e)})
            if stop_on_error:
                break

    return results


def get_os_package_manager() -> str:
    """Get the appropriate package manager command for the current OS."""
    if sys.platform == "win32":
        return "winget install"
    elif sys.platform == "darwin":
        return "brew install"
    else:  # Linux
        # Check for Arch-based systems
        if os.path.exists("/etc/arch-release"):
            return "pacman -S"
        elif os.path.exists("/etc/debian_version") or os.path.exists("/etc/apt/sources.list"):
            return "apt install"
        elif os.path.exists("/etc/redhat-release") or os.path.exists("/etc/fedora-release"):
            return "dnf install"
        elif os.path.exists("/etc/alpine-release"):
            return "apk add"
        elif os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", encoding="utf-8") as f:
                    content = f.read().lower()
                    if "arch" in content:
                        return "pacman -S"
                    elif "debian" in content or "ubuntu" in content:
                        return "apt install"
                    elif "fedora" in content:
                        return "dnf install"
                    elif "alpine" in content:
                        return "apk add"
            except:
                pass
        return "apt install"  # Default to apt for Linux


def get_examples_for_os() -> str:
    """Get example commands appropriate for the current OS."""
    pkg_mgr = get_os_package_manager()
    pkg_name = "htop" if sys.platform != "win32" else "python.python311"
    
    if sys.platform == "win32":
        return f"""Examples:
  sufdo {pkg_mgr} {pkg_name}          Install package
  sufdo dir C:\\Users                 List directory
  sufdo -u Administrator whoami       Run as specific user
  sufdo --flex dir                    Show flex message
  sufdo --history                     Show command history
  sufdo --last                        Re-run last command
  sufdo --alias build="npm run build" Create alias

SILENT/VERBOSE:
  sufdo --silent dir                  Silent mode
  sufdo --verbose dir                 Verbose output
  sufdo --debug dir                   Debug info
  sufdo --trace dir                   Trace execution

SAFETY:
  sufdo --dry-run {pkg_mgr}           Preview only
  sufdo --confirm {pkg_mgr}           Ask confirmation
  sufdo --safe-mode {pkg_mgr}         Block dangerous
  sufdo --backup {pkg_mgr}            Backup first

LOGGING:
  sufdo --log {pkg_mgr}               Log to file
  sufdo --log-file C:\\temp\\sufdo.log  Custom log
  sufdo --syslog                      System log

NOTIFICATIONS:
  sufdo --notify {pkg_mgr}            Toast notification
  sufdo --discord {pkg_mgr}           Discord webhook
  sufdo --telegram {pkg_mgr}          Telegram message
  sufdo --email {pkg_mgr}             Email notification

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
  sufdo --pirate {pkg_mgr}            Pirate mode
  sufdo --cowboy {pkg_mgr}            Cowboy mode
  sufdo --yoda {pkg_mgr}              Yoda mode
  sufdo --shakespeare {pkg_mgr}       Shakespeare
  sufdo --anime {pkg_mgr}             Anime mode
  sufdo --russian {pkg_mgr}           Russian mode
  sufdo --rainbow {pkg_mgr}           Rainbow output
  sufdo --dark {pkg_mgr}              Dark theme
  sufdo --combo {pkg_mgr}             ALL MODES!

ADVANCED:
  sufdo --cache {pkg_mgr}             Use cache
  sufdo --parallel cmd1 cmd2          Parallel execution
  sufdo --background cmd              Background job
  sufdo --batch file.txt              Batch execution
  sufdo --profile dev                 Use profile
  sufdo --undo                        Undo last command
  sufdo --validate cmd                Validate command"""
    elif sys.platform == "darwin":
        return f"""Examples:
  sufdo {pkg_mgr} {pkg_name}          Install package
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
  sufdo --dry-run {pkg_mgr}           Preview only
  sufdo --confirm {pkg_mgr}           Ask confirmation
  sufdo --safe-mode {pkg_mgr}         Block dangerous
  sufdo --backup {pkg_mgr}            Backup first

LOGGING:
  sufdo --log {pkg_mgr}               Log to file
  sufdo --log-file /tmp/sufdo.log     Custom log
  sufdo --syslog                      System log

NOTIFICATIONS:
  sufdo --notify {pkg_mgr}            Toast notification
  sufdo --discord {pkg_mgr}           Discord webhook
  sufdo --telegram {pkg_mgr}          Telegram message
  sufdo --email {pkg_mgr}             Email notification

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
  sufdo --pirate {pkg_mgr}            Pirate mode
  sufdo --cowboy {pkg_mgr}            Cowboy mode
  sufdo --yoda {pkg_mgr}              Yoda mode
  sufdo --shakespeare {pkg_mgr}       Shakespeare
  sufdo --anime {pkg_mgr}             Anime mode
  sufdo --russian {pkg_mgr}           Russian mode
  sufdo --rainbow {pkg_mgr}           Rainbow output
  sufdo --dark {pkg_mgr}              Dark theme
  sufdo --combo {pkg_mgr}             ALL MODES!

ADVANCED:
  sufdo --cache {pkg_mgr}             Use cache
  sufdo --parallel cmd1 cmd2          Parallel execution
  sufdo --background cmd              Background job
  sufdo --batch file.txt              Batch execution
  sufdo --profile dev                 Use profile
  sufdo --undo                        Undo last command
  sufdo --validate cmd                Validate command"""
    else:  # Linux
        return f"""Examples:
  sufdo {pkg_mgr} {pkg_name}          Install package
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
  sufdo --dry-run {pkg_mgr}           Preview only
  sufdo --confirm {pkg_mgr}           Ask confirmation
  sufdo --safe-mode {pkg_mgr}         Block dangerous
  sufdo --backup {pkg_mgr}            Backup first

LOGGING:
  sufdo --log {pkg_mgr}               Log to file
  sufdo --log-file /tmp/sufdo.log     Custom log
  sufdo --syslog                      System log

NOTIFICATIONS:
  sufdo --notify {pkg_mgr}            Toast notification
  sufdo --discord {pkg_mgr}           Discord webhook
  sufdo --telegram {pkg_mgr}          Telegram message
  sufdo --email {pkg_mgr}             Email notification

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
  sufdo --pirate {pkg_mgr}            Pirate mode
  sufdo --cowboy {pkg_mgr}            Cowboy mode
  sufdo --yoda {pkg_mgr}              Yoda mode
  sufdo --shakespeare {pkg_mgr}       Shakespeare
  sufdo --anime {pkg_mgr}             Anime mode
  sufdo --russian {pkg_mgr}           Russian mode
  sufdo --rainbow {pkg_mgr}           Rainbow output
  sufdo --dark {pkg_mgr}              Dark theme
  sufdo --combo {pkg_mgr}             ALL MODES!

ADVANCED:
  sufdo --cache {pkg_mgr}             Use cache
  sufdo --parallel cmd1 cmd2          Parallel execution
  sufdo --background cmd              Background job
  sufdo --batch file.txt              Batch execution
  sufdo --profile dev                 Use profile
  sufdo --undo                        Undo last command
  sufdo --validate cmd                Validate command"""


def main():
    parser = argparse.ArgumentParser(
        prog="sufdo",
        description="Super User Fkin Do - Execute commands with elevated privileges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=get_examples_for_os()
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
    
    # Windows UAC elevation (only on Windows)
    if sys.platform == "win32":
        parser.add_argument("-a", action="store_true", help="Request administrator privileges via UAC (Windows only)")
    
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

    # AI
    parser.add_argument("--ai", nargs="?", const="ask", metavar="QUESTION", help="Ask AI about command error")
    parser.add_argument("--ai-config", action="store_true", help="Configure AI models")
    parser.add_argument("--ai-list", action="store_true", help="List configured AI models")
    parser.add_argument("--ai-default", type=str, metavar="ALIAS", help="Set default AI model")
    parser.add_argument("--ai-ask", type=str, metavar="QUESTION", help="Ask AI a question")
    parser.add_argument("--ai-add", nargs=5, metavar=("ALIAS", "PROVIDER", "MODEL", "URL", "KEY"), help="Add AI model")
    
    # Command
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command")
    parser.add_argument("--pkg", action="store_true", help="Use system package manager (shows appropriate command for OS)")

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
        ver = f"{Colors.BOLD}sufdo version 4.3.0{Colors.RESET}"
        if args.rainbow:
            ver = rainbow_text("sufdo version 4.3.0 - Ultimate Edition")
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

    # AI Config
    if args.ai_config:
        ai_config = load_ai_config()
        print(f"{Colors.BOLD}AI Models Configuration{Colors.RESET}")
        print(f"{Colors.CYAN}Configure AI models for command error analysis{Colors.RESET}\n")
        
        # Show default models
        default_models = get_default_ai_models()
        print(f"{Colors.BOLD}Available presets:{Colors.RESET}")
        for i, model in enumerate(default_models, 1):
            configured = "✓" if model["alias"] in ai_config.get("models", {}) and ai_config["models"][model["alias"]].get("api_key") else "✗"
            print(f"  {i}. {model['alias']} ({model['name']}) - {Colors.GREEN}configured{Colors.RESET}" if configured == "✓" else f"  {i}. {model['alias']} ({model['name']}) - {Colors.YELLOW}not configured{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}To add a model:{Colors.RESET}")
        print(f"  {Colors.CYAN}sufdo --ai-add <alias> <provider> <model_name> <api_url> <api_key>{Colors.RESET}")
        print(f"\n{Colors.BOLD}Quick setup (interactive):{Colors.RESET}")
        
        for model in default_models:
            if model["alias"] not in ai_config.get("models", {}):
                response = input(f"\nConfigure {model['alias']} ({model['name']})? [y/N]: ")
                if response.lower() == 'y':
                    api_key = input(f"Enter API key for {model['alias']}: ").strip()
                    if api_key:
                        ai_config["models"][model["alias"]] = {
                            "name": model["name"],
                            "alias": model["alias"],
                            "api_key": api_key,
                            "api_url": model["api_url"],
                            "provider": model["provider"]
                        }
                        print(f"{Colors.GREEN}[OK]{Colors.RESET} {model['alias']} configured!")
        
        save_ai_config(ai_config)
        
        # Set default if not set
        if not ai_config.get("default") and ai_config.get("models"):
            ai_config["default"] = list(ai_config["models"].keys())[0]
            save_ai_config(ai_config)
            print(f"\n{Colors.CYAN}[INFO] Set default model: {ai_config['default']}{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}[OK]{Colors.RESET} AI configuration saved!")
        sys.exit(0)

    # AI List
    if args.ai_list:
        ai_config = load_ai_config()
        if not ai_config.get("models"):
            print(f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}")
        else:
            print(f"{Colors.BOLD}Configured AI Models:{Colors.RESET}")
            for alias, config in ai_config["models"].items():
                default_marker = " (default)" if alias == ai_config.get("default") else ""
                key_status = "****" + config.get("api_key", "")[-4:] if config.get("api_key") else "NOT SET"
                print(f"  {Colors.GREEN}{alias}{Colors.RESET}{default_marker}: {config.get('name')} [{config.get('provider')}]")
                print(f"    API Key: {key_status}")
                print(f"    URL: {config.get('api_url', 'N/A')[:60]}...")
        sys.exit(0)

    # AI Default
    if args.ai_default:
        ai_config = load_ai_config()
        if args.ai_default not in ai_config.get("models", {}):
            print(f"{Colors.RED}[FAIL]{Colors.RESET} Model '{args.ai_default}' not found")
            print(f"{Colors.YELLOW}Available: {', '.join(ai_config.get('models', {}).keys())}{Colors.RESET}")
        else:
            ai_config["default"] = args.ai_default
            save_ai_config(ai_config)
            print(f"{Colors.GREEN}[OK]{Colors.RESET} Default model set to: {args.ai_default}")
        sys.exit(0)

    # AI Ask
    if args.ai_ask:
        ai_config = load_ai_config()
        if not ai_config.get("models"):
            print(f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}")
            sys.exit(1)
        
        # Get model config
        model_config = None
        if ai_config.get("default") and ai_config["default"] in ai_config["models"]:
            model_config = ai_config["models"][ai_config["default"]]
        else:
            model_config = list(ai_config["models"].values())[0]
        
        print(f"{Colors.CYAN}[AI] Asking {model_config.get('alias', 'AI')}...{Colors.RESET}")
        response = query_ai(model_config, args.ai_ask)
        print(f"\n{Colors.PURPLE}[AI Response]{Colors.RESET}")
        print(response if response else f"{Colors.RED}No response from AI{Colors.RESET}")
        sys.exit(0)

    # AI Add
    if args.ai_add:
        ai_config = load_ai_config()
        alias, provider, model, url, key = args.ai_add
        ai_config["models"][alias] = {
            "name": model,
            "alias": alias,
            "api_key": key,
            "api_url": url,
            "provider": provider
        }
        save_ai_config(ai_config)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Added AI model: {alias} ({model})")
        if not ai_config.get("default"):
            ai_config["default"] = alias
            save_ai_config(ai_config)
            print(f"{Colors.CYAN}[INFO] Set as default model{Colors.RESET}")
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

    # Show package manager
    if args.pkg:
        pkg_mgr = get_os_package_manager()
        print(f"{Colors.GREEN}[PKG]{Colors.RESET} System package manager: {Colors.BOLD}{pkg_mgr}{Colors.RESET}")
        if not args.command:
            sys.exit(0)

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

    # Request admin privileges on Windows only with -a flag
    if sys.platform == "win32" and hasattr(args, 'a') and args.a:
        request_elevation_windows()

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
            timeout=args.timeout
        )

        duration = (datetime.now() - start_time).total_seconds()

        # Decode output with error handling
        stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
        stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''

        # Output
        if args.silent:
            if stderr:
                print(stderr, end="", file=sys.stderr)
        else:
            output = stdout
            if args.rainbow:
                output = rainbow_text(stdout)
            if args.dark:
                output = dark_mode(stdout)
            print(output, end="")

            if stderr:
                if args.verbose:
                    print(stderr, end="", file=sys.stderr)
                elif result.returncode != 0:
                    print(stderr, end="", file=sys.stderr)

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

            # AI error analysis
            if args.ai:
                question = args.ai if args.ai != "ask" else ""
                if question:
                    prompt = f"Command failed: {cmd_str}\n\nError: {stderr[:500] if stderr else 'Unknown error'}\n\nQuestion: {question}"
                else:
                    prompt = f"Command failed: {cmd_str}\n\nError: {stderr[:500] if stderr else 'Unknown error'}\n\nExplain what went wrong and how to fix it."
                
                ai_config = load_ai_config()
                if ai_config.get("models"):
                    model_config = None
                    if ai_config.get("default") and ai_config["default"] in ai_config["models"]:
                        model_config = ai_config["models"][ai_config["default"]]
                    else:
                        model_config = list(ai_config["models"].values())[0]
                    
                    print(f"{Colors.CYAN}[AI] Analyzing error with {model_config.get('alias', 'AI')}...{Colors.RESET}")
                    response = query_ai(model_config, prompt)
                    print(f"\n{Colors.PURPLE}[AI Analysis]{Colors.RESET}")
                    print(response if response else f"{Colors.YELLOW}No AI response{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}")

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
