#!/usr/bin/env python3
"""
sufdo/aliases.py - Alias management and batch execution (Optimized)

Provides command alias creation, expansion, and batch file execution.
"""

import json
import subprocess
from typing import Dict, List

from .utils import ensure_config_dir, ALIASES_FILE

# In-memory cache for aliases
_aliases_cache: Dict = None

# Frozen preset data
_ALIAS_PRESETS: Dict[str, Dict[str, str]] = {
    "git": {"gs": "git status", "ga": "git add", "gc": "git commit", "gp": "git push"},
    "docker": {"db": "docker build", "dr": "docker run", "dp": "docker ps"},
    "npm": {"ni": "npm install", "ns": "npm start", "nt": "npm test", "nb": "npm build"},
    "python": {"pi": "pip install", "pr": "python -m http.server", "pl": "python -m http.server 8080"},
}

__all__ = [
    'load_aliases', 'save_aliases', 'expand_alias', 'load_batch_file',
    'execute_batch', 'get_alias_presets'
]


def load_aliases() -> Dict:
    """
    Load user aliases from file (cached).
    
    Returns:
        Dictionary mapping alias names to commands.
    """
    global _aliases_cache
    if _aliases_cache is not None:
        return _aliases_cache
    
    if not ALIASES_FILE.exists():
        _aliases_cache = {}
    else:
        try:
            with open(ALIASES_FILE, encoding="utf-8") as f:
                _aliases_cache = json.load(f)
        except:
            _aliases_cache = {}
    return _aliases_cache


def save_aliases(aliases: Dict) -> None:
    """
    Save aliases to file.
    
    Args:
        aliases: Dictionary mapping alias names to commands.
    """
    global _aliases_cache
    _aliases_cache = aliases
    ensure_config_dir()
    with open(ALIASES_FILE, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2, ensure_ascii=False)


def expand_alias(command: List[str], aliases: Dict) -> List[str]:
    """
    Expand alias with arguments support.
    
    Args:
        command: Command as list of arguments.
        aliases: Aliases dictionary.
    
    Returns:
        Expanded command as list of arguments.
    """
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


def load_batch_file(filepath: str) -> List[str]:
    """
    Load commands from batch file.
    
    Args:
        filepath: Path to batch file.
    
    Returns:
        List of commands (excluding comments and empty lines).
    """
    with open(filepath, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def execute_batch(commands: List[str], stop_on_error: bool = True, parallel: bool = False) -> List[Dict]:
    """
    Execute batch of commands.
    
    Args:
        commands: List of command strings.
        stop_on_error: Stop on first error (default: True).
        parallel: Execute in parallel (default: False).
    
    Returns:
        List of execution results.
    """
    from .execution import execute_parallel
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


def get_alias_presets() -> Dict[str, Dict[str, str]]:
    """
    Get alias presets for common tools.
    
    Returns:
        Dictionary of preset name to aliases mapping.
    """
    return _ALIAS_PRESETS
