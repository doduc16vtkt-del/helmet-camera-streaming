# Telemetry Protocol Specification
# Đặc tả Giao thức Telemetry

## Overview / Tổng quan

The telemetry system uses **nRF24L01+** 2.4GHz RF modules to transmit sensor data and status information from helmet camera units to the central receiver station.

Hệ thống telemetry sử dụng module RF **nRF24L01+** 2.4GHz để truyền dữ liệu cảm biến và thông tin trạng thái từ thiết bị camera mũ bảo hiểm đến trạm thu trung tâm.

## RF Parameters / Tham số RF

| Parameter | Value | Notes |
|-----------|-------|-------|
| Frequency | 2.4GHz ISM band | Channel 0-125 |
| Channel | 76 (2476 MHz) | Configurable, avoid WiFi |
| Data Rate | 250 kbps | For maximum range |
| TX Power | 0 dBm (PA_MAX) | 1mW on nRF24L01+ |
| Auto-ACK | Enabled | Reliable delivery |
| Retries | 15 attempts | With 1.25ms delay |
| CRC | 2 bytes | Error detection |
| Payload | Dynamic | 1-32 bytes |

## Addressing / Địa chỉ

**Pipe Address:** `HLMT1` (5 bytes: 0x48, 0x4C, 0x4D, 0x54, 0x31)

- All camera units transmit to the same address
- Receiver listens on pipe 1 with this address
- Device ID differentiates between cameras

## Packet Types / Các loại gói tin

### 1. Telemetry Data Packet (TELEM)

Regular sensor data transmission, sent every 1 second.

Truyền dữ liệu cảm biến định kỳ, gửi mỗi 1 giây.

**Format (Text Protocol):**
```
TELEM:DEVICE_ID:VOLTAGE:PERCENT:TEMPERATURE:UPTIME
```

**Example:**
```
TELEM:HELMET_01:11.45:76:42.3:1234
```

**Fields:**
- `DEVICE_ID`: Unique camera identifier (string, max 16 chars)
- `VOLTAGE`: Battery voltage in volts (float, 2 decimals)
- `PERCENT`: Battery percentage 0-100 (integer)
- `TEMPERATURE`: Temperature in Celsius (float, 1 decimal)
- `UPTIME`: System uptime in seconds (integer)

**Binary Format (Alternative):**
```c
struct TelemetryPacket {
    char type[8];           // "TELEM\0\0\0"
    char device_id[16];     // Device identifier
    float battery_voltage;  // Battery voltage (V)
    uint8_t battery_percent;// Battery percent (0-100)
    int8_t rssi;           // Signal strength (dBm)
    float temperature;      // Temperature (°C)
    uint32_t uptime;        // Uptime (seconds)
    uint16_t error_count;   // Error counter
    uint8_t checksum;       // XOR checksum
} __attribute__((packed));

// Total size: 48 bytes
```

### 2. Device Information Packet (INFO)

Sent once on startup to announce device presence.

Gửi một lần khi khởi động để thông báo sự hiện diện của thiết bị.

**Format:**
```
INFO:DEVICE_ID:VERSION
```

**Example:**
```
INFO:HELMET_01:1.0.0
```

**Fields:**
- `DEVICE_ID`: Device identifier
- `VERSION`: Firmware version (e.g., "1.0.0")

### 3. Alert Packet (ALERT)

Sent immediately when critical conditions occur.

Gửi ngay lập tức khi xảy ra tình trạng nghiêm trọng.

**Format:**
```
ALERT:ALERT_CODE:TIMESTAMP
```

**Example:**
```
ALERT:11:123456789
```

**Alert Codes:**
| Code | Name | Description |
|------|------|-------------|
| 10 | BATTERY_LOW | Battery < 30% |
| 11 | BATTERY_CRITICAL | Battery < 10% |
| 12 | HIGH_TEMPERATURE | Temperature > 70°C |
| 13 | SIGNAL_WEAK | RSSI < -85 dBm |
| 14 | CAMERA_ERROR | Camera failure |
| 15 | RF_ERROR | RF transmission failure |

## Transmission Timing / Thời gian truyền

```
Time (s)    Event
--------    -----
0           Power on, initialize
2           Send INFO packet
3           Send first TELEM packet
4           Send TELEM packet
5           Send TELEM packet
...         Continue every 1s
```

**On Alert:**
```
Alert occurs → Send ALERT immediately → Resume normal TELEM
```

## Error Handling / Xử lý lỗi

### Checksum Calculation

**Simple XOR Checksum:**
```c
uint8_t calculate_checksum(uint8_t* data, size_t length) {
    uint8_t checksum = 0;
    for (size_t i = 0; i < length; i++) {
        checksum ^= data[i];
    }
    return checksum;
}
```

### Packet Validation

