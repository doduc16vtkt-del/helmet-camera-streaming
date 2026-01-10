"""
Video Capture Module
Module chụp video

Captures video from USB video capture devices (RF receiver output)
Chụp video từ thiết bị chụp USB (đầu ra bộ thu RF)

Author: Helmet Camera RF System
License: MIT
"""

import logging
import cv2
import threading
import queue
import time
import platform

logger = logging.getLogger(__name__)

class VideoCapture:
    """Video capture from USB devices"""
    
    def __init__(self, config):
        """
        Initialize video capture
        
        Args:
            config: System configuration dictionary
        """
        self.config = config
        self.captures = {}
        self.capture_threads = {}
        self.frame_queues = {}
        self.running = {}
    
    def start_capture(self, device_id, device_path=None):
        """
        Start capturing video from a device
        
        Args:
            device_id: Unique identifier for this capture
            device_path: Path to video device (auto-detected if None)
            
        Returns:
            bool: True if successful
        """
        if device_id in self.captures:
            logger.warning(f"Capture {device_id} already running")
            return True
        
        try:
            # Auto-detect platform and configure device path
            if device_path is None:
                if platform.system() == 'Windows':
                    # Windows uses integer device IDs
                    if isinstance(device_id, int):
                        device_path = device_id
                    else:
                        # Try to convert to int, raise error if invalid
                        try:
                            device_path = int(device_id)
                        except (ValueError, TypeError):
                            logger.error(f"Invalid device_id for Windows: {device_id}. Must be integer (0, 1, 2, ...)")
                            return False
                    logger.info(f"Windows detected: using device ID {device_path}")
                else:
                    # Linux uses device paths
                    device_path = f'/dev/video{device_id}'
                    logger.info(f"Linux detected: using device path {device_path}")
            
            # Open video capture device with platform-specific backend
            if platform.system() == 'Windows':
                # Use DirectShow backend on Windows for better performance
                cap = cv2.VideoCapture(device_path, cv2.CAP_DSHOW)
                logger.info(f"Using DirectShow backend for device {device_path}")
            else:
                # Use default backend (V4L2 on Linux)
                cap = cv2.VideoCapture(device_path)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video device {device_path}")
                return False
            
            # Configure capture
            capture_config = self.config.get('capture', {})
            
            # Set resolution
            resolution = capture_config.get('resolution', '640x480').split('x')
            width, height = int(resolution[0]), int(resolution[1])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Set FPS
            fps = capture_config.get('fps', 30)
            cap.set(cv2.CAP_PROP_FPS, fps)
            
            # Set format if supported
            fmt = capture_config.get('format', 'MJPEG')
            if fmt == 'MJPEG':
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            # Windows-specific optimizations
            if platform.system() == 'Windows':
                # Minimal buffer for low latency
                buffer_size = capture_config.get('buffer_size', 1)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
                logger.info(f"Set buffer size to {buffer_size} for low latency")
                
                # Try to enable hardware acceleration
                if capture_config.get('hardware_acceleration', True):
                    try:
                        # Check if VIDEO_ACCELERATION_ANY is available (OpenCV 4.5.1+)
                        if hasattr(cv2, 'VIDEO_ACCELERATION_ANY'):
                            cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
                            logger.info("Hardware acceleration enabled")
                        else:
                            logger.info("Hardware acceleration not available in this OpenCV version")
                    except Exception as e:
                        logger.warning(f"Could not enable hardware acceleration: {e}")
            
            self.captures[device_id] = cap
            self.frame_queues[device_id] = queue.Queue(maxsize=30)
            self.running[device_id] = True
            
            # Start capture thread
            thread = threading.Thread(
                target=self._capture_loop,
                args=(device_id,),
                daemon=True
            )
            thread.start()
            self.capture_threads[device_id] = thread
            
            logger.info(f"Started video capture {device_id} from {device_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start capture: {e}")
            return False
    
    def stop_capture(self, device_id):
        """
        Stop capturing video
        
        Args:
            device_id: Identifier for capture to stop
        """
        if device_id not in self.captures:
            return
        
        # Stop capture thread
        self.running[device_id] = False
        
        # Wait for thread to finish
        if device_id in self.capture_threads:
            self.capture_threads[device_id].join(timeout=2.0)
            del self.capture_threads[device_id]
        
        # Release capture device
        if device_id in self.captures:
            self.captures[device_id].release()
            del self.captures[device_id]
        
        # Clean up queue
        if device_id in self.frame_queues:
            del self.frame_queues[device_id]
        
        logger.info(f"Stopped video capture {device_id}")
    
    def get_frame(self, device_id):
        """
        Get latest frame from capture
        
        Args:
            device_id: Identifier for capture
            
        Returns:
            numpy.ndarray: Frame image, or None if not available
        """
        if device_id not in self.frame_queues:
            return None
        
        try:
            # Get latest frame (non-blocking)
            frame = self.frame_queues[device_id].get_nowait()
            return frame
        except queue.Empty:
            return None
    
    def _capture_loop(self, device_id):
        """
        Background thread for capturing frames
        
        Args:
            device_id: Identifier for this capture
        """
        logger.info(f"Capture loop started for {device_id}")
        cap = self.captures[device_id]
        frame_queue = self.frame_queues[device_id]
        
        while self.running.get(device_id, False):
            try:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame from {device_id}")
                    time.sleep(0.1)
                    continue
                
                # Add frame to queue (drop oldest if full)
                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()  # Remove oldest
                    except queue.Empty:
                        pass
                
                frame_queue.put(frame)
                
            except Exception as e:
                logger.error(f"Error in capture loop {device_id}: {e}")
                time.sleep(0.1)
        
        logger.info(f"Capture loop stopped for {device_id}")
    
    def is_capturing(self, device_id):
        """Check if a device is currently capturing"""
        return device_id in self.captures and self.running.get(device_id, False)
    
    def list_captures(self):
        """List all active captures"""
        return list(self.captures.keys())
