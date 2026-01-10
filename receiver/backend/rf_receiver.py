"""
RF Receiver Module
Module thu tín hiệu RF

Manages RF video receivers and channel selection
Quản lý bộ thu video RF và chọn kênh

Author: Helmet Camera RF System
License: MIT
"""

import logging
import serial
import time

logger = logging.getLogger(__name__)

class RFReceiver:
    """RF video receiver management"""
    
    def __init__(self, config):
        """
        Initialize RF receiver
        
        Args:
            config: System configuration dictionary
        """
        self.config = config
        self.receivers = {}
        self.current_channels = {}
        self.initialized = False
    
    def initialize(self):
        """Initialize RF receivers"""
        try:
            logger.info("Initializing RF receivers...")
            
            # Setup each receiver device
            receiver_devices = self.config.get('receiver', {}).get('receiver_devices', [])
            
            if not receiver_devices:
                logger.warning("No receiver devices configured")
                # Setup default single receiver
                self.receivers['default'] = {
                    'device': '/dev/video0',
                    'channels': list(range(1, 9)),
                    'current_channel': 1
                }
            else:
                for rx_config in receiver_devices:
                    rx_name = rx_config.get('name', 'RX_UNKNOWN')
                    self.receivers[rx_name] = {
                        'device': rx_config.get('device'),
                        'channels': rx_config.get('channels', []),
                        'current_channel': rx_config.get('channels', [1])[0]
                    }
                    logger.info(f"Configured receiver {rx_name} on {rx_config.get('device')}")
            
            self.initialized = True
            logger.info(f"Initialized {len(self.receivers)} RF receiver(s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RF receivers: {e}")
            return False
    
    def set_channel(self, receiver_name, channel):
        """
        Set RF channel for a receiver
        
        Args:
            receiver_name: Name of receiver
            channel: Channel number (1-8)
            
        Returns:
            bool: True if successful
        """
        if receiver_name not in self.receivers:
            logger.error(f"Receiver {receiver_name} not found")
            return False
        
        if channel < 1 or channel > 8:
            logger.error(f"Invalid channel {channel}, must be 1-8")
            return False
        
        try:
            # In a real implementation, this would:
            # 1. Send command to RF receiver module to change channel
            # 2. Wait for channel switch to complete
            # 3. Verify signal quality
            
            # For demonstration, just update state
            self.receivers[receiver_name]['current_channel'] = channel
            self.current_channels[receiver_name] = channel
            
            logger.info(f"Receiver {receiver_name} switched to channel {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set channel: {e}")
            return False
    
    def get_signal_strength(self, receiver_name):
        """
        Get signal strength (RSSI) for a receiver
        
        Args:
            receiver_name: Name of receiver
            
        Returns:
            int: RSSI value in dBm, or None if not available
        """
        if receiver_name not in self.receivers:
            return None
        
        # In real implementation, query RF receiver for RSSI
        # For now, return simulated value
        return -75  # dBm
    
    def scan_channels(self, receiver_name):
        """
        Scan all channels and return signal strengths
        
        Args:
            receiver_name: Name of receiver
            
        Returns:
            dict: Channel to RSSI mapping
        """
        if receiver_name not in self.receivers:
            return {}
        
        channel_rssi = {}
        available_channels = self.receivers[receiver_name].get('channels', [])
        
        # In real implementation:
        # 1. Iterate through each channel
        # 2. Measure RSSI for each
        # 3. Return results
        
        # Simulated scan results
        for channel in available_channels:
            # Simulate varying signal strength
            channel_rssi[channel] = -90 + (channel * 2)  # dBm
        
        return channel_rssi
    
    def get_receiver_info(self, receiver_name):
        """Get information about a receiver"""
        if receiver_name in self.receivers:
            return self.receivers[receiver_name]
        return None
    
    def list_receivers(self):
        """List all configured receivers"""
        return list(self.receivers.keys())
