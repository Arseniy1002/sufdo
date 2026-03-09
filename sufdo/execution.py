#!/usr/bin/env python3
"""
sufdo/execution.py - Command execution utilities (Refactored)

Provides parallel and background command execution with proper error handling.
"""

import subprocess
import os
import signal
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

__all__ = ['execute_parallel', 'execute_background', 'get_background_jobs', 'kill_background_job', 'execute_with_timeout']


def execute_with_timeout(
    command: str,
    timeout: int = 60,
    capture_output: bool = True
) -> Dict:
    """
    Execute command with timeout and error handling.

    Args:
        command: Command string to execute.
        timeout: Timeout in seconds (default: 60).
        capture_output: Whether to capture stdout/stderr.

    Returns:
        Dict with command, stdout, stderr, returncode, and optional error.
    """
    result = {
        "command": command,
        "stdout": "",
        "stderr": "",
        "returncode": -1,
        "timed_out": False,
        "interrupted": False
    }

    try:
        proc_result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            timeout=timeout
        )
        result["returncode"] = proc_result.returncode
        if capture_output:
            result["stdout"] = proc_result.stdout.decode('utf-8', errors='replace') if proc_result.stdout else ''
            result["stderr"] = proc_result.stderr.decode('utf-8', errors='replace') if proc_result.stderr else ''

    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        result["error"] = f"Command timed out after {timeout} seconds"
        result["returncode"] = 124

    except subprocess.SubprocessError as e:
        result["error"] = f"Subprocess error: {str(e)}"
        result["returncode"] = 1

    except OSError as e:
        result["error"] = f"OS error: {str(e)}"
        result["returncode"] = 1

    except KeyboardInterrupt:
        result["interrupted"] = True
        result["error"] = "Interrupted by user"
        result["returncode"] = 130

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        result["returncode"] = 1

    return result


def execute_parallel(
    commands: List[str],
    max_workers: int = 4,
    timeout: int = 60
) -> List[Dict]:
    """
    Execute commands in parallel using thread pool.

    Args:
        commands: List of command strings to execute.
        max_workers: Maximum number of parallel workers (default: 4).
        timeout: Timeout per command in seconds (default: 60).

    Returns:
        List of execution results with stdout, stderr, and returncode.
    """
    results = []

    def run_cmd(cmd: str) -> Dict:
        return execute_with_timeout(cmd, timeout=timeout)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(run_cmd, cmd): cmd for cmd in commands}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except FuturesTimeoutError:
                    cmd = futures[future]
                    results.append({
                        "command": cmd,
                        "error": f"Future timed out",
                        "returncode": 124
                    })
                except KeyboardInterrupt:
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    results.append({
                        "command": "parallel_executor",
                        "error": "Interrupted by user",
                        "returncode": 130,
                        "interrupted": True
                    })
                    break
                except Exception as e:
                    cmd = futures[future]
                    results.append({
                        "command": cmd,
                        "error": str(e),
                        "returncode": 1
                    })
    except KeyboardInterrupt:
        results.append({
            "command": "parallel_executor",
            "error": "Interrupted by user",
            "returncode": 130,
            "interrupted": True
        })
    except Exception as e:
        results.append({
            "command": "parallel_executor",
            "error": f"Executor error: {str(e)}",
            "returncode": 1
        })

    return results


def execute_background(command: str, cwd: Optional[str] = None) -> Optional[int]:
    """
    Execute command in background.

    Args:
        command: Command string to execute.
        cwd: Working directory (optional).

    Returns:
        Process ID of background process, or None on error.
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return process.pid
    except OSError as e:
        print(f"OS error starting background process: {e}")
        return None
    except Exception as e:
        print(f"Error starting background process: {e}")
        return None


# Global list to track background jobs
_background_jobs: List[Dict] = []


def register_background_job(pid: int, command: str) -> None:
    """
    Register a background job for tracking.

    Args:
        pid: Process ID.
        command: Command that was executed.
    """
    _background_jobs.append({
        "pid": pid,
        "command": command,
        "started": True
    })


def get_background_jobs() -> List[Dict]:
    """
    Get list of background jobs.

    Returns:
        List of background job info dicts.
    """
    # Clean up finished jobs
    active_jobs = []
    for job in _background_jobs:
        try:
            # Check if process is still running
            os.kill(job["pid"], 0)
            active_jobs.append(job)
        except OSError:
            # Process finished
            pass

    return active_jobs


def kill_background_job(pid: int) -> bool:
    """
    Kill background job by PID.

    Args:
        pid: Process ID to kill.

    Returns:
        True if killed successfully, False otherwise.
    """
    try:
        if os.name == "nt":
            # Windows
            os.kill(pid, signal.CTRL_BREAK_EVENT)  # type: ignore
        else:
            # Unix-like
            os.kill(pid, signal.SIGTERM)
        return True
    except OSError:
        # Process already finished
        return False
    except Exception:
        return False


def kill_all_background_jobs() -> int:
    """
    Kill all tracked background jobs.

    Returns:
        Number of jobs killed.
    """
    killed = 0
    for job in get_background_jobs():
        if kill_background_job(job["pid"]):
            killed += 1
    return killed
