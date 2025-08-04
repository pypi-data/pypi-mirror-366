# Fix for "unknown option `--json'" Error

## What This Error Means

The error "unknown option `--json'" occurs when:
- You're trying to use a `--json` flag with a command that doesn't support it
- The command expects a different format for JSON output
- You might be using an older version of a tool that doesn't have JSON support

## Common Scenarios and Solutions

### 1. PM2 Commands
If you're trying to get JSON output from PM2:

```bash
# ❌ Wrong (PM2 doesn't use --json)
pm2 status --json

# ✅ Correct - PM2 uses 'jlist' command for JSON
pm2 jlist

# ✅ Or use prettylist for formatted JSON
pm2 prettylist
```

### 2. Git Commands
Some git commands support JSON, others don't:

```bash
# ❌ Wrong
git status --json

# ✅ Use porcelain format instead
git status --porcelain

# ✅ Or for machine-readable output
git status --porcelain=v2
```

### 3. Vector DB Query Commands
If you're trying to get JSON output from vector-db-query:

```bash
# Check if the command supports --format json instead
vector-db-query query "your query" --format json

# Or check available options
vector-db-query query --help
```

## How to Find Correct Options

### 1. Check Help
Always check the help for available options:
```bash
command --help
# or
command -h
```

### 2. Check Documentation
Look for the command's documentation or man page:
```bash
man command
```

### 3. Common JSON Output Alternatives
Different tools use different flags for JSON output:
- `--json` (npm, gh cli)
- `--format json` (many CLI tools)
- `--output json` (AWS CLI, Azure CLI)
- `-o json` (kubectl)
- `jlist` or `json` subcommand (PM2)

## Specific PM2 JSON Commands

Since you're working with PM2, here are the JSON-related commands:

```bash
# Get process list as JSON
pm2 jlist

# Get specific process info as JSON
pm2 jlist | jq '.[] | select(.name=="ansera-monitor")'

# Pretty print JSON
pm2 prettylist

# Save process list
pm2 save

# Show ecosystem file in JSON format
cat ecosystem.config.js
```

## Quick Debug Steps

1. **Identify the command** that's giving the error
2. **Check its help**: `command --help`
3. **Look for output format options** like:
   - `--format`
   - `--output`
   - `-o`
   - Specific JSON subcommands
4. **Try without the flag** - some commands output JSON by default

## Example Fix Workflow

```bash
# If you were trying:
some-command --json

# First check help:
some-command --help | grep -i json

# Look for format options:
some-command --help | grep -i "format\|output"

# Try common alternatives:
some-command --format json
some-command --output json
some-command -o json
```

Need help with a specific command? Let me know which command is giving you this error!