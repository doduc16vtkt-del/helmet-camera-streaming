# ESP32-CAM Firmware for Helmet Camera RF System
# Firmware ESP32-CAM cho Hệ thống Camera Mũ Bảo Hiểm RF

This firmware enables the ESP32-CAM to function as a helmet-mounted camera unit with RF video transmission and telemetry capabilities.

Firmware này cho phép ESP32-CAM hoạt động như một camera gắn trên mũ bảo hiểm với khả năng truyền video RF và telemetry.

## Features / Tính năng

- **Video Capture**: OV2640 camera module support / Hỗ trợ camera OV2640
- **RF Video Transmission**: 5.8GHz analog video transmission / Truyền video analog 5.8GHz
- **Telemetry**: 2.4GHz data link using nRF24L01+ / Kết nối dữ liệu 2.4GHz qua nRF24L01+
- **Power Management**: Battery monitoring and low-power modes / Giám sát pin và chế độ tiết kiệm điện
- **Multi-channel Support**: 8 channel support (5.8GHz) / Hỗ trợ 8 kênh (5.8GHz)

## Hardware Requirements / Yêu cầu phần cứng

### Required / Bắt buộc
- **ESP32-CAM** board with OV2640 camera (~100k VND)
- **5.8GHz Video Transmitter** (TS5823, TX5258, or similar) (~200k VND)
- **nRF24L01+** module for telemetry (~30k VND)
- **3S LiPo Battery** (11.1V, 1000-2000mAh) (~150k VND)
- **Voltage Regulator** (5V for ESP32-CAM) (~20k VND)
- **Antenna** for 5.8GHz (cloverleaf or patch) (~50k VND)

### Optional / Tùy chọn
- GPS module for location tracking
- IMU sensor for orientation data
- Additional voltage divider circuit for battery monitoring

## Pin Configuration / Cấu hình chân

### ESP32-CAM Default Pins
Camera pins are predefined by the ESP32-CAM board.

### nRF24L01+ Connections
```
nRF24L01+    ESP32-CAM
---------    ---------
VCC     -->  3.3V
GND     -->  GND
CE      -->  GPIO 2
CSN     -->  GPIO 14
SCK     -->  GPIO 12
MOSI    -->  GPIO 13
MISO    -->  GPIO 15
```

### Power Monitoring
```
Battery Voltage Divider --> GPIO 33 (ADC1_CH5)
```

**Note**: Pin assignments can be changed in `config.h` / **Lưu ý**: Có thể thay đổi chân trong `config.h`

## Installation / Cài đặt

### 1. Install Arduino IDE
Download and install Arduino IDE from https://www.arduino.cc/

### 2. Install ESP32 Board Support
1. Open Arduino IDE
2. Go to File → Preferences
3. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to Tools → Board → Board Manager
5. Search for "ESP32" and install "ESP32 by Espressif Systems"

### 3. Install Required Libraries
Install the following libraries via Library Manager (Sketch → Include Library → Manage Libraries):
- **RF24** by TMRh20 (for nRF24L01+)

### 4. Configure Settings
Edit `config.h` to match your hardware setup:
- Device ID
- RF channels
- Pin assignments
- Battery configuration

### 5. Upload Firmware
1. Connect ESP32-CAM via USB-to-Serial adapter
2. Select board: "AI Thinker ESP32-CAM"
3. Select correct COM port
4. Put ESP32-CAM in programming mode (GPIO 0 to GND, press reset)
5. Click Upload
6. Remove GPIO 0 connection and press reset

## Configuration / Cấu hình

### config.h Settings
```cpp
#define DEVICE_ID "HELMET_01"        // Unique identifier
#define RF_VIDEO_CHANNEL 1           // 5.8GHz channel (1-8)
#define RF_VIDEO_POWER 25            // TX power in mW
#define RF_TELEMETRY_CHANNEL 76      // 2.4GHz channel
#define BATTERY_LOW_VOLTAGE 10.5     // Low battery threshold
```

### YAML Configuration
Alternatively, load settings from `configs/camera_config.yaml` (requires SD card reader).

## Usage / Sử dụng

### First Boot
1. Power on the device
2. LED will blink 3 times during initialization
3. LED will blink 5 times when ready
4. System starts streaming video and telemetry

### LED Indicators / Chỉ báo LED
- **3 quick blinks**: System starting / Hệ thống khởi động
- **5 quick blinks**: System ready / Hệ thống sẵn sàng
- **Slow blinking**: Normal operation / Hoạt động bình thường
- **2 slow blinks**: Low battery warning / Cảnh báo pin yếu
- **Fast continuous blinking**: Error state / Trạng thái lỗi

### Serial Monitor
Connect to serial port at 115200 baud to see debug information:
- Battery voltage and percentage
- Telemetry transmission status
- Camera capture status
- Error messages

## Telemetry Data / Dữ liệu Telemetry

The system transmits the following data every second:
- Device ID
- Battery voltage and percentage
- Signal strength (RSSI)
- Temperature
- Uptime
- Error count

## Troubleshooting / Xử lý sự cố

### Camera Initialization Failed
- Check camera ribbon cable connection
- Verify board is genuine ESP32-CAM with OV2640
- Try different power supply (some cameras need stable 5V 1A+)

### nRF24L01+ Not Working
- Check all pin connections
- Ensure nRF24 is powered with 3.3V (NOT 5V!)
- Try adding 10µF capacitor across VCC and GND
- Check for pin conflicts with camera

### Low Battery Too Soon
- Calibrate voltage divider ratio in config.h
- Check actual battery voltage with multimeter
- Adjust VOLTAGE_DIVIDER_RATIO constant

### Video Not Transmitting
- Check 5.8GHz TX module is powered correctly
- Verify channel selection on TX module
- Check antenna connection
- Ensure receiver is on same channel

## Performance / Hiệu suất

- **Video Resolution**: 640x480 @ 30fps
- **Video Latency**: < 100ms (analog) / <100ms (analog)
- **Battery Life**: ~2-3 hours with 1500mAh battery / ~2-3 giờ với pin 1500mAh
- **Telemetry Range**: ~300m line-of-sight / ~300m tầm nhìn thẳng
- **Video Range**: ~500m with good antennas / ~500m với anten tốt

## Safety / An toàn

⚠️ **WARNING / CẢNH BÁO**:
- Check local regulations for 5.8GHz and 2.4GHz transmission
- Do not exceed legal transmission power limits
- Use appropriate antennas to avoid interference
- Monitor battery voltage to prevent over-discharge

## License / Giấy phép

MIT License - See LICENSE file for details

## Support / Hỗ trợ

For issues and questions:
- Check documentation in `/docs` folder
- Review troubleshooting guide
- Open issue on GitHub

## Credits / Ghi công

Developed for helmet camera RF streaming system
Phát triển cho hệ thống truyền video camera mũ bảo hiểm qua RF
