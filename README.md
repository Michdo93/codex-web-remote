# Autonomous Headless Codex Desktop on Proxmox LXC (Debian 13)

Deploy an autonomous, headless instance of **Codex Desktop** inside a Proxmox LXC container running **Debian 13 (Trixie)**. This project includes a complete virtual desktop stack (`Xvfb`, `openbox`, `x11vnc`), a custom lightweight full-screen web wrapper (`Flask` + `FFmpeg`), and pre-configured **openHAB MCP Server** integration via `mcp-remote`.

---

## Prerequisites & Proxmox Configuration

1. **LXC Container Creation**: 
   - Recommended OS template: **Debian 13 (Standard)**
   - **Important**: Ensure **Nest (Nesting)** is enabled in the Proxmox LXC options (`Features` -> `Nesting: Enabled`), as Electron/Chromium requires it.
   - Allocate sufficient storage and RAM (at least 2GB RAM / 10GB Disk).

---

## Complete Installation Guide

Run the following commands directly inside your root SSH shell of the Debian 13 LXC container.

### Step 1: System Dependencies & Toolchain
Update the system and install all required display drivers, window managers, streaming tools, and Node.js:

```bash
apt update && apt upgrade -y
apt install -y \
    xvfb \
    openbox \
    x11vnc \
    ffmpeg \
    xdotool \
    chromium \
    xdg-utils \
    nodejs \
    npm \
    curl \
    git \
    dos2unix
```

### Step 2: Install Rust Toolchain (Required for Codex/System Packages if building dependencies)

```bash
curl --proto '=https' --tlsv1.2 -sSf [https://sh.rustup.rs](https://sh.rustup.rs) | sh -s -- -y
source "$HOME/.cargo/env"
```

### Step 3: Install Codex Desktop Package

Download and install your Codex Desktop `.deb` package (adjust path/filename to your local package build):

```bash
dpkg -i /path/to/codex-desktop*.deb
apt --fix-broken install -y
```

### Step 4: Setup VNC Password

Configure a secure VNC password for emergency remote access:

```bash
mkdir -p /root/.vnc
x11vnc -storepasswd "YOUR_SECURE_PASSWORD" /root/.vnc/passwd
chmod 600 /root/.vnc/passwd
```

### Step 5: Configure MCP Server (openHAB Integration)

Create or update the Codex configuration file at `/root/.config/Codex/config.toml` (or `~/.codex/config.toml` depending on your version):

```toml
[mcp_servers.openhab]
command = "npx"
args = [
  "-y",
  "mcp-remote",
  "http://<YOUR_OPENHAB_IP>:8081/sse",
  "--allow-http"
]
```

### Step 6: Deploy Project Files

1. Create the project directory:
```bash
mkdir -p /opt/codex-web
```

2. Place `server.py`, `requirements.txt`, `start-codex-headless.sh`, and `codex-web.service` into their respective system locations:
* Copy `server.py` and `requirements.txt` to `/opt/codex-web/`
* Copy `start-codex-headless.sh` to `/usr/local/bin/start-codex-headless.sh`
* Copy `codex-web.service` to `/etc/systemd/system/codex-web.service`

3. Set proper permissions and clean line endings:
```bash
dos2unix /usr/local/bin/start-codex-headless.sh
chmod +x /usr/local/bin/start-codex-headless.sh
```

4. Install Python dependencies:
```bash
pip3 install -r /opt/codex-web/requirements.txt --break-system-packages
```

---

## First-Time Login (OAuth Authentication)

Because Codex requires an initial OpenAI/ChatGPT sign-in, you must authenticate once via VNC:

1. Connect via any VNC Viewer to: `your-lxc-ip:5900` (Password set in Step 4).
2. If Codex requests a browser login, click **"Browser didn't open"**, copy the authentication URL, and paste it into a browser running on your workstation, or open Chromium directly inside the container via SSH:
```bash
export DISPLAY=:99
chromium --no-sandbox "YOUR_OAUTH_URL" &
```

3. Complete the login flow. Session tokens are saved under `/root/.config/Codex/`.

---

## Service Activation & Startup

Enable and start the systemd service for autonomous background operation:

```bash
systemctl daemon-reload
systemctl enable --now codex-web.service
```

Check service health:

```bash
systemctl status codex-web.service
```

---

## Accessing the Web Remote

Open your browser and navigate to:

```text
http://<YOUR_LXC_IP>:8080
```

You will see a clean, full-screen, interactive remote session of your Codex instance with direct click and keyboard support, fully integrated with your local openHAB smart home environment!
