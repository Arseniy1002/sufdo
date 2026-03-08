# Day 2 Features - Safety Modes (v3.2.0)

## Planned Functions

### 1. --dry-run mode
- Preview command without execution
- Shows what would be run
- Exit code 0 always

### 2. --confirm mode
- Ask for confirmation before running
- Timeout support
- Custom prompt messages

### 3. --safe-mode
- Block destructive commands
- Blacklist: rm -rf, dd, mkfs, etc.
- Override with --force

### 4. --no-destructive
- Alias for safe-mode
- Prevents file deletion

### 5. --backup
- Create backup before operations
- Backup directory: ~/.sufdo/backups/
- Timestamped backups

## Implementation Status
- [ ] dry_run.py
- [ ] confirm.py  
- [ ] safe_mode.py
- [ ] backup.py
- [ ] blacklist.json
