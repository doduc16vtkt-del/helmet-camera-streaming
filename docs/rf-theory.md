# RF Theory Basics
# Cơ bản về Lý thuyết RF

A beginner-friendly guide to radio frequency fundamentals for the Helmet Camera RF System.

Hướng dẫn thân thiện về các nguyên lý cơ bản của tần số vô tuyến cho Hệ thống Camera Mũ Bảo Hiểm RF.

## What is RF? / RF là gì?

**RF (Radio Frequency)** refers to electromagnetic waves used for wireless communication. Think of it like invisible light waves that can carry information through the air.

**RF (Tần số vô tuyến)** đề cập đến sóng điện từ được sử dụng cho truyền thông không dây. Hãy nghĩ về nó như các sóng ánh sáng vô hình có thể mang thông tin qua không khí.

### Frequency / Tần số

Frequency is how fast the wave oscillates, measured in Hertz (Hz).

Tần số là tốc độ dao động của sóng, đo bằng Hertz (Hz).

- **1 Hz** = 1 cycle per second
- **1 kHz** = 1,000 Hz
- **1 MHz** = 1,000,000 Hz
- **1 GHz** = 1,000,000,000 Hz

**Our system uses:**
- **2.4 GHz** (2,400 MHz) - Telemetry
- **5.8 GHz** (5,800 MHz) - Video

## Frequency Bands / Băng tần

### 2.4 GHz ISM Band

**Industrial, Scientific, Medical (ISM) band** - License-free worldwide.

**Băng ISM** - Không cần giấy phép trên toàn thế giới.

- **Range**: 2400-2483.5 MHz
- **Channels**: 79-83 channels (1 MHz spacing)
- **Used by**: WiFi, Bluetooth, nRF24L01+
- **Advantage**: Good range, penetrates walls
- **Disadvantage**: Crowded, interference from WiFi

### 5.8 GHz ISM Band

**Higher frequency ISM band** - Also license-free.

**Băng ISM tần số cao hơn** - Cũng không cần giấy phép.

- **Range**: 5725-5875 MHz
- **Used by**: FPV drones, video transmission
- **Advantage**: Less crowded, more bandwidth
- **Disadvantage**: Shorter range, doesn't penetrate walls as well

## Wavelength / Bước sóng

The physical length of one wave cycle.

Chiều dài vật lý của một chu kỳ sóng.

**Formula / Công thức:**
```
λ (wavelength) = c (speed of light) / f (frequency)
λ = 300,000,000 m/s / f
```

**Examples:**
- **2.4 GHz**: λ = 12.5 cm (about 5 inches)
- **5.8 GHz**: λ = 5.2 cm (about 2 inches)

**Why it matters:**
- Antenna length is typically λ/4 or λ/2
- Obstacles larger than λ cause more reflection

## Antennas / Ăngten

### Antenna Basics

An antenna converts electrical signals to radio waves (and vice versa).

Ăngten chuyển đổi tín hiệu điện thành sóng vô tuyến (và ngược lại).

### Antenna Types / Các loại ăngten

**1. Dipole / Lưỡng cực**
- Simple wire antenna
- Length: λ/2
- Omnidirectional (radiates in all directions)
- Used for: nRF24L01+ modules

**2. Monopole (Duck Antenna) / Đơn cực**
- Vertical antenna with ground plane
- Length: λ/4
- Omnidirectional
- Common on portable devices

**3. Cloverleaf / Lá cỏ ba**
- Circular polarized
- Compact design
- Good for FPV video transmission
- Works well at any orientation

**4. Patch Antenna / Ăngten miếng**
- Flat, directional
- Higher gain
- Used for receivers
- Must point toward transmitter

### Antenna Gain / Độ lợi ăngten

Measured in **dBi** (decibels relative to isotropic antenna).

Đo bằng **dBi** (decibel so với ăngten đẳng hướng).

- **0 dBi**: Omnidirectional, radiates equally in all directions
- **2 dBi**: Slight directionality
- **5-10 dBi**: Directional, longer range in one direction

