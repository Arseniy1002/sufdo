#!/usr/bin/env python3
"""
sufdo/commands/ai_commands.py - AI-related command handlers

Handles all AI model configuration and query commands.
"""

import sys
from typing import Optional, Dict, Any

from ..ai import (
    get_default_ai_models, load_ai_config, save_ai_config,
    query_ai, analyze_command_error
)
from ..utils import Colors


def handle_ai_config() -> None:
    """Handle --ai-config: Interactive AI models configuration."""
    ai_config = load_ai_config()
    print(f"{Colors.BOLD}AI Models Configuration{Colors.RESET}")
    print(f"{Colors.CYAN}Configure AI models for command error analysis{Colors.RESET}\n")

    default_models = get_default_ai_models()
    print(f"{Colors.BOLD}Available presets:{Colors.RESET}")
    for i, model in enumerate(default_models, 1):
        configured = "✓" if model["alias"] in ai_config.get("models", {}) and ai_config["models"][model["alias"]].get("api_key") else "✗"
        status_color = Colors.GREEN if configured == "✓" else Colors.YELLOW
        print(f"  {i}. {model['alias']} ({model['name']}) - {status_color}{configured == '✓' and 'configured' or 'not configured'}{Colors.RESET}")

    print(f"\n{Colors.BOLD}To add a model:{Colors.RESET}")
    print(f"  {Colors.CYAN}sufdo --ai-add <alias> <provider> <model_name> <api_url> <api_key>{Colors.RESET}")
    print(f"\n{Colors.BOLD}Quick setup (interactive):{Colors.RESET}")

    for model in default_models:
        if model["alias"] not in ai_config.get("models", {}):
            try:
                response = input(f"\nConfigure {model['alias']} ({model['name']})? [y/N]: ")
            except EOFError:
                response = 'n'
            if response.lower() == 'y':
                try:
                    api_key = input(f"Enter API key for {model['alias']}: ").strip()
                except EOFError:
                    api_key = ""
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


def handle_ai_list() -> None:
    """Handle --ai-list: List configured AI models."""
    ai_config = load_ai_config()
    if not ai_config.get("models"):
        print(f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Configured AI Models:{Colors.RESET}")
    for alias, config in ai_config["models"].items():
        default_marker = " (default)" if alias == ai_config.get("default") else ""
        key_status = "****" + config.get("api_key", "")[-4:] if config.get("api_key") else "NOT SET"
        print(f"  {Colors.GREEN}{alias}{Colors.RESET}{default_marker}: {config.get('name')} [{config.get('provider')}]")
        print(f"    API Key: {key_status}")
        print(f"    URL: {config.get('api_url', 'N/A')[:60]}...")


def handle_ai_default(model_alias: str) -> None:
    """
    Handle --ai-default: Set default AI model.

    Args:
        model_alias: Alias of the model to set as default.
    """
    ai_config = load_ai_config()
    if model_alias not in ai_config.get("models", {}):
        print(f"{Colors.RED}[FAIL]{Colors.RESET} Model '{model_alias}' not found")
        available = ', '.join(ai_config.get('models', {}).keys())
        if available:
            print(f"{Colors.YELLOW}Available: {available}{Colors.RESET}")
        return

    ai_config["default"] = model_alias
    save_ai_config(ai_config)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Default model set to: {model_alias}")


def handle_ai_ask(question: str) -> None:
    """
    Handle --ai-ask: Ask AI a question.

    Args:
        question: Question to ask the AI.
    """
    ai_config = load_ai_config()
    if not ai_config.get("models"):
        print(f"{Colors.YELLOW}[AI] No AI models configured. Run: sufdo --ai-config{Colors.RESET}")
        sys.exit(1)

    model_config: Optional[Dict[str, Any]] = None
    if ai_config.get("default") and ai_config["default"] in ai_config["models"]:
        model_config = ai_config["models"][ai_config["default"]]
    elif ai_config["models"]:
        model_config = list(ai_config["models"].values())[0]

    if model_config:
        print(f"{Colors.CYAN}[AI] Asking {model_config.get('alias', 'AI')}...{Colors.RESET}")
        response = query_ai(model_config, question)
        print(f"\n{Colors.PURPLE}[AI Response]{Colors.RESET}")
        print(response if response else f"{Colors.RED}No response from AI{Colors.RESET}")


def handle_ai_add(alias: str, provider: str, model: str, url: str, key: str) -> None:
    """
    Handle --ai-add: Add custom AI model.

    Args:
        alias: Model alias name.
        provider: Provider name (openai, google, etc.).
        model: Model name.
        url: API URL.
        key: API key.
    """
    ai_config = load_ai_config()
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
