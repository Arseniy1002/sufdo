# sufdo

**Super User Fkin Do**

A sudo-like utility for executing commands with elevated privileges.

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

# Show version
python sufdo.py --version
```

## Examples

```bash
python sufdo.py apt update
python sufdo.py -u www-data ls /var/www
python sufdo.py systemctl restart nginx
```

## License

MIT
