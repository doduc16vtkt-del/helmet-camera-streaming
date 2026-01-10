# Deployment Guide
# Hướng dẫn Triển khai

Complete guide for deploying the Helmet Camera RF Streaming System in production.

Hướng dẫn đầy đủ để triển khai Hệ thống Truyền Video Camera Mũ Bảo Hiểm RF trong thực tế.

## Pre-Deployment Checklist / Danh sách kiểm tra trước triển khai

### Hardware Preparation

**Camera Units:**
- [ ] All ESP32-CAM boards tested and working
- [ ] nRF24L01+ modules tested for telemetry
- [ ] 5.8GHz video transmitters configured
- [ ] Batteries fully charged and tested
- [ ] Voltage regulators set to 5V
- [ ] Antennas securely attached
- [ ] Enclosures assembled and weather-sealed
- [ ] Mounting hardware ready

**Receiver Station:**
- [ ] Raspberry Pi 4 or PC ready
- [ ] Operating system installed and updated
- [ ] All USB capture cards tested
- [ ] 5.8GHz receivers configured
- [ ] Antennas mounted and positioned
- [ ] Network connection available
- [ ] Power supply adequate (35W+)
- [ ] Backup power (UPS) recommended

### Software Preparation

**Firmware:**
- [ ] ESP32-CAM firmware compiled and tested
- [ ] Configuration files customized
- [ ] Device IDs assigned uniquely
- [ ] RF channels allocated

**Receiver Software:**
- [ ] Backend dependencies installed
- [ ] Configuration file edited
- [ ] Database initialized (if used)
- [ ] Logging configured
- [ ] Storage paths created

## Step 1: Site Survey / Khảo sát địa điểm

### RF Environment Assessment

1. **Identify RF sources**
   ```bash
   # Scan for WiFi networks
   sudo iwlist wlan0 scan | grep -E "(ESSID|Frequency|Quality)"
   
   # List nearby 2.4 GHz channels
   # Choose channel with least interference
   ```

2. **Test signal coverage**
   - Walk the deployment area
   - Mark dead zones
   - Identify obstacles (metal, concrete)
   - Plan antenna positioning

3. **Range testing**
   ```bash
   # Test RF link at maximum expected distance
   cd scripts
   python3 test_rf_link.py --channel 76 --timeout 60
   ```

### Power and Network

1. **Power availability**
   - Identify outlet locations
   - Calculate total power needs
   - Plan cable routing

2. **Network connectivity**
   - Ethernet recommended over WiFi
   - Test internet speed (if cloud features needed)
   - Configure static IP for receiver

## Step 2: Install Camera Units / Lắp đặt thiết bị camera

### Firmware Installation

1. **Flash firmware to ESP32-CAM**
   ```bash
   cd firmware/esp32-cam
   arduino-cli compile --fqbn esp32:esp32:esp32cam helmet_camera_rf
   arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32cam helmet_camera_rf
   ```

2. **Configure each unit**
   ```cpp
   // In config.h, set unique ID for each camera
   #define DEVICE_ID "HELMET_01"  // Change for each unit
   #define RF_VIDEO_CHANNEL 1      // Assign different channels
   #define RF_TELEMETRY_CHANNEL 76 // Same for all
   ```

3. **Test each unit individually**
   - Power on camera
   - Check serial output (115200 baud)
   - Verify LED blink pattern (3 blinks → 5 blinks → slow blink)
   - Test video signal on receiver
   - Verify telemetry reception

### Physical Installation

1. **Helmet mounting**
   - Use provided 3D printed mount or adhesive mount
   - Position camera for optimal view
   - Ensure antenna is vertical and clear
   - Route cables neatly
   - Secure with zip ties

2. **Battery placement**
   - Mount battery securely (velcro or pouch)
   - Protect from impacts
   - Allow easy access for charging
   - Label with voltage warning

3. **Weatherproofing**
   - Seal enclosure with silicone
   - Protect connectors with heat shrink
   - Use waterproof cases if outdoor use

## Step 3: Install Receiver Station / Lắp đặt trạm thu

### Hardware Setup

