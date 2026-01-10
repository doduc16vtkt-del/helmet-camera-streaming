# Windows Hardware Guide
# Hướng dẫn phần cứng cho Windows

Comprehensive hardware recommendations and setup guide for Windows-based receiver stations.

Hướng dẫn chi tiết về phần cứng và cài đặt cho trạm thu dựa trên Windows.

---

## Table of Contents

1. [Computer Requirements](#computer-requirements)
2. [USB Capture Cards](#usb-capture-cards)
3. [USB Hubs](#usb-hubs)
4. [RF Receivers](#rf-receivers)
5. [Network Equipment](#network-equipment)
6. [Storage Solutions](#storage-solutions)
7. [Complete System Builds](#complete-system-builds)
8. [Latency Testing](#latency-testing)
9. [Windows-Specific Tips](#windows-specific-tips)

---

## Computer Requirements

### Desktop PC vs Laptop

**Desktop PC (Recommended):**
- ✅ More USB ports and controllers
- ✅ Better cooling for 24/7 operation
- ✅ Upgradeable (RAM, GPU, storage)
- ✅ More reliable for long-term use
- ❌ Not portable

**Laptop:**
- ✅ Portable
- ✅ Built-in UPS (battery)
- ❌ Limited USB ports
- ❌ Thermal throttling under load
- ❌ Difficult to upgrade

### CPU Requirements

**Entry Level (1-2 cameras):**
- Intel Core i3-10100 / AMD Ryzen 3 3100
- 4 cores, 8 threads
- ~$100

**Mid-Range (4 cameras):**
- Intel Core i5-12400 / AMD Ryzen 5 5600
- 6 cores, 12 threads
- ~$180

**High-End (8 cameras):**
- Intel Core i7-13700 / AMD Ryzen 7 5800X
- 8+ cores, 16+ threads
- ~$350+

**Important:** Intel CPUs have Quick Sync (built-in hardware encoder), which is very useful.

### GPU Requirements

**Integrated Graphics (Intel/AMD):**
- Sufficient for 1-2 cameras
- Use Intel Quick Sync for encoding
- Free (included with CPU)

**Entry Level GPU:**
- NVIDIA GTX 1050 Ti / AMD RX 560
- Good for 4 cameras with GPU encoding
- ~$150

**Mid-Range GPU:**
- NVIDIA RTX 3060 / AMD RX 6600
- Excellent for 8 cameras
- Hardware encoder (NVENC/AMF)
- ~$300

**High-End GPU:**
- NVIDIA RTX 4060/4070
- Professional-level performance
- Multiple encoding sessions
- ~$400+

**Recommendation:** NVIDIA GPUs preferred for NVENC encoder support.

### RAM Requirements

- **8 GB**: Minimum for 1-2 cameras
- **16 GB**: Recommended for 4 cameras
- **32 GB**: Ideal for 8 cameras with recording

**Speed:** DDR4-3200 or faster

### Storage Requirements

**Operating System:**
- 50 GB minimum
- SSD recommended

**Recording Storage:**

Per camera, per hour (1080p):
- Low quality (CRF 28): ~500 MB/hour
- Medium quality (CRF 23): ~1 GB/hour
- High quality (CRF 18): ~2 GB/hour

**Example calculation (4 cameras, 24/7, 7 days retention):**
- 4 cameras × 1 GB/hour × 24 hours × 7 days = **672 GB**
- Add 30% overhead = **~900 GB minimum**

**Recommendations:**
- **256 GB SSD**: OS + software
- **1-2 TB HDD/SSD**: Recordings (for 4 cameras)
- **4+ TB HDD**: Long-term storage (8 cameras)

**Best setup:**
- OS on NVMe SSD (fast boot, app loading)
- Recordings on SATA SSD or HDD (capacity, cost-effective)

---

## USB Capture Cards

### Top Recommendations

#### Professional Grade

**1. Elgato Cam Link 4K (~$130)**
- ✅ Excellent quality and low latency
- ✅ Plug-and-play, no drivers needed
- ✅ 4K capable (though 1080p recommended)
- ✅ MJPEG hardware encoding
- ❌ Expensive for multiple cameras

**2. AVerMedia Live Gamer Portable 2 Plus (~$150)**
- ✅ Hardware encoding
- ✅ Can record standalone (SD card)
- ✅ Passthrough port
- ❌ Bulky
- ❌ Overkill for simple capture

#### Budget Options

**3. Mirabox USB 3.0 HDMI Capture (~$30)**
- ✅ Good quality for price
- ✅ USB 3.0, low latency (~80-120ms)
- ✅ Supports 1080p60
- ⚠️ Some driver issues on Windows
- ✅ DirectShow compatible

**4. Pengo USB 3.0 HDMI Capture (~$25)**
- ✅ Very affordable
- ✅ Decent latency (~100-150ms)
- ✅ Works with most USB 3.0 ports
- ⚠️ Quality varies by batch

**5. Generic USB 3.0 HDMI Capture (~$15-20)**
- ⚠️ Hit or miss quality
- ⚠️ May have high latency (200-300ms)
- ⚠️ Driver issues common
- ✅ Very cheap for testing

#### Avoid

**❌ EasyCap USB 2.0**
- USB 2.0 bandwidth limited
- High latency (300-500ms)
- Poor Windows 10/11 driver support
- Low resolution (480p max typically)

### Features to Look For

**Essential:**
- ✅ USB 3.0 (minimum 5 Gbps)
- ✅ UVC (USB Video Class) compliant
- ✅ DirectShow support
- ✅ HDMI input (or composite for older receivers)

**Nice to Have:**
- ✅ MJPEG hardware encoding
- ✅ Multiple resolution support
- ✅ HDCP bypass (if needed)
- ✅ Passthrough port

### Tested Capture Cards for Windows

| Model | Latency | Quality | Windows 11 | DirectShow | Price |
|-------|---------|---------|------------|------------|-------|
| Elgato Cam Link 4K | ~60ms | Excellent | ✅ | ✅ | $130 |
| Mirabox HDMI USB 3.0 | ~100ms | Good | ✅ | ✅ | $30 |
| Pengo HDMI USB 3.0 | ~120ms | Good | ✅ | ✅ | $25 |
| Generic "MS2109" chip | ~150ms | Fair | ⚠️ | ✅ | $20 |
| AVerMedia LGP2+ | ~80ms | Excellent | ✅ | ✅ | $150 |

**Recommendation for budget builds:** Mirabox or Pengo cards (4-pack ~$100-120)

---

## USB Hubs

### Why You Need a Hub

For 4+ cameras, you'll exceed USB ports and bandwidth of single controller.

### Powered vs Bus-Powered

**Powered Hub (Recommended):**
- ✅ External power adapter
- ✅ Stable power for all devices
- ✅ No voltage drop issues
- ✅ Can support high-power devices

**Bus-Powered Hub:**
- ❌ Draws power from PC
- ❌ May cause voltage issues
- ❌ Limited to low-power devices
- ✅ More portable

### Recommendations

**1. Anker 10-Port USB 3.0 Hub (~$50)**
- ✅ Powered (12V 4A adapter)
- ✅ Individual port switches
- ✅ 10 ports (good for 8 cameras)
- ✅ Reliable, well-built

**2. Sabrent 4-Port USB 3.0 Hub (~$15)**
- ✅ Powered (12V 2.5A)
- ✅ Compact
- ✅ Good for 4 cameras
- ✅ Budget-friendly

**3. Plugable 7-Port USB 3.0 Hub (~$35)**
- ✅ Powered (15W adapter)
- ✅ 7 ports
- ✅ Good Windows compatibility

### Hub Configuration Tips

**Spread the load:**
- Don't plug all cameras into one hub
- Use multiple hubs on different USB controllers
- Check USB controller mapping (see Windows-Specific Tips)

**Example 8-camera setup:**
- Hub 1 (rear USB 3.0 controller): Cameras 0-3
- Hub 2 (front USB 3.0 controller): Cameras 4-7

---

## RF Receivers

### 5.8GHz Video Receivers

The RF receiver outputs analog video (composite or HDMI), which goes into USB capture card.

**Recommended Models:**

**1. RC832 / RC305 (~$15-20)**
- ✅ Classic FPV receiver
- ✅ 40 channels (Raceband supported)
- ✅ Composite AV output
- ✅ Built-in screen (useful for setup)
- ⚠️ Needs AV-to-HDMI converter for HDMI capture cards

**2. RX5808 Module (~$10)**
- ✅ Bare module (DIY friendly)
- ✅ SPI control for channel switching
- ✅ Very affordable
- ❌ Requires additional circuitry
- ❌ No built-in display

**3. Eachine ROTG02 (~$40)**
- ✅ Dual diversity receiver
- ✅ HDMI output (direct connection)
- ✅ 48 channels
- ✅ Good sensitivity
- ⚠️ More expensive

**4. ImmersionRC Duo5800 V2 (~$70)**
- ✅ Professional-grade
- ✅ Dual diversity
- ✅ HDMI output
- ✅ Excellent sensitivity
- ❌ Expensive

### AV-to-HDMI Converters

If using composite output receivers (RC832), you need converter:

**Recommended:**
- Generic "Composite to HDMI" converter (~$10)
- RCA AV to HDMI 1080p (~$12)

**Don't get:**
- HDMI to AV (wrong direction!)

---

## Network Equipment

### Wired Ethernet (Recommended)

**Gigabit Ethernet:**
- Lowest latency
- Most reliable
- Best for multi-camera streaming

**Basic Switch:**
- Netgear GS305 5-Port Gigabit Switch (~$20)
- TP-Link TL-SG105 5-Port Gigabit Switch (~$18)

### WiFi (Acceptable)

**WiFi 6 (802.11ax) Recommended:**
- TP-Link Archer AX21 (~$80)
- ASUS RT-AX55 (~$90)

**Minimum WiFi 5 (802.11ac):**
- 5GHz band only for video
- 2.4GHz for management only

**Tips:**
- Use 5GHz for lowest latency
- Avoid interference (use WiFi analyzer)
- Position router close to PC

---

## Storage Solutions

### SSD vs HDD

**SSD Advantages:**
- ✅ Fast read/write
- ✅ Low latency
- ✅ Silent operation
- ✅ Shock resistant
- ❌ More expensive per GB

**HDD Advantages:**
- ✅ Cheap per GB
- ✅ Large capacities (4TB+)
- ❌ Slower
- ❌ Moving parts (noise, failure)

**Recommendation:**
- OS + App: NVMe/SATA SSD (256GB)
- Recordings: SATA SSD (1-2TB) or HDD (2-4TB)

### Specific Models

**NVMe SSD (OS):**
- Samsung 970 EVO Plus 250GB (~$40)
- WD Black SN770 500GB (~$50)
- Crucial P3 500GB (~$35)

**SATA SSD (Recordings):**
- Crucial MX500 1TB (~$70)
- Samsung 870 EVO 1TB (~$100)
- WD Blue 3D NAND 1TB (~$75)

**HDD (Bulk Storage):**
- WD Purple 2TB (~$60) - Surveillance-grade
- Seagate Skyhawk 4TB (~$100) - Surveillance-grade
- WD Blue 2TB (~$50) - Standard desktop

**Surveillance-grade HDDs:**
- Designed for 24/7 operation
- Better suited for continuous recording
- Longer warranty

---

## Complete System Builds

### Budget Build (~$600)
**For 4 cameras, basic monitoring**

- **PC:** Dell Optiplex 7010 (used, ~$150)
  - Intel i5-3470, 8GB RAM, 256GB SSD
- **GPU:** Integrated Intel HD Graphics
- **Capture Cards:** 4× Pengo USB 3.0 HDMI (~$100)
- **USB Hub:** Sabrent 4-Port Powered Hub (~$15)
- **Storage:** 1TB HDD for recordings (~$50)
- **RF Receivers:** 4× RC832 (~$60)
- **AV Converters:** 4× Composite to HDMI (~$40)
- **Antennas:** 4× 5.8GHz circular (~$60)
- **Cables:** HDMI, USB, power (~$25)

**Total:** ~$600

**Performance:**
- 4 cameras @ 720p30
- ~150ms latency
- 24/7 operation capable
- Basic GPU encoding

---

### Mid-Range Build (~$1200)
**For 4-8 cameras, good quality**

- **PC:** Custom build or pre-built
  - Intel i5-12400 or AMD Ryzen 5 5600, 16GB RAM
  - 256GB NVMe SSD + 1TB SATA SSD (~$400-500)
- **GPU:** NVIDIA GTX 1650 (~$150)
- **Capture Cards:** 8× Mirabox USB 3.0 HDMI (~$240)
- **USB Hubs:** 2× Anker 10-Port (~$100)
- **RF Receivers:** 8× RC832 (~$120)
- **AV Converters:** 8× Composite to HDMI (~$80)
- **Antennas:** 8× 5.8GHz high-gain (~$120)
- **Network:** Gigabit switch (~$20)
- **Cables & Misc:** (~$50)

**Total:** ~$1280

**Performance:**
- 8 cameras @ 1080p30
- <120ms latency
- NVENC GPU encoding
- 1 week recording retention
- 24/7 reliable operation

---

### High-End Build (~$2000)
**For 8 cameras, professional quality**

- **PC:** High-performance custom build
  - Intel i7-13700K or AMD Ryzen 7 7700X, 32GB RAM
  - 500GB NVMe SSD + 2TB NVMe SSD (~$800)
- **GPU:** NVIDIA RTX 3060 or RTX 4060 (~$350)
- **Capture Cards:** 8× Elgato Cam Link 4K (~$1000)
  - Or 8× Mirabox (~$240) to save money
- **USB Hubs:** 2× High-quality powered hubs (~$100)
- **RF Receivers:** 8× Eachine ROTG02 (~$320)
- **Antennas:** 8× Professional diversity (~$240)
- **Network:** Managed Gigabit switch (~$80)
- **UPS:** 1500VA UPS backup (~$150)
- **Cables & Accessories:** (~$100)

**Total:** ~$2000-3000 (depending on capture card choice)

**Performance:**
- 8 cameras @ 1080p60
- <80ms latency
- Professional NVENC encoding
- Multiple recording profiles
- Redundancy and backup
- Professional monitoring

---

## Latency Testing

### Measuring End-to-End Latency

**Glass-to-Glass Test:**

1. Place camera and monitor side-by-side
2. Camera films monitor showing video feed
3. Use stopwatch or phone camera recording at slow-motion
4. Count frames between source and display

**Example:**
- 3 frames at 30fps = 3/30 = 100ms latency

### Expected Latencies

**Component breakdown:**

| Component | Latency |
|-----------|---------|
| Camera (ESP32-CAM) | 30-50ms |
| RF transmission (5.8GHz analog) | 5-10ms |
| USB capture card (budget) | 80-150ms |
| USB capture card (premium) | 40-80ms |
| Network + encoding | 20-50ms |
| Display | 10-30ms |
| **Total (budget):** | **185-320ms** |
| **Total (premium):** | **105-220ms** |

**Target:** < 250ms for acceptable FPV-style monitoring

### Tools

**Windows Latency Testing:**
- OBS Studio latency display
- Custom Python script with timestamp overlay
- High-speed camera (phone at 240fps)

---

## Windows-Specific Tips

### USB Controller Mapping

Windows groups USB ports by controller. Check mapping:

1. Open Device Manager
2. View → Devices by connection
3. Expand USB controllers
4. See which ports connect to which controller

**Strategy:**
- Distribute cameras across different controllers
- Don't overload single controller bandwidth

### USB 3.0 vs 2.0 Identification

**Physical:**
- USB 3.0: Blue inside
- USB 2.0: Black/white inside

**In Device Manager:**
- USB 3.0: "USB 3.0 eXtensible Host Controller"
- USB 2.0: "USB 2.0 Enhanced Host Controller"

### DirectShow Filters

Some capture cards need DirectShow filters installed:

1. Install K-Lite Codec Pack (Basic) from codecguide.com
2. Includes necessary DirectShow components
3. Restart after installation

### Power Management

**Prevent USB power saving:**

For each USB Root Hub in Device Manager:
1. Right-click → Properties
2. Power Management tab
3. Uncheck "Allow the computer to turn off this device to save power"

**Disable sleep:**
- Control Panel → Power Options
- Set sleep to Never for all power plans

### Performance Monitoring

**Task Manager (basic):**
- Ctrl+Shift+Esc
- Performance tab
- Monitor CPU, GPU, RAM, Disk

**GPU-Z (advanced):**
- Download from techpowerup.com
- Real-time GPU monitoring
- Check encoding usage

**nvidia-smi (NVIDIA):**
```powershell
nvidia-smi -l 1
```
Shows GPU usage every 1 second

---

## FAQ

**Q: Can I use a laptop?**
A: Yes, but be aware of limitations (fewer USB ports, thermal throttling). External powered USB hub required for 4+ cameras.

**Q: Do I need a GPU?**
A: Not required for 1-2 cameras. Highly recommended for 4+ cameras to use hardware encoding (NVENC/Quick Sync).

**Q: What about Raspberry Pi?**
A: This guide is Windows-specific. Pi is covered in main deployment guide. Windows offers better multi-camera performance and GPU encoding.

**Q: Best USB capture card for Windows?**
A: Budget: Mirabox/Pengo (~$25). Premium: Elgato Cam Link 4K (~$130).

**Q: Can I mix different capture cards?**
A: Yes, the system supports mixed devices. Each is identified by device ID (0, 1, 2, etc.).

**Q: How much bandwidth per camera?**
A: USB 3.0 allows ~400MB/s. Each 1080p30 MJPEG stream uses ~30-50MB/s. Theoretical limit: 8 cameras per controller.

---

**Last updated:** 2026-01-10

**See also:**
- [Windows Deployment Guide](windows-deployment.md)
- [Main Hardware Setup Guide](hardware-setup.md)
