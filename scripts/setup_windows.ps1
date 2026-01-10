# Windows Setup Script for Helmet Camera RF Receiver
# Script cài đặt Windows cho máy thu Camera Mũ Bảo Hiểm RF
#
# Run as Administrator / Chạy với quyền quản trị viên
# .\scripts\setup_windows.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Continue"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Failure { Write-Host $args -ForegroundColor Red }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🚀 Helmet Camera Receiver - Windows Setup" -ForegroundColor Cyan
Write-Host "   Cài đặt Windows - Máy thu Camera Mũ" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Failure "❌ This script must be run as Administrator!"
    Write-Failure "   Script này phải chạy với quyền quản trị viên!"
    Write-Host ""
    Write-Info "Right-click PowerShell and select 'Run as Administrator'"
    Write-Info "Nhấp chuột phải PowerShell và chọn 'Run as Administrator'"
    exit 1
}

# Step 1: Check Python
Write-Info "Step 1/7: Checking Python installation..."
Write-Info "Bước 1/7: Kiểm tra cài đặt Python..."

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -ge 3 -and $minor -ge 8) {
            Write-Success "✅ Python $pythonVersion detected"
        } else {
            Write-Warning "⚠️  Python version is too old: $pythonVersion"
            Write-Warning "   Please install Python 3.8 or newer"
            Write-Info "   Download from: https://www.python.org/downloads/"
        }
    }
} catch {
    Write-Failure "❌ Python not found!"
    Write-Info "   Please install Python 3.8 or newer"
    Write-Info "   Download from: https://www.python.org/downloads/"
    Write-Info "   Vui lòng cài đặt Python 3.8 trở lên"
}

Write-Host ""

# Step 2: Check FFmpeg
Write-Info "Step 2/7: Checking FFmpeg installation..."
Write-Info "Bước 2/7: Kiểm tra cài đặt FFmpeg..."

try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    if ($ffmpegVersion) {
        Write-Success "✅ FFmpeg installed"
    }
} catch {
    Write-Warning "⚠️  FFmpeg not found"
    Write-Info "   Installing FFmpeg via Chocolatey..."
    
    # Check if Chocolatey is installed
    try {
        choco --version | Out-Null
        Write-Info "   Chocolatey found, installing FFmpeg..."
        choco install ffmpeg -y
        Write-Success "✅ FFmpeg installed"
    } catch {
        Write-Warning "   Chocolatey not found"
        Write-Info "   Please install FFmpeg manually:"
        Write-Info "   1. Download from: https://www.gyan.dev/ffmpeg/builds/"
        Write-Info "   2. Extract to C:\ffmpeg"
        Write-Info "   3. Add C:\ffmpeg\bin to system PATH"
    }
}

Write-Host ""

# Step 3: Check Git
Write-Info "Step 3/7: Checking Git installation..."
Write-Info "Bước 3/7: Kiểm tra cài đặt Git..."

try {
    $gitVersion = git --version 2>&1
    if ($gitVersion) {
        Write-Success "✅ $gitVersion detected"
    }
} catch {
    Write-Warning "⚠️  Git not found (optional)"
    Write-Info "   Download from: https://git-scm.com/download/win"
}

Write-Host ""

# Step 4: Install Python packages
Write-Info "Step 4/7: Installing Python packages..."
Write-Info "Bước 4/7: Cài đặt các gói Python..."

$requirementsPath = "receiver\backend\requirements.txt"

if (Test-Path $requirementsPath) {
    try {
        # Upgrade pip first
        Write-Info "   Upgrading pip..."
        python -m pip install --upgrade pip | Out-Null
        
        # Install requirements
        Write-Info "   Installing packages from requirements.txt..."
        python -m pip install -r $requirementsPath
        
        # Install Windows-specific packages
        Write-Info "   Installing Windows-specific packages..."
        python -m pip install psutil pywin32
        
        Write-Success "✅ Python packages installed"
    } catch {
        Write-Failure "❌ Failed to install Python packages"
        Write-Info "   Error: $_"
    }
} else {
    Write-Warning "⚠️  requirements.txt not found at $requirementsPath"
}

Write-Host ""

# Step 5: Configure Windows Firewall
Write-Info "Step 5/7: Configuring Windows Firewall..."
Write-Info "Bước 5/7: Cấu hình tường lửa Windows..."

