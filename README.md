# Helmet Camera RF Streaming System
# Hệ thống Truyền Video Camera Mũ Bảo Hiểm qua RF

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-ESP32%20%7C%20RaspberryPi-blue)]()
[![RF](https://img.shields.io/badge/RF-2.4GHz%20%7C%205.8GHz-green)]()

A complete RF-based video streaming system for helmet-mounted cameras to a central monitoring station. Pure RF transmission without WiFi or cellular networks.

Hệ thống truyền video hoàn chỉnh dựa trên RF từ camera gắn trên mũ bảo hiểm đến trạm giám sát trung tâm. Truyền RF thuần túy không dùng WiFi hay mạng di động.

## 🎯 Features / Tính năng

### Camera Unit / Thiết bị Camera
- ✅ **ESP32-CAM** firmware with OV2640 camera support
- ✅ **5.8GHz RF** video transmission (analog FPV)
- ✅ **2.4GHz RF** telemetry via nRF24L01+
- ✅ **Battery monitoring** with voltage sensing
- ✅ **Power management** with low-power modes
- ✅ **Multi-channel support** (8 channels)
- ✅ **Raspberry Pi** alternative implementation

### Central Station / Trạm Trung Tâm
- ✅ **Multi-camera receiver** (up to 8 cameras)
- ✅ **Real-time monitoring** dashboard
- ✅ **Video recording** with configurable storage
- ✅ **Channel scanning** and auto-switching
- ✅ **Telemetry reception** (battery, signal, temperature)
- ✅ **Web-based interface** with responsive design
- ✅ **RESTful API** for integration

### Dashboard / Bảng Điều Khiển
- ✅ **Grid/List/Single** view modes
- ✅ **Live video** streaming
- ✅ **Signal strength** indicators
- ✅ **Battery status** display
- ✅ **Recording controls** per camera
- ✅ **Channel selection** interface
- ✅ **Vietnamese + English** bilingual

## 📋 Table of Contents / Mục lục

- [Hardware Requirements](#hardware-requirements--yêu-cầu-phần-cứng)
- [Quick Start](#quick-start--bắt-đầu-nhanh)
- [Project Structure](#project-structure--cấu-trúc-dự-án)
- [Installation](#installation--cài-đặt)
- [Configuration](#configuration--cấu-hình)
- [Usage](#usage--sử-dụng)
- [Documentation](#documentation--tài-liệu)
- [Performance](#performance--hiệu-suất)
- [Troubleshooting](#troubleshooting--xử-lý-sự-cố)
- [Contributing](#contributing--đóng-góp)
- [License](#license--giấy-phép)

## 🔧 Hardware Requirements / Yêu cầu phần cứng

### Camera Unit (per helmet) / Thiết bị camera (mỗi mũ)

| Component | Model | Price (VND) | Notes |
|-----------|-------|-------------|-------|
| Microcontroller | ESP32-CAM | ~100,000 | With OV2640 camera |
| RF Video TX | TS5823/TX5258 | ~200,000 | 5.8GHz 25-600mW |
| RF Telemetry | nRF24L01+ | ~30,000 | 2.4GHz module |
| Battery | LiPo 3S 1500mAh | ~150,000 | 11.1V battery |
| Voltage Regulator | LM2596 5V | ~20,000 | Step-down converter |
| Antenna | Cloverleaf 5.8GHz | ~50,000 | For video TX |
| **Total per helmet** | | **~550,000** | ~$23 USD |

### Central Receiver Station / Trạm thu trung tâm

| Component | Model | Price (VND) | Notes |
|-----------|-------|-------------|-------|
| Computer | Raspberry Pi 4 4GB | ~1,500,000 | Or laptop/PC |
| RF Video RX | RC832/RX5808 | ~300,000 | 5.8GHz receiver |
| USB Capture | EasyCap/HDMI | ~200,000 | Per receiver |
| RF Telemetry | nRF24L01+ | ~30,000 | 2.4GHz module |
| Antennas | Circular 5.8GHz | ~100,000 | High gain |
| Storage | 256GB SSD | ~500,000 | For recordings |
| **Total station** | | **~2,630,000** | ~$110 USD |

**🛒 Where to buy in Vietnam / Mua ở đâu tại Việt Nam:**
- [Hshop.vn](https://hshop.vn) - ESP32-CAM, RF modules
- [Nshop.vn](https://nshop.vn) - FPV equipment
- [iChip.vn](https://ichip.vn) - Electronics components

## 🚀 Quick Start / Bắt đầu nhanh

### 1. Clone Repository
```bash
git clone https://github.com/doduc16vtkt-del/helmet-camera-streaming.git
cd helmet-camera-streaming
```

### 2. Setup Camera Unit
```bash
cd firmware/esp32-cam
# Open helmet_camera_rf.ino in Arduino IDE
# Configure settings in config.h
# Upload to ESP32-CAM
```

### 3. Setup Receiver Station
```bash
cd receiver/backend
pip3 install -r requirements.txt
python3 app.py
```

### 4. Open Dashboard
Navigate to `http://localhost:8080` in your web browser.

## 📁 Project Structure / Cấu trúc dự án

```
helmet-camera-streaming/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
│
├── configs/                     # Configuration files
│   ├── camera_config.yaml       # Camera unit settings
│   └── receiver_config.yaml     # Receiver station settings
│
├── firmware/                    # Firmware for camera units
│   ├── esp32-cam/              # ESP32-CAM Arduino code
│   │   ├── helmet_camera_rf.ino
│   │   ├── config.h
│   │   ├── camera_handler.cpp/h
│   │   ├── rf_transmitter.cpp/h
│   │   ├── telemetry.cpp/h
│   │   ├── power_management.cpp/h
│   │   └── README.md
│   │
│   └── raspberry-pi/           # Raspberry Pi Python code
│       ├── camera_rf_client.py
│       ├── rf_controller.py
│       ├── requirements.txt
│       └── README.md
│
├── receiver/                    # Central station code
│   ├── backend/                # Python backend
│   │   ├── app.py              # Flask server
│   │   ├── rf_receiver.py
│   │   ├── video_capture.py
│   │   ├── channel_manager.py
│   │   ├── telemetry_receiver.py
│   │   ├── storage.py
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── frontend/               # Web dashboard
│       ├── index.html
│       ├── css/dashboard.css
│       └── js/
│           ├── dashboard.js
│           ├── video-player.js
│           └── telemetry-display.js
│
├── docs/                        # Documentation
│   ├── architecture.md          # System architecture
│   ├── hardware-setup.md        # Hardware guide
│   ├── rf-theory.md            # RF basics
│   ├── deployment.md           # Deployment guide
│   ├── telemetry-protocol.md   # Protocol specs
│   └── images/                 # Diagrams
│
├── scripts/                     # Utility scripts
│   ├── setup_firmware.sh
│   ├── setup_receiver.sh
│   ├── test_rf_link.py
│   └── channel_scanner.py
│
├── hardware/                    # Hardware files
│   ├── BOM.csv                 # Bill of materials
│   ├── schematics/             # Circuit diagrams
│   └── 3d-models/              # Mount designs
│
└── tests/                       # Test files
    ├── test_camera.py
    ├── test_rf_transmission.py
    └── test_telemetry.py
```

## 💿 Installation / Cài đặt

### Camera Unit Setup

See detailed instructions in [`firmware/esp32-cam/README.md`](firmware/esp32-cam/README.md)

**Quick steps:**
1. Install Arduino IDE and ESP32 board support
2. Install RF24 library
3. Configure `config.h` with your settings
4. Upload firmware to ESP32-CAM

### Receiver Station Setup

See detailed instructions in [`receiver/backend/README.md`](receiver/backend/README.md)

**Quick steps:**
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip libopencv-dev librf24-dev ffmpeg -y

# Install Python packages
cd receiver/backend
pip3 install -r requirements.txt

# Run server
python3 app.py
```

## ⚙️ Configuration / Cấu hình

### Camera Configuration
Edit `configs/camera_config.yaml`:
```yaml
camera:
  resolution: "640x480"
  fps: 30

rf_video:
  channel: 1        # 1-8
  power: "25mW"     # 25mW, 200mW, 600mW

rf_telemetry:
  channel: 76       # 0-125
  device_id: "HELMET_01"

power:
  battery_type: "LiPo_3S"
  voltage_alarm: 10.5
```

### Receiver Configuration
Edit `configs/receiver_config.yaml`:
```yaml
receiver:
  channels: [1, 2, 3, 4, 5, 6, 7, 8]
  scan_interval: 1000
  auto_switch: true

dashboard:
  host: "0.0.0.0"
  port: 8080

recording:
  enabled: true
  path: "./recordings"
  format: "mp4"
  retention_days: 7
```

## 🎮 Usage / Sử dụng

### Starting the System

**1. Power on camera units**
- LED blinks 3 times: Starting
- LED blinks 5 times: Ready
- Slow blink: Normal operation

**2. Start receiver station**
```bash
cd receiver/backend
python3 app.py
```

**3. Open dashboard**
- Navigate to `http://localhost:8080`
- View live camera feeds
- Monitor telemetry data
- Control recording

### Dashboard Features

- **Grid View**: View multiple cameras simultaneously
- **Single View**: Focus on one camera
- **Recording**: Click record button per camera
- **Channel Select**: Switch RF channels
- **Signal Monitor**: View RSSI and battery status

## 📚 Documentation / Tài liệu

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Architecture](docs/architecture.md)**: System design and RF link budget
- **[Hardware Setup](docs/hardware-setup.md)**: Assembly and wiring guide
- **[RF Theory](docs/rf-theory.md)**: Radio frequency basics
- **[Deployment](docs/deployment.md)**: Installation and testing
- **[Telemetry Protocol](docs/telemetry-protocol.md)**: Data format specs

## 📊 Performance / Hiệu suất

### Camera Unit
- **Video Resolution**: 640x480 @ 30fps
- **Video Latency**: < 100ms (analog)
- **Telemetry Rate**: 1Hz
- **Battery Life**: 2-3 hours (1500mAh)
- **RF Video Range**: ~500m (line of sight)
- **RF Telemetry Range**: ~300m (line of sight)

### Receiver Station
- **Max Cameras**: 8 simultaneous
- **CPU Usage**: ~40% (4 cameras @ 640x480 on Pi 4)
- **Storage**: ~1GB per hour per camera (H.264)
- **Web Latency**: < 200ms

## 🔧 Troubleshooting / Xử lý sự cố

### Camera not starting
- Check power supply (5V 1A minimum)
- Verify camera ribbon cable connection
- Check serial monitor for error messages

### No video signal
- Verify RF channel matches receiver
- Check antenna connections
- Ensure transmitter is powered
- Try different channel

### Telemetry not received
- Check nRF24L01+ connections
- Verify 3.3V power (not 5V!)
- Ensure matching channels
- Add 10µF capacitor to nRF24 VCC

### Low battery warning
- Calibrate voltage divider in config
- Check battery voltage with multimeter
- Replace or charge battery

See detailed troubleshooting in each component's README.

## 🤝 Contributing / Đóng góp

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚖️ License / Giấy phép

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support / Hỗ trợ

- **Issues**: [GitHub Issues](https://github.com/doduc16vtkt-del/helmet-camera-streaming/issues)
- **Documentation**: See `docs/` folder
- **Discussions**: [GitHub Discussions](https://github.com/doduc16vtkt-del/helmet-camera-streaming/discussions)

## ⚠️ Legal Notice / Thông báo pháp lý

**Vietnam / Việt Nam:**
- Check VNTA regulations for 2.4GHz and 5.8GHz transmission
- Maximum transmission power may be regulated
- Use appropriate antennas to minimize interference

**Other countries:**
- Verify local regulations for ISM band usage
- RF transmission may require licensing
- Follow power limits and antenna restrictions

## 🙏 Acknowledgments / Lời cảm ơn

- ESP32 and Arduino communities
- RF24 library maintainers
- FPV community for RF knowledge
- Vietnamese maker community

## 📈 Roadmap / Lộ trình

- [ ] Add GPS tracking support
- [ ] Implement IMU data transmission
- [ ] Add audio transmission
- [ ] Mobile app for monitoring
- [ ] Cloud storage integration
- [ ] AI-based video analysis

---

**Made with ❤️ for safety and monitoring applications**

**Được tạo ra với ❤️ cho các ứng dụng an toàn và giám sát**
