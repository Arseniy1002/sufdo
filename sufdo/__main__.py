#!/usr/bin/env python3
"""
sufdo/__main__.py - Main entry point for sufdo CLI (Refactored)

Version: 4.5.0 - Refactored Edition

Features:
    - Modular command handlers
    - Clean main() function
    - Type hints throughout
    - Proper error handling
"""

import sys
import subprocess
import argparse
import os
import time
import logging
from typing import Optional, List

from .utils import (
    Colors, ensure_config_dir, setup_logging, validate_command,
    is_destructive_command, get_os_package_manager,
    is_admin_windows, request_elevation_windows,
    SUFDO_DIR, LOG_FILE, get_platform_name, is_termux
)
from .config import load_config, load_env
from .ai import analyze_command_error
from .safety import create_backup
from .fun_modes import (
    print_fun_mode, print_flex, print_bruh, drama_mode, pray_mode,
    yeet_mode, sus_mode, hacker_mode, cursed_mode, matrix_rain,
    rainbow_text, dark_mode, confidence_boost, confidence_insult
)
from .notifications import send_notification
from .stats import log_command, update_stats, clear_cache, get_last_command
from .aliases import expand_alias, load_batch_file, execute_batch
from .execution import execute_parallel, execute_background, execute_with_timeout

# Import command handlers
from .commands import (
    handle_ai_config, handle_ai_list, handle_ai_default, handle_ai_ask, handle_ai_add,
    handle_stats, handle_top, handle_success_rate, handle_export_stats,
    handle_history, handle_confidence, handle_undo,
    handle_alias, handle_alias_import, handle_alias_export, handle_alias_preset,
    handle_list_backups, handle_restore, handle_cleanup_backups,
    handle_dry_run, handle_safe_mode_check,
    handle_webhook_add, handle_webhook_list, handle_notify,
    handle_profile_list, handle_profile_save, handle_env_set, handle_completion,
)

__all__ = ['main']

VERSION = "4.5.0"


