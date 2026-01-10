#!/bin/bash
# Setup script for receiver station
# Script cài đặt cho trạm thu

set -e

echo "========================================"
echo "Helmet Camera RF Receiver Setup"
echo "Cài đặt Trạm Thu Camera Mũ Bảo Hiểm RF"
echo "========================================"
echo ""

# Check if running on supported system
if [[ ! -f /etc/os-release ]]; then
    echo "ERROR: Unsupported operating system"
    exit 1
fi

source /etc/os-release
echo "Detected OS: $PRETTY_NAME"
echo ""

# Update system
echo "Step 1: Updating system..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo ""
echo "Step 2: Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    libopencv-dev \
    python3-opencv \
    librf24-dev \
    ffmpeg \
    libavcodec-extra \
    v4l-utils \
    git

# Enable SPI (for nRF24L01+)
echo ""
echo "Step 3: Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt 2>/dev/null; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI enabled (reboot required)"
else
    echo "SPI already enabled"
fi

# Install Python dependencies
echo ""
echo "Step 4: Installing Python packages..."
cd "$(dirname "$0")/../receiver/backend"
pip3 install --user -r requirements.txt

# Create necessary directories
echo ""
echo "Step 5: Creating directories..."
mkdir -p ~/helmet-camera-streaming/logs
mkdir -p ~/helmet-camera-streaming/recordings

# Set permissions
echo ""
echo "Step 6: Setting permissions..."
sudo usermod -a -G video $USER
sudo usermod -a -G gpio $USER
sudo usermod -a -G spi $USER

# Test RF24 installation
echo ""
echo "Step 7: Testing RF24 installation..."
if python3 -c "import RF24" 2>/dev/null; then
    echo "✓ RF24 library installed successfully"
else
    echo "⚠ RF24 library not found, attempting manual install..."
    pip3 install --user RF24
fi

# Test OpenCV installation
echo ""
echo "Step 8: Testing OpenCV installation..."
if python3 -c "import cv2" 2>/dev/null; then
    echo "✓ OpenCV installed successfully"
else
    echo "✗ OpenCV installation failed"
fi

# Configure firewall (if UFW is installed)
if command -v ufw &> /dev/null; then
    echo ""
    echo "Step 9: Configuring firewall..."
    sudo ufw allow 8080/tcp comment "Helmet Camera Dashboard"
    sudo ufw allow 8081/tcp comment "Helmet Camera WebSocket"
fi

echo ""
echo "========================================"
echo "Setup Complete! / Cài đặt hoàn tất!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Reboot if SPI was just enabled: sudo reboot"
echo "2. Configure settings in configs/receiver_config.yaml"
echo "3. Start receiver: cd receiver/backend && python3 app.py"
echo "4. Open dashboard: http://localhost:8080"
echo ""
echo "Các bước tiếp theo:"
echo "1. Khởi động lại nếu vừa bật SPI: sudo reboot"
echo "2. Cấu hình trong configs/receiver_config.yaml"
echo "3. Khởi động trạm thu: cd receiver/backend && python3 app.py"
echo "4. Mở dashboard: http://localhost:8080"
echo ""
