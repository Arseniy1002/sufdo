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

## Installation

```bash
# Make executable
chmod +x sufdo.py

# Optional: create symlink in PATH
sudo ln -s $(pwd)/sufdo.py /usr/local/bin/sufdo
```

## Basic Usage

```bash
# Run command as root (default)
python sufdo.py <command>

# Run command as specific user
python sufdo.py -u <username> <command>

# Run with timeout (30 seconds)
python sufdo.py -t 30 <command>

# Show version
python sufdo.py --version
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
python sufdo.py apt update
python sufdo.py systemctl restart nginx

# Execute with timeout
python sufdo.py -t 60 python long_script.py

# Re-run last command
python sufdo.py --last
python sufdo.py -!  # shorthand

# View history
python sufdo.py --history

# Create aliases
python sufdo.py --alias build="npm run build"
python sufdo.py --alias deploy="git push && ssh server deploy"

# List aliases
python sufdo.py --alias

# Show flex message after success
python sufdo.py --flex ls -la

# Disable colors
python sufdo.py --no-color ls -la

# Go full chaos
python sufdo.py --combo --flex rm -rf /tmp/*
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
