#!/usr/bin/env python3
"""
sufdo/stats.py - Statistics, history, cache, confidence management (Optimized)

Provides command history tracking, usage statistics, caching, and confidence level management.
All data is cached in memory to minimize file I/O operations.
"""

import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from .utils import ensure_config_dir, Colors
from .utils import HISTORY_FILE, STATS_FILE, CACHE_FILE, CONFIDENCE_FILE

# In-memory caches to avoid repeated file reads
_cache: Dict[str, Any] = {
    'stats': None,
    'confidence': None,
    'history': None,
    'cache': None,
}


def _load_json_file(filepath, default):
    """
    Load JSON file with error handling.
    
    Args:
        filepath: Path to JSON file.
        default: Default value if file doesn't exist or error occurs.
    
    Returns:
        Loaded data or default value.
    """
    if not filepath.exists():
        return default
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def _save_json_file(filepath, data) -> None:
    """
    Save data to JSON file with error handling.
    
    Args:
        filepath: Path to JSON file.
        data: Data to save.
    """
    ensure_config_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============ History ============

def log_command(command: str, user: str, exit_code: int, duration: float) -> None:
    """
    Log command execution to history file.
    
    Args:
        command: Executed command string.
        user: User who ran the command.
        exit_code: Command exit code.
        duration: Execution duration in seconds.
    """
    history = _cache['history']
    if history is None:
        history = _load_json_file(HISTORY_FILE, [])
    
    history.append({
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "user": user,
        "exit_code": exit_code,
        "duration": duration
    })
    
    history = history[-100:]  # Keep last 100
    _cache['history'] = history
    _save_json_file(HISTORY_FILE, history)


def get_last_command() -> Optional[str]:
    """
    Get the last executed command from history.
    
    Returns:
        Last command string or None if no history.
    """
    history = _cache['history']
    if history is None:
        history = _load_json_file(HISTORY_FILE, [])
        _cache['history'] = history
    
    if history:
        return history[-1]["command"]
    return None


def get_undo_command() -> Optional[Dict]:
    """
    Get the last command entry for undo operation.
    
    Returns:
        Last command entry dict or None if no history.
    """
    history = _cache['history']
    if history is None:
        history = _load_json_file(HISTORY_FILE, [])
        _cache['history'] = history
    
    if history:
        return history[-1]
    return None


def print_history() -> None:
    """Print command history to stdout."""
    history = _cache['history']
    if history is None:
        history = _load_json_file(HISTORY_FILE, [])
        _cache['history'] = history
    
    if not history:
        print(f"{Colors.YELLOW}No history yet. Go break something!{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Command History:{Colors.RESET}\n")
    for i, entry in enumerate(history[-10:], 1):
        status = "[OK]" if entry["exit_code"] == 0 else "[FAIL]"
        print(f"  {i}. {status} {entry['command']}")
        print(f"     {Colors.CYAN}{entry['timestamp']}{Colors.RESET} | user: {entry['user']} | exit: {entry['exit_code']} | {entry['duration']:.2f}s")


# ============ Statistics ============

def load_stats() -> Dict:
    """
    Load usage statistics (cached).
    
    Returns:
        Statistics dictionary with command counts and timings.
    """
    if _cache['stats'] is None:
        _cache['stats'] = _load_json_file(STATS_FILE, {"total": 0, "success": 0, "failure": 0, "commands": {}, "times": {}})
    return _cache['stats']


def save_stats(stats: Dict) -> None:
    """
    Save usage statistics to file.
    
    Args:
        stats: Statistics dictionary to save.
    """
    _cache['stats'] = stats
    _save_json_file(STATS_FILE, stats)


def update_stats(command: str, exit_code: int, duration: float) -> None:
    """
    Update usage statistics after command execution.
    
    Args:
        command: Executed command string.
        exit_code: Command exit code.
        duration: Execution duration in seconds.
    """
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


def print_stats() -> None:
    """Print usage statistics to stdout."""
    stats = load_stats()

    print(f"{Colors.BOLD}Usage Statistics:{Colors.RESET}\n")
    print(f"  Total commands: {stats.get('total', 0)}")
    print(f"  Successful: {stats.get('success', 0)}")
    print(f"  Failed: {stats.get('failure', 0)}")

    total = stats.get('total', 0)
    success = stats.get('success', 0)
    if total > 0:
        print(f"  Success rate: {success / total * 100:.1f}%")

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


# ============ Confidence ============

def get_confidence() -> int:
    """
    Get user's current confidence level (cached).
    
    Returns:
        Confidence level percentage (0-100).
    """
    if _cache['confidence'] is None:
        data = _load_json_file(CONFIDENCE_FILE, {"level": 100})
        _cache['confidence'] = data.get("level", 100)
    return _cache['confidence']


def set_confidence(level: int) -> None:
    """
    Set confidence level.
    
    Args:
        level: Confidence level percentage (0-100).
    """
    _cache['confidence'] = level
    _save_json_file(CONFIDENCE_FILE, {"level": level})


def print_confidence() -> None:
    """Print current confidence level with visual bar."""
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


# ============ Cache ============

def load_cache() -> Dict:
    """
    Load command cache (cached).
    
    Returns:
        Cache dictionary with stored command outputs.
    """
    if _cache['cache'] is None:
        _cache['cache'] = _load_json_file(CACHE_FILE, {})
    return _cache['cache']


def save_cache(cache: Dict) -> None:
    """
    Save command cache to file.
    
    Args:
        cache: Cache dictionary to save.
    """
    _cache['cache'] = cache
    _save_json_file(CACHE_FILE, cache)


def get_cache_key(command: str) -> str:
    """
    Generate MD5 cache key for command.
    
    Args:
        command: Command string to hash.
    
    Returns:
        MD5 hash string.
    """
    return hashlib.md5(command.encode()).hexdigest()


def get_from_cache(command: str, ttl: int = 300) -> Optional[Any]:
    """
    Get command output from cache if not expired.
    
    Args:
        command: Command string to lookup.
        ttl: Time to live in seconds (default: 300).
    
    Returns:
        Cached output or None if not found/expired.
    """
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


def save_to_cache(command: str, output: Any, ttl: int = 300) -> None:
    """
    Save command output to cache.
    
    Args:
        command: Command string.
        output: Output to cache.
        ttl: Time to live in seconds (default: 300).
    """
    cache = load_cache()
    key = get_cache_key(command)
    cache[key] = {
        "output": output,
        "timestamp": time.time(),
        "ttl": ttl
    }
    save_cache(cache)


def clear_cache() -> None:
    """Clear all cached data."""
    _cache['cache'] = {}
    _save_json_file(CACHE_FILE, {})
