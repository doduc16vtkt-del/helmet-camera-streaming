"""
Windows Camera Manager
Quản lý Camera cho Windows

Optimized multi-camera capture for Windows using DirectShow backend
Chụp đa camera tối ưu cho Windows sử dụng DirectShow

Author: Helmet Camera RF System
License: MIT
"""

import logging
import cv2
import threading
import queue
import time
import platform
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CameraStats:
    """Statistics for a camera"""
    device_id: int
    fps: float
    frame_count: int
    dropped_frames: int
    latency_ms: float
    last_frame_time: float
    is_active: bool


class WindowsCamera:
    """
    Single camera capture with DirectShow optimization
    Chụp camera đơn với tối ưu DirectShow
    """
    
    def __init__(self, device_id: int, config: dict):
        """
        Initialize Windows camera
        
        Args:
            device_id: Camera device index (0, 1, 2, ...)
            config: Camera configuration dictionary
        """
        self.device_id = device_id
        self.config = config
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=2)  # Minimal queue for low latency
        self.running = False
        self.thread = None
        self.stats = CameraStats(
            device_id=device_id,
            fps=0.0,
            frame_count=0,
            dropped_frames=0,
            latency_ms=0.0,
            last_frame_time=0.0,
            is_active=False
        )
        self._lock = threading.Lock()
        
    def start(self) -> bool:
        """
        Start camera capture
        
        Returns:
            bool: True if successful
        """
        if self.running:
            logger.warning(f"Camera {self.device_id} already running")
            return True
        
        try:
            # Open with DirectShow backend
            self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.device_id}")
                return False
            
            # Configure camera settings
            capture_config = self.config.get('capture', {})
            
            # Set resolution
            resolution = capture_config.get('resolution', '640x480').split('x')
            width, height = int(resolution[0]), int(resolution[1])
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Set FPS
            fps = capture_config.get('fps', 30)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            
            # MJPEG format for better performance
            if capture_config.get('format', 'MJPEG') == 'MJPEG':
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            # Low-latency settings
            buffer_size = capture_config.get('buffer_size', 1)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            
            # Hardware acceleration
            if capture_config.get('hardware_acceleration', True):
                try:
                    self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
                    logger.info(f"Hardware acceleration enabled for camera {self.device_id}")
                except Exception as e:
                    logger.warning(f"Could not enable hardware acceleration: {e}")
            
            # Start capture thread
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            self.stats.is_active = True
            logger.info(f"Started camera {self.device_id} ({width}x{height} @ {fps}fps)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera {self.device_id}: {e}")
            return False
    
    def stop(self):
        """Stop camera capture"""
        if not self.running:
            return
        
        self.running = False
        
        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.stats.is_active = False
        logger.info(f"Stopped camera {self.device_id}")
    
    def get_frame(self) -> Optional[Tuple[bool, any]]:
        """
        Get latest frame from camera
        
        Returns:
            Tuple of (success, frame) or None if no frame available
        """
        try:
            frame = self.frame_queue.get_nowait()
            return (True, frame)
        except queue.Empty:
            return None
    
    def get_stats(self) -> CameraStats:
        """Get camera statistics"""
        with self._lock:
            return self.stats
    
    def _capture_loop(self):
        """Background thread for capturing frames"""
        logger.info(f"Capture loop started for camera {self.device_id}")
        
        frame_times = []
        last_stats_update = time.time()
        
        while self.running:
            try:
                start_time = time.time()
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame from camera {self.device_id}")
                    with self._lock:
                        self.stats.dropped_frames += 1
                    time.sleep(0.01)
                    continue
                
                # Calculate latency
                capture_time = time.time()
                latency_ms = (capture_time - start_time) * 1000
                
                # Add frame to queue (drop oldest if full)
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                        with self._lock:
                            self.stats.dropped_frames += 1
                    except queue.Empty:
                        pass
                
                self.frame_queue.put(frame)
                
                # Update statistics
                with self._lock:
                    self.stats.frame_count += 1
                    self.stats.latency_ms = latency_ms
                    self.stats.last_frame_time = capture_time
                
                # Calculate FPS every second
                frame_times.append(capture_time)
                if capture_time - last_stats_update >= 1.0:
                    # Remove old frame times
                    frame_times = [t for t in frame_times if capture_time - t < 1.0]
                    with self._lock:
                        self.stats.fps = len(frame_times)
                    last_stats_update = capture_time
                
            except Exception as e:
                logger.error(f"Error in capture loop for camera {self.device_id}: {e}")
                time.sleep(0.1)
        
        logger.info(f"Capture loop stopped for camera {self.device_id}")


