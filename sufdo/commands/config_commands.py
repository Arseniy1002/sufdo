#!/usr/bin/env python3
"""
sufdo/commands/config_commands.py - Configuration command handlers

Handles profiles, environment variables, and shell completion.
"""

from typing import Dict, Optional

from ..config import load_config, save_config, load_env, save_env, load_profiles, save_profile
from ..utils import Colors


def handle_profile_list() -> None:
    """Handle --profile-list: List all profiles."""
    profiles = load_profiles()
    print(f"{Colors.BOLD}Profiles:{Colors.RESET}")
    for name in profiles:
        print(f"  {Colors.GREEN}{name}{Colors.RESET}")


def handle_profile_save(name: str, config: Optional[Dict] = None) -> None:
    """
    Handle --profile-save: Save current config as profile.

    Args:
        name: Profile name.
        config: Config to save (uses current config if None).
    """
    if config is None:
        config = load_config()
    save_profile(name, config)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Profile '{name}' saved")


def handle_env_set(key: str, value: str) -> None:
    """
    Handle --env-set: Set environment variable.

    Args:
        key: Environment variable name.
        value: Environment variable value.
    """
    env = load_env()
    env[key] = value
    save_env(env)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {key}={value}")


def handle_env_list() -> None:
    """Handle listing environment variables."""
    env = load_env()
    if env:
        print(f"{Colors.BOLD}Environment Variables:{Colors.RESET}")
        for key, value in env.items():
            print(f"  {Colors.GREEN}{key}{Colors.RESET}={Colors.CYAN}{value}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No environment variables set.{Colors.RESET}")


def handle_completion(shell: str) -> None:
    """
    Handle --completion: Generate shell completion script.

    Args:
        shell: Shell type (bash, zsh, fish).
    """
    sufdo_flags = (
        "--help --version --silent --verbose --stats --history --last "
        "--alias --flex --timeout --dry-run --confirm --safe-mode --backup "
        "--log --notify --discord --telegram --pirate --cowboy --yoda "
        "--rainbow --combo"
    )

    if shell == "bash":
        print(f'complete -W "{sufdo_flags}" sufdo')
    elif shell == "zsh":
        print(f"""#compdef sufdo
_sufdo_flags=({sufdo_flags})
compadd $_sufdo_flags""")
    elif shell == "fish":
        print(f'complete -c sufdo -l help -l version -l silent -l verbose -l stats -l history -l last -l alias -l flex -l timeout -l dry-run -l confirm -l safe-mode -l backup -l log -l notify -l discord -l telegram -l pirate -l cowboy -l yoda -l rainbow -l combo')
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Unknown shell: {shell}")
