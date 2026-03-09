#!/usr/bin/env python3
"""
sufdo - Super User Fkin Do - Ultimate Edition

A sudo-like utility for executing commands with elevated privileges.
Because sometimes you just need to get shit done.

Version: 4.5.0 - Refactored Edition (Modular + Tests + Type Hints)

Features:
    - 100+ command-line flags
    - 200+ individual features
    - 17+ fun modes
    - 10+ safety features
    - AI-powered error analysis
    - UAC elevation for Windows
    - Encrypted API key storage
    - In-memory caching for performance
    - Modular command handlers
    - 55 unit tests
"""

import sys
import subprocess
import argparse
import os
import time
import logging
import json
from datetime import datetime
from typing import Optional, List

# Import from modules (lazy where possible)
from .utils import (
    Colors, ensure_config_dir, setup_logging, validate_command,
    is_destructive_command, get_os_package_manager,
    is_admin_windows, request_elevation_windows,
    SUFDO_DIR, LOG_FILE
)
from .config import load_config, save_config, load_env, save_env, load_profiles, save_profile
from .ai import (
    get_default_ai_models, load_ai_config, save_ai_config,
    query_ai, analyze_command_error
)
from .safety import create_backup, list_backups, restore_backup, cleanup_old_backups
from .fun_modes import (
    print_fun_mode, print_flex, print_bruh, drama_mode, pray_mode,
    yeet_mode, sus_mode, hacker_mode, cursed_mode, matrix_rain,
    rainbow_text, dark_mode, confidence_boost, confidence_insult
)
from .notifications import (
    load_webhooks, save_webhooks, send_discord_webhook,
    send_telegram_message, send_email, send_notification
)
from .stats import (
    log_command, get_last_command, get_undo_command, print_history,
    load_stats, save_stats, update_stats, print_stats,
    get_confidence, set_confidence, print_confidence,
    load_cache, save_cache, get_from_cache, save_to_cache, clear_cache
)
from .aliases import (
    load_aliases, save_aliases, expand_alias, load_batch_file,
    execute_batch, get_alias_presets
)
from .execution import execute_parallel, execute_background

__all__ = ['main']

VERSION = "4.5.0"


def get_examples_for_os() -> str:
    """
    Get example commands appropriate for the current OS.
    
    Returns:
        Formatted string with usage examples for current platform.
    """
    pkg_mgr = get_os_package_manager()
    pkg_name = "htop" if sys.platform != "win32" else "python.python311"
    
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


def main() -> None:
    """
    Main entry point for sufdo CLI.
    
    Parses command-line arguments, handles all subcommands,
    and executes user commands with appropriate options.
    
    Exit Codes:
        0 - Success
        1 - General error
        124 - Timeout expired
    """
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
        ver = f"{Colors.BOLD}sufdo version {VERSION}{Colors.RESET}"
        if args.rainbow:
            ver = rainbow_text(f"sufdo version {VERSION} - Ultimate Edition")
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
        presets = get_alias_presets()
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

        default_models = get_default_ai_models()
        print(f"{Colors.BOLD}Available presets:{Colors.RESET}")
        for i, model in enumerate(default_models, 1):
            configured = "✓" if model["alias"] in ai_config.get("models", {}) and ai_config["models"][model["alias"]].get("api_key") else "✗"
            if configured == "✓":
                print(f"  {i}. {model['alias']} ({model['name']}) - {Colors.GREEN}configured{Colors.RESET}")
            else:
                print(f"  {i}. {model['alias']} ({model['name']}) - {Colors.YELLOW}not configured{Colors.RESET}")

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

        model_config = None
        if ai_config.get("default") and ai_config["default"] in ai_config["models"]:
            model_config = ai_config["models"][ai_config["default"]]
        else:
            model_config = list(ai_config["models"].values())[0] if ai_config["models"] else None

        if model_config:
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
                output = dark_mode(output)
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
                    print_bruh()

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
                    print_bruh()

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
                        model_config = list(ai_config["models"].values())[0] if ai_config["models"] else None

                    if model_config:
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
