#!/usr/bin/env python3
"""
sufdo/commands/notify_commands.py - Notification and webhook command handlers

Handles webhook management and notification sending.
"""

from typing import Dict, Optional

from ..notifications import load_webhooks, save_webhooks, send_notification
from ..utils import Colors


def handle_webhook_add(webhook_type: str, url: str) -> None:
    """
    Handle --webhook-add: Add a webhook.

    Args:
        webhook_type: Type of webhook (discord, telegram, slack).
        url: Webhook URL.
    """
    webhooks = load_webhooks()
    webhooks[webhook_type] = url
    save_webhooks(webhooks)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Webhook '{webhook_type}' added")


def handle_webhook_list() -> None:
    """Handle --webhook-list: List all configured webhooks."""
    webhooks = load_webhooks()
    print(f"{Colors.BOLD}Webhooks:{Colors.RESET}")
    for name, url in webhooks.items():
        status = f"{Colors.GREEN}configured{Colors.RESET}" if url else f"{Colors.RED}not set{Colors.RESET}"
        print(f"  {name}: {status}")


def handle_notify(
    title: str,
    message: str,
    sound: bool = False,
    discord: bool = False,
    telegram: bool = False,
    email: bool = False
) -> None:
    """
    Handle notification sending.

    Args:
        title: Notification title.
        message: Notification body.
        sound: Whether to play sound.
        discord: Send to Discord webhook.
        telegram: Send to Telegram.
        email: Send via email.
    """
    # System notification
    send_notification(title, message, sound)

    # Discord webhook
    if discord:
        webhooks = load_webhooks()
        discord_url = webhooks.get("discord")
        if discord_url:
            from ..notifications import send_discord_webhook
            send_discord_webhook(discord_url, f"{title}: {message}")
            print(f"{Colors.GREEN}[OK]{Colors.RESET} Discord notification sent")
        else:
            print(f"{Colors.YELLOW}[WARN]{Colors.RESET} Discord webhook not configured")

    # Telegram
    if telegram:
        webhooks = load_webhooks()
        telegram_url = webhooks.get("telegram")
        if telegram_url:
            from ..notifications import send_telegram_message
            # Parse bot_token and chat_id from URL
            parts = telegram_url.split("/")
            if len(parts) >= 2:
                bot_token = parts[-2]
                chat_id = parts[-1]
                send_telegram_message(bot_token, chat_id, f"{title}: {message}")
                print(f"{Colors.GREEN}[OK]{Colors.RESET} Telegram notification sent")
            else:
                print(f"{Colors.YELLOW}[WARN]{Colors.RESET} Invalid Telegram URL format")
        else:
            print(f"{Colors.YELLOW}[WARN]{Colors.RESET} Telegram webhook not configured")

    # Email would require additional config - placeholder for now
    if email:
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Email notifications require SMTP configuration")
