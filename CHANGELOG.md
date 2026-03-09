# Changelog

All notable changes to sufdo will be documented in this file.

## [4.4.0] - 2026-03-09

### 🔧 Optimization
- **In-memory caching** for frequently read JSON files (stats, config, aliases, webhooks, ai_config)
- **`__slots__`** for Colors class — memory savings
- **Frozen collections** (tuple, frozenset) for immutable data
- **Function result caching** for `get_os_package_manager()`
- **Optimized `rainbow_text()`** — using list instead of string concatenation
- **Timeouts for urllib** — 10-30 seconds instead of infinite

### 📝 Type Hints
- Added **type hints** to all modules
- Added **docstrings** for all public functions
- `__all__` exports for all modules

### 🔒 Security
- **API key encryption** (base64 + salt + checksum)
- Command validation before execution

### 🧪 Tests
- Added **unittest tests** (25 tests)
- Tests for: Colors, destructive commands, encryption, aliases, rainbow text, cache keys

### 📄 Documentation
- Complete docstrings for all functions
- CHANGELOG.md

### 🐛 Fixes
- Enabled **ANSI color support in Windows PowerShell**
- Fixed circular imports

---

## [4.2.0] - 2026-03-08

### Added
- Windows UAC elevation (`-a` flag)
- AI error analysis (GPT, Gemini, DeepSeek, OpenRouter)
- 17+ fun modes (pirate, cowboy, yoda, hacker, matrix, etc.)
- Notifications (Discord, Telegram, email, system)
- Aliases and presets (git, docker, npm, python)
- Statistics and confidence tracking
- Backup/restore functionality
- Command history (last 100)
- Cache for command output
- Profiles and environment variables
- Batch execution
- Parallel execution

---

## [4.1.0] - 2026-03-07

### Added
- Silent/verbose modes
- Debug and trace modes
- Logging to file
- Safe mode for blocking destructive commands
- Dry-run mode

---

## [4.0.0] - 2026-03-06

### Changed
- First public release
- Basic sudo-like utility functionality
- Windows, Linux, macOS support

---

## Types of Changes

- **Added** — new features
- **Changed** — changes in existing functionality
- **Deprecated** — will be removed soon
- **Removed** — removed features
- **Fixed** — bug fixes
- **Security** — security improvements
- **Optimized** — performance improvements
