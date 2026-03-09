#!/usr/bin/env python3
"""
sufdo/commands/ - Command handlers for sufdo CLI

This package contains modular command handlers to keep main() clean.
"""

from .ai_commands import handle_ai_config, handle_ai_list, handle_ai_default, handle_ai_ask, handle_ai_add
from .stats_commands import handle_stats, handle_top, handle_success_rate, handle_export_stats, handle_history, handle_confidence, handle_undo
from .alias_commands import handle_alias, handle_alias_import, handle_alias_export, handle_alias_preset
from .safety_commands import handle_list_backups, handle_restore, handle_cleanup_backups, handle_dry_run, handle_safe_mode_check, handle_validate_command
from .notify_commands import handle_webhook_add, handle_webhook_list, handle_notify
from .config_commands import handle_profile_list, handle_profile_save, handle_env_set, handle_completion

__all__ = [
    'handle_ai_config', 'handle_ai_list', 'handle_ai_default', 'handle_ai_ask', 'handle_ai_add',
    'handle_stats', 'handle_top', 'handle_success_rate', 'handle_export_stats',
    'handle_history', 'handle_confidence', 'handle_undo',
    'handle_alias', 'handle_alias_import', 'handle_alias_export', 'handle_alias_preset',
    'handle_list_backups', 'handle_restore', 'handle_cleanup_backups',
    'handle_dry_run', 'handle_safe_mode_check', 'handle_validate_command',
    'handle_webhook_add', 'handle_webhook_list', 'handle_notify',
    'handle_profile_list', 'handle_profile_save', 'handle_env_set', 'handle_completion',
]
