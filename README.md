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

## Installation

```bash
# Make executable
chmod +x sufdo.py

# Optional: create symlink in PATH
sudo ln -s $(pwd)/sufdo.py /usr/local/bin/sufdo
```

## Usage

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

## Examples

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
```

## Command History

All executed commands are stored in `~/.sufdo/history.json`

## Aliases

Aliases are stored in `~/.sufdo/aliases.json`

## License

MIT

---

**⚠️ Disclaimer:** Use responsibly. The authors are not responsible for any damage caused by misuse of this tool.
