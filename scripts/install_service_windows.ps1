# Windows Service Installation Script
# Script cài đặt dịch vụ Windows
#
# Run as Administrator / Chạy với quyền quản trị viên
# .\scripts\install_service_windows.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Failure { Write-Host $args -ForegroundColor Red }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🔧 Windows Service Installation" -ForegroundColor Cyan
Write-Host "   Cài đặt dịch vụ Windows" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Failure "❌ This script must be run as Administrator!"
    exit 1
}

# Check Python
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✅ $pythonVersion found"
} catch {
    Write-Failure "❌ Python not found!"
    exit 1
}

Write-Host ""

# Check pywin32
Write-Info "Checking pywin32 package..."
try {
    python -c "import win32serviceutil" 2>$null
    Write-Success "✅ pywin32 is installed"
} catch {
    Write-Warning "⚠️  pywin32 not found, installing..."
    python -m pip install pywin32
    
    # Run post-install script
    Write-Info "Running pywin32 post-install script..."
    python "$env:PYTHONPATH\Scripts\pywin32_postinstall.py" -install
    
    Write-Success "✅ pywin32 installed"
}

Write-Host ""

# Service configuration
$serviceName = "HelmetCameraService"
$displayName = "Helmet Camera RF Receiver"
$description = "RF video streaming receiver for helmet cameras"
$servicePath = Join-Path (Get-Location) "receiver\backend\windows_service.py"

Write-Info "Service Configuration:"
Write-Host "  Name: $serviceName" -ForegroundColor White
Write-Host "  Display Name: $displayName" -ForegroundColor White
Write-Host "  Path: $servicePath" -ForegroundColor White
Write-Host ""

# Check if service already exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if ($existingService) {
    Write-Warning "⚠️  Service already exists!"
    $response = Read-Host "Do you want to reinstall? (y/n)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Info "Stopping service if running..."
        try {
            Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        } catch {}
        
        Write-Info "Removing existing service..."
        python $servicePath remove
        Start-Sleep -Seconds 2
        Write-Success "✅ Existing service removed"
    } else {
        Write-Info "Installation cancelled"
        exit 0
    }
}

Write-Host ""

# Install service
Write-Info "Installing Windows Service..."
try {
    python $servicePath install
    Write-Success "✅ Service installed successfully!"
} catch {
    Write-Failure "❌ Failed to install service"
    Write-Info "Error: $_"
    exit 1
}

Write-Host ""

# Configure service startup type
Write-Info "Configuring service to start automatically..."
try {
    Set-Service -Name $serviceName -StartupType Automatic
    Write-Success "✅ Service set to start automatically on boot"
} catch {
    Write-Warning "⚠️  Could not set automatic startup"
}

Write-Host ""

# Ask if user wants to start service now
$startNow = Read-Host "Do you want to start the service now? (y/n)"

if ($startNow -eq 'y' -or $startNow -eq 'Y') {
    Write-Info "Starting service..."
    try {
        Start-Service -Name $serviceName
        Start-Sleep -Seconds 3
        
        $service = Get-Service -Name $serviceName
        if ($service.Status -eq 'Running') {
            Write-Success "✅ Service started successfully!"
        } else {
            Write-Warning "⚠️  Service status: $($service.Status)"
        }
    } catch {
        Write-Failure "❌ Failed to start service"
        Write-Info "Error: $_"
        Write-Info "Check logs at: logs\service.log"
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Show service management commands
Write-Info "Service Management Commands:"
Write-Host ""
Write-Host "Start service:" -ForegroundColor Cyan
Write-Host "  Start-Service $serviceName" -ForegroundColor White
Write-Host "  Or: python $servicePath start" -ForegroundColor White
Write-Host ""
Write-Host "Stop service:" -ForegroundColor Cyan
Write-Host "  Stop-Service $serviceName" -ForegroundColor White
Write-Host "  Or: python $servicePath stop" -ForegroundColor White
Write-Host ""
Write-Host "Check status:" -ForegroundColor Cyan
Write-Host "  Get-Service $serviceName" -ForegroundColor White
Write-Host ""
Write-Host "View service in Windows Services Manager:" -ForegroundColor Cyan
Write-Host "  services.msc" -ForegroundColor White
Write-Host ""
Write-Host "Remove service:" -ForegroundColor Cyan
Write-Host "  python $servicePath remove" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Cyan
Write-Host "  Get-Content logs\service.log -Tail 50 -Wait" -ForegroundColor White
Write-Host ""

# Additional information
Write-Info "Service Features:"
Write-Host "  ✅ Starts automatically on system boot" -ForegroundColor White
Write-Host "  ✅ Restarts automatically on failure" -ForegroundColor White
Write-Host "  ✅ Runs in background (no console window)" -ForegroundColor White
Write-Host "  ✅ Integrates with Windows Event Viewer" -ForegroundColor White
Write-Host ""

Write-Info "Dashboard will be available at: http://localhost:8080"
Write-Host ""

# Pause at the end
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
