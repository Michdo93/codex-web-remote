#!/bin/bash
export DISPLAY=:99

# 1. Virtual Framebuffer
Xvfb :99 -screen 0 1280x800x24 &
sleep 2

# 2. Lightweight Window Manager
openbox &
sleep 1

# 3. Emergency VNC Server (Password Protected)
x11vnc -display :99 -rfbauth /root/.vnc/passwd -forever -bg -quiet

# 4. Codex Desktop (Bypassing sandbox for root execution)
codex-desktop --no-sandbox &
sleep 3

# 5. Flask Web Server in Foreground
cd /opt/codex-web
exec python3 server.py
