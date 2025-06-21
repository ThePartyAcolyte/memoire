#!/bin/bash
# MnemoX Lite - Raspberry Pi Installation Script
# Automated setup for Raspberry Pi OS

set -e  # Exit on any error

echo "🍓 MnemoX Lite - Raspberry Pi Setup"
echo "===================================="

# Check if running on Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "📍 Continuing anyway..."
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    sqlite3 \
    curl \
    htop \
    ufw

# Create project directory
echo "📁 Creating project directory..."
PROJECT_DIR="/home/pi/mnemox-lite"
if [ -d "$PROJECT_DIR" ]; then
    echo "📂 Directory already exists, backing up..."
    sudo mv "$PROJECT_DIR" "${PROJECT_DIR}.backup.$(date +%s)"
fi

# Clone repository
echo "⬇️  Cloning MnemoX Lite repository..."
cd /home/pi
git clone https://github.com/ThePartyAcolyte/mnemox-lite.git
cd mnemox-lite
git checkout remote-deployment

# Set ownership
sudo chown -R pi:pi /home/pi/mnemox-lite

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create data directory
echo "💾 Creating data directory..."
mkdir -p data
mkdir -p logs

# Create environment file template
echo "⚙️  Creating environment configuration..."
cat > .env << EOF
# MnemoX Lite Configuration for Raspberry Pi
GOOGLE_API_KEY=your_google_api_key_here
PORT=8080
ENABLE_GUI=false

# Pi-specific optimizations
MAX_CONCURRENT_CONNECTIONS=5
MAX_MESSAGE_SIZE=524288
PING_INTERVAL=60
EOF

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/mnemox-lite.service > /dev/null << EOF
[Unit]
Description=MnemoX Lite - Semantic Memory Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/mnemox-lite
Environment=PATH=/home/pi/mnemox-lite/venv/bin
ExecStart=/home/pi/mnemox-lite/venv/bin/python run_pi.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/pi/mnemox-lite/data /home/pi/mnemox-lite/logs

[Install]
WantedBy=multi-user.target
EOF

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 8080/tcp
sudo ufw --force enable

# Set permissions
echo "🔐 Setting permissions..."
chmod +x run_pi.py
chmod 644 .env
chmod -R 755 data logs

# Enable and start service (will fail without API key, but that's expected)
echo "🚀 Configuring service..."
sudo systemctl daemon-reload
sudo systemctl enable mnemox-lite

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit the API key:"
echo "   nano /home/pi/mnemox-lite/.env"
echo "   # Replace 'your_google_api_key_here' with your actual key"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl start mnemox-lite"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status mnemox-lite"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u mnemox-lite -f"
echo ""
echo "5. Get your Pi's IP address:"
echo "   hostname -I"
echo ""
echo "📱 Your clients will connect to: ws://YOUR_PI_IP:8080"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl stop mnemox-lite     # Stop service"
echo "   sudo systemctl restart mnemox-lite  # Restart service"
echo "   sudo systemctl disable mnemox-lite  # Disable auto-start"
echo ""
echo "🍓 Happy memory augmentation!"