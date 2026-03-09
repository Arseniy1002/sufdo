#!/usr/bin/env python3
"""
sufdo/commands/stats_commands.py - Statistics and history command handlers

Handles stats, history, confidence, and undo commands.
"""

import json
from typing import Optional, Dict

from ..stats import (
    load_stats, print_stats, print_history, get_last_command,
    get_undo_command, get_confidence, print_confidence
)
from ..utils import Colors


def handle_stats() -> None:
    """Handle --stats: Print usage statistics."""
    print_stats()


def handle_top() -> None:
    """Handle --top: Print top commands."""
    stats = load_stats()
    commands = stats.get('commands', {})
    if not commands:
        print(f"{Colors.YELLOW}No commands executed yet.{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Top Commands:{Colors.RESET}")
    sorted_cmds = sorted(commands.items(), key=lambda x: x[1], reverse=True)[:5]
    for cmd, count in sorted_cmds:
        print(f"  {cmd}: {count} times")


def handle_success_rate() -> None:
    """Handle --success-rate: Print success rate."""
    stats = load_stats()
    total = stats.get('total', 0)
    success = stats.get('success', 0)
    if total > 0:
        rate = success / total * 100
        print(f"Success rate: {rate:.1f}% ({success}/{total})")
    else:
        print("No commands executed yet")


def handle_export_stats(filepath: str) -> None:
    """
    Handle --export-stats: Export statistics to JSON file.

    Args:
        filepath: Path to export stats to.
    """
    stats = load_stats()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Stats exported to {filepath}")
    except IOError as e:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Could not export stats: {e}")


def handle_history() -> None:
    """Handle --history: Print command history."""
    print_history()


def handle_confidence() -> None:
    """Handle --confidence: Print confidence level."""
    print_confidence()


def handle_undo() -> Optional[Dict]:
    """
    Handle --undo: Get last command for undo operation.

    Returns:
        Last command entry dict or None if no history.
    """
    last_entry = get_undo_command()
    if not last_entry:
        print(f"{Colors.YELLOW}No commands to undo.{Colors.RESET}")
        return None

    print(f"{Colors.CYAN}[UNDO] Last command: {last_entry['command']}{Colors.RESET}")
    print(f"{Colors.CYAN}[UNDO] Exit code: {last_entry['exit_code']}{Colors.RESET}")
    print(f"{Colors.CYAN}[UNDO] Duration: {last_entry['duration']:.2f}s{Colors.RESET}")
    return last_entry


def get_last_command_str() -> Optional[str]:
    """
    Get last command as string.

    Returns:
        Last command string or None.
    """
    return get_last_command()
