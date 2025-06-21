# MnemoX Lite - Raspberry Pi Setup Guide

Complete guide for deploying MnemoX Lite on Raspberry Pi 3/4 for local network access.

## 🍓 Prerequisites

### Hardware
- **Raspberry Pi 3 or 4** (Pi 3 minimum, Pi 4 recommended)
- **MicroSD card** (16GB minimum, 32GB recommended)
- **Stable internet connection** (for Google API calls)
- **Local network access**

### Software
- **Raspberry Pi OS Lite (64-bit)** - Recommended
- **Google AI API Key** - [Get here](https://makersuite.google.com/app/apikey)

## 🚀 Quick Installation

### Method 1: Automated Script (Recommended)

1. **Boot your Pi** with Raspberry Pi OS
2. **Enable SSH** (if using headless):
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```
3. **Run the installer**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/ThePartyAcolyte/mnemox-lite/remote-deployment/install_pi.sh | bash
   ```
4. **Set your API key**:
   ```bash
   nano /home/pi/mnemox-lite/.env
   # Replace: GOOGLE_API_KEY=your_google_api_key_here
   ```
5. **Start the service**:
   ```bash
   sudo systemctl start mnemox-lite
   ```

### Method 2: Manual Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv git sqlite3

# Clone repository
cd /home/pi
git clone https://github.com/ThePartyAcolyte/mnemox-lite.git
cd mnemox-lite
git checkout remote-deployment

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GOOGLE_API_KEY

# Run server
python run_pi.py
```

## 🌐 Network Configuration

### Get Your Pi's IP Address
```bash
hostname -I
# Example output: 192.168.1.100
```

### Test Local Connection
```bash
# On the Pi
curl -I http://localhost:8080

# From another device on same network
curl -I http://192.168.1.100:8080
```

### Configure Router (Optional)
- **Static IP**: Assign fixed IP to your Pi
- **Port Forwarding**: For external access (port 8080)
- **Local DNS**: Set hostname like `mnemox.local`

## 📱 Client Configuration

### For Claude Desktop
Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mnemox-pi": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-websocket", "ws://192.168.1.100:8080"],
      "env": {}
    }
  }
}
```

### For Multiple Devices
All devices on your local network can use the same configuration:
- **Desktop**: `ws://192.168.1.100:8080`
- **Laptop**: `ws://192.168.1.100:8080`  
- **Work Computer**: `ws://192.168.1.100:8080`

## 🔧 Service Management

### Systemd Service Commands
```bash
# Start service
sudo systemctl start mnemox-lite

# Stop service
sudo systemctl stop mnemox-lite

# Restart service
sudo systemctl restart mnemox-lite

# Check status
sudo systemctl status mnemox-lite

# View logs
sudo journalctl -u mnemox-lite -f

# Enable auto-start on boot
sudo systemctl enable mnemox-lite

# Disable auto-start
sudo systemctl disable mnemox-lite
```

### Manual Operation
```bash
# Run in foreground (for testing)
cd /home/pi/mnemox-lite
source venv/bin/activate
python run_pi.py

# Run in background
nohup python run_pi.py > logs/mnemox.log 2>&1 &
```

## 📊 Monitoring & Performance

### System Resources
```bash
# Check memory usage
free -h

# Check CPU usage
htop

# Check disk space
df -h

# Monitor Pi temperature
vcgencmd measure_temp
```

### MnemoX Specific
```bash
# Check service logs
sudo journalctl -u mnemox-lite --since "1 hour ago"

# Monitor data directory
ls -la /home/pi/mnemox-lite/data/

# Check database size
sqlite3 /home/pi/mnemox-lite/data/mnemox.db ".schema"
```

### Performance Tips for Pi 3
- **Memory**: ~300-500MB usage expected
- **CPU**: Modest usage, spikes during embedding
- **Storage**: SSD via USB improves performance
- **Cooling**: Heat sink recommended for sustained use

## 🔒 Security Configuration

### Firewall Setup
```bash
# Enable firewall
sudo ufw enable

# Allow MnemoX port
sudo ufw allow 8080/tcp

# Allow SSH (if using)
sudo ufw allow ssh

# Check status
sudo ufw status
```

### SSL/TLS (Optional)
For HTTPS access, set up reverse proxy:

```bash
# Install nginx
sudo apt install nginx

# Configure SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
```

### Access Control
- Consider VPN for remote access
- Use strong API keys
- Regular security updates: `sudo apt update && sudo apt upgrade`

## 🐛 Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check logs
sudo journalctl -u mnemox-lite --no-pager

# Common causes:
# - Missing API key in .env
# - Permission issues
# - Port already in use
```

**Memory Issues**
```bash
# Check available memory
free -m

# If low memory:
# - Reduce max_concurrent_connections in config
# - Clear browser cache
# - Restart service periodically
```

**Network Connection Issues**
```bash
# Test local connectivity
ping 192.168.1.100

# Test WebSocket
wscat -c ws://192.168.1.100:8080

# Check firewall
sudo ufw status
```

**Performance Issues**
```bash
# Monitor system load
top

# Check temperature throttling
vcgencmd get_throttled

# Optimize:
# - Add heat sink/fan
# - Use faster SD card (Class 10/A1)
# - Consider Pi 4 upgrade
```

### Log Locations
- **System logs**: `/var/log/syslog`
- **Service logs**: `sudo journalctl -u mnemox-lite`
- **Application logs**: `/home/pi/mnemox-lite/logs/`

## 🔄 Updates & Maintenance

### Updating MnemoX Lite
```bash
cd /home/pi/mnemox-lite
git pull origin remote-deployment
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart mnemox-lite
```

### System Updates
```bash
# Regular system updates
sudo apt update && sudo apt upgrade -y

# Pi-specific updates
sudo rpi-update  # Use cautiously
```

### Backup Strategy
```bash
# Backup data directory
tar -czf mnemox-backup-$(date +%Y%m%d).tar.gz data/

# Full system backup (to external drive)
sudo dd if=/dev/mmcblk0 of=/media/usb/pi-backup.img bs=4M status=progress
```

## 📈 Performance Optimization

### Pi 3 Optimizations
- **GPU Memory**: `sudo raspi-config` → Advanced → Memory Split → 16MB
- **CPU Governor**: `sudo cpufreq-set -g performance`
- **Swap**: Increase if needed: `sudo dphys-swapfile swapoff && sudo nano /etc/dphys-swapfile`
- **SD Card**: Use high-quality Class 10 or better

### Pi 4 Optimizations
- **USB 3.0 SSD**: Boot from SSD for better I/O
- **More RAM**: 4GB+ models handle concurrent connections better
- **Better cooling**: Official fan case or heat sinks

## 🌟 Advanced Features

### Multiple Pi Setup
- **Load balancing**: Multiple Pis with HAProxy
- **Redundancy**: Primary + backup Pi configuration
- **Shared storage**: Network-attached storage for data

### External Access
- **Dynamic DNS**: DuckDNS, No-IP for remote access
- **VPN**: OpenVPN server on Pi for secure access
- **Cloudflare Tunnel**: Zero-config external access

---

## 📞 Quick Reference

### Essential Commands
```bash
# Service status
sudo systemctl status mnemox-lite

# View logs
sudo journalctl -u mnemox-lite -f

# Test connection
curl -I http://localhost:8080

# Get Pi IP
hostname -I

# Restart service
sudo systemctl restart mnemox-lite
```

### File Locations
- **Service**: `/etc/systemd/system/mnemox-lite.service`
- **Application**: `/home/pi/mnemox-lite/`
- **Data**: `/home/pi/mnemox-lite/data/`
- **Logs**: `/home/pi/mnemox-lite/logs/`
- **Config**: `/home/pi/mnemox-lite/.env`

### Network Info
- **Local URL**: `ws://[PI_IP_ADDRESS]:8080`
- **Default Port**: `8080`
- **Protocol**: WebSocket (ws://)
- **TLS**: Not enabled by default

**Your Pi is now a centralized memory server! 🧠🍓**