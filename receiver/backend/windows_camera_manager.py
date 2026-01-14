"""
Windows-optimized camera manager with MSMF backend
Ultra-low latency for Windows PC - FIXED VERSION
"""
import cv2
import numpy as np
import threading
import queue
import time
from typing import Dict, Optional
import psutil
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindowsCamera:
    """
    Single camera handler optimized for Windows MSMF backend
    """
    def __init__(self, device_id: int, width: int = 640, height: int = 480, fps: int = 30):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = False
        self.thread = None
        self.last_frame_time = 0
        self.frame_count = 0
        
    def start(self) -> bool:
        """Initialize and start camera capture with MSMF backend"""
        try:
            logger.info(f"Opening camera {self.device_id} with Media Foundation (MSMF)...")
            
            # Use MSMF backend (best for Windows 10/11)
            self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_MSMF)
            
            if not self. cap.isOpened():
                logger.error(f"Failed to open camera {self.device_id}")
                return False
            
            logger.info(f"✅ Camera {self.device_id} opened with MSMF")
            
            # CRITICAL: Read initial frame BEFORE setting properties
            logger.info("Capturing initial frame to initialize camera...")
            ret, test_frame = self.cap.read()
            
            if not ret:
                logger.error("Failed to capture initial frame")
                self.cap.release()
                return False
            
            logger.info(f"✅ Initial frame captured:  {test_frame.shape}")
            
            # Now try to set properties (camera may ignore them)
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Low latency
            except Exception as e:
                logger.warning(f"Could not set all properties: {e}")
            
            # Get actual settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera {self.device_id} actual settings:  {actual_width}x{actual_height} @{actual_fps:. 1f}fps")
            
            # Start capture thread
            self.running = True
            self.thread = threading. Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"✅ Camera {self.device_id} started successfully")
            return True
            
        except Exception as e: 
            logger.error(f"Error starting camera {self.device_id}:  {e}")
            if self.cap:
                self. cap.release()
            return False
    
    def _capture_loop(self):
        """Continuous capture loop (runs in separate thread)"""
        while self.running:
            ret, frame = self.cap.read()
            
            if ret:
                # Non-blocking put (drop if queue full)
                try:
                    self.frame_queue.put_nowait(frame)
                    self.frame_count += 1
                    self.last_frame_time = time.time()
                except queue. Full:
                    pass  # Drop old frame
            else:
                logger.warning(f"Camera {self.device_id}:  Failed to read frame")
                time.sleep(0.01)
    
    def read(self) -> tuple:
        """Read latest frame (non-blocking)"""
        try:
            frame = self.frame_queue.get(timeout=0.1)
            return True, frame
        except queue.Empty:
            return False, None
    
    def get_fps(self) -> float:
        """Calculate actual FPS"""
        if self.last_frame_time > 0:
            return self.fps
        return 0.0
    
    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2. 0)
        if self.cap:
            self.cap.release()
        logger.info(f"Camera {self.device_id} stopped")


class WindowsMultiCameraManager:
    """
    Manage multiple cameras on Windows with MSMF backend
    """
    def __init__(self, max_cameras: int = 8):
        self.max_cameras = max_cameras
        self.cameras: Dict[int, WindowsCamera] = {}
        self.running = False
        
    def discover_cameras(self) -> list:
        """Auto-discover connected cameras with MSMF"""
        logger.info("Discovering cameras with MSMF backend...")
        available = []
        
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
            if cap. isOpened():
                # Test if can read frames
                ret, _ = cap.read()
                if ret:
                    available.append(i)
                    logger. info(f"Found camera at index {i}")
                cap.release()
            else:
                break
        
        logger.info(f"Total cameras found: {len(available)}")
        return available
    
    def start_camera(self, device_id: int) -> bool:
        """Start a specific camera"""
        if device_id in self.cameras:
            logger.warning(f"Camera {device_id} already started")
            return True
        
        if len(self.cameras) >= self.max_cameras:
            logger. error(f"Max cameras ({self. max_cameras}) reached")
            return False
        
        camera = WindowsCamera(device_id)
        if camera.start():
            self.cameras[device_id] = camera
            return True
        return False
    
    def start_all_cameras(self) -> int:
        """Start all discovered cameras"""
        available = self.discover_cameras()
        started = 0
        
        for device_id in available[: self.max_cameras]:
            if self.start_camera(device_id):
                started += 1
        
        self.running = True
        logger.info(f"Started {started}/{len(available)} cameras")
        return started
    
    def get_frames(self) -> Dict[str, np.ndarray]:
        """Get latest frames from all cameras"""
        frames = {}
        for device_id, camera in self. cameras.items():
            ret, frame = camera.read()
            if ret:
                frames[f"camera_{device_id}"] = frame
        return frames
    
    def get_stats(self) -> dict:
        """Get system and camera stats"""
        return {
            "active_cameras": len(self.cameras),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "camera_fps": {
                f"camera_{id}": cam.get_fps() 
                for id, cam in self.cameras.items()
            }
        }
    
    def stop_all(self):
        """Stop all cameras"""
        self.running = False
        for camera in self.cameras.values():
            camera.stop()
        self.cameras.clear()
        logger.info("All cameras stopped")


