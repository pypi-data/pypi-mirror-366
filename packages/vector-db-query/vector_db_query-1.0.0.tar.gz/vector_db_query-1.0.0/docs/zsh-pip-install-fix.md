# Fix for zsh "no matches found" Error

When installing Python packages with extras in zsh, you may encounter:
```
zsh: no matches found: vector-db-query[monitoring]
```

## Solutions

### Option 1: Escape the brackets (Recommended)
```bash
pip install vector-db-query\[monitoring\]
```

### Option 2: Use quotes
```bash
pip install "vector-db-query[monitoring]"
```

### Option 3: Use single quotes
```bash
pip install 'vector-db-query[monitoring]'
```

### Option 4: Disable globbing temporarily
```bash
noglob pip install vector-db-query[monitoring]
```

### Option 5: Switch to bash for the command
```bash
bash -c "pip install vector-db-query[monitoring]"
```

## Why this happens

- zsh treats square brackets `[]` as glob patterns for filename expansion
- When no files match the pattern, zsh shows "no matches found"
- This is a common issue with zsh when installing Python packages with extras

## Permanent fix

Add this to your `~/.zshrc` to always disable globbing for pip:
```bash
alias pip='noglob pip'
```

Then reload your shell:
```bash
source ~/.zshrc
```