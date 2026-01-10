# Hardware Setup Guide
# Hướng dẫn Lắp ráp Phần cứng

Complete guide for assembling the Helmet Camera RF System hardware.

Hướng dẫn đầy đủ để lắp ráp phần cứng Hệ thống Camera Mũ Bảo Hiểm RF.

## Bill of Materials (BOM) / Danh sách vật tư

### Camera Unit (Per Helmet) / Thiết bị camera (mỗi mũ)

| # | Component | Specification | Qty | Price (VND) | Where to Buy |
|---|-----------|---------------|-----|-------------|--------------|
| 1 | ESP32-CAM | AI-Thinker with OV2640 | 1 | 100,000 | Hshop, iChip |
| 2 | 5.8GHz Video TX | TS5823, TX5258, or similar, 25-600mW | 1 | 200,000 | Nshop, FPV stores |
| 3 | nRF24L01+ | With PA+LNA (long range) | 1 | 30,000 | Hshop, iChip |
| 4 | LiPo Battery | 3S 11.1V 1500-2000mAh | 1 | 150,000 | RC/FPV stores |
| 5 | Voltage Regulator | LM2596 DC-DC 5V 3A | 1 | 20,000 | iChip, Hshop |
| 6 | 5.8GHz Antenna | Cloverleaf or pagoda, RHCP | 1 | 50,000 | FPV stores |
| 7 | 2.4GHz Antenna | Duck antenna for nRF24 | 1 | 15,000 | Hshop |
| 8 | Connectors | XT60, JST, SMA cables | - | 30,000 | Electronic stores |
| 9 | Case/Mount | 3D printed or commercial | 1 | 50,000 | 3D printing service |
| 10 | Resistors | For voltage divider (33kΩ, 10kΩ) | 2 | 1,000 | iChip |
| 11 | Capacitors | 10µF, 100µF electrolytic | 3 | 3,000 | iChip |
| 12 | Wires | Silicone wire 22AWG | 1m | 10,000 | Electronic stores |
| | **Total per unit** | | | **~659,000** | **~$27 USD** |

### Central Receiver Station / Trạm thu trung tâm

| # | Component | Specification | Qty | Price (VND) | Where to Buy |
|---|-----------|---------------|-----|-------------|--------------|
| 1 | Raspberry Pi 4 | 4GB RAM (or use existing PC) | 1 | 1,500,000 | Official distributors |
| 2 | MicroSD Card | 64GB Class 10 or better | 1 | 200,000 | Electronic stores |
| 3 | Power Supply | 5V 3A USB-C for Pi 4 | 1 | 100,000 | Official distributors |
| 4 | 5.8GHz RX | RC832, RX5808, or similar | 4 | 1,200,000 | FPV stores |
| 5 | USB Capture | EasyCap or HDMI capture | 4 | 800,000 | Lazada, Shopee |
| 6 | nRF24L01+ | With PA+LNA | 1 | 30,000 | Hshop, iChip |
| 7 | 5.8GHz Antennas | Circular polarized, high gain | 4 | 400,000 | FPV stores |
| 8 | 2.4GHz Antenna | For nRF24 | 1 | 15,000 | Hshop |
| 9 | USB Hub | Powered USB 3.0 hub | 1 | 150,000 | Electronic stores |
| 10 | Case/Enclosure | For Pi and equipment | 1 | 100,000 | 3D printing or buy |
| 11 | Cables | USB, SMA extension cables | - | 100,000 | Electronic stores |
| 12 | Storage | External SSD 256GB (optional) | 1 | 500,000 | Electronic stores |
| | **Total station** | | | **~5,095,000** | **~$213 USD** |

**Note / Lưu ý:** Prices are approximate and may vary. Shop around for best deals.

### Tools Required / Công cụ cần thiết

- Soldering iron and solder / Mỏ hàn và thiếc hàn
- Wire strippers / Kìm tuốt dây
- Multimeter / Đồng hồ vạn năng
- Heat shrink tubing / Ống co nhiệt
- Hot glue gun / Súng bắn keo nóng
- Small screwdrivers / Tua vít nhỏ
- 3D printer (optional) / Máy in 3D (tùy chọn)

## Camera Unit Assembly / Lắp ráp thiết bị camera

### Step 1: Prepare ESP32-CAM

1. **Inspect ESP32-CAM board**
   - Check camera ribbon cable is secure
   - Verify no physical damage

