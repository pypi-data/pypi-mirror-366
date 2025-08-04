# PM2 Directory Fix - Complete Solution

## The Problem
PM2 is looking for `ecosystem.config.js` in:
```
/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/ecosystem.config.js
```

But it's actually in:
```
/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query/ecosystem.config.js
```

## Immediate Solutions

### Solution 1: Always CD First (Simplest)
```bash
# Always do this before any PM2 command:
cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"
pm2 status
```

### Solution 2: Use Full Path
```bash
# From anywhere:
pm2 start "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query/ecosystem.config.js"
pm2 stop "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query/ecosystem.config.js"
```

### Solution 3: Create a Symlink (One-time setup)
```bash
# Create a symbolic link in the Ansera directory
cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera"
ln -s vector-db-query/ecosystem.config.js ecosystem.config.js

# Now PM2 will find it from either directory
```

### Solution 4: Add to Shell Profile (Permanent)
Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
# Vector DB Query PM2 alias
alias vdq='cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"'
alias vdq-pm2='cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query" && pm2'

# Usage:
# vdq-pm2 status
# vdq-pm2 start ecosystem.config.js
```

Then reload your shell:
```bash
source ~/.zshrc
```

## Quick Check - Is PM2 Running?

From the correct directory:
```bash
cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"
pm2 list
```

## Complete Reset (If Needed)

If things are confused:
```bash
# 1. Kill all PM2 processes
pm2 kill

# 2. Navigate to correct directory
cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"

# 3. Start fresh
pm2 start ecosystem.config.js --only ansera-monitor

# 4. Save the state
pm2 save
```

## Verify It's Working

1. Check status:
   ```bash
   cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"
   pm2 status
   ```

2. Access dashboard:
   - Open http://localhost:8501
   - You should see "PM2 is managing X Ansera services"

## Pro Tip: PM2 Startup Script

To avoid directory issues permanently:
```bash
# Save current PM2 process list
cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"
pm2 save

# Generate startup script
pm2 startup

# Follow the instructions it gives you
```

This ensures PM2 remembers where your services are, even after reboot!