try {
    # HTTP/WebSocket port
    $ruleName1 = "Helmet Camera - HTTP"
    $existingRule1 = Get-NetFirewallRule -DisplayName $ruleName1 -ErrorAction SilentlyContinue
    
    if ($existingRule1) {
        Write-Info "   Firewall rule '$ruleName1' already exists"
    } else {
        New-NetFirewallRule -DisplayName $ruleName1 `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort 8080 `
            -Action Allow `
            -Profile Any | Out-Null
        Write-Success "   ✅ Added firewall rule for TCP 8080"
    }
    
    # WebRTC UDP ports
    $ruleName2 = "Helmet Camera - WebRTC"
    $existingRule2 = Get-NetFirewallRule -DisplayName $ruleName2 -ErrorAction SilentlyContinue
    
    if ($existingRule2) {
        Write-Info "   Firewall rule '$ruleName2' already exists"
    } else {
        New-NetFirewallRule -DisplayName $ruleName2 `
            -Direction Inbound `
            -Protocol UDP `
            -LocalPort 49152-65535 `
            -Action Allow `
            -Profile Any | Out-Null
        Write-Success "   ✅ Added firewall rule for UDP 49152-65535"
    }
    
    Write-Success "✅ Firewall rules configured"
} catch {
    Write-Failure "❌ Failed to configure firewall"
    Write-Info "   Error: $_"
}

Write-Host ""

# Step 6: Optimize USB and Power Settings
Write-Info "Step 6/7: Optimizing USB and power settings..."
Write-Info "Bước 6/7: Tối ưu cài đặt USB và nguồn..."

try {
    # Disable USB selective suspend
    Write-Info "   Disabling USB selective suspend..."
    powercfg /change usb-selective-suspend-setting 0
    
    # Set power plan to High Performance
    Write-Info "   Setting power plan to High Performance..."
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    
    Write-Success "✅ Power settings optimized for 24/7 operation"
    Write-Info "   Note: This will increase power consumption"
    Write-Info "   Lưu ý: Điều này sẽ tăng mức tiêu thụ điện"
} catch {
    Write-Warning "⚠️  Could not optimize power settings"
    Write-Info "   You can manually set these in Windows Power Options"
}

Write-Host ""

# Step 7: Create desktop shortcut
Write-Info "Step 7/7: Creating desktop shortcut..."
Write-Info "Bước 7/7: Tạo lối tắt trên màn hình..."

try {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Helmet Camera Receiver.lnk"
    $targetPath = "python.exe"
    $workingDir = Join-Path (Get-Location) "receiver\backend"
    $arguments = "app.py"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $targetPath
    $shortcut.Arguments = $arguments
    $shortcut.WorkingDirectory = $workingDir
    $shortcut.Description = "Helmet Camera RF Receiver Station"
    $shortcut.Save()
    
    Write-Success "✅ Desktop shortcut created"
} catch {
    Write-Warning "⚠️  Could not create desktop shortcut"
    Write-Info "   Error: $_"
}

Write-Host ""

# Display GPU information
Write-Info "Detecting GPU..."
Write-Info "Phát hiện GPU..."

try {
    $gpu = Get-WmiObject Win32_VideoController | Select-Object -First 1
    if ($gpu) {
        Write-Success "✅ GPU: $($gpu.Name)"
        Write-Info "   Video RAM: $([math]::Round($gpu.AdapterRAM / 1GB, 2)) GB"
    }
} catch {
    Write-Info "   Could not detect GPU"
}

Write-Host ""

# Create necessary directories
Write-Info "Creating necessary directories..."
$dirs = @("logs", "recordings")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Info "   Created directory: $dir"
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ Setup Complete! / Cài đặt hoàn tất!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps / Bước tiếp theo:" -ForegroundColor Cyan
Write-Host "1. Connect USB capture cards / Kết nối thẻ chụp USB" -ForegroundColor White
Write-Host "2. Run: cd receiver\backend" -ForegroundColor White
Write-Host "3. Run: python app.py" -ForegroundColor White
Write-Host "4. Open browser: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Or double-click the desktop shortcut!" -ForegroundColor Yellow
Write-Host "Hoặc nhấp đúp vào lối tắt trên màn hình!" -ForegroundColor Yellow
Write-Host ""
Write-Host "For troubleshooting, see: docs\windows-deployment.md" -ForegroundColor Cyan
Write-Host ""

# Pause at the end
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