**Trade-off:**
- Higher gain = Longer range in one direction
- Lower gain = Coverage in all directions

### Polarization / Phân cực

The orientation of the electromagnetic field.

Hướng của trường điện từ.

**Linear Polarization:**
- **Vertical**: Antenna vertical, waves oscillate up/down
- **Horizontal**: Antenna horizontal, waves oscillate left/right

**Circular Polarization:**
- **RHCP** (Right-Hand Circular Polarized): Spiral clockwise
- **LHCP** (Left-Hand Circular Polarized): Spiral counter-clockwise

**Why use circular polarization?**
- Works regardless of orientation
- Reduces multipath interference
- Preferred for moving objects (FPV drones, helmet cameras)

## RF Propagation / Truyền sóng RF

### Line of Sight (LOS) / Tầm nhìn thẳng

Best case: Clear path between transmitter and receiver.

Trường hợp tốt nhất: Đường dẫn rõ ràng giữa máy phát và máy thu.

**Free Space Path Loss (FSPL):**
```
FSPL (dB) = 20 × log10(d) + 20 × log10(f) + 20 × log10(4π/c)

Where:
- d = distance (meters)
- f = frequency (Hz)
- c = speed of light (3×10^8 m/s)
```

**Example for 5.8 GHz at 500m:**
```
FSPL = 20 × log10(500) + 20 × log10(5.8×10^9) + 92.45
FSPL ≈ 54 + 175.3 + 92.45 = 100 dB
```

### Obstacles / Vật cản

Different materials affect RF signals differently:

Các vật liệu khác nhau ảnh hưởng đến tín hiệu RF khác nhau:

| Material | Attenuation @ 2.4 GHz | Attenuation @ 5.8 GHz |
|----------|----------------------|----------------------|
| Air | 0 dB | 0 dB |
| Wood | 2-3 dB | 3-4 dB |
| Drywall | 3-4 dB | 4-5 dB |
| Concrete | 10-15 dB | 15-20 dB |
| Metal | 20-40 dB | 30-50 dB |
| Human body | 3-5 dB | 5-8 dB |

**Tip:** Metal is the worst! Avoid placing antennas near metal objects.

### Reflection and Multipath / Phản xạ và đa đường

RF signals can bounce off surfaces, creating multiple paths.

Tín hiệu RF có thể phản xạ từ các bề mặt, tạo ra nhiều đường dẫn.

**Effects:**
- **Constructive interference**: Signals add up (stronger)
- **Destructive interference**: Signals cancel out (weaker)
- **Fading**: Rapid fluctuations in signal strength

**Solution:**
- Use circular polarization
- Diversity antennas (multiple antennas)
- Higher mounting positions

## Power and Range / Công suất và Phạm vi

### Transmit Power / Công suất phát

Measured in **mW** (milliwatts) or **dBm** (decibels relative to 1mW).

Đo bằng **mW** (miliwatt) hoặc **dBm** (decibel so với 1mW).

**Conversion:**
```
dBm = 10 × log10(mW)

Examples:
1 mW = 0 dBm
10 mW = 10 dBm
100 mW = 20 dBm
1000 mW (1W) = 30 dBm
```

**Our system:**
- **nRF24L01+**: 0 dBm (1 mW)
- **5.8 GHz TX**: 14 dBm (25 mW), 23 dBm (200 mW), or 28 dBm (600 mW)

⚠️ **Legal limits vary by country!** Check local regulations.

### Receiver Sensitivity / Độ nhạy máy thu

The minimum signal strength the receiver can detect.

Cường độ tín hiệu tối thiểu mà máy thu có thể phát hiện.

**Typical values:**
- **nRF24L01+**: -94 dBm @ 250 kbps
- **5.8 GHz RX**: -90 dBm (analog video)

**Better sensitivity = Longer range**

### Link Budget / Ngân sách đường truyền

Calculate if the link will work:

