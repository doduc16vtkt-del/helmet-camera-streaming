# Circuit Schematics
# Sơ đồ mạch điện

## ESP32-CAM Camera Unit Schematic

### Overview

Complete wiring diagram for the helmet camera unit including:
- ESP32-CAM board
- nRF24L01+ telemetry module
- 5.8GHz video transmitter
- Battery and power management
- Voltage divider for battery monitoring

### Main Components Connections

```
                        ┌──────────────────────┐
                        │    3S LiPo Battery   │
                        │    11.1V 1500mAh     │
                        └──────────┬───────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    │                           │
         ┌──────────┴────────┐       ┌─────────┴──────────┐
         │  LM2596 Buck      │       │  5.8GHz Video TX   │
         │  Converter        │       │  TS5823/TX5258     │
         │  Output: 5V 3A    │       │  Input: 7-24V      │
         └──────────┬────────┘       └────────────────────┘
                    │
                    │ 5V
         ┌──────────┴────────┐
         │                   │
    ┌────┴──────────┐   ┌────┴─────────┐
    │  ESP32-CAM    │   │  nRF24L01+   │
    │  (5V input)   │   │  (3.3V)      │
    └───────────────┘   └──────────────┘
```

### Detailed Pin Connections

**ESP32-CAM to nRF24L01+:**
```
ESP32-CAM          nRF24L01+
---------          ----------
3.3V          →    VCC (+ 10µF cap to GND)
GND           →    GND
GPIO 2        →    CE
GPIO 14       →    CSN
GPIO 12       →    SCK
GPIO 13       →    MOSI
GPIO 15       →    MISO
```

**Battery Monitoring (Voltage Divider):**
```
Battery+ ────┬──── 33kΩ ────┬──── GPIO 33 (ADC)
             │              │
          (11.1V)         10kΩ
             │              │
Battery- ────┴──────────────┴──── GND

Calculation:
Vout = Vin × (R2 / (R1 + R2))
Vout = 11.1V × (10k / (33k + 10k))
Vout = 11.1V × 0.233 = 2.58V (safe for 3.3V ADC)
```

### Power Distribution

```
                    LiPo 3S (11.1V nominal)
                            │
                ┌───────────┴───────────┐
                │                       │
       ┌────────┴────────┐    ┌────────┴──────────┐
       │  LM2596 (5V)    │    │  Video TX (11.1V) │
       │  Vin: 7-24V     │    │  25-600mW         │
       │  Vout: 5V       │    └───────────────────┘
       │  Iout: 3A max   │
       └────────┬────────┘
                │ 5V
       ┌────────┴────────┐
       │                 │
  ┌────┴────┐      ┌─────┴──────┐
  │ESP32-CAM│      │ nRF24L01+  │
  │ ~500mA  │      │ (via 3.3V) │
  └─────────┘      │  ~15mA     │
                   └────────────┘
```

### PCB Layout Considerations

**Ground Plane:**
- Use solid ground plane on PCB
- Keep RF sections separate from digital
- Star ground configuration

**Decoupling Capacitors:**
- 10µF near nRF24L01+ VCC/GND
- 100µF near LM2596 output
- 0.1µF near ESP32-CAM VCC pins

**Antenna Placement:**
- Keep antennas away from PCB ground
- Route antenna traces with 50Ω impedance
- Minimum 5mm clearance around antennas

## Receiver Station Schematic

### Block Diagram

```
┌───────────────────────────────────────────────┐
│         5.8GHz RF Receivers (×4)              │
│                                               │
│  RX1    RX2    RX3    RX4                     │
│   │      │      │      │                      │
│   └──────┴──────┴──────┘                      │
│          │                                    │
│    Composite Video                            │
└──────────┼────────────────────────────────────┘
           │
    ┌──────┴──────┐
    │ USB Capture │
    │   Cards ×4  │
    └──────┬──────┘
           │ USB
    ┌──────┴──────────────────┐
    │    Raspberry Pi 4       │
    │                         │
    │  ┌──────────────────┐   │
    │  │   nRF24L01+      │   │
    │  │   (SPI)          │   │
    │  └──────────────────┘   │
    │                         │
    │  ┌──────────────────┐   │
    │  │   Ethernet       │───┼─→ Network
    │  └──────────────────┘   │
    └─────────────────────────┘
```

### nRF24L01+ Connection to Raspberry Pi

```
nRF24L01+     Raspberry Pi 4
---------     -------------
VCC      →    Pin 1  (3.3V)
GND      →    Pin 6  (GND)
CE       →    Pin 15 (GPIO 22)
CSN      →    Pin 24 (GPIO 8 / CE0)
SCK      →    Pin 23 (GPIO 11 / SCLK)
MOSI     →    Pin 19 (GPIO 10 / MOSI)
MISO     →    Pin 21 (GPIO 9 / MISO)
```

## Component Specifications

### LM2596 Buck Converter
- **Input**: 4.5-40V DC
- **Output**: 1.25-37V DC (adjustable)
- **Current**: 3A maximum
- **Efficiency**: 92% typical
- **Protection**: Thermal shutdown, current limit

### nRF24L01+ PA+LNA
- **Frequency**: 2400-2525 MHz
- **Power**: -18 to 0 dBm (adjustable)
- **Range**: 1000m (line of sight with PA+LNA)
- **Data Rate**: 250kbps, 1Mbps, 2Mbps
- **Voltage**: 1.9-3.6V

### 5.8GHz Video Transmitter (TS5823)
- **Frequency**: 5645-5945 MHz (40 channels)
- **Power**: 25mW, 200mW, 600mW (selectable)
- **Input**: 7-24V DC
- **Video Input**: NTSC/PAL composite

## Safety Notes

⚠️ **Warnings:**

1. **LiPo Battery Safety**
   - Never short circuit battery terminals
   - Use balanced charger
   - Monitor cell voltages
   - Store at 3.8V per cell

2. **Voltage Regulator Heat**
   - LM2596 may need heatsink
   - Allow ventilation
   - Monitor temperature

3. **RF Power**
   - Keep antennas connected when transmitting
   - Don't exceed legal power limits
   - Keep antennas away from body

4. **Static Discharge**
   - nRF24L01+ is sensitive to ESD
   - Use proper grounding
   - Handle with anti-static precautions

## Files

**Note**: Full KiCad schematic files and Gerber files for PCB manufacturing can be added here when available.

**Lưu ý**: Các tệp sơ đồ KiCad đầy đủ và tệp Gerber để sản xuất PCB có thể được thêm vào đây khi có sẵn.

### Recommended PCB Manufacturers in Vietnam

- **JLCPCB**: https://jlcpcb.com/ (ships to Vietnam)
- **PCBWay**: https://www.pcbway.com/ (ships to Vietnam)
- **Local**: Search for "gia công PCB" in major cities

## References

- ESP32-CAM Schematic: https://github.com/SeeedDocument/forum_doc/blob/master/reg/ESP32_CAM_V1.6.pdf
- LM2596 Datasheet: https://www.ti.com/lit/ds/symlink/lm2596.pdf
- nRF24L01+ Datasheet: https://www.nordicsemi.com/
