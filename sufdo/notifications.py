#!/usr/bin/env python3
"""
sufdo/notifications.py - Notification systems (Optimized)

Provides system notifications, Discord webhooks, Telegram messages, and email notifications.
"""

import sys
import os
import smtplib
import json
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

from .utils import ensure_config_dir, WEBHOOKS_FILE

# In-memory cache for webhooks
_webhooks_cache: Optional[Dict] = None

__all__ = [
    'load_webhooks', 'save_webhooks', 'send_discord_webhook',
    'send_telegram_message', 'send_email', 'send_notification'
]


def load_webhooks() -> Dict:
    """
    Load webhook configurations from file (cached).
    
    Returns:
        Dictionary with webhook URLs for discord, telegram, slack.
    """
    global _webhooks_cache
    if _webhooks_cache is not None:
        return _webhooks_cache
    
    if not WEBHOOKS_FILE.exists():
        _webhooks_cache = {"discord": None, "telegram": None, "slack": None}
    else:
        try:
            with open(WEBHOOKS_FILE, encoding="utf-8") as f:
                _webhooks_cache = json.load(f)
        except:
            _webhooks_cache = {"discord": None, "telegram": None, "slack": None}
    return _webhooks_cache


def save_webhooks(webhooks: Dict) -> None:
    """
    Save webhook configurations to file.
    
    Args:
        webhooks: Dictionary with webhook URLs.
    """
    global _webhooks_cache
    _webhooks_cache = webhooks
    ensure_config_dir()
    with open(WEBHOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(webhooks, f, indent=2, ensure_ascii=False)


def send_discord_webhook(webhook_url: str, message: str) -> bool:
    """
    Send message to Discord webhook.
    
    Args:
        webhook_url: Discord webhook URL.
        message: Message content to send.
    
    Returns:
        True if sent successfully, False otherwise.
    """
    try:
        data = json.dumps({"content": message}).encode('utf-8')
        req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send message to Telegram chat.
    
    Args:
        bot_token: Telegram bot API token.
        chat_id: Target chat ID.
        message: Message content to send.
    
    Returns:
        True if sent successfully, False otherwise.
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": message}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False


def send_email(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    to_email: str,
    subject: str,
    body: str
) -> bool:
    """
    Send email notification via SMTP.
    
    Args:
        smtp_server: SMTP server hostname.
        smtp_port: SMTP server port.
        username: SMTP username.
        password: SMTP password.
        to_email: Recipient email address.
        subject: Email subject.
        body: Email body text.
    
    Returns:
        True if sent successfully, False otherwise.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False


def send_notification(title: str, message: str, sound: bool = False) -> None:
    """
    Send system notification (Windows/macOS/Linux).
    
    Args:
        title: Notification title.
        message: Notification body text.
        sound: Whether to play sound (default: False).
    """
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"{title}\n\n{message}", "sufdo", 0x40)
        elif sys.platform == "darwin":
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
        else:
            os.system(f'notify-send "{title}" "{message}"')

        if sound:
            print('\a')
    except:
        pass