1. **Mount receivers and antennas**
   ```
   Antenna positioning:
   - Height: 2-3 meters above ground
   - Clear line of sight to operating area
   - Spacing: 30cm+ between antennas
   - Orientation: Vertical for omnidirectional
   ```

2. **Connect USB devices**
   ```bash
   # Verify all video devices are detected
   ls -l /dev/video*
   
   # Should show: /dev/video0, /dev/video1, etc.
   
   # Check device info
   v4l2-ctl -d /dev/video0 --all
   ```

3. **Connect nRF24L01+**
   - Follow wiring diagram in hardware setup guide
   - Add 10µF capacitor across VCC/GND
   - Test connection:
     ```bash
     cd scripts
     python3 test_rf_link.py --channel 76
     ```

### Software Installation

1. **Run setup script**
   ```bash
   cd scripts
   chmod +x setup_receiver.sh
   ./setup_receiver.sh
   ```

2. **Configure receiver settings**
   ```bash
   # Edit configuration
   nano configs/receiver_config.yaml
   
   # Update:
   # - Device paths (/dev/video0, etc.)
   # - Channel assignments
   # - Recording path
   # - Dashboard port
   ```

3. **Test receiver**
   ```bash
   cd receiver/backend
   python3 app.py
   
   # Should show:
   # - System initialized
   # - Dashboard available at http://0.0.0.0:8080
   ```

4. **Open dashboard**
   - Navigate to `http://receiver-ip:8080`
   - Should see dashboard interface
   - Cameras will appear as they connect

## Step 4: System Configuration / Cấu hình hệ thống

### Channel Allocation

**5.8 GHz Video Channels:**
```
Camera 1: Channel 1 (5705 MHz)
Camera 2: Channel 3 (5665 MHz)
Camera 3: Channel 5 (5885 MHz)
Camera 4: Channel 7 (5925 MHz)
```

**2.4 GHz Telemetry:**
```
All cameras: Channel 76 (2476 MHz)
(Away from WiFi channels 1, 6, 11)
```

### Performance Tuning

1. **Video quality**
   - Adjust JPEG quality in camera config
   - Balance quality vs. bandwidth
   - Test at different settings

2. **Telemetry rate**
   - Default: 1 Hz (once per second)
   - Increase for more frequent updates
   - Decrease to reduce RF traffic

3. **Recording settings**
   - Choose codec (H.264 recommended)
   - Set quality/bitrate
   - Configure retention policy

## Step 5: Testing / Kiểm tra

### Individual Tests

1. **Camera power test**
   ```
   - Full charge battery
   - Power on camera
   - Run for 2+ hours
   - Monitor battery drain
   - Verify low battery alert
   ```

2. **Video quality test**
   ```
   - Check video clarity
   - Test at different lighting
   - Verify frame rate
   - Check for interference
   ```

3. **Telemetry test**
   ```bash
   # Monitor telemetry for 5 minutes
   cd scripts
   python3 test_rf_link.py --channel 76 --timeout 300
   
   # Verify:
   # - Consistent packet reception
   # - Accurate battery readings
   # - Temperature within limits
   ```

4. **Range test**
   ```
   - Start at 10m distance
   - Move progressively further
   - Note signal degradation points
   - Mark maximum reliable range
   ```

### Integrated System Test

1. **Multi-camera test**
   - Power on all cameras
   - Verify all appear on dashboard
   - Check for channel interference
   - Monitor CPU/memory usage

2. **Recording test**
   - Start recording on all cameras
   - Record for 10+ minutes
   - Stop recording
   - Verify files are playable
   - Check file sizes

3. **Stress test**
   - Run system for 4+ hours
   - Monitor for errors
   - Check log files
   - Verify auto-reconnection

4. **Failover test**
   - Power off one camera
   - Verify removal from dashboard
   - Power back on
   - Verify reconnection

## Step 6: Production Deployment / Triển khai sản xuất

### Create System Service

**Receiver as systemd service:**
```bash
# Create service file
sudo nano /etc/systemd/system/helmet-camera-receiver.service

# Add content:
[Unit]
Description=Helmet Camera RF Receiver
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/helmet-camera-streaming/receiver/backend
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable helmet-camera-receiver
sudo systemctl start helmet-camera-receiver

# Check status
sudo systemctl status helmet-camera-receiver
```

