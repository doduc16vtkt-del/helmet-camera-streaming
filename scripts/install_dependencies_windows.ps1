# Windows Dependency Installation Script
# Script cài đặt các phụ thuộc cho Windows
#
# Run this to install all required dependencies
# Chạy script này để cài đặt tất cả các phụ thuộc cần thiết

param(
    [switch]$IncludeTorch = $false
)

$ErrorActionPreference = "Stop"

function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Failure { Write-Host $args -ForegroundColor Red }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📦 Installing Dependencies" -ForegroundColor Cyan
Write-Host "   Cài đặt các phụ thuộc" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Info "Checking Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✅ $pythonVersion found"
} catch {
    Write-Failure "❌ Python not found!"
    Write-Info "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
}

Write-Host ""

# Upgrade pip
Write-Info "Upgrading pip..."
try {
    python -m pip install --upgrade pip
    Write-Success "✅ pip upgraded"
} catch {
    Write-Warning "⚠️  Could not upgrade pip"
}

Write-Host ""

# Install requirements.txt
Write-Info "Installing Python packages from requirements.txt..."
$requirementsPath = "receiver\backend\requirements.txt"

if (Test-Path $requirementsPath) {
    try {
        python -m pip install -r $requirementsPath
        Write-Success "✅ Packages installed from requirements.txt"
    } catch {
        Write-Failure "❌ Failed to install packages"
        exit 1
    }
} else {
    Write-Warning "⚠️  requirements.txt not found at $requirementsPath"
}

Write-Host ""

# Install Windows-specific packages
Write-Info "Installing Windows-specific packages..."
try {
    # Performance monitoring
    python -m pip install psutil
    
    # Windows service support
    python -m pip install pywin32
    
    Write-Success "✅ Windows-specific packages installed"
} catch {
    Write-Warning "⚠️  Could not install some Windows-specific packages"
}

Write-Host ""

# Install FFmpeg
Write-Info "Checking FFmpeg..."
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Success "✅ FFmpeg already installed"
} catch {
    Write-Warning "⚠️  FFmpeg not found"
    Write-Info "Attempting to install FFmpeg via Chocolatey..."
    
    # Check Chocolatey
    try {
        choco --version | Out-Null
        choco install ffmpeg -y
        Write-Success "✅ FFmpeg installed via Chocolatey"
    } catch {
        Write-Warning "⚠️  Chocolatey not found"
        Write-Info "Please install FFmpeg manually:"
        Write-Info "1. Download from: https://www.gyan.dev/ffmpeg/builds/"
        Write-Info "2. Extract to C:\ffmpeg"
        Write-Info "3. Add C:\ffmpeg\bin to system PATH"
        Write-Info "4. Restart terminal"
    }
}

Write-Host ""

# Optional: PyTorch for GPU acceleration
if ($IncludeTorch) {
    Write-Info "Installing PyTorch (CUDA support)..."
    Write-Info "This may take several minutes..."
    
    try {
        # Install PyTorch with CUDA support
        python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        Write-Success "✅ PyTorch installed with CUDA support"
    } catch {
        Write-Warning "⚠️  Could not install PyTorch"
        Write-Info "You can install it manually later for GPU acceleration"
    }
    
    Write-Host ""
}

# Check Visual C++ Redistributables
Write-Info "Checking Visual C++ Redistributables..."
$vcRedist = Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*Visual C++*Redistributable*"}
if ($vcRedist) {
    Write-Success "✅ Visual C++ Redistributables found"
} else {
    Write-Warning "⚠️  Visual C++ Redistributables not detected"
    Write-Info "Some features may not work without them"
    Write-Info "Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe"
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ Dependencies Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Summary
Write-Info "Installed packages:"
Write-Host "  - Flask and Flask-SocketIO (web server)" -ForegroundColor White
Write-Host "  - OpenCV (video processing)" -ForegroundColor White
Write-Host "  - PyYAML (configuration)" -ForegroundColor White
Write-Host "  - psutil (performance monitoring)" -ForegroundColor White
Write-Host "  - pywin32 (Windows service support)" -ForegroundColor White

if ($IncludeTorch) {
    Write-Host "  - PyTorch (GPU acceleration)" -ForegroundColor White
}

Write-Host ""
Write-Info "Next steps:"
Write-Host "1. Run setup script: .\scripts\setup_windows.ps1" -ForegroundColor White
Write-Host "2. Start server: python receiver\backend\app.py" -ForegroundColor White
Write-Host ""
