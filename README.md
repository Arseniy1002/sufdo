# sufdo v4.0.0 - Ultimate Edition

**Super User Fkin Do** - The most feature-rich sudo alternative ever created.

> Because sometimes you just need to get shit done. With style.

## 🎯 Quick Stats

- **100+** command-line flags
- **200+** individual features
- **15** fun modes
- **10** safety features
- **5** notification methods
- **Unlimited** swag

## 📦 Installation

```bash
pip install -e .
```

## 🚀 Features by Category

### 🔇 Silent/Verbose Modes (4 flags)
| Flag | Description |
|------|-------------|
| `--silent`, `-q`, `--quiet` | Silent mode - only errors |
| `--verbose`, `-V` | Detailed output |
| `--debug` | Debug information |
| `--trace` | Execution tracing |

### 🛡️ Safety Modes (8 flags)
| Flag | Description |
|------|-------------|
| `--dry-run` | Preview without executing |
| `--confirm` | Ask for confirmation |
| `--safe-mode` | Block destructive commands |
| `--no-destructive` | Alias for safe-mode |
| `--backup` | Create backup before |
| `--restore` | Restore from backup |
| `--list-backups` | List all backups |
| `--cleanup-backups` | Clean old backups |

### 📝 Logging (5 flags)
| Flag | Description |
|------|-------------|
| `--log` | Log to file |
| `--log-file` | Custom log path |
| `--log-level` | Log level (DEBUG/INFO/WARN/ERROR) |
| `--syslog` | System logging |
| `--rotate-logs` | Log rotation |

### 🔔 Notifications (7 flags)
| Flag | Description |
|------|-------------|
| `--notify` | Toast notification |
| `--notify-sound` | With sound |
| `--discord` | Discord webhook |
| `--telegram` | Telegram bot |
| `--email` | Email notification |
| `--webhook-add` | Add webhook |
| `--webhook-list` | List webhooks |

### 📊 Statistics (5 flags)
| Flag | Description |
|------|-------------|
| `--stats` | Usage statistics |
| `--top` | Top commands |
| `--success-rate` | Success rate |
| `--export-stats` | Export to JSON/CSV |
| `--confidence` | Confidence level |

### 🔷 Aliases (8 flags)
| Flag | Description |
|------|-------------|
| `--alias` | Create/list aliases |
| `--alias-import` | Import from JSON |
| `--alias-export` | Export to JSON |
| `--alias-share` | Share via gist |
| `--alias-preset` | Preset packages |
| Presets: `git`, `docker`, `npm`, `python` |

### 🎭 Fun Modes (15 flags)
| Flag | Description |
|------|-------------|
| `--pirate` | Pirate phrases 🏴‍☠️ |
| `--cowboy` | Cowboy expressions 🤠 |
| `--yoda` | Yoda speak 🟢 |
| `--shakespeare` | Shakespeare style 🎭 |
| `--anime` | Anime quotes 🌸 |
| `--russian` | Russian expressions 🇷🇺 |
| `--rainbow` | Rainbow output 🌈 |
| `--dark` | Dark theme 🌑 |
| `--drama` | Dramatic messages 🎬 |
| `--pray` | Pray before execution 🙏 |
| `--yeet` | YEET mode 🚀 |
| `--sus` | Among Us mode 👨‍🚀 |
| `--hacker` | Hacker terminal 💻 |
| `--cursed` | Cursed mode 👻 |
| `--matrix` | Matrix rain 🟢 |
| `--bruh` | Bruh commentary |
| `--combo` | **ALL MODES AT ONCE** |

### ⚡ Performance (6 flags)
| Flag | Description |
|------|-------------|
| `--cache` | Cache command output |
| `--clear-cache` | Clear cache |
| `--parallel` | Parallel execution |
| `--background` | Background job |
| `--priority` | Priority (low/normal/high) |
| `--batch` | Batch file execution |

