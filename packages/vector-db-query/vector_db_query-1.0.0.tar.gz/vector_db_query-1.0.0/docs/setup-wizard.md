# Data Sources Setup Wizard

The Vector DB Query system includes an interactive setup wizard to help you configure data sources quickly and easily.

## Overview

The setup wizard guides you through:
- Selecting data sources to configure
- Entering authentication credentials
- Configuring sync settings
- Testing connections
- Saving configuration

## Quick Start

```bash
# Run the setup wizard
vdq setup

# Show quick start guide
vdq quickstart

# Create example configuration
vdq quickstart --example

# Show credential obtaining guide
vdq quickstart --show-credentials

# Reset configuration
vdq reset
```

## Setup Wizard Features

### 1. Source Selection
Choose which data sources you want to configure:
- Gmail (IMAP/OAuth2)
- Fireflies.ai (API)
- Google Drive (OAuth2)

### 2. Gmail Configuration
- Email address
- OAuth2 credentials file
- Folder selection (INBOX, Sent, Drafts, etc.)
- Initial history days
- Advanced filters (sender whitelist/blacklist)

### 3. Fireflies Configuration
- API key (stored securely in keyring)
- Webhook settings (optional)
- Meeting duration filters
- Platform filters (Zoom, Teams, etc.)
- User inclusion/exclusion lists

### 4. Google Drive Configuration
- OAuth2 credentials file
- Search patterns (e.g., "Notes by Gemini")
- Specific folder IDs (optional)
- Shared drives and shortcuts options

### 5. Processing Options
- Deduplication settings
  - Similarity threshold
  - Cross-source checking
- Performance settings
  - Parallel processing
  - Concurrent items limit
- NLP processing
  - Entity extraction
  - Sentiment analysis
  - Key phrase extraction

### 6. Connection Testing
The wizard can test each configured source to ensure:
- Authentication works
- API access is granted
- Network connectivity is good

## Configuration Storage

The wizard saves configuration to:
- `config/default.yaml` - Main configuration file
- `.gmail_token.json` - Gmail OAuth token (gitignored)
- `.gdrive_token.json` - Google Drive OAuth token (gitignored)
- System keyring - Sensitive API keys

## Security Best Practices

1. **OAuth Credentials**
   - Download from Google Cloud Console
   - Never commit to version control
   - Use separate credentials for production

2. **API Keys**
   - Stored in system keyring when possible
   - Use environment variables as fallback
   - Rotate regularly

3. **Token Files**
   - Automatically gitignored
   - Contains refresh tokens
   - Delete to force re-authentication

## Example Configuration

Run `vdq quickstart --example` to create:
- `config/datasources.example.yaml` - Full example configuration
- `.env.example` - Environment variables template

## Common Setup Scenarios

### Personal Email and Meetings
```bash
vdq setup
# Enable: Gmail, Google Drive
# Skip: Fireflies (if not using)
```

### Team Collaboration
```bash
vdq setup
# Enable: All sources
# Configure: Shared drives, team meeting platforms
```

### Minimal Setup
```bash
vdq setup --source gmail
# Configure only Gmail
```

## Troubleshooting

### OAuth2 Issues
- Ensure APIs are enabled in Google Cloud Console
- Add your email as a test user
- Check OAuth consent screen configuration

### Connection Failures
- Verify network connectivity
- Check firewall settings
- Ensure correct API permissions

### Missing Credentials
- Run `vdq quickstart --show-credentials` for detailed instructions
- Visit provider websites to generate API keys
- Check file paths are correct

## Next Steps

After setup:
1. Run initial sync: `vdq datasources sync`
2. Monitor progress: `vdq monitor`
3. Configure filters: `vdq datasources configure`
4. Check status: `vdq datasources status`

## Advanced Configuration

For advanced users, edit `config/default.yaml` directly to configure:
- Complex filter rules
- Custom NLP settings
- Advanced deduplication options
- Performance tuning

See [Configuration Reference](configuration.md) for all available options.