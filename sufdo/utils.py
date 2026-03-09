#!/usr/bin/env python3
"""
sufdo/utils.py - Utility functions and constants (Optimized)

Provides core utilities including path management, colors, logging,
and platform-specific helper functions.
"""

import sys
import os
import logging
import shutil
from pathlib import Path
from typing import Tuple

# Enable ANSI colors on Windows
if sys.platform == "win32":
    try:
        from ctypes import windll
        kernel32 = windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

# Config paths - computed once at module load
SUFDO_DIR: Path = Path.home() / ".sufdo"
HISTORY_FILE: Path = SUFDO_DIR / "history.json"
ALIASES_FILE: Path = SUFDO_DIR / "aliases.json"
CONFIDENCE_FILE: Path = SUFDO_DIR / "confidence.json"
LOG_FILE: Path = SUFDO_DIR / "sufdo.log"
CONFIG_FILE: Path = SUFDO_DIR / "config.json"
STATS_FILE: Path = SUFDO_DIR / "stats.json"
CACHE_FILE: Path = SUFDO_DIR / "cache.json"
BACKUP_DIR: Path = SUFDO_DIR / "backups"
PROFILES_DIR: Path = SUFDO_DIR / "profiles"
ENV_FILE: Path = SUFDO_DIR / ".env"
WEBHOOKS_FILE: Path = SUFDO_DIR / "webhooks.json"
AI_CONFIG_FILE: Path = SUFDO_DIR / "ai_models.json"


