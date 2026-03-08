#!/usr/bin/env python3
"""
sufdo Commit Scheduler v2.0
Автоматически создаёт коммиты и пушит на GitHub
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCHEDULE_FILE = Path(__file__).parent / "commit_schedule.json"
PROJECT_DIR = Path(__file__).parent

# Все функции по дням (20 функций в день × 10 дней = 200 функций)
FEATURES_BY_DAY = {
    1: [
        "Add --silent mode for quiet execution",
        "Add --verbose/-V mode for detailed output",
        "Add --quiet/-q alias for silent mode",
        "Add --debug mode for debugging",
        "Add --trace mode for execution tracing",
        "Add silent/verbose config options",
        "Add verbose logging with timestamps",
        "Add debug output for subprocess calls",
        "Add trace output for function calls",
        "Add color codes for verbose mode",
        "Add verbose help messages",
        "Add silent mode tests",
        "Add verbose mode tests",
        "Add debug mode documentation",
        "Add trace mode examples",
        "Add QUIET_LEVEL config option",
        "Add VERBOSE_LEVEL config option",
        "Add silent mode for aliases",
        "Add verbose mode for history",
        "Add debug mode for confidence system",
    ],
    2: [
        "Add --dry-run mode to preview commands",
        "Add --confirm mode for user confirmation",
        "Add --safe-mode to block destructive commands",
        "Add --no-destructive flag",
        "Add --backup before file operations",
        "Add dry-run output formatting",
        "Add confirm prompt with timeout",
        "Add safe-mode command blacklist",
        "Add backup directory configuration",
        "Add restore from backup feature",
        "Add dry-run for aliases",
        "Add confirm for dangerous operations",
        "Add safe-mode tests",
        "Add backup rotation",
        "Add backup compression",
        "Add dry-run exit code 0",
        "Add confirm custom messages",
        "Add safe-mode whitelist",
        "Add backup cleanup old files",
        "Add safety documentation",
    ],
    3: [
        "Add --log flag for file logging",
        "Add --log-file to specify log path",
        "Add --log-level for verbosity",
        "Add --syslog integration",
        "Add --rotate-logs for log rotation",
        "Add log format configuration",
        "Add log timestamps with timezone",
        "Add log rotation by size",
        "Add log rotation by date",
        "Add log compression for old logs",
        "Add syslog facility configuration",
        "Add log levels: DEBUG, INFO, WARN, ERROR",
        "Add log filtering by command",
        "Add log search functionality",
        "Add log export to JSON",
        "Add log export to CSV",
        "Add log viewer command",
        "Add log statistics",
        "Add log cleanup old entries",
        "Add logging documentation",
    ],
    4: [
        "Add --notify for toast notifications",
        "Add --notify-sound option",
        "Add --discord webhook integration",
        "Add --telegram bot notifications",
        "Add --email notifications",
        "Add Windows toast notification",
        "Add Linux notify-send integration",
        "Add macOS terminal-notifier support",
        "Add custom notification sounds",
        "Add notification duration setting",
        "Add Discord webhook configuration",
        "Add Telegram bot setup",
        "Add email SMTP configuration",
        "Add notification templates",
        "Add notification on success only",
        "Add notification on failure only",
        "Add notification for long commands",
        "Add notification priority levels",
        "Add notification rate limiting",
        "Add notification documentation",
    ],
    5: [
        "Add --stats for usage statistics",
        "Add --top for top commands",
        "Add --time for execution time stats",
        "Add --success-rate calculation",
        "Add --export-stats to JSON/CSV",
        "Add total commands executed stat",
        "Add average execution time stat",
        "Add success/failure ratio stat",
        "Add most used flags stat",
        "Add most used modes stat",
        "Add daily/weekly/monthly stats",
        "Add stats visualization",
        "Add stats comparison",
        "Add stats export formats",
        "Add stats reset command",
        "Add stats backup",
        "Add stats import",
        "Add stats API endpoint",
        "Add stats dashboard",
        "Add stats documentation",
    ],
    6: [
        "Add alias arguments ($1, $2, ...)",
        "Add --alias-import from file",
        "Add --alias-export to file",
        "Add --alias-share via gist",
        "Add --alias-preset packages",
        "Add alias argument validation",
        "Add alias default values",
        "Add alias optional arguments",
        "Add alias variadic arguments",
        "Add alias nested arguments",
        "Add alias import from URL",
        "Add alias export formats",
        "Add alias share to GitHub",
        "Add alias preset: git",
        "Add alias preset: docker",
        "Add alias preset: npm",
        "Add alias preset: python",
        "Add alias preset: system",
        "Add alias community repository",
        "Add alias documentation",
    ],
    7: [
        "Add --pirate mode with phrases",
        "Add --cowboy mode with phrases",
        "Add --yoda mode (speak like Yoda)",
        "Add --shakespeare mode",
        "Add --russian mode with expressions",
        "Add pirate greetings",
        "Add pirate farewell messages",
        "Add cowboy howdy messages",
        "Add cowboy yeehaw messages",
        "Add Yoda speak transformer",
        "Add Yoda wisdom quotes",
        "Add Shakespeare greetings",
        "Add Shakespeare farewell",
        "Add Shakespeare insults",
        "Add Russian greetings",
        "Add Russian farewell",
        "Add Russian encouragement",
        "Add mode combination support",
        "Add custom phrase files",
        "Add fun modes documentation",
    ],
    8: [
        "Add --anime mode with quotes",
        "Add --dark theme",
        "Add --rainbow output",
        "Add --matrix digital rain",
        "Add --hacker terminal style",
        "Add anime opening quotes",
        "Add anime victory quotes",
        "Add anime defeat quotes",
        "Add dark mode colors",
        "Add dark mode config",
        "Add rainbow color cycling",
        "Add rainbow speed option",
        "Add matrix rain animation",
        "Add matrix green colors",
        "Add hacker access messages",
        "Add hacker progress bars",
        "Add hacker success messages",
        "Add hacker error messages",
        "Add fun modes tests",
        "Add fun modes documentation",
    ],
    9: [
        "Add --cache for command caching",
        "Add --parallel execution",
        "Add --background mode",
        "Add --priority levels",
        "Add --batch file execution",
        "Add cache TTL configuration",
        "Add cache invalidation",
        "Add cache size limit",
        "Add parallel max workers",
        "Add parallel progress bar",
        "Add background job list",
        "Add background job kill",
        "Add priority: low, normal, high",
        "Add priority queue implementation",
        "Add batch file format",
        "Add batch parallel option",
        "Add batch stop on error",
        "Add batch continue on error",
        "Add performance benchmarks",
        "Add performance documentation",
    ],
    10: [
        "Add --profile for config profiles",
        "Add --env for environment variables",
        "Add --completion for bash/zsh",
        "Add --validate command validation",
        "Add --undo last command",
        "Add profile: dev, prod, test",
        "Add profile switch command",
        "Add profile export/import",
        "Add env in alias expansion",
        "Add env file support (.env)",
        "Add bash completion script",
        "Add zsh completion script",
        "Add fish completion script",
        "Add validate command exists",
        "Add validate permissions",
        "Add undo history",
        "Add undo restore state",
        "Add undo multiple levels",
        "Add integration documentation",
        "Add integration tests",
    ],
}


def create_schedule():
    """Создать расписание коммитов"""
    schedule = []
    today = datetime.now()
    
    for day_num, features in FEATURES_BY_DAY.items():
        commit_date = today + timedelta(days=day_num - 1)
        # Коммиты в 18:00 каждого дня
        commit_time = commit_date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        for i, feature in enumerate(features):
            schedule.append({
                "day": day_num,
                "feature": feature,
                "scheduled_time": commit_time.isoformat(),
                "done": False,
                "version": f"v3.{day_num}.0",
                "pushed": False
            })
    
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Created schedule: {len(schedule)} commits")
    print(f"File: {SCHEDULE_FILE}")
    print(f"Period: {today.date()} - {(today + timedelta(days=len(FEATURES_BY_DAY))).date()}")
    
    return schedule


def run_commit(message, version):
    """Выполнить git commit"""
    try:
        # Проверка изменений
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        if not result.stdout.strip():
            print(f"[SKIP] No changes for commit: {message}")
            return False
        
        # Add все файлы
        subprocess.run(
            ["git", "add", "-A"],
            cwd=PROJECT_DIR,
            capture_output=True,
            encoding="utf-8"
        )
        
        # Commit
        commit_msg = f"{message}\n\nVersion: {version}\nAuto-committed by sufdo scheduler"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        
        print(f"[OK] Committed: {message[:50]}...")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Commit failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def run_push():
    """Выполнить git push"""
    try:
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        print("[OK] Pushed to GitHub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Push failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Push error: {e}")
        return False


def check_and_run():
    """Проверить и выполнить запланированные коммиты"""
    if not SCHEDULE_FILE.exists():
        print("[FAIL] Schedule not found. Run: python commit_scheduler.py --create")
        return
    
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        schedule = json.load(f)
    
    now = datetime.now()
    changed = False
    committed = 0
    
    for item in schedule:
        if item["done"]:
            continue
        
        scheduled = datetime.fromisoformat(item["scheduled_time"])
        if scheduled <= now:
            print(f"\n[HACK] Running commit: {item['feature']}")
            if run_commit(item["feature"], item["version"]):
                item["done"] = True
                changed = True
                committed += 1
    
    if changed:
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        print(f"\n[STATS] Commits done: {committed}")
        
        # Авто-пуш после коммитов
        print("\n[PUSH] Pushing to GitHub...")
        run_push()
    else:
        print("[WAIT] No commits to run")


def show_status():
    """Показать статус расписания"""
    if not SCHEDULE_FILE.exists():
        print("[FAIL] Schedule not found")
        return
    
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        schedule = json.load(f)
    
    total = len(schedule)
    done = sum(1 for item in schedule if item["done"])
    pending = total - done
    
    print(f"\n[STATUS] Schedule status:")
    print(f"   Total commits: {total}")
    print(f"   Done: {done}")
    print(f"   Pending: {pending}")
    print(f"   Progress: {done/total*100:.1f}%")
    
    # Следующий коммит
    next_commit = next((item for item in schedule if not item["done"]), None)
    if next_commit:
        scheduled = datetime.fromisoformat(next_commit["scheduled_time"])
        print(f"\n[NEXT] Next commit:")
        print(f"   {next_commit['feature']}")
        print(f"   {scheduled.strftime('%Y-%m-%d %H:%M')}")


def install_scheduler():
    """Установить в планировщик задач Windows"""
    script_path = Path(__file__).absolute()
    python_exe = sys.executable
    
    # Создаем .bat файл для планировщика
    bat_content = f'@echo off\ncd /d "{PROJECT_DIR}"\n"{python_exe}" "{script_path}" check'
    bat_path = PROJECT_DIR / "run_scheduler.bat"
    
    with open(bat_path, "w") as f:
        f.write(bat_content)
    
    print(f"[OK] Created batch file: {bat_path}")
    print(f"\nTo install in Windows Task Scheduler, run:")
    print(f'   schtasks /Create /TN "sufdo_scheduler" /TR "{bat_path}" /SC HOURLY /RL HIGHEST')
    print(f"\nOr manually open taskschd.msc and create a task")


def reset_schedule():
    """Сбросить расписание"""
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        
        for item in schedule:
            item["done"] = False
            item["pushed"] = False
        
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        
        print("[OK] Schedule reset")
    else:
        print("[FAIL] Schedule not found")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--create":
            create_schedule()
        elif cmd == "check":
            check_and_run()
        elif cmd == "status":
            show_status()
        elif cmd == "install":
            install_scheduler()
        elif cmd == "push":
            run_push()
        elif cmd == "reset":
            reset_schedule()
        else:
            print("Commands: --create, check, status, install, push, reset")
    else:
        print("sufdo Commit Scheduler v2.0")
        print("\nCommands:")
        print("  python commit_scheduler.py --create  - Create schedule")
        print("  python commit_scheduler.py check     - Check and run commits + auto push")
        print("  python commit_scheduler.py status    - Show status")
        print("  python commit_scheduler.py install   - Install in Task Scheduler")
        print("  python commit_scheduler.py push      - Push to GitHub")
        print("  python commit_scheduler.py reset     - Reset schedule")
