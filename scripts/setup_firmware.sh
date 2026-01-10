#!/bin/bash
# Setup script for ESP32-CAM firmware development
# Script cài đặt cho phát triển firmware ESP32-CAM

set -e

echo "========================================"
echo "ESP32-CAM Firmware Setup"
echo "Cài đặt Firmware ESP32-CAM"
echo "========================================"
echo ""

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    echo "Unknown OS: $OSTYPE"
    OS="unknown"
fi

echo "Detected OS: $OS"
echo ""

# Arduino CLI installation
echo "Step 1: Checking Arduino CLI..."
if command -v arduino-cli &> /dev/null; then
    echo "✓ Arduino CLI already installed"
    arduino-cli version
else
    echo "Installing Arduino CLI..."
    
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
        sudo mv bin/arduino-cli /usr/local/bin/
    elif [[ "$OS" == "mac" ]]; then
        brew install arduino-cli
    else
        echo "Please install Arduino CLI manually from:"
        echo "https://arduino.github.io/arduino-cli/latest/installation/"
        exit 1
    fi
fi

# Initialize Arduino CLI
echo ""
echo "Step 2: Initializing Arduino CLI..."
arduino-cli config init

# Install ESP32 board support
echo ""
echo "Step 3: Installing ESP32 board support..."
arduino-cli config add board_manager.additional_urls https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32

# Install required libraries
echo ""
echo "Step 4: Installing required libraries..."
arduino-cli lib install "RF24"

# List available boards
echo ""
echo "Step 5: Verifying ESP32 installation..."
arduino-cli board listall esp32

# Instructions
echo ""
echo "========================================"
echo "Setup Complete! / Cài đặt hoàn tất!"
echo "========================================"
echo ""
echo "To compile and upload firmware:"
echo "Để biên dịch và tải firmware:"
echo ""
echo "1. Connect ESP32-CAM via USB-to-Serial adapter"
echo "   Kết nối ESP32-CAM qua adapter USB-to-Serial"
echo ""
echo "2. Put ESP32-CAM in programming mode:"
echo "   Đưa ESP32-CAM vào chế độ lập trình:"
echo "   - Connect GPIO 0 to GND"
echo "   - Press reset button"
echo ""
echo "3. Find serial port:"
echo "   Tìm cổng serial:"
echo "   arduino-cli board list"
echo ""
echo "4. Compile:"
echo "   Biên dịch:"
echo "   cd firmware/esp32-cam"
echo "   arduino-cli compile --fqbn esp32:esp32:esp32cam helmet_camera_rf"
echo ""
echo "5. Upload:"
echo "   Tải lên:"
echo "   arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32cam helmet_camera_rf"
echo "   (Replace /dev/ttyUSB0 with your port)"
echo ""
echo "6. Disconnect GPIO 0 from GND and press reset"
echo "   Ngắt kết nối GPIO 0 khỏi GND và nhấn reset"
echo ""

echo "Alternative: Use Arduino IDE"
echo "Thay thế: Sử dụng Arduino IDE"
echo ""
echo "1. Install Arduino IDE from https://www.arduino.cc/"
echo "2. Add ESP32 board support in Preferences"
echo "3. Install RF24 library from Library Manager"
echo "4. Open helmet_camera_rf.ino"
echo "5. Select board: AI Thinker ESP32-CAM"
echo "6. Select port and upload"
echo ""