**Receiver side:**
1. Check packet length is valid
2. Verify checksum matches
3. Parse fields and validate ranges
4. Discard invalid packets
5. Log errors for debugging

### Retry Mechanism

**nRF24L01+ Auto-Retry:**
- Enabled by default
- 15 retry attempts
- 1.25ms delay between retries
- Total timeout: ~20ms

**Application Level:**
- If transmission fails after retries, increment error counter
- Continue with next packet (don't block)
- Telemetry is best-effort, occasional loss acceptable

## Communication Flow / Luồng truyền thông

```
┌──────────────┐                           ┌──────────────┐
│Camera Unit   │                           │   Receiver   │
│(ESP32-CAM)   │                           │(Raspberry Pi)│
└──────────────┘                           └──────────────┘
       │                                          │
       │ Power On                                 │
       ├────────────────────────────────────────→│
       │                                          │ Initialize
       │                                          │ Start Listening
       │                                          │
       │ INFO Packet                              │
       ├────────────────────────────────────────→│
       │                                          │ Log Device Info
       │                                          │
       │ TELEM Packet (1Hz)                       │
       ├────────────────────────────────────────→│
       │                                          │ Update Dashboard
       │              ACK                         │
       │←────────────────────────────────────────┤
       │                                          │
       │ TELEM Packet                             │
       ├────────────────────────────────────────→│
       │                                          │ Update Dashboard
       │              ACK                         │
       │←────────────────────────────────────────┤
       │                                          │
       │ [Low Battery Detected]                   │
       │ ALERT Packet                             │
       ├────────────────────────────────────────→│
       │                                          │ Show Alert
       │              ACK                         │
       │←────────────────────────────────────────┤
       │                                          │ Send Notification
       │                                          │
       │ Continue TELEM...                        │
       ├────────────────────────────────────────→│
```

## Implementation Examples / Ví dụ triển khai

### Transmitter (ESP32-CAM)

```cpp
// Send telemetry data
TelemetryData data;
strcpy(data.device_id, "HELMET_01");
data.battery_voltage = 11.45;
data.battery_percent = 76;
data.temperature = 42.3;
data.uptime = 1234;

// Calculate checksum
data.checksum = calculateChecksum((uint8_t*)&data, sizeof(data) - 1);

// Transmit
if (radio.write(&data, sizeof(data))) {
    Serial.println("Telemetry sent");
} else {
    Serial.println("Telemetry failed");
}
```

### Receiver (Raspberry Pi)

```python
# Receive telemetry data
if radio.available():
    payload_size = radio.getDynamicPayloadSize()
    payload = radio.read(payload_size)
    
    # Parse text protocol
    message = payload.decode('utf-8')
    if message.startswith('TELEM:'):
        parts = message.split(':')
        telemetry = {
            'device_id': parts[1],
            'battery_voltage': float(parts[2]),
            'battery_percent': int(parts[3]),
            'temperature': float(parts[4]),
            'uptime': float(parts[5])
        }
        
        # Update dashboard
        update_dashboard(telemetry)
```

## Range and Reliability / Phạm vi và độ tin cậy

**Expected Performance:**
- **Line of Sight**: 300-500m
- **Indoor/Obstacles**: 50-100m
- **Packet Loss**: < 1% (typical)
- **Latency**: < 50ms

**Factors Affecting Range:**
- **Antenna quality**: PA+LNA modules perform better
- **Obstacles**: Walls, metal reduce range
- **Interference**: WiFi on same channel
- **Orientation**: Antennas should be vertical
- **Power**: nRF24L01+ limited to 0dBm

## Debugging / Gỡ lỗi

### Test Transmission
```bash
cd scripts
python3 test_rf_link.py --channel 76 --transmit --count 10
```

### Test Reception
```bash
cd scripts
python3 test_rf_link.py --channel 76 --timeout 30
```

### Monitor Serial Output (ESP32)
```
Arduino IDE → Tools → Serial Monitor (115200 baud)

Example output:
Telemetry sent - Battery: 76% (11.45V), Temp: 42.3C, Uptime: 1234s
```

### Check nRF24 Status
```python
radio.printDetails()  # Shows configuration
radio.testCarrier()   # Check for carrier (interference)
radio.testRPD()       # Received Power Detector
```

## Future Enhancements / Cải tiến tương lai

1. **Binary Protocol**: More efficient than text
2. **Compression**: Reduce packet size
3. **Encryption**: AES encryption for security
4. **GPS Data**: Add location tracking
5. **IMU Data**: Orientation information
6. **Two-way Communication**: Commands from receiver
7. **Multi-hop**: Extend range via relay nodes

## References / Tham khảo

- nRF24L01+ Datasheet: https://www.nordicsemi.com/
- RF24 Library: https://github.com/nRF24/RF24
- Protocol Design Guide: https://www.rfwireless-world.com/
