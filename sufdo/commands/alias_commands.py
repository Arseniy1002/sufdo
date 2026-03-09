#!/usr/bin/env python3
"""
sufdo/commands/alias_commands.py - Alias command handlers

Handles alias creation, import, export, and preset commands.
"""

import json
from typing import Dict, List, Optional

from ..aliases import load_aliases, save_aliases, get_alias_presets
from ..utils import Colors


def handle_alias(aliases_to_create: Optional[List[str]] = None) -> None:
    """
    Handle --alias: List or create aliases.

    Args:
        aliases_to_create: List of alias definitions (name=command) or None to list.
    """
    aliases = load_aliases()

    if aliases_to_create is None:
        # List aliases
        if aliases:
            print(f"{Colors.BOLD}Aliases:{Colors.RESET}")
            for name, cmd in aliases.items():
                print(f"  {Colors.GREEN}{name}{Colors.RESET} = {Colors.CYAN}{cmd}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No aliases.{Colors.RESET}")
    else:
        # Create aliases
        created = 0
        for alias_def in aliases_to_create:
            if "=" in alias_def:
                name, cmd = alias_def.split("=", 1)
                aliases[name] = cmd
                print(f"{Colors.GREEN}[OK]{Colors.RESET} Alias '{name}' created")
                created += 1
            else:
                print(f"{Colors.RED}[FAIL]{Colors.RESET} Invalid alias format: {alias_def}")
        if created > 0:
            save_aliases(aliases)


def handle_alias_import(filepath: str) -> None:
    """
    Handle --alias-import: Import aliases from JSON file.

    Args:
        filepath: Path to JSON file with aliases.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            new_aliases = json.load(f)
        aliases = load_aliases()
        aliases.update(new_aliases)
        save_aliases(aliases)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Imported {len(new_aliases)} aliases")
    except FileNotFoundError:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} File not found: {filepath}")
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Invalid JSON: {e}")
    except IOError as e:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Error reading file: {e}")


def handle_alias_export(filepath: str) -> None:
    """
    Handle --alias-export: Export aliases to JSON file.

    Args:
        filepath: Path to export aliases to.
    """
    aliases = load_aliases()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(aliases, f, indent=2)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Exported {len(aliases)} aliases")
    except IOError as e:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Could not export: {e}")


def handle_alias_preset(preset_name: str) -> None:
    """
    Handle --alias-preset: Load preset aliases.

    Args:
        preset_name: Name of preset (git, docker, npm, python).
    """
    presets = get_alias_presets()
    if preset_name not in presets:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Unknown preset: {preset_name}")
        print(f"{Colors.YELLOW}Available: {', '.join(presets.keys())}{Colors.RESET}")
        return

    aliases = load_aliases()
    preset_aliases = presets[preset_name]
    aliases.update(preset_aliases)
    save_aliases(aliases)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Loaded {preset_name} preset ({len(preset_aliases)} aliases)")