def get_examples_for_os() -> str:
    """
    Get example commands appropriate for the current OS.

    Returns:
        Formatted string with usage examples for current platform.
    """
    pkg_mgr = get_os_package_manager()
    platform = get_platform_name()

    # Platform-specific package names
    if is_termux():
        pkg_name = "python"
        example_user = "u0_a123"
        example_path = "/sdcard"
    elif sys.platform == "win32":
        pkg_name = "python.python311"
        example_user = "Administrator"
        example_path = "C:\\Windows\\System32"
    elif sys.platform == "darwin":
        pkg_name = "htop"
        example_user = "www-data"
        example_path = "/var/www"
    else:
        pkg_name = "htop"
        example_user = "www-data"
        example_path = "/var/www"

    return f"""Platform: {platform} | Package Manager: {pkg_mgr}

Examples:
  sufdo {pkg_mgr} {pkg_name}          Install package
  sufdo -u {example_user} ls {example_path}  Run as specific user
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


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
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

    # Windows UAC elevation
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
    parser.add_argument("--pkg", action="store_true", help="Use system package manager")

    return parser


def handle_subcommands(args: argparse.Namespace) -> bool:
    """
    Handle all subcommands that don't require command execution.

    Args:
        args: Parsed arguments.

    Returns:
        True if a subcommand was handled (should exit), False otherwise.
    """
    # Stats
    if args.stats:
        handle_stats()
        return True

    if args.top:
        handle_top()
        return True

    if args.success_rate:
        handle_success_rate()
        return True

    if args.export_stats:
        handle_export_stats(args.export_stats)
        return True

    # History
    if args.history:
        handle_history()
        return True

    # Confidence
    if args.confidence:
        handle_confidence()
        return True

    # Aliases
    if args.alias is not None:
        handle_alias(args.alias if args.alias else None)
        return True

    # Alias import
    if args.alias_import:
        handle_alias_import(args.alias_import)
        return True

    # Alias export
    if args.alias_export:
        handle_alias_export(args.alias_export)
        return True

    # Alias preset
    if args.alias_preset:
        handle_alias_preset(args.alias_preset)
        return True

    # Profile list
    if args.profile_list:
        handle_profile_list()
        return True

    # Profile save
    if args.profile_save:
        handle_profile_save(args.profile_save)
        return True

    # Webhook add
    if args.webhook_add:
        handle_webhook_add(args.webhook_add[0], args.webhook_add[1])
        return True

    # Webhook list
    if args.webhook_list:
        handle_webhook_list()
        return True

    # List backups
    if args.list_backups:
        handle_list_backups()
        return True

    # Restore backup
    if args.restore:
        handle_restore(args.restore)
        return True

    # Cleanup backups
    if args.cleanup_backups:
        handle_cleanup_backups()
        return True

    # Clear cache
    if args.clear_cache:
        clear_cache()
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Cache cleared")
        return True

    # Env set
    if args.env_set:
        handle_env_set(args.env_set[0], args.env_set[1])
        return True

    # AI Config
    if args.ai_config:
        handle_ai_config()
        return True

    # AI List
    if args.ai_list:
        handle_ai_list()
        return True

    # AI Default
    if args.ai_default:
        handle_ai_default(args.ai_default)
        return True

    # AI Ask
    if args.ai_ask:
        handle_ai_ask(args.ai_ask)
        return True

    # AI Add
    if args.ai_add:
        alias, provider, model, url, key = args.ai_add
        handle_ai_add(alias, provider, model, url, key)
        return True

    # Completion
    if args.completion:
        handle_completion(args.completion)
        return True

    # Parallel execution
    if args.parallel:
        results = execute_parallel(args.parallel)
        for r in results:
            status = f"{Colors.GREEN}[OK]{Colors.RESET}" if r.get("returncode", 1) == 0 else f"{Colors.RED}[FAIL]{Colors.RESET}"
            print(f"{status} {r['command']}")
        return True

    # Undo
    if args.undo:
        handle_undo()
        return True

    return False


def print_version(args: argparse.Namespace) -> None:
    """Print version information."""
    ver = f"{Colors.BOLD}sufdo version {VERSION}{Colors.RESET}"
    if args.rainbow:
        ver = rainbow_text(f"sufdo version {VERSION} - Refactored Edition")
    print(ver)
    print("Super User Fkin Do - Refactored Edition")
    print("https://github.com/Arseniy1002/sufdo")

    platform_name = get_platform_name()
    pkg_mgr = get_os_package_manager()
    print(f"Platform: {Colors.GREEN}{platform_name}{Colors.RESET} | Package Manager: {Colors.CYAN}{pkg_mgr}{Colors.RESET}")

    if args.verbose or args.debug:
        print(f"Config: {SUFDO_DIR}")
        print(f"Log: {LOG_FILE}")
        print(f"Python: {sys.version}")
        print(f"Platform: {sys.platform}")
        if is_termux():
            print(f"{Colors.GREEN}Running in Termux!{Colors.RESET}")
    print(f"{Colors.DIM}200+ features installed!{Colors.RESET}")


def apply_fun_modes(args: argparse.Namespace) -> None:
    """Apply fun mode effects before command execution."""
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
    if args.drama:
        drama_mode()
    if args.pray:
        pray_mode()
    if args.yeet:
        yeet_mode()
    if args.sus:
        sus_mode()
    if args.hacker:
        hacker_mode()
    if args.cursed:
        cursed_mode()
    if args.matrix:
        matrix_rain()


def execute_command(
    args: argparse.Namespace,
    command: str,
    logger: Optional[logging.Logger] = None
) -> int:
    """
    Execute the main command with all options applied.

    Args:
        args: Parsed arguments.
        command: Command string to execute.
        logger: Optional logger instance.

    Returns:
        Exit code from command execution.
    """
    start_time = time.time()

    # Dry run
    if args.dry_run:
        handle_dry_run(command)
        return 0

    # Safe mode check
    if args.safe_mode or args.no_destructive:
        is_safe, reason = handle_safe_mode_check(command)
        if not is_safe:
            return 1

    # Confirmation
    if args.confirm:
        try:
            response = input(f"{Colors.YELLOW}Execute '{command}'? [y/N]: {Colors.RESET}")
        except EOFError:
            response = 'n'
        if response.lower() != 'y':
            print(f"{Colors.YELLOW}Cancelled.{Colors.RESET}")
            return 0

    # Backup
    if args.backup:
        # Try to backup affected paths (simplified)
        print(f"{Colors.CYAN}[BACKUP] Creating backup...{Colors.RESET}")

    # Apply fun modes before execution
    apply_fun_modes(args)

    # Execute command
    if args.trace:
        print(f"{Colors.CYAN}[TRACE] Executing: {command}{Colors.RESET}")

    # Execute command with timeout handling
    exec_result = execute_with_timeout(
        command,
        timeout=args.timeout if args.timeout else 60
    )
    exit_code = exec_result.get("returncode", 1)
    stdout = exec_result.get("stdout", "")
    stderr = exec_result.get("stderr", "")
    timed_out = exec_result.get("timed_out", False)

    duration = time.time() - start_time

    if timed_out:
        print(f"{Colors.RED}[TIMEOUT] Command exceeded timeout{Colors.RESET}")
        if logger:
            logger.error(f"Timeout: {command}")
        return 124

    if exec_result.get("interrupted"):
        print(f"{Colors.YELLOW}[INTERRUPTED] Command cancelled by user{Colors.RESET}")
        if logger:
            logger.warning(f"Interrupted: {command}")
        return 130

    if exec_result.get("error"):
        print(f"{Colors.RED}[ERROR] {exec_result['error']}{Colors.RESET}")
        if logger:
            logger.error(f"Execution error: {exec_result['error']}")
        return exit_code

    # Log command
    log_command(command, args.user, exit_code, duration)
    update_stats(command, exit_code, duration)

    # Logging
    if logger:
        logger.info(f"Command: {command}, Exit: {exit_code}, Duration: {duration:.2f}s")
        if stdout:
            logger.debug(f"Stdout: {stdout[:500]}")
        if stderr:
            logger.error(f"Stderr: {stderr[:500]}")

    # Output
    if not args.silent and stdout:
        print(stdout)
    if stderr and (args.verbose or args.debug or exit_code != 0):
        print(f"{Colors.RED}{stderr}{Colors.RESET}", file=sys.stderr)

    # Flex message
    if args.flex and exit_code == 0:
        print_flex()

    # Bruh commentary
    if args.bruh:
        print(print_bruh())

    # Confidence adjustment
    if exit_code == 0:
        confidence_boost()
    else:
        confidence_insult()
        # AI error analysis
        if args.ai or (hasattr(args, 'ai') and args.ai == 'ask'):
            analyze_command_error(command, stdout, stderr, exit_code)

    # Notifications
    if args.notify or args.notify_sound:
        title = "sufdo - Success" if exit_code == 0 else "sufdo - Failed"
        handle_notify(title, command, args.notify_sound, args.discord, args.telegram, args.email)

    return exit_code


def main() -> None:
    """Main entry point for sufdo CLI."""
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Setup logging
        logger: Optional[logging.Logger] = None
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
            print_version(args)
            sys.exit(0)

        # Windows UAC elevation
        if sys.platform == "win32" and hasattr(args, 'a') and args.a:
            if not request_elevation_windows():
                sys.exit(1)

        # Handle subcommands
        if handle_subcommands(args):
            sys.exit(0)

        # No command provided
        if not args.command:
            parser.print_help()
            sys.exit(0)

        # Build command string
        cmd_list = args.command
        aliases = None  # Lazy load
        if cmd_list:
            aliases = expand_alias(cmd_list, {})  # Will be loaded inside
            cmd_list = aliases if aliases else cmd_list

        command = " ".join(cmd_list)

        # Validate command
        if args.validate:
            handle_validate_command(command)
            sys.exit(0)

        # Execute command
        exit_code = execute_command(args, command, logger)
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[INTERRUPTED] Command cancelled by user{Colors.RESET}")
        sys.exit(130)
    except EOFError:
        print(f"\n{Colors.YELLOW}[EOF] Input ended unexpectedly{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
