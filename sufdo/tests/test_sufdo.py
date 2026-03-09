#!/usr/bin/env python3
"""
sufdo/tests/test_sufdo.py - Unit tests for sufdo utility

Run with: python -m unittest discover -s sufdo/tests
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sufdo.utils import (
    Colors, DESTRUCTIVE_COMMANDS, is_destructive_command,
    validate_command, get_os_package_manager, is_termux, get_platform_name
)
from sufdo.ai import encrypt_key, decrypt_key
from sufdo.safety import create_backup, list_backups, restore_backup, cleanup_old_backups
from sufdo.aliases import expand_alias, get_alias_presets
from sufdo.fun_modes import rainbow_text, dark_mode, get_fun_phrase
from sufdo.stats import get_cache_key


class TestColors(unittest.TestCase):
    """Test Colors class."""
    
    def test_colors_have_values(self):
        """Test that color constants have values."""
        self.assertTrue(Colors.RED)
        self.assertTrue(Colors.GREEN)
        self.assertTrue(Colors.RESET)
    
    def test_colors_defined(self):
        """Test that Colors has expected attributes."""
        self.assertTrue(hasattr(Colors, 'RED'))
        self.assertTrue(hasattr(Colors, 'GREEN'))
        self.assertTrue(hasattr(Colors, 'RESET'))


class TestDestructiveCommands(unittest.TestCase):
    """Test destructive command detection."""
    
    def test_detects_rm_rf_root(self):
        """Test detection of rm -rf /."""
        self.assertTrue(is_destructive_command("rm -rf /"))
        self.assertTrue(is_destructive_command("RM -RF /"))
    
    def test_detects_format(self):
        """Test detection of format command."""
        self.assertTrue(is_destructive_command("format C:"))
    
    def test_allows_safe_commands(self):
        """Test that safe commands are not flagged."""
        self.assertFalse(is_destructive_command("ls -la"))
        self.assertFalse(is_destructive_command("echo hello"))
        self.assertFalse(is_destructive_command("cat file.txt"))


class TestValidateCommand(unittest.TestCase):
    """Test command validation."""
    
    def test_valid_command(self):
        """Test validation of existing command."""
        valid, msg = validate_command("python --version")
        self.assertTrue(valid)
    
    def test_invalid_command(self):
        """Test validation of non-existing command."""
        valid, msg = validate_command("nonexistentcommand12345")
        self.assertFalse(valid)
        self.assertIn("not found", msg)


class TestKeyEncryption(unittest.TestCase):
    """Test API key encryption."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypted key can be decrypted."""
        original = "sk-1234567890abcdef"
        encrypted = encrypt_key(original)
        decrypted = decrypt_key(encrypted)
        self.assertEqual(original, decrypted)
    
    def test_empty_key(self):
        """Test encryption of empty key."""
        self.assertEqual(encrypt_key(""), "")
        self.assertEqual(decrypt_key(""), "")
    
    def test_encrypted_key_has_checksum(self):
        """Test that encrypted key contains checksum."""
        encrypted = encrypt_key("test_key")
        self.assertIn(":", encrypted)


class TestAliasExpansion(unittest.TestCase):
    """Test alias expansion."""
    
    def test_simple_alias(self):
        """Test simple alias expansion."""
        aliases = {"gs": "git status"}
        result = expand_alias(["gs"], aliases)
        self.assertEqual(result, ["git", "status"])
    
    def test_alias_with_args(self):
        """Test alias expansion with arguments."""
        aliases = {"gs": "git status"}
        result = expand_alias(["gs", "-s"], aliases)
        self.assertEqual(result, ["git", "status", "-s"])
    
    def test_nonexistent_alias(self):
        """Test that non-alias returns unchanged."""
        aliases = {"gs": "git status"}
        result = expand_alias(["git", "status"], aliases)
        self.assertEqual(result, ["git", "status"])
    
    def test_alias_presets_exist(self):
        """Test that alias presets are available."""
        presets = get_alias_presets()
        self.assertIn("git", presets)
        self.assertIn("docker", presets)
        self.assertIn("npm", presets)


class TestRainbowText(unittest.TestCase):
    """Test rainbow text generation."""
    
    def test_rainbow_text_contains_reset(self):
        """Test that rainbow text ends with reset."""
        result = rainbow_text("test")
        self.assertIn(Colors.RESET, result)
    
    def test_rainbow_text_has_correct_length(self):
        """Test that rainbow text has correct structure."""
        result = rainbow_text("test")
        # Each char gets color code + char, plus reset at end
        self.assertTrue(len(result) > len("test"))
    
    def test_dark_mode(self):
        """Test dark mode text."""
        result = dark_mode("test")
        self.assertIn(Colors.DIM, result)
        self.assertIn("test", result)


