# Central Receiver Backend
# Backend trạm tiếp nhận trung tâm

Flask-based backend server for receiving RF camera feeds and managing the dashboard.

Backend server dựa trên Flask để nhận luồng camera RF và quản lý bảng điều khiển.

## Features / Tính năng

- **Multi-camera Support**: Handle up to 8 cameras simultaneously
- **RF Channel Management**: Automatic and manual channel selection
- **Telemetry Reception**: Receive battery, signal, and status data
- **Video Recording**: Record streams to disk
- **RESTful API**: HTTP API for control and monitoring
- **WebSocket Streaming**: Real-time video and telemetry updates
- **Storage Management**: Automatic cleanup of old recordings

## Installation / Cài đặt

### System Dependencies
```bash
# OpenCV dependencies
sudo apt install libopencv-dev python3-opencv -y

# RF24 library
sudo apt install librf24-dev -y

# Video codecs
sudo apt install ffmpeg libavcodec-extra -y
```

### Python Dependencies
```bash
cd receiver/backend
pip3 install -r requirements.txt
```

## Configuration / Cấu hình

Edit `configs/receiver_config.yaml` to configure:
- Receiver devices and channels
- Recording settings
- Dashboard port and settings
- Telemetry receiver settings

## Usage / Sử dụng

### Start Server
```bash
cd receiver/backend
python3 app.py
```

The server will start on `http://0.0.0.0:8080` by default.

### API Endpoints

#### Status
```
GET /api/status
```
Returns system status.

#### List Cameras
```
GET /api/cameras
```
Returns list of active cameras.

#### Get Telemetry
```
GET /api/telemetry/<device_id>
```
Get telemetry data for specific camera.

#### Start Recording
```
POST /api/recording/start/<device_id>
```
Start recording for a camera.

#### Stop Recording
```
POST /api/recording/stop/<device_id>
```
Stop recording for a camera.

#### Set Channel
```
POST /api/channel/set/<device_id>/<channel>
```
Set RF channel for a camera.

#### List Recordings
```
GET /api/recordings
```
List all saved recordings.

### WebSocket Events

Connect to WebSocket at `ws://server:8081`

#### Client → Server
- `request_video_frame`: Request video frame for a camera
- `connect`: Connect to server
- `disconnect`: Disconnect from server

#### Server → Client
- `system_status`: System status update
- `telemetry_update`: New telemetry data
- `camera_disconnected`: Camera disconnected
- `recording_started`: Recording started
- `recording_stopped`: Recording stopped

## Architecture / Kiến trúc

```
app.py                  # Main Flask application
├── rf_receiver.py      # RF receiver management
├── video_capture.py    # Video capture from USB devices
├── channel_manager.py  # Channel selection and scanning
├── telemetry_receiver.py  # nRF24L01+ telemetry reception
└── storage.py          # Recording and storage management
```

## Logging / Ghi log

Logs are written to `logs/receiver.log` and console.

Log levels:
- DEBUG: Detailed information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages

## Troubleshooting / Xử lý sự cố

### Video Device Not Found
```bash
# List video devices
v4l2-ctl --list-devices

# Check device info
v4l2-ctl -d /dev/video0 --all
```

### nRF24L01+ Not Working
- Check SPI is enabled: `ls /dev/spi*`
- Verify pin connections
- Ensure 3.3V power supply
- Check with `python3 rf_controller.py` test

### Port Already in Use
```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### High CPU Usage
- Reduce video capture resolution
- Decrease frame rate
- Disable unused cameras

## Performance / Hiệu suất

Recommended hardware:
- **Raspberry Pi 4** with 4GB RAM (or better)
- **USB 3.0** video capture cards
- **SSD storage** for recordings

Expected performance:
- 4 cameras @ 640x480: ~40% CPU on Pi 4
- 8 cameras @ 640x480: ~80% CPU on Pi 4

## License / Giấy phép

MIT License
