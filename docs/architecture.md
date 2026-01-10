# System Architecture
# Kiến trúc Hệ thống

## Overview / Tổng quan

The Helmet Camera RF Streaming System consists of three main components:

Hệ thống Truyền Video Camera Mũ Bảo Hiểm RF bao gồm ba thành phần chính:

1. **Camera Units** (Helmet-mounted) - Thiết bị camera (gắn trên mũ)
2. **RF Communication** (2.4GHz + 5.8GHz) - Truyền thông RF
3. **Central Receiver Station** - Trạm thu trung tâm

## System Block Diagram / Sơ đồ khối hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                     HELMET CAMERA UNIT                       │
│                     (Thiết bị Camera)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌─────────────────┐              │
│  │   Camera     │────────▶│   ESP32-CAM     │              │
│  │   OV2640     │  Video  │  (Main MCU)     │              │
│  └──────────────┘         └────┬─────┬──────┘              │
│                               │     │                       │
│                               │     │                       │
│            ┌──────────────────┘     └────────────────┐     │
│            │                                          │     │
│            ▼                                          ▼     │
│  ┌──────────────────┐                    ┌─────────────────┐│
│  │  5.8GHz Video TX │                    │  2.4GHz nRF24  ││
│  │  (TS5823/TX5258) │                    │  (Telemetry)   ││
│  └────────┬─────────┘                    └────────┬────────┘│
│           │                                       │         │
│           │                                       │         │
│           ▼                                       ▼         │
│    ┌────────────┐                         ┌────────────┐   │
│    │  Antenna   │                         │  Antenna   │   │
│    │  5.8GHz    │                         │  2.4GHz    │   │
│    └────────────┘                         └────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Power Management (LiPo 3S)                 │   │
│  │          Battery, Regulator, Monitoring             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ RF Transmission
                           │ (Truyền RF)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               RF LINK / Đường truyền RF                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  5.8GHz Video:        ────────▶  ~500m range               │
│  2.4GHz Telemetry:    ────────▶  ~300m range               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              CENTRAL RECEIVER STATION                        │
│              (Trạm Thu Trung Tâm)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    ┌────────────┐                         ┌────────────┐   │
│    │  Antenna   │                         │  Antenna   │   │
│    │  5.8GHz    │                         │  2.4GHz    │   │
│    └──────┬─────┘                         └──────┬─────┘   │
│           │                                      │          │
│           ▼                                      ▼          │
│  ┌──────────────────┐                  ┌─────────────────┐ │
│  │  5.8GHz Video RX │                  │  2.4GHz nRF24  │ │
│  │  (RC832/RX5808)  │                  │  (Telemetry)   │ │
│  └────────┬─────────┘                  └────────┬────────┘ │
│           │                                      │          │
│           │ Analog Video                         │ SPI      │
│           ▼                                      ▼          │
│  ┌──────────────────┐                  ┌─────────────────┐ │
│  │  USB Capture     │                  │                 │ │
│  │  (Video to USB)  │──────────────────│  Raspberry Pi 4 │ │
│  └──────────────────┘      USB         │  or PC          │ │
│                                         │                 │ │
│                                         │  - Backend API  │ │
│                                         │  - Video Proc   │ │
│                                         │  - Recording    │ │
│                                         │  - Web Server   │ │
│                                         └────────┬────────┘ │
│                                                  │          │
│                                           HTTP/WebSocket   │
│                                                  │          │
│                                                  ▼          │
│                                         ┌─────────────────┐ │
│                                         │  Web Dashboard  │ │
│                                         │  (Browser)      │ │
│                                         └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow / Luồng dữ liệu

### Video Stream / Luồng video

1. **Camera Capture** - Camera chụp hình
   - OV2640 captures JPEG frames at 30fps
   - Resolution: 640x480 (VGA)
   - JPEG quality: 10 (high quality)

2. **Analog Video Transmission** - Truyền video analog
   - 5.8GHz FPV transmitter (TS5823/TX5258)
   - Channel: 1-8 selectable
   - Power: 25mW, 200mW, or 600mW
   - Latency: < 100ms

3. **Video Reception** - Thu video
   - 5.8GHz receiver (RC832/RX5808)
   - Analog CVBS output
   - Auto gain control

4. **Video Capture** - Chụp video
   - USB video capture card
   - Converts analog to digital
   - MJPEG or raw YUV format

5. **Video Processing** - Xử lý video
   - OpenCV for frame processing
   - H.264 encoding for recording
   - WebSocket streaming to dashboard

### Telemetry Stream / Luồng telemetry

1. **Data Collection** - Thu thập dữ liệu
   - Battery voltage (ADC reading)
   - Temperature (internal sensor)
   - Uptime, error count
   - Device ID

2. **Data Transmission** - Truyền dữ liệu
   - nRF24L01+ 2.4GHz module
   - 250kbps data rate
   - Auto-retry enabled
   - CRC checksum

3. **Data Reception** - Thu dữ liệu
   - nRF24L01+ on Raspberry Pi
   - SPI interface
   - Packet parsing and validation

4. **Data Distribution** - Phân phối dữ liệu
   - Update dashboard via WebSocket
   - Store in database (optional)
   - Trigger alerts if needed

## RF Link Budget / Tính toán đường truyền RF

### 5.8GHz Video Link

**Transmitter:**
- TX Power: 25 dBm (200mW configurable)
- TX Antenna Gain: 2 dBi (cloverleaf)
- Cable Loss: -0.5 dB

**Effective Radiated Power (ERP):**
```
ERP = TX Power + TX Gain - Cable Loss
ERP = 25 + 2 - 0.5 = 26.5 dBm
```

