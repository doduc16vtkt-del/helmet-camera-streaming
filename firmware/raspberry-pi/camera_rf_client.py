#!/usr/bin/env python3
"""
Helmet Camera RF Client for Raspberry Pi
Camera mũ bảo hiểm RF cho Raspberry Pi

Alternative implementation using Raspberry Pi Zero W with Pi Camera
Triển khai thay thế sử dụng Raspberry Pi Zero W với Pi Camera

Author: Helmet Camera RF System
License: MIT
"""

import time
import logging
import signal
import sys
from picamera import PiCamera
from rf_controller import RFController
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CameraRFClient:
    """Main camera client class"""
    
    def __init__(self, config_file='../../configs/camera_config.yaml'):
        """Initialize camera client with configuration"""
        self.config = self.load_config(config_file)
        self.camera = None
        self.rf_controller = None
        self.running = False
        
        # Statistics
        self.frames_captured = 0
        self.frames_transmitted = 0
        self.telemetry_sent = 0
        
    def load_config(self, config_file):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Return default configuration
            return {
                'camera': {
                    'resolution': '640x480',
                    'fps': 30,
                    'encoding': 'h264'
                },
                'rf_telemetry': {
                    'channel': 76,
                    'device_id': 'HELMET_PI_01'
                }
            }
    
    def setup_camera(self):
        """Initialize Pi Camera"""
        try:
            self.camera = PiCamera()
            
            # Parse resolution
            res = self.config['camera']['resolution'].split('x')
            width, height = int(res[0]), int(res[1])
            
            self.camera.resolution = (width, height)
            self.camera.framerate = self.config['camera']['fps']
            
            # Camera settings for outdoor use
            self.camera.exposure_mode = 'auto'
            self.camera.awb_mode = 'auto'
            
            # Warm up camera
            time.sleep(2)
            
            logger.info(f"Camera initialized: {width}x{height} @ {self.camera.framerate}fps")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False
    
    def setup_rf(self):
        """Initialize RF controller"""
        try:
            self.rf_controller = RFController(
                channel=self.config['rf_telemetry']['channel'],
                device_id=self.config['rf_telemetry']['device_id']
            )
            
            if self.rf_controller.begin():
                logger.info("RF controller initialized")
                return True
            else:
                logger.error("RF controller initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"RF setup failed: {e}")
            return False
    
    def capture_and_stream(self):
        """Main capture and streaming loop"""
        try:
            # Start camera preview/recording
            # For RF transmission, we would encode to appropriate format
            # and send via RF transmitter hardware
            
            logger.info("Starting video capture and streaming...")
            
            # In a real implementation:
            # 1. Camera captures frames
            # 2. Frames are encoded (H.264 or similar)
            # 3. Encoded data is sent via USB RF transmitter
            # 4. For analog, camera CVBS output goes directly to RF TX
            
            # For this demo, we'll simulate the process
            while self.running:
                # Capture frame (simulated)
                self.frames_captured += 1
                
                # Transmit frame via RF (simulated)
                # In reality, this would interface with RF hardware
                self.frames_transmitted += 1
                
                # Send telemetry periodically (every second)
                if self.frames_captured % self.config['camera']['fps'] == 0:
                    self.send_telemetry()
                
                # Respect frame rate
                time.sleep(1.0 / self.config['camera']['fps'])
                
        except Exception as e:
            logger.error(f"Error in capture loop: {e}")
            self.running = False
    
    def send_telemetry(self):
        """Send telemetry data via RF"""
        try:
            telemetry_data = {
                'device_id': self.config['rf_telemetry']['device_id'],
                'battery_voltage': self.get_battery_voltage(),
                'battery_percent': self.get_battery_percent(),
                'temperature': self.get_cpu_temperature(),
                'uptime': time.time() - self.start_time,
                'frames_captured': self.frames_captured,
                'frames_transmitted': self.frames_transmitted
            }
            
            if self.rf_controller.send_telemetry(telemetry_data):
                self.telemetry_sent += 1
                logger.debug(f"Telemetry sent: {telemetry_data['battery_percent']}% battery")
            
        except Exception as e:
            logger.error(f"Failed to send telemetry: {e}")
    
    def get_battery_voltage(self):
        """Read battery voltage"""
        # Implementation would read from ADC or battery monitor IC
        # For simulation, return default value
        return 11.5
    
    def get_battery_percent(self):
        """Calculate battery percentage"""
        voltage = self.get_battery_voltage()
        # For 3S LiPo: 12.6V = 100%, 9.9V = 0%
        max_v = 12.6
        min_v = 9.9
        percent = ((voltage - min_v) / (max_v - min_v)) * 100
        return max(0, min(100, int(percent)))
    
    def get_cpu_temperature(self):
        """Read Raspberry Pi CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
            return temp
        except:
            return 0.0
    
    def start(self):
        """Start the camera client"""
        logger.info("=" * 50)
        logger.info("Helmet Camera RF Client Starting")
        logger.info("Hệ thống Camera Mũ Bảo Hiểm RF")
        logger.info("=" * 50)
        
        # Setup components
        if not self.setup_camera():
            logger.error("Failed to initialize camera")
            return False
        
        if not self.setup_rf():
            logger.error("Failed to initialize RF")
            return False
        
        # Send initial device info
        self.rf_controller.send_device_info(
            self.config['rf_telemetry']['device_id'],
            "1.0.0"
        )
        
        # Start streaming
        self.running = True
        self.start_time = time.time()
        
        logger.info("System ready - Video streaming active")
        logger.info("Hệ thống sẵn sàng - Đang truyền video")
        
        try:
            self.capture_and_stream()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the camera client"""
        logger.info("Stopping camera client...")
        self.running = False
        
        if self.camera:
            self.camera.close()
        
        if self.rf_controller:
            self.rf_controller.close()
        
        logger.info(f"Statistics:")
        logger.info(f"  Frames captured: {self.frames_captured}")
        logger.info(f"  Frames transmitted: {self.frames_transmitted}")
        logger.info(f"  Telemetry packets sent: {self.telemetry_sent}")
        logger.info("Shutdown complete")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Signal received, shutting down...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start client
    client = CameraRFClient()
    client.start()

if __name__ == "__main__":
    main()
