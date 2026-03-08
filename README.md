# sufdo

**Super User Fkin Do**

A sudo-like utility for executing commands with elevated privileges. Because sometimes you just need to get shit done.

## Features

- Execute commands with elevated privileges
- Command history tracking
- Re-run last command with `--last`
- Timeout support
- Custom aliases
- Flex messages after successful execution
- Colored output
- **Confidence system** - your confidence goes up/down based on command success
- **Silent/Verbose modes** - control output verbosity
- **Debug/Trace modes** - detailed debugging information
- **Logging** - log all commands to file
- **Auto-commit scheduler** - 200 features rolling out over 10 days

## Roadmap

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for the full roadmap.

**Current version:** 3.1.0

**Coming soon:**
- Day 2: Safety modes (--dry-run, --confirm, --safe-mode)
- Day 3: Logging features (--log, --log-file, --syslog)
- Day 4: Notifications (--notify, --discord, --telegram)
- Day 5: Statistics (--stats, --top, --success-rate)
- And 150+ more features!

## Installation

```bash
# Install from source
pip install .

# Or install in editable mode (for development)
pip install -e .
```

After installation, you can use `sufdo` directly:
```bash
sufdo --version
sufdo ls -la
```

## ROFL Modes (UNIQUE FEATURES!)

### Drama Mode
```bash
python sufdo.py --drama apt update
# [DRAMA] INITIATING DESTRUCTION SEQUENCE...
```

### Pray Mode
```bash
python sufdo.py --pray apt update
# [PRAY] In the name of Linus Torvalds we trust...
```

### YEET Mode
```bash
python sufdo.py --yeet apt update
# [YEET] YEET! Command flying to the kernel!
```

### Sus Mode (Among Us)
```bash
python sufdo.py --sus apt update
# [SUS] Among us... this command looks sus...
```

### Hacker Mode
```bash
python sufdo.py --hacker apt update
# [+] Accessing mainframe...
# [+] Bypassing firewall...
# [+] Injecting SQL...
```

### Cursed Mode
```bash
python sufdo.py --cursed apt update
# [CURSED] t̷h̷i̷s̷ ̷c̷o̷m̷m̷a̷n̷d̷ ̷i̷s̷ ̷c̷u̷r̷s̷e̷d̷
```

### Matrix Mode
```bash
python sufdo.py --matrix apt update
# Matrix rain effect before execution
```

### Bruh Mode
```bash
python sufdo.py --bruh apt update
# Adds bruh commentary after execution
```

### COMBO MODE (Maximum Chaos)
```bash
python sufdo.py --combo apt update
# ALL MODES AT ONCE
```

## Confidence System

Your confidence level changes based on command success/failure:

```bash
# Check confidence
python sufdo.py --confidence
# Confidence Level: [####################] 100%
# MAXIMUM CONFIDENCE! YOU ARE UNSTOPPABLE!
```

- Success: +5-15 confidence
- Failure: -5-20 confidence
- At 0%: You need to touch some grass

## More Examples

```bash
# Basic execution
sufdo apt update
sufdo systemctl restart nginx

# Execute with timeout
sufdo -t 60 python long_script.py

# Re-run last command
sufdo --last
sufdo -!  # shorthand

# View history
sufdo --history

# Create aliases
sufdo --alias build="npm run build"
sufdo --alias deploy="git push && ssh server deploy"

# List aliases
sufdo --alias

# Show flex message after success
sufdo --flex ls -la

# Disable colors
sufdo --no-color ls -la

# Go full chaos
sufdo --combo --flex rm -rf /tmp/*
```

## Command History

All executed commands are stored in `~/.sufdo/history.json`

## Aliases

Aliases are stored in `~/.sufdo/aliases.json`

## Confidence

Confidence level is stored in `~/.sufdo/confidence.json`

## License

MIT

---

**⚠️ Disclaimer:** Use responsibly. The authors are not responsible for any damage caused by misuse of this tool. Or for any confidence depletion resulting from failed commands.

**🎭 Made with chaos and questionable decisions.**
