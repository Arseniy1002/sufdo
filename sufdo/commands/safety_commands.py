#!/usr/bin/env python3
"""
sufdo/commands/safety_commands.py - Safety and backup command handlers

Handles backup, restore, cleanup, dry-run, and safe mode commands.
"""

from typing import List, Tuple, Optional

from ..safety import create_backup, list_backups, restore_backup, cleanup_old_backups
from ..utils import Colors, is_destructive_command, validate_command


def handle_list_backups() -> None:
    """Handle --list-backups: List all backups."""
    backups = list_backups()
    if backups:
        print(f"{Colors.BOLD}Backups:{Colors.RESET}")
        for b in backups:
            print(f"  {b}")
    else:
        print(f"{Colors.YELLOW}No backups.{Colors.RESET}")


def handle_restore(backup_name: str) -> bool:
    """
    Handle --restore: Restore from backup.

    Args:
        backup_name: Name of backup to restore.

    Returns:
        True if restored successfully, False otherwise.
    """
    if restore_backup(backup_name):
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Restored {backup_name}")
        return True
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Could not restore {backup_name}")
        return False


def handle_cleanup_backups(days: int = 30) -> None:
    """
    Handle --cleanup-backups: Clean up old backups.

    Args:
        days: Age threshold in days (default: 30).
    """
    cleanup_old_backups(days)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Cleaned up backups older than {days} days")


def handle_dry_run(command: str) -> None:
    """
    Handle --dry-run: Preview command without execution.

    Args:
        command: Command to preview.
    """
    print(f"{Colors.CYAN}[DRY RUN] Would execute:{Colors.RESET}")
    print(f"  {Colors.YELLOW}{command}{Colors.RESET}")

    # Validate command
    valid, msg = validate_command(command)
    if not valid:
        print(f"  {Colors.RED}{msg}{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}{msg}{Colors.RESET}")

    # Check if destructive
    if is_destructive_command(command):
        print(f"  {Colors.RED}[WARNING] This command is DESTRUCTIVE!{Colors.RESET}")


def handle_safe_mode_check(command: str) -> Tuple[bool, Optional[str]]:
    """
    Handle --safe-mode: Check if command is safe to execute.

    Args:
        command: Command to check.

    Returns:
        Tuple of (is_safe, block_reason) - is_safe is False if blocked.
    """
    if is_destructive_command(command):
        print(f"{Colors.RED}[SAFE MODE] Blocked destructive command: {command}{Colors.RESET}")
        return False, "Destructive command detected"

    # Additional safety checks could be added here
    return True, None


def handle_validate_command(command: str) -> bool:
    """
    Handle --validate: Validate command exists in PATH.

    Args:
        command: Command to validate.

    Returns:
        True if valid, False otherwise.
    """
    valid, msg = validate_command(command)
    if valid:
        print(f"{Colors.GREEN}[VALID] {msg}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[INVALID] {msg}{Colors.RESET}")
    return valid
