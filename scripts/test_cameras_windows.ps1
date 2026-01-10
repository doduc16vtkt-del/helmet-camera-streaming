# Windows Camera Testing Utility
# Tiện ích kiểm tra camera cho Windows
#
# Usage: .\scripts\test_cameras_windows.ps1

$ErrorActionPreference = "Continue"

function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Failure { Write-Host $args -ForegroundColor Red }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📹 Windows Camera Testing Utility" -ForegroundColor Cyan
Write-Host "   Tiện ích kiểm tra camera Windows" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python and OpenCV
Write-Info "Checking requirements..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✅ $pythonVersion found"
} catch {
    Write-Failure "❌ Python not found!"
    exit 1
}

Write-Host ""

# Create test script
$testScript = @"
import cv2
import platform
import sys

def discover_cameras():
    '''Discover all available cameras'''
    print('Scanning for cameras...')
    print('Dang quet tim camera...')
    print()
    
    available_cameras = []
    
    # Try devices 0-9
    for device_id in range(10):
        try:
            cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)
            if cap.isOpened():
                # Get camera info
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                backend = cap.getBackendName()
                
                available_cameras.append({
                    'id': device_id,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'backend': backend
                })
                
                print(f'✅ Camera {device_id} detected')
                print(f'   Resolution: {width}x{height}')
                print(f'   FPS: {fps}')
                print(f'   Backend: {backend}')
                print()
                
                cap.release()
        except Exception as e:
            pass
    
    return available_cameras

def test_camera(device_id, duration=3):
    '''Test a specific camera'''
    print(f'Testing camera {device_id} for {duration} seconds...')
    print(f'Dang kiem tra camera {device_id} trong {duration} giay...')
    print()
    
    try:
        cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print(f'❌ Failed to open camera {device_id}')
            return False
        
        # Configure camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        import time
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if ret:
                frame_count += 1
            else:
                print('⚠️  Failed to read frame')
        
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed
        
        print(f'✅ Test completed')
        print(f'   Total frames: {frame_count}')
        print(f'   Average FPS: {avg_fps:.2f}')
        print(f'   Latency: {1000/avg_fps:.2f}ms per frame')
        print()
        
        cap.release()
        return True
        
    except Exception as e:
        print(f'❌ Error testing camera: {e}')
        return False

def main():
    print('=' * 60)
    print('Windows Camera Testing Utility')
    print('Tien ich kiem tra camera Windows')
    print('=' * 60)
    print()
    print(f'Platform: {platform.system()} {platform.release()}')
    print(f'Python: {platform.python_version()}')
    print(f'OpenCV: {cv2.__version__}')
    print()
    
    # Discover cameras
    cameras = discover_cameras()
    
    if not cameras:
        print('❌ No cameras found!')
        print('   Khong tim thay camera nao!')
        print()
        print('Troubleshooting:')
        print('1. Check if cameras are connected')
        print('2. Check Device Manager for camera status')
        print('3. Try reconnecting USB cables')
        print('4. Check camera drivers are installed')
        return 1
    
    print(f'Found {len(cameras)} camera(s)')
    print(f'Tim thay {len(cameras)} camera')
    print()
    
    # Generate report
    print('=' * 60)
    print('Camera Report / Bao cao Camera')
    print('=' * 60)
    print()
    
    for cam in cameras:
        print(f'Camera {cam["id"]}:')
        print(f'  Device ID: {cam["id"]}')
        print(f'  Resolution: {cam["width"]}x{cam["height"]}')
        print(f'  FPS: {cam["fps"]}')
        print(f'  Backend: {cam["backend"]}')
        print()
    
    # Test each camera
    print('=' * 60)
    print('Testing Cameras / Kiem tra Camera')
    print('=' * 60)
    print()
    
    for cam in cameras:
        test_camera(cam['id'])
    
    print('=' * 60)
    print('Testing Complete / Kiem tra hoan tat')
    print('=' * 60)
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"@

# Save test script to temp file with unique name
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$processId = $PID
$tempScript = Join-Path $env:TEMP "test_cameras_${timestamp}_${processId}.py"
$testScript | Out-File -FilePath $tempScript -Encoding UTF8

# Run test script
Write-Info "Running camera tests..."
Write-Host ""

python $tempScript

# Cleanup
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Info "For more information, see: docs\windows-deployment.md"
Write-Host ""

# Pause at the end
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
