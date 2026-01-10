# Raspberry Pi Camera RF Client
# Client camera RF cho Raspberry Pi

Alternative firmware implementation for Raspberry Pi-based helmet camera.

Triển khai firmware thay thế cho camera mũ bảo hiểm dựa trên Raspberry Pi.

## Hardware Requirements / Yêu cầu phần cứng

- **Raspberry Pi Zero W** or **Pi 4** (~500k - 1.5M VND)
- **Pi Camera Module V2** or **HQ Camera** (~300k - 1.2M VND)
- **nRF24L01+** module for telemetry (~30k VND)
- **5.8GHz RF Video Transmitter** (if needed) (~200k VND)
- **Power supply** (5V 2A minimum) (~50k VND)
- **3S LiPo Battery** with 5V regulator (~150k VND)

## Pin Connections / Kết nối chân

### nRF24L01+ to Raspberry Pi
```
nRF24L01+     Raspberry Pi
---------     ------------
VCC      -->  3.3V (Pin 1 or 17)
GND      -->  GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
CE       -->  GPIO 22 (Pin 15)
CSN      -->  GPIO 8 / CE0 (Pin 24)
SCK      -->  GPIO 11 / SCLK (Pin 23)
MOSI     -->  GPIO 10 / MOSI (Pin 19)
MISO     -->  GPIO 9 / MISO (Pin 21)
```

### Pi Camera
Connect via CSI ribbon cable to camera port.

## Installation / Cài đặt

### 1. Setup Raspberry Pi OS
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### 2. Enable SPI
```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
```

### 3. Install System Dependencies
```bash
# Python and pip
sudo apt install python3-pip python3-dev -y

# GPIO library
sudo apt install python3-rpi.gpio -y

# Camera library
sudo apt install python3-picamera -y

# RF24 library dependencies
sudo apt install libboost-python-dev librf24-dev -y
```

### 4. Install Python Dependencies
```bash
cd firmware/raspberry-pi
pip3 install -r requirements.txt
```

## Configuration / Cấu hình

Edit the configuration file `configs/camera_config.yaml`:

```yaml
camera:
  resolution: "640x480"
  fps: 30
  encoding: "h264"

rf_telemetry:
  channel: 76
  device_id: "HELMET_PI_01"
```

## Usage / Sử dụng

### Start Camera Client
```bash
cd firmware/raspberry-pi
python3 camera_rf_client.py
```

### Run as Service
Create systemd service `/etc/systemd/system/helmet-camera.service`:

```ini
[Unit]
Description=Helmet Camera RF Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/helmet-camera-streaming/firmware/raspberry-pi
ExecStart=/usr/bin/python3 camera_rf_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable helmet-camera.service
sudo systemctl start helmet-camera.service
```

### Check Status
```bash
sudo systemctl status helmet-camera.service
journalctl -u helmet-camera.service -f
```

## Features / Tính năng

- ✅ Pi Camera video capture / Chụp video từ Pi Camera
- ✅ nRF24L01+ telemetry transmission / Truyền telemetry qua nRF24L01+
- ✅ Battery monitoring / Giám sát pin
- ✅ Temperature monitoring / Giám sát nhiệt độ
- ✅ Automatic reconnection / Tự động kết nối lại
- ✅ Graceful shutdown / Tắt máy an toàn

## Performance / Hiệu suất

- **Video Resolution**: Up to 1920x1080 @ 30fps (Pi Camera V2)
- **Power Consumption**: ~2-3W (Pi Zero W) / ~5-7W (Pi 4)
- **Battery Life**: ~2-4 hours with 10000mAh power bank
- **Telemetry Range**: ~300m line-of-sight
- **Boot Time**: ~20-30 seconds

## Troubleshooting / Xử lý sự cố

### Camera Not Detected
```bash
# Check camera
vcgencmd get_camera

# Should show: supported=1 detected=1
# If not, check ribbon cable connection
```

### nRF24L01+ Not Working
```bash
# Test SPI
ls /dev/spi*
# Should show /dev/spidev0.0 and /dev/spidev0.1

# Check connections with multimeter
# Ensure 3.3V power (NOT 5V!)
```

### Permission Denied
```bash
# Add user to gpio and spi groups
sudo usermod -a -G gpio,spi,video pi
# Logout and login again
```

### High CPU Temperature
```bash
# Check temperature
vcgencmd measure_temp

# If > 70°C, add heatsink or cooling
# Reduce camera resolution/fps
```

## Advantages over ESP32-CAM
## Ưu điểm so với ESP32-CAM

- ✅ Higher video quality (up to 1080p)
- ✅ More processing power
- ✅ Easier debugging (full Linux OS)
- ✅ More GPIO pins available
- ✅ Native Python support

## Disadvantages / Nhược điểm

- ❌ Higher power consumption / Tiêu thụ điện cao hơn
- ❌ Larger size / Kích thước lớn hơn
- ❌ Higher cost / Chi phí cao hơn
- ❌ Longer boot time / Thời gian khởi động lâu hơn

## License / Giấy phép

MIT License

## Support / Hỗ trợ

See main project documentation in `/docs` folder.