class WindowsMultiCameraManager:
    """
    Multi-camera manager for Windows
    Quản lý đa camera cho Windows
    """
    
    def __init__(self, config: dict):
        """
        Initialize multi-camera manager
        
        Args:
            config: System configuration dictionary
        """
        self.config = config
        self.cameras: Dict[int, WindowsCamera] = {}
        self._lock = threading.Lock()
    
    def discover_cameras(self) -> List[int]:
        """
        Auto-discover available cameras
        
        Returns:
            List of available camera device IDs
        """
        logger.info("Discovering cameras...")
        available_cameras = []
        
        # Try to open cameras 0-9
        for device_id in range(10):
            try:
                cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)
                if cap.isOpened():
                    available_cameras.append(device_id)
                    # Get camera name if available
                    try:
                        backend_name = cap.getBackendName()
                        logger.info(f"Found camera {device_id} (backend: {backend_name})")
                    except:
                        logger.info(f"Found camera {device_id}")
                    cap.release()
            except Exception as e:
                logger.debug(f"No camera at index {device_id}: {e}")
        
        logger.info(f"Discovered {len(available_cameras)} cameras: {available_cameras}")
        return available_cameras
    
    def start_camera(self, device_id: int) -> bool:
        """
        Start capturing from a camera
        
        Args:
            device_id: Camera device ID
            
        Returns:
            bool: True if successful
        """
        with self._lock:
            if device_id in self.cameras:
                logger.warning(f"Camera {device_id} already started")
                return True
            
            camera = WindowsCamera(device_id, self.config)
            if camera.start():
                self.cameras[device_id] = camera
                return True
            return False
    
    def stop_camera(self, device_id: int):
        """
        Stop capturing from a camera
        
        Args:
            device_id: Camera device ID
        """
        with self._lock:
            if device_id in self.cameras:
                self.cameras[device_id].stop()
                del self.cameras[device_id]
    
    def stop_all_cameras(self):
        """Stop all cameras"""
        with self._lock:
            for camera in self.cameras.values():
                camera.stop()
            self.cameras.clear()
    
    def get_frame(self, device_id: int) -> Optional[Tuple[bool, any]]:
        """
        Get latest frame from a camera
        
        Args:
            device_id: Camera device ID
            
        Returns:
            Tuple of (success, frame) or None
        """
        with self._lock:
            if device_id in self.cameras:
                return self.cameras[device_id].get_frame()
        return None
    
    def get_all_stats(self) -> Dict[int, CameraStats]:
        """
        Get statistics for all cameras
        
        Returns:
            Dictionary mapping device_id to CameraStats
        """
        stats = {}
        with self._lock:
            for device_id, camera in self.cameras.items():
                stats[device_id] = camera.get_stats()
        return stats
    
    def get_active_cameras(self) -> List[int]:
        """Get list of active camera IDs"""
        with self._lock:
            return list(self.cameras.keys())