### Monitoring and Logging

1. **Set up log rotation**
   ```bash
   sudo nano /etc/logrotate.d/helmet-camera
   
   # Add:
   /home/pi/helmet-camera-streaming/logs/*.log {
       daily
       rotate 7
       compress
       delaycompress
       missingok
       notifempty
   }
   ```

2. **Monitor system health**
   ```bash
   # Check logs
   tail -f ~/helmet-camera-streaming/logs/receiver.log
   
   # Monitor system resources
   htop
   
   # Check disk space
   df -h
   ```

### User Training

1. **Operator training**
   - Dashboard navigation
   - Starting/stopping recording
   - Channel selection
   - Reading telemetry
   - Basic troubleshooting

2. **Maintenance training**
   - Battery charging procedures
   - Daily system checks
   - Log review
   - Backup procedures

## Step 7: Maintenance / Bảo trì

### Daily Checks

- [ ] Check all cameras power on correctly
- [ ] Verify telemetry from all units
- [ ] Review recordings from previous day
- [ ] Check disk space availability
- [ ] Monitor for errors in logs

### Weekly Maintenance

- [ ] Charge all batteries fully
- [ ] Clean camera lenses
- [ ] Check antenna connections
- [ ] Review system performance
- [ ] Delete old recordings if needed

### Monthly Maintenance

- [ ] Update firmware if new version available
- [ ] Test all cameras at maximum range
- [ ] Inspect cables and connectors
- [ ] Back up configuration files
- [ ] Review and optimize settings

## Troubleshooting Guide / Hướng dẫn xử lý sự cố

### Camera won't start

1. Check power supply voltage (should be 5V)
2. Verify battery is charged
3. Check serial output for error messages
4. Try reloading firmware

### No video signal

1. Verify TX and RX on same channel
2. Check antenna connections
3. Move closer for initial test
4. Try different channel
5. Check video TX is powered

### Telemetry not received

1. Verify nRF24 connections
2. Check channel matches
3. Test with test_rf_link.py script
4. Try different nRF24 module

### Poor range

1. Check antenna orientation (vertical)
2. Remove obstacles if possible
3. Increase TX power (if legal)
4. Use better antennas
5. Ensure clear line of sight

### Dashboard not accessible

1. Check backend service is running
2. Verify correct port (default 8080)
3. Check firewall rules
4. Test from local browser first

## Safety Guidelines / Hướng dẫn an toàn

### Electrical Safety

- Use proper voltage regulators
- Don't mix up battery polarity
- Insulate all connections
- Use fuses where appropriate

### RF Safety

- Keep antennas 20cm+ from body when transmitting
- Don't exceed legal power limits
- Use proper antennas (not makeshift)

### Battery Safety

- Use LiPo charging bags
- Never discharge below 3.0V/cell
- Monitor temperature during charge
- Dispose damaged batteries properly

### Operational Safety

- Ensure cameras don't obstruct vision
- Secure all equipment to prevent falls
- Follow workplace safety procedures
- Have emergency shutdown procedure

## Backup and Recovery / Sao lưu và Phục hồi

### Regular Backups

```bash
# Backup configuration
cp -r ~/helmet-camera-streaming/configs ~/backup/

# Backup recordings (to external drive)
rsync -av ~/helmet-camera-streaming/recordings /mnt/backup/

# Backup database (if used)
# mysqldump or sqlite3 .dump
```

### Disaster Recovery

1. **System failure recovery**
   - Keep spare Raspberry Pi with image
   - Document all configurations
   - Have backup power supply

2. **Data recovery**
   - Maintain offsite backups
   - Test restore procedures
   - Document recovery steps

## Support and Resources / Hỗ trợ và Tài nguyên

- **Documentation**: See `/docs` folder
- **GitHub Issues**: Report bugs and issues
- **Community**: Join discussions
- **Email**: [Project support email]

---

**Good luck with your deployment!**

**Chúc bạn triển khai thành công!**