class Colors:
    """ANSI color codes for terminal output."""
    __slots__ = ()  # Prevent instance dict creation
    RED: str = "\033[91m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    PURPLE: str = "\033[95m"
    CYAN: str = "\033[96m"
    WHITE: str = "\033[97m"
    RESET: str = "\033[0m"
    BOLD: str = "\033[1m"
    DIM: str = "\033[2m"
    BLINK: str = "\033[5m"
    REVERSE: str = "\033[7m"
    ORANGE: str = "\033[33m"
    PINK: str = "\033[95m"


# Destructive commands blacklist - frozen set for faster lookup
DESTRUCTIVE_COMMANDS: frozenset = frozenset([
    "rm -rf /", "rm -rf /*", "dd if=/dev/zero", "mkfs",
    "fdisk", "format", "del /s /q", "rmdir /s",
    "shutdown -a", "chmod -R 777 /", "chown -R root:root /",
])

# Pre-computed color mappings for fun modes
FUN_MODE_COLORS: dict = {
    "pirate": Colors.YELLOW, "cowboy": Colors.YELLOW, "yoda": Colors.GREEN,
    "shakespeare": Colors.PURPLE, "anime": Colors.CYAN, "russian": Colors.RED,
}

__all__ = [
    'SUFDO_DIR', 'HISTORY_FILE', 'ALIASES_FILE', 'CONFIDENCE_FILE',
    'LOG_FILE', 'CONFIG_FILE', 'STATS_FILE', 'CACHE_FILE',
    'BACKUP_DIR', 'PROFILES_DIR', 'ENV_FILE', 'WEBHOOKS_FILE', 'AI_CONFIG_FILE',
    'Colors', 'DESTRUCTIVE_COMMANDS', 'FUN_MODE_COLORS',
    'ensure_config_dir', 'setup_logging', 'validate_command',
    'is_destructive_command', 'get_os_package_manager',
    'is_admin_windows', 'request_elevation_windows'
]


def ensure_config_dir() -> None:
    """Create config directory if it doesn't exist."""
    SUFDO_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging to file.
    
    Args:
        log_file: Path to log file. Defaults to LOG_FILE.
        level: Logging level. Defaults to logging.INFO.
    
    Returns:
        Logger instance configured for sufdo.
    """
    ensure_config_dir()
    log_path = log_file or LOG_FILE

    logging.basicConfig(
        filename=log_path,
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode='a',
        force=True
    )
    return logging.getLogger('sufdo')


def validate_command(command: str) -> Tuple[bool, str]:
    """
    Validate command exists in PATH.
    
    Args:
        command: Command string to validate.
    
    Returns:
        Tuple of (is_valid, message).
    """
    cmd = command.split()[0]
    if not shutil.which(cmd):
        return False, f"Command '{cmd}' not found in PATH"
    return True, "OK"


def is_destructive_command(command: str) -> bool:
    """
    Check if command is in the destructive blacklist.
    
    Args:
        command: Command string to check.
    
    Returns:
        True if command is destructive, False otherwise.
    """
    cmd_lower = command.lower()
    return any(destructive in cmd_lower for destructive in DESTRUCTIVE_COMMANDS)


def get_os_package_manager() -> str:
    """
    Get the appropriate package manager command for the current OS.
    
    Returns:
        Package manager command (e.g., 'apt install', 'winget install').
    """
    if sys.platform == "win32":
        return "winget install"
    elif sys.platform == "darwin":
        return "brew install"
    
    # Linux - cache result in function attribute
    if hasattr(get_os_package_manager, "_cached"):
        return get_os_package_manager._cached
    
    pkg_mgr = "apt install"  # default
    
    if os.path.exists("/etc/arch-release"):
        pkg_mgr = "pacman -S"
    elif os.path.exists("/etc/debian_version") or os.path.exists("/etc/apt/sources.list"):
        pkg_mgr = "apt install"
    elif os.path.exists("/etc/redhat-release") or os.path.exists("/etc/fedora-release"):
        pkg_mgr = "dnf install"
    elif os.path.exists("/etc/alpine-release"):
        pkg_mgr = "apk add"
    elif os.path.exists("/etc/os-release"):
        try:
            with open("/etc/os-release", encoding="utf-8") as f:
                content = f.read().lower()
                if "arch" in content:
                    pkg_mgr = "pacman -S"
                elif "debian" in content or "ubuntu" in content:
                    pkg_mgr = "apt install"
                elif "fedora" in content:
                    pkg_mgr = "dnf install"
                elif "alpine" in content:
                    pkg_mgr = "apk add"
        except:
            pass
    
    get_os_package_manager._cached = pkg_mgr
    return pkg_mgr


def is_admin_windows() -> bool:
    """
    Check if running as administrator on Windows.
    
    Returns:
        True if running as admin, False otherwise.
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def request_elevation_windows() -> bool:
    """
    Request elevation on Windows via UAC prompt.
    
    Returns:
        True if already admin or elevation successful, False if cancelled.
    """
    if sys.platform != "win32":
        return True

    if is_admin_windows():
        return True

    print(f"{Colors.YELLOW}[SUDO] Requesting administrator privileges...{Colors.RESET}")

    try:
        import ctypes
        script_path = os.path.abspath(sys.argv[0]).replace("'", "''")
        args_escaped = ' '.join(sys.argv[1:]).replace("'", "''")
        python_exec = sys.executable.replace("'", "''")

        ps_command = (
            f"Write-Host '[SUDO] Running elevated...' -ForegroundColor Yellow; "
            f"& '{python_exec}' '{script_path}' {args_escaped}; "
            f"Write-Host ''; "
            f"Write-Host '[SUDO] Command complete.' -ForegroundColor Green"
        )

        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", "powershell",
            f"-Command \"{ps_command}\"", None, 1
        )

        if result > 32:
            print(f"{Colors.GREEN}[SUDO] Elevated window opened. Command will execute there.{Colors.RESET}")
            print(f"{Colors.GREEN}[SUDO] This window remains open with your history.{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}[SUDO] UAC cancelled or failed (error: {result}){Colors.RESET}")
            return False

    except Exception as e:
        print(f"{Colors.RED}[SUDO] Elevation error: {e}{Colors.RESET}")
        return False
