# sufdo v3.10.0 - Complete Edition

**Super User Fkin Do** - Execute commands with elevated privileges. Because sometimes you just need to get shit done.

## 🎯 Features

### Core
- ✅ Execute commands with elevated privileges
- ✅ Command history tracking
- ✅ Re-run last command (`--last`, `-!`)
- ✅ Timeout support (`--timeout`, `-t`)
- ✅ Custom aliases with arguments (`$1`, `$2`, `$@`)
- ✅ Confidence system
- ✅ Cross-platform (Windows, Linux, macOS)

### Silent/Verbose Modes
- ✅ `--silent`, `-q`, `--quiet` - Silent mode
- ✅ `--verbose`, `-V` - Verbose output
- ✅ `--debug` - Debug information
- ✅ `--trace` - Execution tracing

### Safety Modes
- ✅ `--dry-run` - Preview without executing
- ✅ `--confirm` - Ask for confirmation
- ✅ `--safe-mode` - Block destructive commands
- ✅ `--backup` - Backup before operations

### Logging
- ✅ `--log` - Log to file
- ✅ `--log-file` - Custom log path
- ✅ `--log-level` - Log level (DEBUG, INFO, WARN, ERROR)

### Statistics
- ✅ `--stats` - Usage statistics
- ✅ `--top` - Top commands
- ✅ Success rate tracking
- ✅ Execution time tracking

### Fun Modes
- ✅ `--pirate` - Pirate phrases
- ✅ `--cowboy` - Cowboy phrases
- ✅ `--yoda` - Yoda speak
- ✅ `--shakespeare` - Shakespeare style
- ✅ `--anime` - Anime quotes
- ✅ `--rainbow` - Rainbow output
- ✅ `--drama` - Dramatic messages
- ✅ `--pray` - Pray before execution
- ✅ `--yeet` - YEET mode
- ✅ `--sus` - Among Us mode
- ✅ `--hacker` - Hacker terminal
- ✅ `--cursed` - Cursed mode
- ✅ `--matrix` - Matrix rain
- ✅ `--bruh` - Bruh commentary
- ✅ `--combo` - ALL MODES AT ONCE

## 📊 Statistics

```bash
sufdo --stats
# Usage Statistics:
#   Total commands: 150
#   Successful: 142
#   Failed: 8
#   Success rate: 94.7%
```

## 🎭 Fun Examples

```bash
# Pirate mode
sufdo --pirate apt update
# [PIRATE] Ahoy matey!

# Cowboy mode
sufdo --cowboy ls -la
# [COWBOY] Howdy partner!

# Yoda mode
sufdo --yoda echo "Hello"
# [YODA] May the Force be with you.

# Rainbow mode
sufdo --rainbow --version
# (rainbow colored output)

# Combo mode (maximum chaos)
sufdo --combo echo "CHAOS"
```

## 🔧 Installation

```bash
# Install from source
pip install .

# Or editable mode
pip install -e .
```

## 📁 Config Files

All config files stored in `~/.sufdo/`:
- `config.json` - User configuration
- `history.json` - Command history
- `aliases.json` - User aliases
- `confidence.json` - Confidence level
- `stats.json` - Usage statistics
- `cache.json` - Command cache
- `sufdo.log` - Log file
- `backups/` - Backup directory

## 🚀 Auto-Commit Scheduler

sufdo includes an auto-commit scheduler that rolls out features over 10 days:

```bash
# Create schedule (200 features over 10 days)
python commit_scheduler.py --create

# Check status
python commit_scheduler.py status

# Run pending commits + auto push
python commit_scheduler.py check

# Install in Task Scheduler (Windows)
python commit_scheduler.py install
```

### Windows Task Scheduler Setup

```cmd
schtasks /Create /TN "sufdo_scheduler" /TR "C:\path\to\sufdo\run_scheduler.bat" /SC HOURLY /RL HIGHEST
```

## 📈 Roadmap

| Day | Version | Features |
|-----|---------|----------|
| 1 | v3.1.0 | Silent/Verbose modes ✅ |
| 2 | v3.2.0 | Safety modes ✅ |
| 3 | v3.3.0 | Logging ✅ |
| 4 | v3.4.0 | Notifications |
| 5 | v3.5.0 | Statistics ✅ |
| 6 | v3.6.0 | Advanced aliases ✅ |
| 7 | v3.7.0 | Fun modes part 1 ✅ |
| 8 | v3.8.0 | Fun modes part 2 ✅ |
| 9 | v3.9.0 | Performance |
| 10 | v3.10.0 | Integration ✅ |

## 🎯 Usage Examples

```bash
# Basic
sufdo apt update
sufdo -u www-data ls /var

# With safety
sufdo --dry-run rm -rf /tmp/*
sufdo --confirm apt upgrade
sufdo --safe-mode --backup rm important.txt

# With logging
sufdo --log --log-level DEBUG python script.py

# With statistics
sufdo --stats
sufdo --top

# Fun
sufdo --pirate --flex ls -la
sufdo --combo --rainbow echo "Hello"
```

## ⚠️ Disclaimer

Use responsibly. The authors are not responsible for any damage caused by misuse of this tool. Or for any confidence depletion resulting from failed commands.

## 📄 License

MIT

---

**Made with chaos and 200+ features** 🚀
