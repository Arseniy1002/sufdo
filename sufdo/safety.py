#!/usr/bin/env python3
"""
sufdo/safety.py - Safety features (Optimized)

Provides destructive command detection, backup creation, and restoration functionality.
"""

import os
import shutil
import time
from datetime import datetime
from typing import List, Optional

from .utils import ensure_config_dir, Colors, BACKUP_DIR, DESTRUCTIVE_COMMANDS

__all__ = ['create_backup', 'list_backups', 'restore_backup', 'cleanup_old_backups']


def create_backup(path: str) -> Optional[str]:
    """
    Create backup of a file or directory.
    
    Args:
        path: Path to file or directory to backup.
    
    Returns:
        Backup path if successful, None otherwise.
    """
    if not os.path.exists(path):
        return None

    ensure_config_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(path)}_{timestamp}"
    backup_path = BACKUP_DIR / backup_name

    try:
        if os.path.isfile(path):
            shutil.copy2(path, backup_path)
        else:
            shutil.copytree(path, backup_path)
        return str(backup_path)
    except Exception:
        return None


def list_backups() -> List[str]:
    """
    List all backups in backup directory.
    
    Returns:
        List of backup file/directory names.
    """
    ensure_config_dir()
    return [f.name for f in BACKUP_DIR.iterdir()] if BACKUP_DIR.exists() else []


def restore_backup(backup_name: str) -> bool:
    """
    Restore from backup.
    
    Args:
        backup_name: Name of backup to restore.
    
    Returns:
        True if restored successfully, False otherwise.
    """
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        return False

    # Extract original name from backup name
    original_name = '_'.join(backup_name.split('_')[:-2])

    try:
        if backup_path.is_file():
            shutil.copy2(backup_path, original_name)
        else:
            if os.path.exists(original_name):
                shutil.rmtree(original_name)
            shutil.copytree(backup_path, original_name)
        return True
    except Exception:
        return False


def cleanup_old_backups(days: int = 30) -> None:
    """
    Clean up backups older than specified days.
    
    Args:
        days: Age threshold in days (default: 30).
    """
    ensure_config_dir()
    if not BACKUP_DIR.exists():
        return

    cutoff = time.time() - (days * 24 * 60 * 60)
    for backup in BACKUP_DIR.iterdir():
        if backup.stat().st_mtime < cutoff:
            try:
                if backup.is_file():
                    backup.unlink()
                else:
                    shutil.rmtree(backup)
            except Exception:
                pass
