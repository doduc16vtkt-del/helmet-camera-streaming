#!/usr/bin/env python3
"""
RF Controller Module for Raspberry Pi
Module điều khiển RF cho Raspberry Pi

Handles RF transmission via nRF24L01+ module
Xử lý truyền RF qua module nRF24L01+

Author: Helmet Camera RF System
License: MIT
"""

import time
import logging
from RF24 import RF24, RF24_PA_MAX, RF24_250KBPS

logger = logging.getLogger(__name__)

class RFController:
    """RF24 controller for telemetry"""
    
    def __init__(self, channel=76, device_id="HELMET_PI_01"):
        """
        Initialize RF controller
        
        Args:
            channel: RF channel (0-125)
            device_id: Unique device identifier
        """
        self.channel = channel
        self.device_id = device_id
        self.radio = None
        self.address = b"HLMT1"  # 5-byte address
        
        # Statistics
        self.packets_sent = 0
        self.packets_failed = 0
        
        # GPIO pins for nRF24L01+ on Raspberry Pi
        # CE = GPIO 22, CSN = GPIO 8 (CE0)
        self.ce_pin = 22
        self.csn_pin = 0  # SPI CE0
    
    def begin(self):
        """Initialize nRF24L01+ module"""
        try:
            # Initialize radio
            # RF24(CE_PIN, CSN_PIN, SPI_SPEED)
            self.radio = RF24(self.ce_pin, self.csn_pin, 8000000)
            
            if not self.radio.begin():
                logger.error("nRF24L01+ initialization failed")
                return False
            
            # Configure radio
            self.radio.setPALevel(RF24_PA_MAX)  # Maximum power
            self.radio.setDataRate(RF24_250KBPS)  # 250kbps for longer range
            self.radio.setChannel(self.channel)
            self.radio.setAutoAck(True)
            self.radio.enableDynamicPayloads()
            self.radio.setRetries(5, 15)  # 5*250us delay, 15 retries
            
            # Open writing pipe
            self.radio.openWritingPipe(self.address)
            self.radio.stopListening()  # TX mode
            
            logger.info(f"nRF24L01+ initialized on channel {self.channel}")
            return True
            
        except Exception as e:
            logger.error(f"nRF24L01+ initialization error: {e}")
            return False
    
    def send_telemetry(self, data):
        """
        Send telemetry data
        
        Args:
            data: Dictionary containing telemetry data
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert data to bytes
            # In production, use proper protocol (e.g., protobuf, msgpack)
            payload = self._pack_telemetry(data)
            
            # Send packet
            success = self.radio.write(payload)
            
            if success:
                self.packets_sent += 1
                logger.debug(f"Telemetry sent: {self.packets_sent}")
            else:
                self.packets_failed += 1
                logger.warning(f"Telemetry failed: {self.packets_failed}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send telemetry: {e}")
            return False
    
    def send_device_info(self, device_id, version):
        """
        Send device information
        
        Args:
            device_id: Device identifier
            version: Firmware version
        """
        try:
            info = f"INFO:{device_id}:{version}".encode('utf-8')
            success = self.radio.write(info)
            
            if success:
                logger.info(f"Device info sent: {device_id} v{version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send device info: {e}")
            return False
    
    def send_alert(self, alert_code):
        """
        Send alert/warning
        
        Args:
            alert_code: Alert code number
        """
        try:
            alert = f"ALERT:{alert_code}:{int(time.time())}".encode('utf-8')
            success = self.radio.write(alert)
            
            if success:
                logger.warning(f"Alert sent: {alert_code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def _pack_telemetry(self, data):
        """
        Pack telemetry data into bytes
        
        Args:
            data: Dictionary with telemetry data
            
        Returns:
            bytes: Packed data
        """
        # Simple text-based protocol for demonstration
        # Production should use binary protocol (struct, protobuf, etc.)
        payload = (
            f"TELEM:"
            f"{data.get('device_id', 'UNKNOWN')}:"
            f"{data.get('battery_voltage', 0.0):.2f}:"
            f"{data.get('battery_percent', 0)}:"
            f"{data.get('temperature', 0.0):.1f}:"
            f"{data.get('uptime', 0):.0f}"
        )
        
        return payload.encode('utf-8')
    
    def get_statistics(self):
        """Get transmission statistics"""
        return {
            'packets_sent': self.packets_sent,
            'packets_failed': self.packets_failed,
            'success_rate': (
                self.packets_sent / (self.packets_sent + self.packets_failed) * 100
                if (self.packets_sent + self.packets_failed) > 0 else 0
            )
        }
    
    def close(self):
        """Close RF controller"""
        if self.radio:
            logger.info("Closing RF controller")
            stats = self.get_statistics()
            logger.info(f"RF Statistics: {stats}")

if __name__ == "__main__":
    # Test code
    logging.basicConfig(level=logging.DEBUG)
    
    rf = RFController(channel=76, device_id="TEST_01")
    if rf.begin():
        print("RF Controller initialized successfully")
        
        # Send test telemetry
        test_data = {
            'device_id': 'TEST_01',
            'battery_voltage': 11.5,
            'battery_percent': 75,
            'temperature': 45.2,
            'uptime': 123.4
        }
        
        rf.send_telemetry(test_data)
        rf.close()