class WindowsPerformanceMonitor:
    """Monitor Windows system performance"""
    
    @staticmethod
    def get_gpu_info():
        """Get GPU information (NVIDIA only)"""
        import subprocess
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                gpu_util, mem_used, mem_total = result.stdout.strip().split(',')
                return {
                    "gpu_utilization": float(gpu_util),
                    "memory_used_mb": float(mem_used),
                    "memory_total_mb": float(mem_total)
                }
        except: 
            pass
        return None
    
    @staticmethod
    def print_stats(camera_manager:  WindowsMultiCameraManager):
        """Print comprehensive stats"""
        stats = camera_manager.get_stats()
        gpu_info = WindowsPerformanceMonitor.get_gpu_info()
        
        print("\n" + "="*60)
        print("WINDOWS PERFORMANCE STATS")
        print("="*60)
        print(f"Active Cameras: {stats['active_cameras']}")
        print(f"CPU Usage: {stats['cpu_percent']:.1f}%")
        print(f"RAM Usage: {stats['memory_percent']:.1f}%")
        
        if gpu_info:
            print(f"GPU Usage: {gpu_info['gpu_utilization']:.1f}%")
            print(f"GPU Memory: {gpu_info['memory_used_mb']:.0f}/{gpu_info['memory_total_mb']:.0f} MB")
        
        print("\nCamera FPS:")
        for cam, fps in stats['camera_fps']. items():
            print(f"  {cam}: {fps:.1f} FPS")
        
        print("="*60 + "\n")


# Test functions
def test_camera(device_id: int, duration: float = 3.0):
    """Test single camera for specified duration"""
    logger.info(f"Testing camera {device_id} for {duration} seconds...")
    
    camera = WindowsCamera(device_id)
    
    if not camera.start():
        return {"success": False, "error": "Failed to start camera"}
    
    # Capture frames for duration
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = camera.read()
        if ret:
            frame_count += 1
            # Could display frame here if needed
            # cv2.imshow(f'Camera {device_id}', frame)
            # cv2.waitKey(1)
        time.sleep(0.03)  # ~30fps
    
    camera.stop()
    # cv2.destroyAllWindows()
    
    actual_fps = frame_count / duration
    
    return {
        "success":  True,
        "frames_captured": frame_count,
        "duration": duration,
        "fps":  actual_fps
    }


# Main test
if __name__ == "__main__":
    print("="*60)
    print("Windows Camera Manager Test")
    print("="*60)
    
    # Discover cameras
    manager = WindowsMultiCameraManager()
    available = manager.discover_cameras()
    
    if not available:
        print("\n❌ No cameras found!")
        exit(1)
    
    print(f"\nFound {len(available)} cameras\n")
    
    # Test first camera
    print("Testing first camera...")
    result = test_camera(available[0], duration=3.0)
    
    if result["success"]: 
        print(f"\n✅ Test result: {result}")
        print(f"   Captured {result['frames_captured']} frames in {result['duration']:. 1f}s")
        print(f"   Average FPS: {result['fps']:.1f}")
    else:
        print(f"\n❌ Test failed: {result. get('error')}")
        exit(1)
    
    # Start all cameras
    print("\n" + "="*60)
    print("Starting all cameras...")
    print("="*60)
    
    started = manager.start_all_cameras()
    
    if started == 0:
        print("❌ No cameras started")
        exit(1)
    
    print(f"\n✅ {started} camera(s) started\n")
    print("Press Ctrl+C to stop.. .\n")
    
    try:
        while True:
            # Print stats every 5 seconds
            WindowsPerformanceMonitor.print_stats(manager)
            time.sleep(5)
            
    except KeyboardInterrupt: 
        print("\n\nStopping...")
    finally:
        manager.stop_all()
        print("✅ Cleanup complete")