### 🔧 Integration (8 flags)
| Flag | Description |
|------|-------------|
| `--profile` | Use config profile |
| `--profile-list` | List profiles |
| `--profile-save` | Save profile |
| `--env` | Load .env file |
| `--env-set` | Set env variable |
| `--completion` | Shell completion (bash/zsh/fish) |
| `--validate` | Validate command |
| `--undo` | Undo last command |

### 📜 History & Core (10 flags)
| Flag | Description |
|------|-------------|
| `--history` | Command history |
| `--last`, `-!` | Re-run last |
| `--user`, `-u` | Run as user |
| `--version`, `-v` | Show version |
| `--timeout`, `-t` | Timeout seconds |
| `--flex` | Flex message |
| `--no-color` | Disable colors |
| `--command` | Command to execute |

## 💡 Examples

### Basic Usage
```bash
sufdo apt update
sufdo -u www-data ls /var/www
```

### Safety First
```bash
sufdo --dry-run rm -rf /tmp/*
sufdo --confirm --backup apt upgrade
sufdo --safe-mode rm important.txt  # Blocked!
```

### Maximum Fun
```bash
sufdo --pirate --flex ls -la
# [PIRATE] Ahoy matey!
# [FLEX] Command executed with extreme prejudice!

sufdo --yoda echo "Hello"
# [YODA] May the Force be with you.

sufdo --combo echo "CHAOS"
# ALL MODES AT ONCE!
```

### Notifications
```bash
# Setup Discord webhook
sufdo --webhook-add discord https://discord.com/api/webhooks/...

# Execute with notification
sufdo --discord apt update
```

### Statistics
```bash
sufdo --stats
# Usage Statistics:
#   Total commands: 150
#   Successful: 142
#   Failed: 8
#   Success rate: 94.7%

sufdo --top
# Top Commands:
#   git: 45 times
#   docker: 32 times
#   npm: 28 times
```

### Aliases
```bash
# Create alias
sufdo --alias gs="git status"

# Use alias
sufdo gs

# Import preset
sufdo --alias-preset git
sufdo --alias-preset docker
sufdo --alias-preset npm

# Export aliases
sufdo --alias-export my-aliases.json
```

### Performance
```bash
# Parallel execution
sufdo --parallel "cmd1" "cmd2" "cmd3"

# Background job
sufdo --background python long_script.py

# Batch execution
sufdo --batch commands.txt

# With caching
sufdo --cache apt update
```

### Profiles & Environment
```bash
# Save profile
sufdo --profile-save dev

# Use profile
sufdo --profile dev apt update

# Set env variable
sufdo --env-set API_KEY secret123

# Load .env file
sufdo --env python app.py
```

## 📁 Config Files

All stored in `~/.sufdo/`:

| File | Purpose |
|------|---------|
| `config.json` | User configuration |
| `history.json` | Command history (last 100) |
| `aliases.json` | User aliases |
| `confidence.json` | Confidence level |
| `stats.json` | Usage statistics |
| `cache.json` | Command cache |
| `webhooks.json` | Notification webhooks |
| `.env` | Environment variables |
| `sufdo.log` | Log file |
| `backups/` | Backup directory |
| `profiles/` | Config profiles |

## 🎮 Fun Mode Phrases

### Pirate 🏴‍☠️
> "Ahoy matey!", "Shiver me timbers!", "All hands on deck!", "Savvy?"

### Cowboy 🤠
> "Howdy partner!", "Yeehaw!", "This town ain't big enough!"

### Yoda 🟢
> "Do or do not, there is no try.", "May the Force be with you."

### Shakespeare 🎭
> "To be or not to be, that is the question."

### Anime 🌸
> "I'm gonna be the Pirate King!", "This is the power of friendship!"

### Russian 🇷🇺
> "Ё-моё!", "Ёперный театр!", "Ёлки-палки!"

## ⚠️ Disclaimer

Use responsibly. The authors are not responsible for:
- Any damage caused by misuse
- Confidence depletion from failed commands
- Excessive yeeting
- Accidental pirate transformations

## 📄 License

MIT

---

**Made with chaos, 100+ flags, and 200+ features** 🚀

**GitHub:** https://github.com/Arseniy1002/sufdo

**Version:** 4.0.0 Ultimate Edition
