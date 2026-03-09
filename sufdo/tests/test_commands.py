#!/usr/bin/env python3
"""
sufdo/tests/test_commands.py - Unit tests for command handlers

Tests for the modular command handler functions.
"""

import unittest
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sufdo.commands.ai_commands import (
    handle_ai_config, handle_ai_list, handle_ai_default, handle_ai_ask, handle_ai_add
)
from sufdo.commands.stats_commands import (
    handle_stats, handle_top, handle_success_rate, handle_export_stats,
    handle_history, handle_confidence, handle_undo
)
from sufdo.commands.alias_commands import (
    handle_alias, handle_alias_import, handle_alias_export, handle_alias_preset
)
from sufdo.commands.safety_commands import (
    handle_list_backups, handle_restore, handle_cleanup_backups,
    handle_dry_run, handle_safe_mode_check, handle_validate_command
)
from sufdo.commands.notify_commands import (
    handle_webhook_add, handle_webhook_list, handle_notify
)
from sufdo.commands.config_commands import (
    handle_profile_list, handle_profile_save, handle_env_set, handle_completion
)
from sufdo.utils import Colors


class TestAICommands(unittest.TestCase):
    """Test AI command handlers."""

    @patch('sufdo.commands.ai_commands.load_ai_config')
    @patch('sufdo.commands.ai_commands.save_ai_config')
    @patch('sufdo.commands.ai_commands.get_default_ai_models')
    @patch('builtins.input', side_effect=EOFError())
    def test_handle_ai_list_empty(self, mock_input, mock_get_models, mock_save, mock_load):
        """Test AI list with no configured models."""
        mock_load.return_value = {"models": {}, "default": None}
        mock_get_models.return_value = []
        
        # Should not raise
        handle_ai_list()

    @patch('sufdo.commands.ai_commands.load_ai_config')
    @patch('sufdo.commands.ai_commands.save_ai_config')
    def test_handle_ai_default(self, mock_save, mock_load):
        """Test setting default AI model."""
        mock_load.return_value = {"models": {"gpt": {"name": "gpt-4"}}, "default": None}
        
        # Should not raise
        handle_ai_default("gpt")
        
        # Verify save was called with updated config
        mock_save.assert_called()

    @patch('sufdo.commands.ai_commands.load_ai_config')
    @patch('sufdo.commands.ai_commands.save_ai_config')
    def test_handle_ai_add(self, mock_save, mock_load):
        """Test adding AI model."""
        mock_load.return_value = {"models": {}, "default": None}
        
        handle_ai_add("test", "openai", "gpt-4", "https://api.openai.com", "sk-test")
        
        mock_save.assert_called()


class TestStatsCommands(unittest.TestCase):
    """Test stats command handlers."""

    def test_handle_stats(self):
        """Test handle_stats doesn't raise."""
        # Should not raise
        handle_stats()

    def test_handle_history(self):
        """Test handle_history doesn't raise."""
        # Should not raise
        handle_history()

    def test_handle_confidence(self):
        """Test handle_confidence doesn't raise."""
        # Should not raise
        handle_confidence()

    @patch('sufdo.commands.stats_commands.load_stats')
    def test_handle_top_empty(self, mock_load):
        """Test handle_top with no commands."""
        mock_load.return_value = {"commands": {}}
        handle_top()  # Should not raise

    @patch('sufdo.commands.stats_commands.load_stats')
    def test_handle_success_rate_empty(self, mock_load):
        """Test handle_success_rate with no commands."""
        mock_load.return_value = {"total": 0, "success": 0}
        handle_success_rate()  # Should not raise

    @patch('sufdo.commands.stats_commands.load_stats')
    @patch('tempfile.mktemp')
    def test_handle_export_stats(self, mock_mktemp, mock_load):
        """Test exporting stats."""
        import tempfile
        mock_load.return_value = {"total": 10, "success": 8}
        
        # Create temp file properly
        fd, temp_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        
        try:
            handle_export_stats(temp_path)
            # Verify file was written
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertIn("total", data)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestAliasCommands(unittest.TestCase):
    """Test alias command handlers."""

    @patch('sufdo.commands.alias_commands.load_aliases')
    @patch('sufdo.commands.alias_commands.save_aliases')
    def test_handle_alias_create(self, mock_save, mock_load):
        """Test creating alias."""
        mock_load.return_value = {}
        
        handle_alias(["gs=git status"])
        
        mock_save.assert_called()

    @patch('sufdo.commands.alias_commands.load_aliases')
    def test_handle_alias_list_empty(self, mock_load):
        """Test listing empty aliases."""
        mock_load.return_value = {}
        handle_alias(None)  # Should not raise

    @patch('sufdo.commands.alias_commands.get_alias_presets')
    @patch('sufdo.commands.alias_commands.load_aliases')
    @patch('sufdo.commands.alias_commands.save_aliases')
    def test_handle_alias_preset(self, mock_save, mock_load, mock_presets):
        """Test loading alias preset."""
        mock_presets.return_value = {"git": {"gs": "git status"}}
        mock_load.return_value = {}
        
        handle_alias_preset("git")
        
        mock_save.assert_called()

    def test_handle_alias_preset_unknown(self):
        """Test unknown preset."""
        # Should print error, not raise
        handle_alias_preset("nonexistent_preset")


