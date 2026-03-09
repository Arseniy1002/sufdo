#!/usr/bin/env python3
"""
sufdo/config.py - Configuration management (Optimized)

Handles user configuration, environment variables, and profiles with in-memory caching.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from .utils import ensure_config_dir, CONFIG_FILE, ENV_FILE, PROFILES_DIR

# In-memory cache for config
_config_cache: Optional[Dict] = None
_env_cache: Optional[Dict] = None
_profiles_cache: Optional[Dict] = None

__all__ = [
    'load_config', 'save_config', 'load_env', 'save_env', 
    'load_profiles', 'save_profile'
]


def load_config() -> Dict:
    """
    Load user configuration from file (cached).
    
    Returns:
        Configuration dictionary with user preferences.
    """
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    
    if not CONFIG_FILE.exists():
        _config_cache = {
            "quiet_level": 0, 
            "verbose_level": 1, 
            "theme": "default", 
            "profile": "default"
        }
    else:
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                _config_cache = json.load(f)
        except:
            _config_cache = {}
    return _config_cache


def save_config(config: Dict) -> None:
    """
    Save user configuration to file.
    
    Args:
        config: Configuration dictionary to save.
    """
    global _config_cache
    _config_cache = config
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_env() -> Dict:
    """
    Load environment variables from .env file (cached).
    
    Returns:
        Dictionary of environment variable key-value pairs.
    """
    global _env_cache
    if _env_cache is not None:
        return _env_cache
    
    _env_cache = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    _env_cache[key.strip()] = value.strip()
    return _env_cache


def save_env(env: Dict) -> None:
    """
    Save environment variables to .env file.
    
    Args:
        env: Dictionary of environment variables to save.
    """
    global _env_cache
    _env_cache = env
    ensure_config_dir()
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for key, value in env.items():
            f.write(f"{key}={value}\n")


def load_profiles() -> Dict:
    """
    Load all profiles from profiles directory (cached).
    
    Returns:
        Dictionary of profile names to configurations.
    """
    global _profiles_cache
    if _profiles_cache is not None:
        return _profiles_cache
    
    _profiles_cache = {"default": {}}
    if not PROFILES_DIR.exists():
        return _profiles_cache
    
    for profile_file in PROFILES_DIR.glob("*.json"):
        try:
            with open(profile_file, encoding="utf-8") as f:
                _profiles_cache[profile_file.stem] = json.load(f)
        except:
            pass
    return _profiles_cache


def save_profile(name: str, config: Dict) -> None:
    """
    Save a profile configuration to file.
    
    Args:
        name: Profile name.
        config: Profile configuration dictionary.
    """
    global _profiles_cache
    _profiles_cache = None  # Invalidate cache
    ensure_config_dir()
    with open(PROFILES_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
