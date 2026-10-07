#!/bin/bash
set -euo pipefail
# Terminate this throwaway instance after 20 minutes if the client disappears.
shutdown -h +20
install -d -m 0755 /opt/assignment
cat > /opt/assignment/index.html <<'HTML'
<!doctype html><html lang="en"><meta charset="utf-8"><title>Cloud infrastructure lab</title>
<h1>Session 19 infrastructure verified</h1><p>Vimal Kumar Yadav · 24BCS10273</p>
<p>This response is served by the Terraform-managed EC2 instance.</p></html>
HTML
cat > /etc/systemd/system/assignment-http.service <<'UNIT'
[Unit]
Description=Session 19 temporary HTTP evidence
After=network-online.target
[Service]
User=nobody
ExecStart=/usr/bin/python3 -m http.server 8080 --bind 0.0.0.0 --directory /opt/assignment
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now assignment-http