class TestSafetyCommands(unittest.TestCase):
    """Test safety command handlers."""

    def test_handle_list_backups_empty(self):
        """Test listing empty backups."""
        # Should not raise
        handle_list_backups()

    @patch('sufdo.commands.safety_commands.validate_command')
    def test_handle_dry_run(self, mock_validate):
        """Test dry run."""
        mock_validate.return_value = (True, "OK")
        handle_dry_run("ls -la")  # Should not raise

    def test_handle_safe_mode_check_safe(self):
        """Test safe mode check with safe command."""
        is_safe, reason = handle_safe_mode_check("ls -la")
        self.assertTrue(is_safe)

    def test_handle_safe_mode_check_destructive(self):
        """Test safe mode check with destructive command."""
        is_safe, reason = handle_safe_mode_check("rm -rf /")
        self.assertFalse(is_safe)

    @patch('sufdo.commands.safety_commands.validate_command')
    def test_handle_validate_command(self, mock_validate):
        """Test validate command."""
        mock_validate.return_value = (True, "OK")
        result = handle_validate_command("python")
        self.assertTrue(result)


class TestNotifyCommands(unittest.TestCase):
    """Test notification command handlers."""

    @patch('sufdo.commands.notify_commands.load_webhooks')
    @patch('sufdo.commands.notify_commands.save_webhooks')
    def test_handle_webhook_add(self, mock_save, mock_load):
        """Test adding webhook."""
        mock_load.return_value = {"discord": None}
        handle_webhook_add("discord", "https://discord.com/webhook")
        mock_save.assert_called()

    def test_handle_webhook_list(self):
        """Test listing webhooks."""
        # Should not raise
        handle_webhook_list()


class TestConfigCommands(unittest.TestCase):
    """Test config command handlers."""

    def test_handle_profile_list(self):
        """Test listing profiles."""
        # Should not raise
        handle_profile_list()

    @patch('sufdo.commands.config_commands.load_config')
    @patch('sufdo.commands.config_commands.save_profile')
    def test_handle_profile_save(self, mock_save, mock_load):
        """Test saving profile."""
        mock_load.return_value = {"theme": "default"}
        handle_profile_save("test_profile")
        mock_save.assert_called()

    @patch('sufdo.commands.config_commands.load_env')
    @patch('sufdo.commands.config_commands.save_env')
    def test_handle_env_set(self, mock_save, mock_load):
        """Test setting env variable."""
        mock_load.return_value = {}
        handle_env_set("TEST_KEY", "test_value")
        mock_save.assert_called()

    def test_handle_completion_bash(self):
        """Test bash completion."""
        # Should not raise
        handle_completion("bash")

    def test_handle_completion_zsh(self):
        """Test zsh completion."""
        # Should not raise
        handle_completion("zsh")

    def test_handle_completion_fish(self):
        """Test fish completion."""
        # Should not raise
        handle_completion("fish")


class TestExecution(unittest.TestCase):
    """Test execution module."""

    def test_execute_with_timeout_success(self):
        """Test successful command execution."""
        from sufdo.execution import execute_with_timeout
        result = execute_with_timeout("echo hello", timeout=5)
        self.assertEqual(result["returncode"], 0)
        self.assertIn("hello", result["stdout"])

    def test_execute_with_timeout_expired(self):
        """Test command timeout."""
        from sufdo.execution import execute_with_timeout
        # Use Python to create a delay that can be interrupted
        import sys
        cmd = sys.executable + " -c \"import time; time.sleep(10)\""
        result = execute_with_timeout(cmd, timeout=1)
        # Should timeout (returncode 124) or be killed (returncode != 0)
        self.assertNotEqual(result["returncode"], 0)

    def test_execute_with_timeout_invalid_command(self):
        """Test invalid command."""
        from sufdo.execution import execute_with_timeout
        result = execute_with_timeout("nonexistent_command_12345", timeout=5)
        self.assertNotEqual(result["returncode"], 0)

    def test_execute_parallel(self):
        """Test parallel execution."""
        from sufdo.execution import execute_parallel
        results = execute_parallel(["echo hello", "echo world"])
        self.assertEqual(len(results), 2)
        self.assertTrue(any("hello" in r.get("stdout", "") for r in results))


if __name__ == '__main__':
    unittest.main()