2. **Prepare FTDI adapter for programming**
   ```
   FTDI        ESP32-CAM
   -----       ---------
   3.3V   →    3.3V
   GND    →    GND
   TX     →    U0R (RX)
   RX     →    U0T (TX)
   ```

3. **Connect GPIO 0 to GND for programming mode**

### Step 2: Connect nRF24L01+

**Wiring diagram:**
```
nRF24L01+    ESP32-CAM
---------    ---------
VCC     →    3.3V
GND     →    GND
CE      →    GPIO 2
CSN     →    GPIO 14
SCK     →    GPIO 12
MOSI    →    GPIO 13
MISO    →    GPIO 15
```

**Important / Quan trọng:**
- Add 10µF capacitor across VCC and GND of nRF24
- Keep wires short (< 10cm)
- Use 3.3V only, NOT 5V!

### Step 3: Connect 5.8GHz Video TX

Most FPV video transmitters have:
- **Power input**: 7-24V (connect to LiPo directly)
- **Video input**: Composite video (may need adapter)
- **Audio input**: Optional

**Note:** ESP32-CAM doesn't have analog video output by default. Options:
1. Use camera with CVBS output + ESP32 for telemetry only
2. Use digital transmission (expensive)
3. Use separate analog camera

**Recommended setup:**
```
[Analog Camera] → [5.8GHz TX]
[ESP32-CAM] → [nRF24] (telemetry only)
```

### Step 4: Build Voltage Divider for Battery Monitoring

**Circuit:**
```
Battery+ ────┬──── 33kΩ ────┬──── GPIO 33 (ADC)
             │              │
           (LiPo)         10kΩ
             │              │
Battery- ────┴──────────────┴──── GND

Voltage divider ratio: (33k + 10k) / 10k = 4.3
Max input: 3.3V × 4.3 = 14.19V (safe for 3S LiPo)
```

### Step 5: Power System

**Power Distribution:**
```
                    ┌─── 5.8GHz TX (7-12V)
                    │
LiPo 3S (11.1V) ────┤
                    │
                    └─── LM2596 → 5V ─── ESP32-CAM
                                  │
                                  └─── nRF24L01+ (via 3.3V)
```

**LM2596 Setup:**
1. Connect LiPo to input (observe polarity!)
2. Adjust potentiometer to output exactly 5V
3. Test with multimeter before connecting ESP32

### Step 6: Assembly into Enclosure

1. **Mount components** in 3D printed case or project box
2. **Secure antennas** - ensure they're not touching metal
3. **Cable management** - use zip ties, avoid stress on solder joints
4. **Add padding** - protect from vibration
5. **Ventilation** - ensure airflow for cooling

**Mounting on Helmet:**
- Use velcro or mount on top/side
- Keep antennas clear and vertical
- Balance weight distribution
- Easy battery access

## Central Receiver Station Assembly / Lắp ráp trạm thu

### Step 1: Raspberry Pi Setup

1. **Install Raspberry Pi OS**
   ```bash
   # Download Raspberry Pi Imager
   # Flash to microSD card
   # Insert into Pi and boot
   ```

2. **Enable interfaces**
   ```bash
   sudo raspi-config
   # Enable: SPI, I2C, Camera (if using Pi Camera)
   ```

3. **Update system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Step 2: Connect nRF24L01+

**GPIO connections:**
```
nRF24L01+    Raspberry Pi
---------    ------------
VCC     →    Pin 1  (3.3V)
GND     →    Pin 6  (GND)
CE      →    Pin 15 (GPIO 22)
CSN     →    Pin 24 (GPIO 8, CE0)
SCK     →    Pin 23 (GPIO 11, SCLK)
MOSI    →    Pin 19 (GPIO 10, MOSI)
MISO    →    Pin 21 (GPIO 9, MISO)
```

**Add capacitor:**
- Solder 10µF capacitor between VCC and GND on nRF24

### Step 3: Connect RF Video Receivers

1. **Power RF receivers**
   - Most use 5V or 12V
   - Use appropriate power supply

2. **Connect antennas**
   - SMA connectors
   - Circular polarized recommended
   - Position for best reception

3. **Connect to USB capture cards**
   - AV cable from receiver to capture card
   - Yellow (video), white (audio optional)
   - USB to Raspberry Pi or PC

4. **Verify USB devices**
   ```bash
   ls /dev/video*
   # Should show: /dev/video0, /dev/video1, etc.
   ```

### Step 4: Power System for Station

**Power requirements:**
```
Raspberry Pi 4:      5V @ 3A = 15W
USB Hub (powered):   5V @ 2A = 10W
4× RF Receivers:     5V @ 0.5A each = 10W
Total:               ~35W
```