class TestCacheKey(unittest.TestCase):
    """Test cache key generation."""
    
    def test_same_command_same_key(self):
        """Test that same command produces same key."""
        key1 = get_cache_key("ls -la")
        key2 = get_cache_key("ls -la")
        self.assertEqual(key1, key2)
    
    def test_different_command_different_key(self):
        """Test that different commands produce different keys."""
        key1 = get_cache_key("ls -la")
        key2 = get_cache_key("ls -l")
        self.assertNotEqual(key1, key2)


class TestFunModePhrases(unittest.TestCase):
    """Test fun mode phrase generation."""
    
    def test_pirate_phrases_exist(self):
        """Test that pirate phrases are available."""
        phrase = get_fun_phrase("pirate")
        self.assertTrue(isinstance(phrase, str))
        self.assertTrue(len(phrase) > 0)
    
    def test_yoda_phrases_exist(self):
        """Test that yoda phrases are available."""
        phrase = get_fun_phrase("yoda")
        self.assertTrue(isinstance(phrase, str))
        self.assertTrue(len(phrase) > 0)
    
    def test_unknown_mode_returns_pirate(self):
        """Test that unknown mode returns pirate phrase."""
        phrase = get_fun_phrase("unknown_mode")
        self.assertTrue(isinstance(phrase, str))


class TestOSPackageManager(unittest.TestCase):
    """Test OS package manager detection."""

    def test_returns_string(self):
        """Test that package manager is a string."""
        result = get_os_package_manager()
        self.assertTrue(isinstance(result, str))
        self.assertTrue(len(result) > 0)

    @patch('sys.platform', 'win32')
    def test_windows_package_manager(self):
        """Test Windows package manager."""
        # Clear cache
        if hasattr(get_os_package_manager, "_cached"):
            delattr(get_os_package_manager, "_cached")
        result = get_os_package_manager()
        self.assertEqual(result, "winget install")

    @patch('sys.platform', 'darwin')
    def test_macos_package_manager(self):
        """Test macOS package manager."""
        # Clear cache
        if hasattr(get_os_package_manager, "_cached"):
            delattr(get_os_package_manager, "_cached")
        result = get_os_package_manager()
        self.assertEqual(result, "brew install")

    @patch('os.environ.get')
    @patch('sys.platform', 'linux')
    def test_termux_package_manager(self, mock_getenv):
        """Test Termux package manager."""
        # Mock Termux environment
        def getenv_side_effect(key, default=None):
            if key == "PREFIX":
                return "/data/data/com.termux/files/usr"
            return default
        mock_getenv.side_effect = getenv_side_effect

        # Clear cache
        if hasattr(get_os_package_manager, "_cached"):
            delattr(get_os_package_manager, "_cached")

        result = get_os_package_manager()
        self.assertEqual(result, "pkg install")

    def test_is_termux_false(self):
        """Test is_termux returns False on non-Termux."""
        result = is_termux()
        self.assertFalse(result)

    @patch('os.environ.get')
    def test_is_termux_true_by_prefix(self, mock_getenv):
        """Test is_termux detects Termux by PREFIX."""
        mock_getenv.return_value = "/data/data/com.termux/files/usr"
        self.assertTrue(is_termux())

    @patch('os.path.exists')
    @patch('os.environ.get')
    def test_is_termux_true_by_path(self, mock_getenv, mock_exists):
        """Test is_termux detects Termux by path."""
        mock_getenv.return_value = ""  # Return empty string, not None
        mock_exists.return_value = True
        self.assertTrue(is_termux())

    @patch('sys.platform', 'win32')
    def test_get_platform_name_windows(self):
        """Test get_platform_name for Windows."""
        self.assertEqual(get_platform_name(), "Windows")

    @patch('sys.platform', 'darwin')
    def test_get_platform_name_macos(self):
        """Test get_platform_name for macOS."""
        self.assertEqual(get_platform_name(), "macOS")

    @patch('os.environ.get')
    @patch('sys.platform', 'linux')
    def test_get_platform_name_termux(self, mock_getenv):
        """Test get_platform_name for Termux."""
        mock_getenv.return_value = "/data/data/com.termux/files/usr"
        self.assertEqual(get_platform_name(), "Android (Termux)")


if __name__ == '__main__':
    unittest.main()