class WindowsPerformanceMonitor:
    """
    Performance monitoring for Windows
    Giám sát hiệu suất cho Windows
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self.stats_history = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 5.0):
        """
        Start monitoring system performance
        
        Args:
            interval: Update interval in seconds
        """
        if self.monitoring:
            logger.warning("Performance monitoring already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            self.monitor_thread = None
        logger.info("Performance monitoring stopped")
    
    def get_system_stats(self) -> dict:
        """
        Get current system statistics
        
        Returns:
            Dictionary with CPU, RAM, and GPU stats
        """
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': 0.0,
            'ram_percent': 0.0,
            'ram_used_mb': 0,
            'ram_total_mb': 0,
            'gpu_stats': []
        }
        
        try:
            import psutil
            
            # CPU usage
            stats['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            
            # RAM usage
            mem = psutil.virtual_memory()
            stats['ram_percent'] = mem.percent
            stats['ram_used_mb'] = mem.used // (1024 * 1024)
            stats['ram_total_mb'] = mem.total // (1024 * 1024)
            
        except ImportError:
            logger.warning("psutil not installed, CPU/RAM stats unavailable")
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
        
        # Try to get GPU stats
        stats['gpu_stats'] = self._get_gpu_stats()
        
        return stats
    
    def _get_gpu_stats(self) -> List[dict]:
        """
        Get GPU statistics (NVIDIA, AMD, Intel)
        
        Returns:
            List of GPU statistics dictionaries
        """
        gpu_stats = []
        
        # Try NVIDIA GPUs first
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 6:
                            gpu_stats.append({
                                'type': 'NVIDIA',
                                'index': int(parts[0]),
                                'name': parts[1],
                                'utilization': float(parts[2]),
                                'memory_used_mb': int(parts[3]),
                                'memory_total_mb': int(parts[4]),
                                'temperature_c': int(parts[5])
                            })
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.debug(f"NVIDIA GPU not available: {e}")
        
        # If no NVIDIA GPUs, could add AMD/Intel detection here
        if not gpu_stats:
            gpu_stats.append({
                'type': 'Unknown',
                'name': 'GPU detection not available',
                'utilization': 0.0
            })
        
        return gpu_stats
    
    def _monitor_loop(self, interval: float):
        """Background monitoring loop"""
        logger.info("Performance monitor loop started")
        
        while self.monitoring:
            try:
                stats = self.get_system_stats()
                self.stats_history.append(stats)
                
                # Keep only last 100 samples
                if len(self.stats_history) > 100:
                    self.stats_history = self.stats_history[-100:]
                
                # Log stats
                logger.debug(f"CPU: {stats['cpu_percent']:.1f}% | "
                           f"RAM: {stats['ram_percent']:.1f}% "
                           f"({stats['ram_used_mb']}MB / {stats['ram_total_mb']}MB)")
                
                for gpu in stats['gpu_stats']:
                    if 'utilization' in gpu:
                        logger.debug(f"GPU {gpu.get('index', 0)} ({gpu['name']}): "
                                   f"{gpu['utilization']:.1f}%")
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(interval)
        
        logger.info("Performance monitor loop stopped")
    
    def get_stats_history(self) -> List[dict]:
        """Get historical statistics"""
        return self.stats_history.copy()


# Utility functions
def test_camera(device_id: int, duration: float = 5.0) -> dict:
    """
    Test a camera for a specified duration
    
    Args:
        device_id: Camera device ID
        duration: Test duration in seconds
        
    Returns:
        Dictionary with test results
    """
    logger.info(f"Testing camera {device_id} for {duration} seconds...")
    
    config = {
        'capture': {
            'resolution': '640x480',
            'fps': 30,
            'format': 'MJPEG',
            'buffer_size': 1,
            'hardware_acceleration': True
        }
    }
    
    camera = WindowsCamera(device_id, config)
    
    if not camera.start():
        return {
            'success': False,
            'error': 'Failed to start camera'
        }
    
    # Wait for test duration
    time.sleep(duration)
    
    # Get final stats
    stats = camera.get_stats()
    camera.stop()
    
    return {
        'success': True,
        'device_id': device_id,
        'total_frames': stats.frame_count,
        'dropped_frames': stats.dropped_frames,
        'average_fps': stats.fps,
        'average_latency_ms': stats.latency_ms
    }


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Windows Camera Manager Test")
    print("=" * 60)
    
    # Discover cameras
    config = {
        'capture': {
            'resolution': '640x480',
            'fps': 30,
            'format': 'MJPEG',
            'buffer_size': 1,
            'hardware_acceleration': True
        }
    }
    
    manager = WindowsMultiCameraManager(config)
    available = manager.discover_cameras()
    
    if available:
        print(f"\nFound {len(available)} cameras")
        print("\nTesting first camera...")
        result = test_camera(available[0], duration=3.0)
        print(f"Test result: {result}")
    else:
        print("No cameras found")