**Recommended:**
- Use 12V power supply with buck converters
- Or individual 5V supplies per component
- Ensure adequate cooling

### Step 5: Cable Management and Mounting

1. **Mount receivers** on board or in rack
2. **Label all connections**
3. **Organize USB cables** with hub
4. **Secure antennas** - use stands or mounts
5. **Network connection** - Ethernet for Pi (more reliable than WiFi)

## Testing and Calibration / Kiểm tra và hiệu chỉnh

### Camera Unit Tests

1. **Power-on test**
   ```
   - LED should blink 3 times
   - After 5-10 seconds, blinks 5 times (ready)
   - Slow blink during operation
   ```

2. **Serial monitor check**
   ```
   - Connect to serial at 115200 baud
   - Check for initialization messages
   - No error codes
   ```

3. **Battery voltage test**
   ```
   - Verify voltage reading is accurate
   - Compare with multimeter
   - Adjust VOLTAGE_DIVIDER_RATIO if needed
   ```

4. **RF video test**
   ```
   - Power on camera unit
   - Check video signal on receiver
   - Adjust channel if needed
   ```

5. **Telemetry test**
   ```
   - Start receiver station
   - Check telemetry packets received
   - Verify battery/temperature data
   ```

### Receiver Station Tests

1. **Video capture test**
   ```bash
   # Test video device
   ffplay /dev/video0
   # or
   v4l2-ctl -d /dev/video0 --all
   ```

2. **nRF24 test**
   ```bash
   cd firmware/raspberry-pi
   python3 rf_controller.py
   # Should initialize without errors
   ```

3. **Dashboard test**
   ```bash
   cd receiver/backend
   python3 app.py
   # Open http://localhost:8080
   ```

## Troubleshooting Hardware / Khắc phục sự cố phần cứng

### ESP32-CAM won't program
- Check FTDI connections
- Ensure GPIO 0 is grounded
- Press reset button
- Try different USB cable

### nRF24L01+ not working
- Check power (must be 3.3V)
- Add 10µF capacitor
- Verify all connections
- Try different nRF24 module (many are fake)

### No video signal
- Check antenna connections
- Verify TX/RX on same channel
- Check power to video TX
- Try closer range first

### Battery drains quickly
- Check for short circuits
- Verify voltage regulator efficiency
- Check current draw (should be < 500mA)
- Use higher capacity battery

### Weak RF range
- Check antenna orientation (vertical)
- Use better antennas
- Increase TX power (check regulations!)
- Clear line of sight

## Safety Warnings / Cảnh báo an toàn

⚠️ **IMPORTANT / QUAN TRỌNG:**

1. **LiPo Battery Safety**
   - Never discharge below 3.0V per cell
   - Use LiPo charging bag
   - Monitor temperature
   - Dispose properly if damaged

2. **RF Exposure**
   - Keep antennas away from body when transmitting
   - Use minimum necessary power
   - Follow local regulations

3. **Soldering**
   - Use in ventilated area
   - Avoid breathing fumes
   - Proper tool handling

4. **Electrical**
   - Check polarity before connecting
   - Use fuses where appropriate
   - Avoid short circuits

## Maintenance / Bảo trì

### Regular checks:
- Battery voltage and condition
- Solder joint integrity
- Antenna condition
- Firmware updates
- Clean dust from components

### Replace when needed:
- Batteries (after ~200 cycles)
- Antennas (if damaged)
- RF modules (if performance degrades)

## Where to Buy in Vietnam / Mua ở đâu tại Việt Nam

### Online Stores
- **Hshop.vn**: ESP32, nRF24, components
- **Nshop.vn**: FPV equipment, video TX/RX
- **iChip.vn**: Electronic components
- **Lazada/Shopee**: USB capture, general electronics
- **FPV Facebook groups**: Second-hand equipment

### Physical Stores (HCMC)
- Pham Ngu Lao electronics street
- Tran Quang Khai component shops
- Nguyen Si Hung hobby shops

### Physical Stores (Hanoi)
- Tran Nhat Duat electronics market
- Giang Vo hobby shops

## Additional Resources / Tài nguyên bổ sung

- 3D printed case files: `hardware/3d-models/`
- Schematic diagrams: `hardware/schematics/`
- Wiring photos: `docs/images/`

---

**Note:** Always test components individually before final assembly!

**Lưu ý:** Luôn kiểm tra từng thành phần riêng lẻ trước khi lắp ráp cuối cùng!
