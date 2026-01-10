# Windows Deployment Guide
# Hướng dẫn triển khai trên Windows

Complete guide for deploying the Helmet Camera RF Receiver Station on Windows 10/11.

Hướng dẫn đầy đủ để triển khai Trạm Thu Camera Mũ Bảo Hiểm RF trên Windows 10/11.

---

## Table of Contents / Mục lục

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Quick Start Guide](#quick-start-guide)
4. [Camera Setup](#camera-setup)
5. [Performance Optimization](#performance-optimization)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)
8. [Advanced Configuration](#advanced-configuration)

---

## System Requirements

### Minimum Requirements / Yêu cầu tối thiểu

| Component | Specification |
|-----------|--------------|
| OS | Windows 10 64-bit (version 1809+) or Windows 11 |
| CPU | Intel Core i3 / AMD Ryzen 3 (4 cores) |
| RAM | 8 GB |
| Storage | 50 GB free space (SSD recommended) |
| USB | USB 3.0 ports (1 per camera) |
| Network | 100 Mbps Ethernet or WiFi |

### Recommended Requirements / Yêu cầu đề xuất

| Component | Specification |
|-----------|--------------|
| OS | Windows 11 64-bit (latest) |
| CPU | Intel Core i5/i7 / AMD Ryzen 5/7 (6+ cores) |
| RAM | 16 GB or more |
| Storage | 256 GB+ SSD |
| USB | USB 3.0 ports with powered hub |
| Network | Gigabit Ethernet |
| GPU | NVIDIA GTX 1050+ / AMD RX 560+ (for GPU encoding) |

### Supported Configurations

- **1-2 cameras**: Minimum specs sufficient
- **4 cameras**: Recommended specs
- **8 cameras**: High-end system (i7/Ryzen 7, 16GB+ RAM, dedicated GPU)

---

## Prerequisites Installation

### Step 1: Install Python 3.8+

**Download and Install:**

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download Python 3.11.x (recommended) or 3.8+
3. Run the installer
4. ⚠️ **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"

**Verify Installation:**

```powershell
python --version
# Should output: Python 3.11.x
```

### Step 2: Install Git for Windows (Optional)

**Download and Install:**

1. Go to [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Download and run the installer
3. Use default settings

**Verify Installation:**

```powershell
git --version
# Should output: git version 2.x.x
```

### Step 3: Install FFmpeg

**Method 1: Via Chocolatey (Recommended)**

1. Install Chocolatey (if not installed):
   - Open PowerShell as Administrator
   - Run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. Install FFmpeg:
   ```powershell
   choco install ffmpeg -y
   ```

**Method 2: Manual Installation**

1. Download FFmpeg from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Download "ffmpeg-release-full.7z"
3. Extract to `C:\ffmpeg`
4. Add `C:\ffmpeg\bin` to system PATH:
   - Open "Environment Variables" in System Properties
   - Edit "Path" in System variables
   - Add new entry: `C:\ffmpeg\bin`
   - Click OK and restart terminal

**Verify Installation:**

```powershell
ffmpeg -version
# Should output FFmpeg version information
```

### Step 4: Install Visual C++ Redistributables

Download and install from:
- [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)

This is required for OpenCV and other C++ dependencies.

---

## Quick Start Guide

### Method 1: Automated Setup (Recommended)

1. **Clone the repository:**

```powershell
git clone https://github.com/doduc16vtkt-del/helmet-camera-streaming.git
cd helmet-camera-streaming
```

Or download ZIP from GitHub and extract.

2. **Run setup script (as Administrator):**

```powershell
# Right-click PowerShell and select "Run as Administrator"
.\scripts\setup_windows.ps1
```

The script will:
- ✅ Check Python, FFmpeg, Git
- ✅ Install Python packages
- ✅ Configure Windows Firewall
- ✅ Optimize USB and power settings
- ✅ Create desktop shortcut
- ✅ Detect GPU

3. **Connect USB capture cards**

4. **Start the server:**

```powershell
cd receiver\backend
python app.py
```

Or double-click the desktop shortcut!

5. **Open browser:**

Navigate to [http://localhost:8080](http://localhost:8080)

### Method 2: Manual Setup

1. **Clone repository** (as above)

2. **Install dependencies:**

```powershell
cd helmet-camera-streaming
.\scripts\install_dependencies_windows.ps1
```

3. **Configure firewall manually:**

Open Windows Defender Firewall → Advanced settings → Inbound Rules:
- Allow TCP port 8080
- Allow UDP ports 49152-65535

4. **Start server:**

```powershell
cd receiver\backend
python app.py
```

---

## Camera Setup

### USB Capture Card Recommendations

For best results on Windows:

| Brand/Model | Price | Notes |
|------------|-------|-------|
| Elgato Cam Link 4K | $130 | Professional quality, plug-and-play |
| AVerMedia Live Gamer Portable 2 Plus | $150 | Hardware encoding |
| Mirabox USB 3.0 HDMI Capture | $30 | Budget option, works well |
| Pengo USB 3.0 HDMI Capture | $25 | Basic capture, acceptable latency |
| EasyCap USB 2.0 | $10 | Avoid - high latency, poor drivers |

**Key Features:**
- ✅ USB 3.0 (not USB 2.0)
- ✅ MJPEG hardware encoding
- ✅ DirectShow compatible
- ✅ UVC (USB Video Class) driver support

### Connecting Cameras

1. **Connect RF receivers to USB capture cards**
   - RX1 (5.8GHz Receiver) → HDMI/AV → USB Capture Card

2. **Connect USB capture cards to PC**
   - Use USB 3.0 ports (blue)
   - For 4+ cameras, use powered USB 3.0 hub

3. **Verify in Device Manager**
   - Open Device Manager (Win+X, then M)
   - Expand "Cameras" or "Sound, video and game controllers"
   - Check that devices are listed without warnings

### Testing Cameras

**Method 1: MSMF Test Utility (Recommended)**

Run the comprehensive MSMF test:

```powershell
cd scripts
python test_camera_msmf.py
```

This will:
- Test MSMF backend compatibility
- Verify initialization sequence
- Test camera properties
- Compare backends (MSMF vs DirectShow)
- Provide detailed diagnostics

**Example output:**
```
✅ Camera 0 - MSMF: PASSED
  Resolution: 640x480
  FPS (reported): 30.0
  FPS (measured): 29.8
  Backend: MSMF

✅ Your system is ready for production use!
```

**Method 2: Windows PowerShell Test**

Run the camera test utility:

```powershell
.\scripts\test_cameras_windows.ps1
```

This will:
- Discover all connected cameras
- Show device IDs and capabilities
- Test capture from each camera
- Generate a report

**Example output:**
```
✅ Camera 0 detected
   Resolution: 1920x1080
   FPS: 30
   Backend: MSMF

✅ Camera 1 detected
   Resolution: 1280x720
   FPS: 60
   Backend: MSMF
```

**Method 3: Quick Test in Python**

```python
import cv2

# Test MSMF backend
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
if cap.isOpened():
    ret, frame = cap.read()  # Read initial frame
    if ret:
        print(f"✅ Camera works! Frame: {frame.shape}")
    cap.release()
```

---

## Performance Optimization

### Windows Power Settings

1. **Set High Performance power plan:**

```powershell
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
```

2. **Disable USB selective suspend:**

```powershell
powercfg /change usb-selective-suspend-setting 0
```

Or manually:
- Control Panel → Power Options → Change plan settings
- Change advanced power settings
- USB settings → USB selective suspend setting → Disabled

3. **Prevent sleep during operation:**
- Set "Turn off display" to Never
- Set "Put computer to sleep" to Never

### GPU Acceleration

**NVIDIA GPUs:**

1. Ensure latest drivers from [nvidia.com/drivers](https://www.nvidia.com/drivers)

2. Edit `configs/receiver_config_windows.yaml`:
```yaml
recording:
  codec: "h264_nvenc"  # Use NVIDIA encoder
  use_gpu_encoding: true
  gpu_encoder: "nvenc"
```

3. Verify GPU usage:
```powershell
nvidia-smi
```

**Intel GPUs (Quick Sync):**

1. Enable in BIOS if disabled

2. Configure:
```yaml
recording:
  codec: "h264_qsv"
  use_gpu_encoding: true
  gpu_encoder: "qsv"
```

**AMD GPUs:**

1. Install latest drivers from [amd.com/drivers](https://www.amd.com/drivers)

2. Configure:
```yaml
recording:
  codec: "h264_amf"
  use_gpu_encoding: true
  gpu_encoder: "amf"
```

### Network Optimization

1. **Disable WiFi power saving:**
   - Device Manager → Network adapters
   - Right-click WiFi adapter → Properties
   - Power Management → Uncheck "Allow computer to turn off this device"

2. **Set static IP (for production):**
   - Control Panel → Network → Change adapter settings
   - Right-click adapter → Properties → IPv4 → Properties
   - Set static IP address

3. **Prioritize network traffic:**
   - Open Registry Editor (regedit)
   - Navigate to: `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Psched`
   - Create DWORD: `NonBestEffortLimit` = `0`

### Disk Optimization

1. **Use SSD for recordings**
2. **Enable write caching:**
   - Device Manager → Disk drives
   - Properties → Policies → Enable write caching
3. **Defragment regularly** (for HDD only, not SSD)

---

## Troubleshooting

### Camera Not Detected

**Problem:** Camera doesn't appear in test script or dashboard

**Solutions:**

1. **Check Device Manager:**
   - Open Device Manager (Win+X, then M)
   - Look for yellow warning icons
   - If present, update driver or reinstall

2. **Try different USB port:**
   - USB 3.0 (blue) ports preferred
   - Avoid USB hubs for testing
   - Try front panel vs rear ports

3. **Update camera drivers:**
   - Device Manager → Camera → Update driver
   - Or download from manufacturer website

4. **Check camera in other apps:**
   - Open Windows Camera app
   - Try with VLC or OBS Studio
   - If works there, it's a configuration issue

### Port 8080 Already in Use

**Problem:** Error "Address already in use" when starting server

**Solutions:**

1. **Find process using port 8080:**
```powershell
netstat -ano | findstr :8080
```

2. **Kill the process:**
```powershell
taskkill /PID <PID> /F
```

3. **Or change port in config:**
Edit `configs/receiver_config_windows.yaml`:
```yaml
dashboard:
  port: 8081  # Change to different port
```

### High CPU Usage

**Problem:** CPU usage 80-100% with multiple cameras

**Solutions:**

1. **Enable GPU encoding** (see Performance Optimization section)

2. **Reduce resolution:**
```yaml
capture:
  resolution: "640x480"  # Instead of 1080p
```

3. **Reduce frame rate:**
```yaml
capture:
  fps: 15  # Instead of 30
```

4. **Close unnecessary applications**

5. **Check for malware/antivirus interference**

### Firewall Blocking Connection

**Problem:** Can't access dashboard from browser or remote device

**Solutions:**

1. **Re-run setup script as Administrator:**
```powershell
.\scripts\setup_windows.ps1
```

2. **Manually add firewall rules:**
   - Windows Defender Firewall → Advanced settings
   - Inbound Rules → New Rule
   - Port → TCP → 8080
   - Allow the connection

3. **Temporarily disable firewall for testing:**
   - Control Panel → Windows Defender Firewall
   - Turn off (testing only!)

### Camera Compatibility Issues

**Problem:** Camera fails to open or "MF_E_INVALIDMEDIATYPE" error on Windows 10/11

**Root Cause:**
- DirectShow backend doesn't work reliably on modern Windows 10/11
- MSMF (Media Foundation) backend requires reading initial frame BEFORE setting camera properties
- Some cameras don't support all requested formats/resolutions

**Solutions:**

1. **Verify MSMF backend is configured (v2.0+):**

Check `configs/receiver_config_windows.yaml`:
```yaml
capture:
  backend: msmf  # Should be "msmf", NOT "dshow"
```

2. **Test camera with MSMF utility:**
```powershell
cd scripts
python test_camera_msmf.py
```

This will:
- Test MSMF backend compatibility
- Test initialization sequence
- Compare MSMF vs DirectShow performance
- Provide diagnostics and recommendations

3. **Understand MSMF vs DirectShow:**

| Feature | MSMF (Recommended) | DirectShow (Legacy) |
|---------|-------------------|-------------------|
| Windows 10/11 Support | ✅ Excellent | ⚠️ Limited |
| Initialization | Read frame first, then set properties | Set properties anytime |
| Reliability | ✅ High | ❌ Low on modern Windows |
| Error Code | MF_E_INVALIDMEDIATYPE if wrong order | Various DSHOW errors |

4. **Why initialization order matters:**

MSMF backend requires this sequence:
```python
# 1. Open camera
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

# 2. Read initial frame FIRST (critical!)
ret, frame = cap.read()

# 3. NOW set properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

Setting properties before reading the initial frame causes error -1072873822 (MF_E_INVALIDMEDIATYPE).

5. **Camera format compatibility:**

If camera still fails, try different formats:
```yaml
capture:
  format: "YUYV"  # Instead of MJPEG
```

Or let camera use defaults:
```yaml
capture:
  resolution: "640x480"  # Start with lower resolution
  fps: 30
```

6. **Update system:**
- Windows Update to latest version
- Update camera drivers in Device Manager
- Update OpenCV: `pip install --upgrade opencv-python`

### DirectShow Errors (Legacy)

**Problem:** "Failed to open video device" or DirectShow backend errors

**Note:** As of v2.0, the system uses MSMF backend by default. DirectShow is deprecated.

**Solutions:**

1. **Switch to MSMF backend** (recommended - see Camera Compatibility Issues above)

2. **If you must use DirectShow:**
   - Update OpenCV: `pip install --upgrade opencv-python`
   - Install DirectShow filters: Download K-Lite Codec Pack (Basic) from [codecguide.com](https://codecguide.com)
   - Check camera format compatibility

3. **Reinstall Visual C++ Redistributables**

### Low Frame Rate / High Latency

**Problem:** Video is choppy, latency > 500ms

**Solutions:**

1. **Reduce buffer size:**
```yaml
capture:
  buffer_size: 1  # Minimal latency
```

2. **Use MJPEG format:**
```yaml
capture:
  format: "MJPEG"
```

3. **Enable hardware acceleration:**
```yaml
capture:
  hardware_acceleration: true
```

4. **Check USB bandwidth:**
   - USBTreeView tool shows bandwidth usage
   - Don't overload single USB controller
   - Spread cameras across multiple controllers

5. **Close other USB devices:**
   - External drives, printers, etc.

---

## Production Deployment

### Running as Windows Service

To run 24/7 as a background service:

1. **Install service:**
```powershell
.\scripts\install_service_windows.ps1
```

2. **Start service:**
```powershell
Start-Service HelmetCameraService
```

3. **Check status:**
```powershell
Get-Service HelmetCameraService
```

4. **Stop service:**
```powershell
Stop-Service HelmetCameraService
```

### Auto-start on Boot

The Windows service automatically starts on boot.

Or use Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: When computer starts
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\helmet-camera-streaming\receiver\backend\app.py`

### Remote Access Setup

1. **Port forwarding on router:**
   - Forward external port 8080 to PC's IP:8080

2. **Dynamic DNS (if no static IP):**
   - Use services like No-IP or DynDNS

3. **Authentication:**
   - Enable in config:
   ```yaml
   dashboard:
     auth_enabled: true
     username: "admin"
     password: "secure_password_here"
   ```

4. **HTTPS (recommended for remote):**
   - Use reverse proxy (nginx, IIS)
   - Or Cloudflare Tunnel

### Backup and Restore

**Backup:**
```powershell
# Backup recordings
xcopy /E /I C:\HelmetCamera\Recordings D:\Backup\Recordings

# Backup configuration
copy configs\*.yaml D:\Backup\configs\
```

**Automated backup script:**
Create `backup.bat`:
```batch
@echo off
set SOURCE=C:\HelmetCamera\Recordings
set DEST=D:\Backup\%date:~-4,4%%date:~-7,2%%date:~-10,2%
xcopy /E /I /Y %SOURCE% %DEST%
```

Schedule with Task Scheduler (daily at 2 AM).

### Monitoring and Alerts

1. **Enable logging:**
```yaml
logging:
  level: "INFO"
  file: "logs\\receiver.log"
```

2. **Monitor logs:**
```powershell
Get-Content logs\receiver.log -Tail 50 -Wait
```

3. **Email alerts:**
```yaml
notifications:
  enabled: true
  email_enabled: true
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  smtp_user: "your-email@gmail.com"
  smtp_password: "app-password"
  alert_recipients: ["admin@example.com"]
```

4. **Windows Event Viewer:**
   - Application and Services Logs
   - Look for HelmetCameraService events

---

## Advanced Configuration

### Multi-GPU Setup

For systems with multiple GPUs:

```yaml
performance:
  gpu_acceleration: true
  primary_gpu: 0  # Use first GPU
  encoding_gpu: 1  # Use second GPU for encoding
```

### Quality vs Performance

**Low Latency (Racing/FPV):**
```yaml
capture:
  resolution: "640x480"
  fps: 30
  buffer_size: 1
recording:
  codec: "h264_nvenc"
  quality: 28  # Lower quality, smaller files
```

**High Quality (Security/Surveillance):**
```yaml
capture:
  resolution: "1920x1080"
  fps: 30
  buffer_size: 4
recording:
  codec: "h264_nvenc"
  quality: 18  # Higher quality, larger files
```

### Network Streaming

For remote viewing:

```yaml
network:
  max_bandwidth: 5  # Mbps per stream
  buffer_time: 3    # Seconds
```

---

## Additional Resources

### Useful Tools

- **USBTreeView**: Analyze USB bandwidth and connections
- **GPU-Z**: Monitor GPU usage and specs
- **Process Explorer**: Advanced task manager
- **Wireshark**: Network traffic analysis

### Support

- GitHub Issues: [https://github.com/doduc16vtkt-del/helmet-camera-streaming/issues](https://github.com/doduc16vtkt-del/helmet-camera-streaming/issues)
- Documentation: See `docs/` folder
- Hardware Guide: `docs/windows-hardware-guide.md`

### Updates

Check for updates regularly:
```powershell
git pull origin main
.\scripts\install_dependencies_windows.ps1
```

---

**Last updated:** 2026-01-10

**Made with ❤️ for Windows users**
