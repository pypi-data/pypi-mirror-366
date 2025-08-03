# Manual GPUd Setup for GPU Health Monitoring

If you've started GPU instances through the console or other means without Flow's startup scripts, you can manually install GPUd to enable GPU health monitoring.

## Quick Install

SSH into your GPU instance and run:

```bash
# Install GPUd
curl -fsSL https://pkg.gpud.dev/install.sh | sh -s v0.5.1

# Start GPUd in private mode (no external connectivity)
sudo gpud up --private --web-address="127.0.0.1:15132"
```

## Verify Installation

After installation, verify GPUd is running:

```bash
# Check if GPUd is responding
curl http://localhost:15132/healthz

# View GPU metrics
curl http://localhost:15132/v1/gpu | jq
```

## Enable Flow Health Monitoring

Once GPUd is installed, Flow health commands will automatically detect and use it:

```bash
# Check health of your task
flow health --task <task-name>

# View GPU metrics across all tasks
flow health --gpu
```

## Systemd Service (Optional)

For persistent monitoring across reboots, create a systemd service:

```bash
sudo cat > /etc/systemd/system/gpud.service << 'EOF'
[Unit]
Description=GPUd Health Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/gpud up --private --web-address="127.0.0.1:15132"
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable gpud
sudo systemctl start gpud
```

## Notes

- GPUd runs in private mode with no external connectivity for security
- The default port 15132 is only accessible from localhost
- Flow automatically detects GPUd when checking GPU health
- Tasks started with `flow run` include GPUd automatically