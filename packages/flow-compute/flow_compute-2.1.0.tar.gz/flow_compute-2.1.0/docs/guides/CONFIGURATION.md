# Configuration

Flow SDK configuration through environment variables and config files.

## Environment Variables

### Core
- `FLOW_PROVIDER`: Provider selection (default: `fcp`)
- `FCP_API_KEY`: API authentication token

### API Endpoints
- `FCP_API_URL`: API base URL (default: `https://api.mlfoundry.com`)
- `FCP_WEB_URL`: Dashboard URL (default: `https://app.mlfoundry.com`)
- `FCP_DOCS_URL`: Documentation URL (default: `https://docs.mlfoundry.com`)
- `FCP_STATUS_URL`: Status page URL (default: `https://status.mlfoundry.com`)

### Instance Types
Configure user-friendly names to provider IDs:

```bash
export FCP_INSTANCE_MAPPINGS='{"a100": "instance-id-123", "h100": "instance-id-456"}'
```

Or use `~/.flow/instance_types.json`:
```json
{
  "a100": "instance-id-123",
  "h100": "instance-id-456",
  "4xa100": "instance-id-789"
}
```

### Provider Settings
- `FCP_DEFAULT_PROJECT`: Default project
- `FCP_DEFAULT_REGION`: Default region (default: `us-central1-a`)
- `FCP_SSH_USER`: SSH username (default: `ubuntu`)
- `FCP_SSH_PORT`: SSH port (default: `22`)
- `FCP_LOG_DIR`: Provider logs (default: `/var/log/foundry`)
- `FLOW_LOG_DIR`: SDK logs (default: `/var/log/flow`)

## Configuration Files

Load order (later overrides earlier):
1. `~/.flow/config.yaml` - User config
2. `flow.yaml` - Project config
3. Environment variables

Example `~/.flow/config.yaml`:
```yaml
provider: fcp
fcp:
  project: my-project
  region: us-east-1
  ssh_keys:
    - my-key-name
```

## Custom Providers

Configure a different provider:

```bash
export FLOW_PROVIDER=custom
export FCP_API_URL=https://api.custom-provider.com
export FCP_INSTANCE_MAPPINGS='{"gpu-small": "t2.micro", "gpu-large": "p3.2xlarge"}'
export FCP_SSH_USER=ec2-user
```

## Security

- Never commit API keys
- Use environment variables for credentials
- Hidden directories excluded from git

## Troubleshooting

**Instance types not recognized:**
- Check JSON formatting in `FCP_INSTANCE_MAPPINGS`
- Verify `~/.flow/instance_types.json` validity
- Use `FCP_INCLUDE_DEFAULT_MAPPINGS=true`

**API connection issues:**
- Verify `FCP_API_URL`
- Check API key validity
- Ensure network connectivity