**Receiver:**
- RX Antenna Gain: 5 dBi (patch antenna)
- RX Sensitivity: -90 dBm
- Cable Loss: -0.5 dB

**Path Loss (Free Space, 500m):**
```
Path Loss = 20 × log10(distance) + 20 × log10(frequency) + 20 × log10(4π/c)
Path Loss = 20 × log10(500) + 20 × log10(5800×10^6) + 92.45
Path Loss ≈ 100 dB
```

**Received Signal Strength:**
```
RX Power = ERP + RX Gain - Path Loss - Cable Loss
RX Power = 26.5 + 5 - 100 - 0.5 = -69 dBm
```

**Link Margin:**
```
Link Margin = RX Power - RX Sensitivity
Link Margin = -69 - (-90) = 21 dB  ✓ Good!
```

### 2.4GHz Telemetry Link

**Transmitter:**
- TX Power: 0 dBm (1mW nRF24L01+)
- TX Antenna Gain: 2 dBi
- Cable Loss: -0.5 dB

**Receiver:**
- RX Antenna Gain: 2 dBi
- RX Sensitivity: -94 dBm (250kbps)
- Cable Loss: -0.5 dB

**Path Loss (300m):**
```
Path Loss ≈ 90 dB (at 2.4GHz, 300m)
```

**Received Signal Strength:**
```
RX Power = 0 + 2 - 90 + 2 - 0.5 - 0.5 = -87 dBm
```

**Link Margin:**
```
Link Margin = -87 - (-94) = 7 dB  ✓ Acceptable
```

## Channel Allocation / Phân bổ kênh

### 5.8GHz Video Channels (Band E)

| Channel | Frequency (MHz) | Application |
|---------|----------------|-------------|
| 1 | 5705 | Camera 1 |
| 2 | 5685 | Camera 2 |
| 3 | 5665 | Camera 3 |
| 4 | 5645 | Camera 4 |
| 5 | 5885 | Camera 5 |
| 6 | 5905 | Camera 6 |
| 7 | 5925 | Camera 7 |
| 8 | 5945 | Camera 8 |

**Note**: 20MHz spacing between channels to avoid interference.

### 2.4GHz Telemetry Channels

- **Primary**: Channel 76 (2476 MHz)
- **Backup**: Channel 100 (2500 MHz)
- **Spacing**: Avoid WiFi channels (1, 6, 11)

## Protocol Stack / Ngăn xếp giao thức

### Video Protocol

```
┌──────────────────────────────┐
│     Application Layer        │  Dashboard Display
│     (Hiển thị)              │
├──────────────────────────────┤
│     Transport Layer          │  WebSocket/HTTP
│     (Vận chuyển)            │
├──────────────────────────────┤
│     Processing Layer         │  OpenCV, H.264
│     (Xử lý)                 │
├──────────────────────────────┤
│     Capture Layer            │  USB Video Capture
│     (Chụp)                  │
├──────────────────────────────┤
│     RF Layer                 │  5.8GHz Analog
│     (RF)                    │
└──────────────────────────────┘
```

### Telemetry Protocol

```
┌──────────────────────────────┐
│     Application Layer        │  JSON/Binary Data
│     (Dữ liệu)              │
├──────────────────────────────┤
│     Session Layer            │  Packet Framing
│     (Phiên)                 │
├──────────────────────────────┤
│     Data Link Layer          │  nRF24 Protocol
│     (Liên kết)              │
├──────────────────────────────┤
│     Physical Layer           │  2.4GHz RF
│     (Vật lý)                │
└──────────────────────────────┘
```

## Performance Characteristics / Đặc điểm hiệu suất

### Latency / Độ trễ

| Component | Latency |
|-----------|---------|
| Camera capture | 30ms |
| RF video transmission | 50ms |
| USB capture | 30ms |
| Video processing | 20ms |
| Network streaming | 50ms |
| **Total End-to-End** | **~180ms** |

### Bandwidth / Băng thông

| Stream Type | Bandwidth |
|-------------|-----------|
| Raw video (analog) | N/A (analog) |
| USB capture | ~5 Mbps |
| H.264 encoded | 1-2 Mbps |
| Telemetry | < 1 kbps |

### Reliability / Độ tin cậy

| Metric | Value |
|--------|-------|
| Video packet loss | < 1% (typical) |
| Telemetry delivery | > 99% |
| System uptime | > 99.9% |

## Security Considerations / Xem xét bảo mật

⚠️ **Important / Quan trọng:**

1. **Unencrypted Communication** - Truyền không mã hóa
   - Analog video is not encrypted
   - Telemetry has basic checksum only
   - Consider for public/sensitive use

2. **Frequency Regulations** - Quy định tần số
   - Check local regulations (VNTA in Vietnam)
   - Maximum power limits
   - Licensed vs unlicensed bands

3. **Interference** - Nhiễu
   - WiFi can interfere with 2.4GHz
   - Other FPV users may use same channels
   - Use channel scanning

## Scalability / Khả năng mở rộng

The system supports:
- **Up to 8 cameras** simultaneously
- **Multiple receiver stations** (separate instances)
- **Cloud integration** (future)
- **Recording to NAS** (network storage)

## References / Tham khảo

- FPV Frequency Chart: https://www.fpvmodel.com/fpv-frequency-chart/
- nRF24L01+ Datasheet: https://www.nordicsemi.com/
- RF Link Budget Calculator: https://www.pasternack.com/t-calculator-link-budget.aspx
- VNTA Regulations: http://www.vnta.gov.vn/
