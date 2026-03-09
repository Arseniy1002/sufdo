#!/usr/bin/env python3
"""
sufdo/execution.py - Command execution utilities (Optimized)

Provides parallel and background command execution functionality.
"""

import subprocess
import os
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

__all__ = ['execute_parallel', 'execute_background', 'get_background_jobs', 'kill_background_job']


def execute_parallel(commands: List[str], max_workers: int = 4) -> List[Dict]:
    """
    Execute commands in parallel using thread pool.
    
    Args:
        commands: List of command strings to execute.
        max_workers: Maximum number of parallel workers (default: 4).
    
    Returns:
        List of execution results with stdout, stderr, and returncode.
    """
    results = []

    def run_cmd(cmd: str) -> Dict:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
            return {"command": cmd, "stdout": stdout, "stderr": stderr, "returncode": result.returncode}
        except Exception as e:
            return {"command": cmd, "error": str(e)}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_cmd, cmd): cmd for cmd in commands}
        for future in as_completed(futures):
            results.append(future.result())

    return results


def execute_background(command: str) -> int:
    """
    Execute command in background.
    
    Args:
        command: Command string to execute.
    
    Returns:
        Process ID of background process.
    """
    process = subprocess.Popen(command, shell=True)
    return process.pid


def get_background_jobs() -> List[Dict]:
    """
    Get list of background jobs.
    
    Returns:
        Empty list (placeholder for future implementation).
    """
    return []


def kill_background_job(pid: int) -> bool:
    """
    Kill background job by PID.
    
    Args:
        pid: Process ID to kill.
    
    Returns:
        True if killed successfully, False otherwise.
    """
    try:
        os.kill(pid, 9)
        return True
    except Exception:
        return False
