#!/usr/bin/env python3
"""
sufdo - Super User Fkin Do

A sudo-like utility for executing commands with elevated privileges.
"""

import sys
import subprocess
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        prog="sufdo",
        description="Super User Fkin Do - Execute commands with elevated privileges"
    )
    parser.add_argument(
        "-u", "--user",
        default="root",
        help="Run command as specified user (default: root)"
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information"
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute"
    )

    args = parser.parse_args()

    if args.version:
        print("sufdo version 1.0.0")
        print("Super User Fkin Do")
        sys.exit(0)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the command
    try:
        result = subprocess.run(
            args.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"sufdo: error executing command: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