Tính toán xem đường truyền có hoạt động không:

```
Received Power = TX Power + TX Gain - Path Loss + RX Gain
Link Margin = Received Power - RX Sensitivity

If Link Margin > 0: Link works! ✓
If Link Margin < 0: Link fails! ✗
```

**Example (2.4 GHz, 300m):**
```
RX Power = 0 dBm + 2 dBi - 90 dB + 2 dBi = -86 dBm
Link Margin = -86 dBm - (-94 dBm) = 8 dB ✓
```

**Good link margin:**
- **> 20 dB**: Excellent
- **10-20 dB**: Good
- **5-10 dB**: Acceptable
- **< 5 dB**: Marginal

## Interference / Nhiễu

### Sources of Interference / Nguồn nhiễu

**2.4 GHz:**
- WiFi routers (channels 1, 6, 11)
- Bluetooth devices
- Microwave ovens
- Cordless phones
- Other RC systems

**5.8 GHz:**
- 5 GHz WiFi
- Other FPV systems
- Radar systems

### Avoiding Interference / Tránh nhiễu

1. **Choose different channels**
   - 2.4 GHz: Use channel 76-100 (not 1-25)
   - 5.8 GHz: Use Band E (less common than Band F)

2. **Increase separation**
   - Keep 20 MHz spacing between channels
   - Multiple cameras: Use channels 1, 3, 5, 7

3. **Use shielding**
   - Proper grounding
   - Shielded cables
   - Metal enclosures with filtering

## Vietnam Regulations / Quy định Việt Nam

**VNTA (Vietnam Telecommunications Authority)** regulates RF usage.

**VNTA (Cục Viễn thông Việt Nam)** quy định sử dụng RF.

### ISM Bands

- **2.4 GHz (2400-2483.5 MHz)**: License-free
  - Max power: 100 mW EIRP (check current regulations)
  - Used for WiFi, Bluetooth, etc.

- **5.8 GHz (5725-5850 MHz)**: License-free
  - Max power: 200 mW EIRP (check current regulations)
  - Used for WiFi 5 GHz, FPV systems

⚠️ **Always verify current regulations** at http://www.vnta.gov.vn/

### Important Notes / Lưu ý quan trọng

1. **Power limits**: Don't exceed legal limits
2. **Commercial use**: May require additional licensing
3. **Interference**: Don't interfere with licensed services
4. **Safety**: Keep antennas away from people when transmitting

## Troubleshooting RF Issues / Khắc phục sự cố RF

### Weak Signal / Tín hiệu yếu

**Symptoms:**
- Low RSSI
- Video breakup
- Packet loss

**Solutions:**
1. Check antenna connections (tight SMA connectors)
2. Verify antenna orientation (vertical for omnidirectional)
3. Move closer or to line of sight
4. Increase TX power (if legal)
5. Use better antennas (higher gain)

### No Signal / Không tín hiệu

**Check:**
1. TX and RX on same channel?
2. TX powered on?
3. Antennas connected?
4. Correct frequency band?
5. Receiver working? (test with known good TX)

### Interference / Nhiễu

**Symptoms:**
- Periodic signal drops
- Random disconnections
- Noise in video

**Solutions:**
1. Scan channels, find cleanest one
2. Move away from WiFi routers
3. Use channel with 40+ MHz spacing from WiFi
4. Shield electronics properly

## Further Reading / Đọc thêm

- **Books**:
  - "RF Circuit Design" by Christopher Bowick
  - "The ARRL Handbook for Radio Communications"

- **Online**:
  - https://www.electronics-notes.com/
  - https://www.rfcafe.com/
  - https://www.wirelessinformation.org/

- **Vietnamese Resources**:
  - VNTA Website: http://www.vnta.gov.vn/
  - Vietnam Amateur Radio Club forums

---

**Remember:** RF can seem complex, but with practice it becomes intuitive!

**Ghi nhớ:** RF có thể phức tạp, nhưng với thực hành nó sẽ trở nên trực quan!
